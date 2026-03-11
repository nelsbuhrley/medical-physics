## TOPAS 3D Visualization Tool - Quick Reference

### 📦 Installation

```bash
cd "/Users/nelsbuhrley/CPP_Workspace/TOPAS VISUALISATION"
pip3 install -r requirements.txt
```

### ✅ Verify Installation

```bash
python3 python.py --test
```

### 🚀 Usage Examples

#### 1. Cartesian Coordinates (Default)
```bash
python3 python.py sample_topas_data.csv
```

#### 2. Spherical Coordinates
```bash
python3 python.py sample_spherical_data.csv -c spherical -o results
```

#### 3. Cylindrical Coordinates
```bash
python3 python.py your_data.csv --coordinate-system cylindrical
```

#### 4. Custom Output Location
```bash
python3 python.py input.csv -o /path/to/output.png
```

#### 5. Enable Interactive Display
```bash
python3 python.py data.csv --display
```

#### 6. Remove Zero-Value Points
```bash
python3 python.py data.csv --remove-zeros --display
```

#### 7. Adjust Marker Size Scaling
```bash
# Linear scaling - all points proportional
python3 python.py data.csv --scale-power 1.0

# Quadratic scaling - moderate reduction
python3 python.py data.csv -s 2.0

# Cubic scaling - default behavior
python3 python.py data.csv -s 3.0

# Quartic scaling - aggressive reduction
python3 python.py data.csv --scale-power 4.0
```

### 📁 Output Files

Each run generates:
- **PNG/PDF**: High-resolution static 3D plot
- **HTML**: Interactive Plotly visualization (open in browser)
- **Matplotlib Window**: Interactive pop-up (unless --no-display)

### 🔧 Command-Line Options

```
python3 python.py <input_file> [options]

Required:
  input_file                 CSV file with TOPAS simulation data

Optional:
  -o, --output PATH         Output filename (base name or full path)
  -c, --coordinate-system   cartesian|spherical|cylindrical (default: cartesian)
  -s, --scale-power POWER   Marker size scaling power (default: 3.0)
                            1.0=linear, 2.0=quadratic, 3.0=cubic, 4.0=quartic
  --display                 Enable matplotlib pop-up window (default: disabled)
  --remove-zeros            Remove zero-value points from visualization
  --test                    Run unit tests

Aliases:
  - 'rectangular' = 'cartesian'
```

### 📊 Input CSV Format

```csv
# Comment lines start with #
# They are automatically skipped
x, y, z, value
0.0, 0.0, 0.0, 1.234e-10
1.0, 0.0, 0.0, 2.456e-10
...
```

- First 3 columns: coordinates (x,y,z or r,θ,φ or ρ,φ,z)
- Fourth column: data value (Dose, Fluence, etc.)
- Scientific notation supported
- NaN values automatically filtered

### 🧮 Coordinate Transformations

**Spherical → Cartesian:**
$$x = r \sin(\theta) \cos(\phi)$$
$$y = r \sin(\theta) \sin(\phi)$$
$$z = r \cos(\theta)$$

**Cylindrical → Cartesian:**
$$x = \rho \cos(\phi)$$
$$y = \rho \sin(\phi)$$
$$z = z$$

### 🎨 Visualization Features

- **Dual Encoding**: Size AND color represent data values
- **Smart Sizing**: Configurable power scaling (`--scale-power` / `-s`)
  - **Linear (1.0)**: Proportional sizing for all values
  - **Quadratic (2.0)**: Moderate reduction of small values
  - **Cubic (3.0 - default)**: Strong reduction; 10% value → 0.1% size (100× smaller)
  - **Quartic (4.0+)**: Very aggressive reduction for high dynamic range data
- **Color Map**: Hot colormap (red = high, dark = low)
- **Interactive**: Rotate, zoom, pan in browser
- **High-Res**: 300 DPI PNG exports
- **Zero Handling**: Use `--remove-zeros` to exclude zero-value points

### 🧪 Testing

Run the included unit test suite:
```bash
python3 python.py --test
```

Tests verify:
- Spherical transformations
- Cylindrical transformations
- Vectorized operations
- Numerical accuracy (< 1e-10 error)

### 📖 Full Documentation

See `TOPAS_VISUALIZATION_README.md` for complete documentation.

### 🆘 Common Issues

**"ModuleNotFoundError"**
→ Run: `pip3 install -r requirements.txt`

**"FileNotFoundError"**
→ Check file path, use absolute paths

**No matplotlib window**
→ Window is disabled by default; use `--display` to enable it

**Near-zero values crowding the screen**
→ Use `--remove-zeros` to exclude zero-value points entirely

**"ValueError: at least 4 columns"**
→ Ensure CSV has 3 coords + 1 value column

---

**Author**: Medical Physics Visualization Tool
**Date**: March 2026
