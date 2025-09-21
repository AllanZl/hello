# Quick Start Guide

## SCD Parser and Logical Link Visualizer

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/AllanZl/hello.git
cd hello
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
pip install -e .
```

### Quick Demo

Run the demo to see all features in action:
```bash
python demo.py
```

### Command Line Usage

**Parse an SCD file:**
```bash
python -m scd_parser.cli parse examples/sample_substation.scd --output ./output
```

**Generate visualization:**
```bash
python -m scd_parser.cli visualize ./output --output network.png --format matplotlib
```

**All-in-one command:**
```bash
python -m scd_parser.cli all examples/sample_substation.scd --output ./output --diagram network.svg --format svg
```

### Web Interface

Start the web server:
```bash
python -m scd_parser.web_app
```

Then open http://localhost:5000 in your browser.

### Python API

```python
from scd_parser import SCDParser, LogicalLinkVisualizer

# Parse SCD file
parser = SCDParser()
parser.load_file('your_file.scd')

# Extract data
ieds = parser.extract_ieds()
links = parser.extract_communication_links()

# Generate visualization
visualizer = LogicalLinkVisualizer()
visualizer.set_data(ieds, links)
visualizer.export_to_png('diagram.png')
```

### Features

✅ **SCD File Parsing** - IEC 61850 compliant XML parsing  
✅ **IED Extraction** - Device information and configuration  
✅ **Communication Analysis** - GOOSE, SMV, Client-Server links  
✅ **Network Visualization** - Clear topology diagrams  
✅ **Multiple Export Formats** - PNG, SVG, PDF output  
✅ **Web Interface** - User-friendly upload and visualization  
✅ **CLI Tools** - Batch processing and automation  
✅ **Comprehensive Documentation** - Full API reference  

### Sample Output

The tool processes your SCD file and provides:

- **IED Inventory**: Complete list of devices with details
- **Communication Links**: GOOSE, SMV, and Client-Server connections  
- **Network Statistics**: Density, degree, type distributions
- **Visual Diagrams**: Clear network topology charts
- **Export Options**: Multiple formats for documentation

### Need Help?

- Check the README.md for detailed documentation
- Run tests: `python -m unittest tests.test_scd_parser`
- View examples in the `examples/` directory
- Use `--help` flag with CLI commands for options