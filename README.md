# Medical Physics Tools

A collection of computational tools and visualization software for medical physics applications, primarily focused on TOPAS/Geant4 simulation analysis.

## Contents

### TOPAS VISUALISATION

A comprehensive Python CLI tool for visualizing 3D heatmap data from TOPAS/Geant4 simulation outputs.

**Features:**
- 📊 Triple output format: Interactive Matplotlib, Static PNG/PDF, and Interactive HTML (Plotly)
- 🌐 Multiple coordinate systems: Cartesian, Spherical, and Cylindrical
- 🎯 Configurable marker size scaling with power law control
- 🔍 Smart handling of zero and near-zero values
- 📐 Automatic coordinate transformations

**Quick Start:**
```bash
cd "TOPAS VISUALISATION"
pip3 install -r requirements.txt
python3 python.py --test
python3 python.py sample_topas_data.csv
```

See [TOPAS VISUALISATION/TOPAS_VISUALIZATION_README.md](TOPAS%20VISUALISATION/TOPAS_VISUALIZATION_README.md) for complete documentation.

## Installation

Dependencies vary by tool. See individual tool directories for specific requirements.

## Contributing

This is a personal research repository. Feel free to fork and adapt for your own use.

## License

See individual tool directories for licensing information.

## Author

Medical Physics Research Tools  
March 2026
