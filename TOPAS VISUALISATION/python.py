#!/usr/bin/env python3
"""
TOPAS 3D Visualization Tool

A CLI tool for visualizing 3D heatmap data from TOPAS/Geant4 simulation CSV files.
Supports multiple coordinate systems (Cartesian, Spherical, Cylindrical) and generates
interactive and static visualizations.

Author: Medical Physics Visualization Tool
Date: March 2026
"""

import argparse
import sys
import os
from typing import Tuple, Optional
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go
import warnings


class CoordinateTransformer:
    """Handles coordinate system transformations for 3D visualization data."""

    @staticmethod
    def spherical_to_cartesian(r: np.ndarray, theta: np.ndarray, phi: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Convert spherical coordinates to Cartesian coordinates.

        Args:
            r (np.ndarray): Radial distance
            theta (np.ndarray): Polar angle (angle from z-axis) in radians (0 ≤ θ ≤ π)
            phi (np.ndarray): Azimuthal angle in radians (0 ≤ φ < 2π)

        Returns:
            Tuple[np.ndarray, np.ndarray, np.ndarray]: x, y, z Cartesian coordinates

        Notes:
            Spherical to Cartesian transformation:
            - x = r * sin(θ) * cos(φ)
            - y = r * sin(θ) * sin(φ)
            - z = r * cos(θ)
        """
        x = r * np.sin(theta) * np.cos(phi)
        y = r * np.sin(theta) * np.sin(phi)
        z = r * np.cos(theta)
        return x, y, z

    @staticmethod
    def cylindrical_to_cartesian(rho: np.ndarray, phi: np.ndarray, z: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Convert cylindrical coordinates to Cartesian coordinates.

        Args:
            rho (np.ndarray): Radial distance from z-axis
            phi (np.ndarray): Azimuthal angle in radians
            z (np.ndarray): Height along z-axis

        Returns:
            Tuple[np.ndarray, np.ndarray, np.ndarray]: x, y, z Cartesian coordinates

        Notes:
            Cylindrical to Cartesian transformation:
            - x = ρ * cos(φ)
            - y = ρ * sin(φ)
            - z = z
        """
        x = rho * np.cos(phi)
        y = rho * np.sin(phi)
        return x, y, z


class DataLoader:
    """Handles loading and preprocessing of TOPAS simulation CSV files."""

    @staticmethod
    def load_csv(filepath: str) -> pd.DataFrame:
        """
        Load a CSV file with TOPAS-style headers (lines starting with #).

        Args:
            filepath (str): Path to the CSV file

        Returns:
            pd.DataFrame: Loaded data with columns for coordinates and values

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file is empty or malformed
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Input file not found: {filepath}")

        try:
            # Read CSV, skipping comment lines starting with #
            df = pd.read_csv(filepath, comment='#', skipinitialspace=True)

            if df.empty:
                raise ValueError("CSV file is empty or contains no data rows")

            # Check if we have at least 4 columns (x, y, z, value)
            if df.shape[1] < 4:
                raise ValueError(f"CSV file must have at least 4 columns, found {df.shape[1]}")

            # Rename columns if they don't have proper names
            if df.columns[0].startswith('Unnamed') or not isinstance(df.columns[0], str):
                df.columns = ['coord1', 'coord2', 'coord3', 'value'] + list(df.columns[4:])

            return df

        except pd.errors.EmptyDataError:
            raise ValueError("CSV file is empty")
        except pd.errors.ParserError as e:
            raise ValueError(f"Error parsing CSV file: {str(e)}")

    @staticmethod
    def extract_coordinates(df: pd.DataFrame, coord_system: str = 'cartesian') -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Extract and transform coordinates from the dataframe.

        Args:
            df (pd.DataFrame): Input dataframe with coordinate columns
            coord_system (str): Coordinate system type ('cartesian', 'spherical', 'cylindrical')

        Returns:
            Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]: x, y, z coordinates and values

        Raises:
            ValueError: If coordinate system is invalid or data is malformed
        """
        try:
            # Extract first three columns as coordinates and fourth as value
            coord1 = df.iloc[:, 0].values   # Assume first column is the first coordinate (x, r, or ρ)
            coord2 = df.iloc[:, 1].values   # Assume second column is the second coordinate (y, φ, or φ)
            coord3 = df.iloc[:, 2].values   # Assume third column is the third coordinate (z, θ, or z)
            values = df.iloc[:, 3].values   # Assume fourth column is the data value

            # Remove any NaN values
            mask = ~(np.isnan(coord1) | np.isnan(coord2) | np.isnan(coord3) | np.isnan(values))
            coord1, coord2, coord3, values = coord1[mask], coord2[mask], coord3[mask], values[mask]

            if len(coord1) == 0:
                raise ValueError("No valid data points found after removing NaN values")

            transformer = CoordinateTransformer()

            if coord_system.lower() == 'cartesian' or coord_system.lower() == 'rectangular':
                x, y, z = coord1, coord2, coord3 # No transformation needed
            elif coord_system.lower() == 'spherical':
                x, y, z = transformer.spherical_to_cartesian(coord1, coord3, coord2) # Note: θ is the third column, φ is the second column
            elif coord_system.lower() == 'cylindrical':
                x, y, z = transformer.cylindrical_to_cartesian(coord1, coord2, coord3) # Note: ρ is the first column, φ is the second column, z is the third column
            else:
                raise ValueError(f"Invalid coordinate system: {coord_system}. "
                               f"Must be 'cartesian', 'spherical', or 'cylindrical'")

            return x, y, z, values

        except (IndexError, KeyError) as e:
            raise ValueError(f"Error extracting coordinates: {str(e)}")


class Visualizer:
    """Handles creation of 3D visualizations using Matplotlib and Plotly."""

    @staticmethod
    def plot_matplotlib(x: np.ndarray, y: np.ndarray, z: np.ndarray, values: np.ndarray,
                       title: str = "TOPAS 3D Visualization",
                       save_path: Optional[str] = None,
                       show: bool = True,
                       scale_power: float = 3.0) -> None:
        """
        Create a 3D scatter plot using Matplotlib.

        Args:
            x (np.ndarray): X coordinates
            y (np.ndarray): Y coordinates
            z (np.ndarray): Z coordinates
            values (np.ndarray): Data values for coloring and sizing
            title (str): Plot title
            save_path (Optional[str]): Path to save the figure (PNG/PDF)
            show (bool): Whether to display the plot interactively
            scale_power (float): Power for marker size scaling (default: 3.0 for cubic)
        """
        fig = plt.figure(figsize=(12, 9))
        ax = fig.add_subplot(111, projection='3d')

        # Normalize values for color mapping
        norm_values = (values - values.min()) / (values.max() - values.min() + 1e-10)

        # Scale marker sizes using power scaling to control near-zero visibility
        # Higher powers make values approaching zero progressively much smaller
        # Size range: 5 (near-zero) to 250 (maximum)
        sizes = 5 + 245 * (norm_values ** scale_power)

        # Create scatter plot
        scatter = ax.scatter(x, y, z, c=values, s=sizes, cmap='hot',
                           alpha=0.6, edgecolors='k', linewidth=0.5)

        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax, pad=0.1, shrink=0.8)
        cbar.set_label('Value (Dose/Fluence)', rotation=270, labelpad=20)

        # Labels and title
        ax.set_xlabel('X (cm)', fontsize=10)
        ax.set_ylabel('Y (cm)', fontsize=10)
        ax.set_zlabel('Z (cm)', fontsize=10)
        ax.set_title(title, fontsize=14, fontweight='bold')

        plt.tight_layout()

        # Save if path provided
        if save_path:
            try:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                print(f"✓ Static plot saved: {save_path}")
            except Exception as e:
                print(f"✗ Error saving static plot: {str(e)}", file=sys.stderr)

        # Show if requested
        if show:
            plt.show()
        else:
            plt.close()

    @staticmethod
    def plot_plotly(x: np.ndarray, y: np.ndarray, z: np.ndarray, values: np.ndarray,
                   title: str = "TOPAS 3D Interactive Visualization",
                   save_path: Optional[str] = None,
                   scale_power: float = 3.0) -> None:
        """
        Create an interactive 3D scatter plot using Plotly.

        Args:
            x (np.ndarray): X coordinates
            y (np.ndarray): Y coordinates
            z (np.ndarray): Z coordinates
            values (np.ndarray): Data values for coloring and sizing
            title (str): Plot title
            save_path (Optional[str]): Path to save the HTML file
            scale_power (float): Power for marker size scaling (default: 3.0 for cubic)
        """
        # Normalize values for marker sizing using power scaling
        # Higher powers make values approaching zero progressively much smaller
        norm_values = (values - values.min()) / (values.max() - values.min() + 1e-10)
        # Size range: 0.5 (near-zero) to 15 (maximum)
        sizes = 0.5 + 14.5 * (norm_values ** scale_power)

        # Create 3D scatter plot
        fig = go.Figure(data=[go.Scatter3d(
            x=x, y=y, z=z,
            mode='markers',
            marker=dict(
                size=sizes,
                color=values,
                colorscale='Hot',
                showscale=True,
                colorbar=dict(
                    title="Value<br>(Dose/Fluence)",
                    thickness=20,
                    len=0.7
                ),
                line=dict(color='black', width=0.5),
                opacity=0.8
            ),
            text=[f'Value: {v:.4e}<br>X: {xi:.3f}<br>Y: {yi:.3f}<br>Z: {zi:.3f}'
                  for xi, yi, zi, v in zip(x, y, z, values)],
            hovertemplate='%{text}<extra></extra>'
        )])

        # Update layout
        fig.update_layout(
            title=dict(text=title, font=dict(size=16, family='Arial Black')),
            scene=dict(
                xaxis_title='X (cm)',
                yaxis_title='Y (cm)',
                zaxis_title='Z (cm)',
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.3)
                )
            ),
            width=1000,
            height=800,
            showlegend=False
        )

        # Save HTML file
        if save_path:
            try:
                fig.write_html(save_path)
                print(f"✓ Interactive HTML saved: {save_path}")
            except Exception as e:
                print(f"✗ Error saving HTML file: {str(e)}", file=sys.stderr)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments for the TOPAS visualization tool.

    Returns:
        argparse.Namespace: Parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description='TOPAS 3D Visualization Tool - Visualize simulation data with coordinate transformations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Cartesian coordinates (default)
  python python.py input.csv

  # Spherical coordinates with custom output
  python python.py input.csv -o results -c spherical

  # Cylindrical coordinates
  python python.py input.csv --coordinate-system cylindrical

  # Remove zero-value points entirely
  python python.py input.csv --remove-zeros

  # Use linear scaling instead of cubic
  python python.py input.csv --scale-power 1.0

  # Use quadratic scaling
  python python.py input.csv -s 2.0

  # Save as PDF instead of PNG
  python python.py input.csv -o output.pdf
        """
    )

    parser.add_argument('input_file', type=str,
                       help='Path to input CSV file with TOPAS simulation data')

    parser.add_argument('-o', '--output', type=str, default=None,
                       help='Output filename base (without extension) or full path with extension')

    parser.add_argument('-c', '--coordinate-system', type=str,
                       choices=['cartesian', 'rectangular', 'spherical', 'cylindrical'],
                       default='cartesian',
                       help='Input coordinate system (default: cartesian)')

    parser.add_argument('--display', action='store_false', dest='no_display',
                       help='Enable interactive Matplotlib display')

    parser.add_argument('--remove-zeros', action='store_true',
                       help='Remove points with zero values from visualization')

    parser.add_argument('-s', '--scale-power', type=float, default=3.0,
                       help='Power for marker size scaling (default: 3.0 for cubic). '
                            'Use 1.0 for linear, 2.0 for quadratic, 3.0 for cubic, etc. '
                            'Higher values make small values progressively smaller.')

    return parser.parse_args()


def generate_output_filenames(input_file: str, output_arg: Optional[str]) -> Tuple[str, str]:
    """
    Generate output filenames for static and interactive plots.

    Args:
        input_file (str): Input CSV filename
        output_arg (Optional[str]): User-provided output argument

    Returns:
        Tuple[str, str]: Static plot filename, HTML filename
    """
    if output_arg:
        # Check if output_arg has an extension
        if output_arg.endswith('.png') or output_arg.endswith('.pdf'):
            static_file = output_arg
            base = os.path.splitext(output_arg)[0]
            html_file = f"{base}.html"
        else:
            # Use as base name
            static_file = f"{output_arg}.png"
            html_file = f"{output_arg}.html"
    else:
        # Generate from input filename
        base = os.path.splitext(os.path.basename(input_file))[0]
        static_file = f"{base}_visualization.png"
        html_file = f"{base}_interactive.html"

    return static_file, html_file


def main():
    """Main execution function for the TOPAS visualization tool."""
    try:
        # Parse arguments
        args = parse_arguments()

        print("=" * 60)
        print("TOPAS 3D Visualization Tool")
        print("=" * 60)
        print(f"Input file: {args.input_file}")
        print(f"Coordinate system: {args.coordinate_system}")
        print(f"Marker size scaling: power of {args.scale_power}")
        print()

        # Load data
        print("Loading data...")
        loader = DataLoader()
        df = loader.load_csv(args.input_file)
        print(f"✓ Loaded {len(df)} data points")

        # Extract and transform coordinates
        print(f"Transforming coordinates ({args.coordinate_system} → Cartesian)...")
        x, y, z, values = loader.extract_coordinates(df, args.coordinate_system)
        print(f"✓ Processed {len(x)} valid points")
        print(f"  Value range: [{values.min():.4e}, {values.max():.4e}]")

        # Filter out zeros if requested
        if args.remove_zeros:
            non_zero_mask = values != 0
            zero_count = np.sum(~non_zero_mask)
            x, y, z, values = x[non_zero_mask], y[non_zero_mask], z[non_zero_mask], values[non_zero_mask]
            print(f"✓ Removed {zero_count} zero-value points")
            print(f"  Remaining points: {len(x)}")
            if len(x) == 0:
                raise ValueError("No non-zero points remaining after filtering")
        else:
            zero_count = np.sum(values == 0)
            if zero_count > 0:
                print(f"  Note: {zero_count} zero-value points will be shown with smaller markers")
        print()

        # Generate output filenames
        static_file, html_file = generate_output_filenames(args.input_file, args.output)

        # Create visualizations
        print("Generating visualizations...")
        visualizer = Visualizer()

        # Matplotlib static plot
        visualizer.plot_matplotlib(
            x, y, z, values,
            title=f"TOPAS 3D Visualization - {os.path.basename(args.input_file)}",
            save_path=static_file,
            show=not args.no_display,
            scale_power=args.scale_power
        )

        # Plotly interactive plot
        visualizer.plot_plotly(
            x, y, z, values,
            title=f"TOPAS Interactive 3D Visualization - {os.path.basename(args.input_file)}",
            save_path=html_file,
            scale_power=args.scale_power
        )

        print()
        print("=" * 60)
        print("✓ Visualization complete!")
        print("=" * 60)

    except FileNotFoundError as e:
        print(f"✗ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"✗ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


# ============================================================================
# UNIT TESTS
# ============================================================================

def run_tests():
    """Run unit tests for coordinate transformations."""
    print("\n" + "=" * 60)
    print("Running Unit Tests")
    print("=" * 60 + "\n")

    transformer = CoordinateTransformer()
    test_passed = 0
    test_failed = 0

    # Test 1: Spherical to Cartesian - Point on positive z-axis
    print("Test 1: Spherical to Cartesian (r=1, θ=0, φ=0) → (0, 0, 1)")
    r, theta, phi = np.array([1.0]), np.array([0.0]), np.array([0.0])
    x, y, z = transformer.spherical_to_cartesian(r, theta, phi)
    if np.allclose([x[0], y[0], z[0]], [0, 0, 1], atol=1e-10):
        print("  ✓ PASSED\n")
        test_passed += 1
    else:
        print(f"  ✗ FAILED: Got ({x[0]}, {y[0]}, {z[0]})\n")
        test_failed += 1

    # Test 2: Spherical to Cartesian - Point on positive x-axis
    print("Test 2: Spherical to Cartesian (r=1, θ=π/2, φ=0) → (1, 0, 0)")
    r = np.array([1.0])
    theta = np.array([np.pi/2])
    phi = np.array([0.0])
    x, y, z = transformer.spherical_to_cartesian(r, theta, phi)
    if np.allclose([x[0], y[0], z[0]], [1, 0, 0], atol=1e-10):
        print("  ✓ PASSED\n")
        test_passed += 1
    else:
        print(f"  ✗ FAILED: Got ({x[0]}, {y[0]}, {z[0]})\n")
        test_failed += 1

    # Test 3: Spherical to Cartesian - Point on positive y-axis
    print("Test 3: Spherical to Cartesian (r=1, θ=π/2, φ=π/2) → (0, 1, 0)")
    r = np.array([1.0])
    theta = np.array([np.pi/2])
    phi = np.array([np.pi/2])
    x, y, z = transformer.spherical_to_cartesian(r, theta, phi)
    if np.allclose([x[0], y[0], z[0]], [0, 1, 0], atol=1e-10):
        print("  ✓ PASSED\n")
        test_passed += 1
    else:
        print(f"  ✗ FAILED: Got ({x[0]}, {y[0]}, {z[0]})\n")
        test_failed += 1

    # Test 4: Cylindrical to Cartesian - Point on positive x-axis
    print("Test 4: Cylindrical to Cartesian (ρ=1, φ=0, z=0) → (1, 0, 0)")
    rho = np.array([1.0])
    phi = np.array([0.0])
    z_cyl = np.array([0.0])
    x, y, z = transformer.cylindrical_to_cartesian(rho, phi, z_cyl)
    if np.allclose([x[0], y[0], z[0]], [1, 0, 0], atol=1e-10):
        print("  ✓ PASSED\n")
        test_passed += 1
    else:
        print(f"  ✗ FAILED: Got ({x[0]}, {y[0]}, {z[0]})\n")
        test_failed += 1

    # Test 5: Cylindrical to Cartesian - Point on positive y-axis with z
    print("Test 5: Cylindrical to Cartesian (ρ=2, φ=π/2, z=5) → (0, 2, 5)")
    rho = np.array([2.0])
    phi = np.array([np.pi/2])
    z_cyl = np.array([5.0])
    x, y, z = transformer.cylindrical_to_cartesian(rho, phi, z_cyl)
    if np.allclose([x[0], y[0], z[0]], [0, 2, 5], atol=1e-10):
        print("  ✓ PASSED\n")
        test_passed += 1
    else:
        print(f"  ✗ FAILED: Got ({x[0]}, {y[0]}, {z[0]})\n")
        test_failed += 1

    # Test 6: Vectorized operations
    print("Test 6: Vectorized cylindrical transformation (multiple points)")
    rho = np.array([1.0, 2.0, 3.0])
    phi = np.array([0.0, np.pi/2, np.pi])
    z_cyl = np.array([0.0, 1.0, 2.0])
    x, y, z = transformer.cylindrical_to_cartesian(rho, phi, z_cyl)
    expected_x = np.array([1.0, 0.0, -3.0])
    expected_y = np.array([0.0, 2.0, 0.0])
    expected_z = np.array([0.0, 1.0, 2.0])
    if np.allclose(x, expected_x, atol=1e-10) and np.allclose(y, expected_y, atol=1e-10) and np.allclose(z, expected_z, atol=1e-10):
        print("  ✓ PASSED\n")
        test_passed += 1
    else:
        print(f"  ✗ FAILED\n")
        test_failed += 1

    # Summary
    print("=" * 60)
    print(f"Test Summary: {test_passed} passed, {test_failed} failed")
    print("=" * 60 + "\n")

    return test_failed == 0


if __name__ == "__main__":
    # Check if running tests
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        success = run_tests()
        sys.exit(0 if success else 1)
    else:
        main()
