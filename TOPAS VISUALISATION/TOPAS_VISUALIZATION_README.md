# TOPAS 3D Visualization Tool

A comprehensive Python CLI tool for visualizing 3D heatmap data from TOPAS/Geant4 simulation outputs with support for multiple coordinate systems and interactive visualizations.

## Features

✨ **Core Capabilities**:
- Read TOPAS CSV files with `#` comment headers
- Support for three coordinate systems: Cartesian, Spherical, and Cylindrical
- Automatic coordinate transformation to Cartesian for visualization
- Dual-scale visualization: marker size AND color represent data values

📊 **Triple Output Format**:
1. **Interactive Matplotlib Window**: Immediate 3D visualization (pop-up)
2. **Static PNG/PDF Export**: High-resolution publication-ready figures
3. **Interactive HTML**: Plotly-based 3D visualization for browser viewing

🛡️ **Production-Ready**:
- Comprehensive error handling
- Unit test suite included
- Google-style docstrings
- Modular, maintainable code structure

---

## Installation

### Required Dependencies
```bash
pip install numpy pandas matplotlib plotly
```

### Verify Installation
```bash
python python.py --test
```
This runs the unit test suite to verify coordinate transformations.

---

## Usage

### Basic Syntax
```bash
python python.py <input_file> [options]
```

### Command-Line Arguments

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `input_file` | - | Path to TOPAS CSV file (required) | - |
| `--output` | `-o` | Output filename base or full path | Auto-generated |
| `--coordinate-system` | `-c` | Input coordinate system | `cartesian` |
| `--display` | - | Enable matplotlib popup (default: disabled) | `False` |
| `--remove-zeros` | - | Remove zero-value points entirely | `False` || `--scale-power` | `-s` | Power for marker size scaling | `3.0` |
### Coordinate Systems

- **`cartesian`** or **`rectangular`**: Standard $(x, y, z)$ coordinates
- **`spherical`**: $(r, \theta, \phi)$ where:
  - $r$ = radial distance
  - $\theta$ = polar angle from z-axis (radians)
  - $\phi$ = azimuthal angle (radians)
- **`cylindrical`**: $(\rho, \phi, z)$ where:
  - $\rho$ = radial distance from z-axis
  - $\phi$ = azimuthal angle (radians)
  - $z$ = height

---

## Examples

### Example 1: Cartesian Coordinates (Default)
```bash
# Uses default Cartesian coordinate system
python python.py sample_topas_data.csv

# Outputs:
# - sample_topas_data_visualization.png
# - sample_topas_data_interactive.html
# + Interactive matplotlib window
```

### Example 2: Spherical Coordinates with Custom Output
```bash
python python.py sample_spherical_data.csv -c spherical -o fluence_results

# Outputs:
# - fluence_results.png
# - fluence_results.html
```

### Example 3: Cylindrical Coordinates
```bash
python python.py cylindrical_dose.csv --coordinate-system cylindrical -o dose_cyl
```

### Example 4: Save as PDF Instead of PNG
```bash
python python.py input.csv -o results.pdf

# Outputs:
# - results.pdf
# - results.html
```

### Example 5: Remove Zero-Value Points
```bash
# Remove all points with zero values from visualization
python python.py data.csv --remove-zeros
```

### Example 6: Enable Interactive Display
```bash
# Show matplotlib popup window (disabled by default)
python python.py data.csv --display
```

### Example 7: Custom Marker Size Scaling
```bash
# Use linear scaling (power = 1.0) - all points proportionally sized
python python.py data.csv --scale-power 1.0

# Use quadratic scaling (power = 2.0) - moderate reduction of small values
python python.py data.csv -s 2.0

# Use quartic scaling (power = 4.0) - aggressive reduction of small values
python python.py data.csv -s 4.0
```

---

## Input CSV Format

### File Structure
```csv
# Comment line 1 (metadata)
# Comment line 2 (units)
# Any lines starting with # are ignored
x, y, z, value
0.0, 0.0, 0.0, 1.234e-10
1.0, 0.0, 0.0, 2.456e-10
...
```

### Requirements
- Comment lines must start with `#`
- At least 4 columns: 3 coordinates + 1 value
- Values can be in scientific notation
- Column headers are optional (auto-generated if missing)

---

## Coordinate Transformations

### Spherical → Cartesian
$$
\begin{align}
x &= r \sin(\theta) \cos(\phi) \\
y &= r \sin(\theta) \sin(\phi) \\
z &= r \cos(\theta)
\end{align}
$$

### Cylindrical → Cartesian
$$
\begin{align}
x &= \rho \cos(\phi) \\
y &= \rho \sin(\phi) \\
z &= z
\end{align}
$$

---

## Output Files

### 1. Static PNG/PDF (Matplotlib)
- High-resolution (300 DPI)
- 3D scatter plot with:
  - Color heatmap (hot colormap)
  - Size-scaled markers using cubic power scaling (near-zero values are much smaller)
  - Colorbar with units
  - Axis labels

### 2. Interactive HTML (Plotly)
- Fully interactive 3D manipulation
- Zoom, rotate, pan controls
- Hover tooltips showing exact values
- Exportable as PNG from browser

---

## Running Unit Tests

The tool includes a comprehensive test suite for coordinate transformations:

```bash
python python.py --test
```

**Test Coverage**:
- Spherical to Cartesian (boundary cases)
- Cylindrical to Cartesian (boundary cases)
- Vectorized operations
- Numerical accuracy (tolerance: 1e-10)

---

## Error Handling

The tool gracefully handles:
- ❌ Missing input files
- ❌ Empty CSV files
- ❌ Malformed CSV data
- ❌ Invalid coordinate systems
- ❌ NaN values in data
- ❌ File write permission errors

All errors produce clear, actionable messages.

---

## Marker Sizing Behavior

The tool uses **cubic power scaling** to make near-zero values progressively much smaller, preventing them from crowding the visualization:

### Mathematical Formula
```
normalized_value = (value - min) / (max - min)
marker_size = min_size + size_range × (normalized_value)³
```

### Size Ranges
- **Matplotlib**: 5 to 250 (near-zero points are ~5, maximum values are 250)
- **Plotly**: 0.5 to 15 (near-zero points are ~0.5, maximum values are 15)

### Why Cubic Scaling?
| Value % | Linear Size | Cubic Size | Reduction |
|---------|-------------|------------|-----------|
| 10% max | 10% size | 0.1% size | **100x smaller** |
| 25% max | 25% size | 1.6% size | **16x smaller** |
| 50% max | 50% size | 12.5% size | **4x smaller** |
| 75% max | 75% size | 42% size | **1.8x smaller** |

This exponential reduction ensures that low-value background points don't obscure high-value regions of interest.

### Zero-Value Handling
- **Default**: Zero values shown with minimum marker size (5 for static, 0.5 for interactive)
- **`--remove-zeros`**: Zero-value points completely excluded from visualization

---

## Code Structure

```
python.py
├── CoordinateTransformer      # Coordinate system conversions
├── DataLoader                 # CSV parsing and preprocessing
├── Visualizer                 # Matplotlib and Plotly plotting
├── parse_arguments()          # CLI argument parsing
├── generate_output_filenames()# Output path generation
├── main()                     # Main execution logic
└── run_tests()                # Unit test suite
```

---

## Customization

### Modify Colormaps
Edit line in `Visualizer.plot_matplotlib()`:
```python
scatter = ax.scatter(x, y, z, c=values, s=sizes, cmap='hot', ...)
```
Options: `'viridis'`, `'plasma'`, `'inferno'`, `'coolwarm'`, etc.

### Adjust Marker Sizes
Edit scaling in both plotting methods or use the `--scale-power` argument:
```python
# Matplotlib
sizes = 5 + 245 * (norm_values ** scale_power)  # Change min (5), range (245), or power

# Plotly
sizes = 0.5 + 14.5 * (norm_values ** scale_power)  # Change min (0.5), range (14.5), or power
```

**Command-line control:**
```bash
# Linear scaling
python python.py data.csv --scale-power 1.0

# Cubic scaling (default)
python python.py data.csv -s 3.0

# Very aggressive scaling
python python.py data.csv -s 5.0
```

---

## Troubleshooting

### Issue: "FileNotFoundError"
- Verify the input file path is correct
- Use absolute paths if relative paths fail

### Issue: "ValueError: CSV file must have at least 4 columns"
- Ensure your CSV has 3 coordinate columns + 1 value column
- Check for missing commas or extra delimiters

### Issue: Matplotlib window doesn't appear
- Use `--no-display` flag and view PNG/HTML outputs instead
- Check if running in a headless environment

### Issue: All markers are the same size/color
- Verify your value column has variation (not all same values)
- Check for NaN values being filtered out

---

## Performance Notes

- **Large datasets** (>100k points): Consider downsampling for faster rendering
- **HTML file size**: Proportional to number of data points
- **Memory usage**: ~5x the size of input CSV in RAM

---

## Citation

If using this tool for publications, please reference:
```
TOPAS 3D Visualization Tool (2026)
Medical Physics Visualization Package
```

---

## License

See project LICENSE file for details.

---

## Support

For issues or feature requests, please refer to the project repository or contact the development team.
