#!/usr/bin/env python3
"""
Demo script for SCD Parser and Visualizer

This script demonstrates the key features of the SCD parser and visualizer.
"""

import os
import sys
from pathlib import Path

# Add the package to path if running from source
sys.path.insert(0, str(Path(__file__).parent))

from scd_parser import SCDParser, LogicalLinkVisualizer

def run_demo():
    """Run a complete demonstration of the SCD parser and visualizer"""
    print("=" * 60)
    print("SCD Parser and Logical Link Visualizer Demo")
    print("=" * 60)
    
    # Path to sample SCD file
    sample_scd = Path(__file__).parent / "examples" / "sample_substation.scd"
    
    if not sample_scd.exists():
        print(f"❌ Sample SCD file not found: {sample_scd}")
        return False
    
    print(f"📁 Using sample SCD file: {sample_scd}")
    
    # Step 1: Parse SCD file
    print("\n🔍 Step 1: Parsing SCD file...")
    parser = SCDParser()
    
    if not parser.load_file(str(sample_scd)):
        print("❌ Failed to load SCD file")
        return False
    
    print("✅ SCD file loaded successfully")
    
    # Extract IEDs
    print("\n📋 Extracting IED information...")
    ieds = parser.extract_ieds()
    print(f"✅ Found {len(ieds)} IEDs:")
    
    for ied in ieds:
        print(f"   • {ied.name} ({ied.type}) - {ied.manufacturer}")
        print(f"     Logical Devices: {len(ied.logical_devices)}, Access Points: {len(ied.access_points)}")
    
    # Extract logical links
    print("\n🔗 Extracting communication links...")
    links = parser.extract_communication_links()
    print(f"✅ Found {len(links)} communication links:")
    
    link_types = {}
    for link in links:
        link_types[link.link_type] = link_types.get(link.link_type, 0) + 1
        if len([l for l in links if l.link_type == link.link_type]) <= 3:  # Show first 3 of each type
            print(f"   • {link.source_ied} → {link.target_ied} ({link.link_type})")
    
    print(f"\n📊 Link type summary:")
    for link_type, count in link_types.items():
        print(f"   • {link_type}: {count}")
    
    # Extract substation info
    print("\n🏭 Substation information...")
    substation_info = parser.get_substation_info()
    if substation_info:
        print(f"✅ Substation: {substation_info.get('name', 'Unknown')}")
        print(f"   Description: {substation_info.get('desc', 'No description')}")
    
    # Step 2: Generate visualization
    print("\n🎨 Step 2: Generating network visualization...")
    visualizer = LogicalLinkVisualizer()
    visualizer.set_data(ieds, links)
    
    # Create demo output directory
    demo_dir = Path(__file__).parent / "demo_output"
    demo_dir.mkdir(exist_ok=True)
    
    # Generate matplotlib diagram
    print("📈 Generating matplotlib diagram...")
    try:
        matplotlib_path = demo_dir / "network_diagram_matplotlib.png"
        result = visualizer.generate_matplotlib_diagram(str(matplotlib_path))
        print(f"✅ Matplotlib diagram saved: {result}")
    except Exception as e:
        print(f"❌ Matplotlib diagram failed: {e}")
    
    # Try to generate SVG with graphviz (might fail if not installed)
    print("🖼️ Attempting to generate SVG diagram...")
    try:
        svg_path = demo_dir / "network_diagram.svg"
        result = visualizer.export_to_svg(str(svg_path))
        print(f"✅ SVG diagram saved: {result}")
    except Exception as e:
        print(f"⚠️ SVG diagram failed (Graphviz may not be installed): {e}")
    
    # Step 3: Show network statistics
    print("\n📊 Step 3: Network statistics...")
    stats = visualizer.get_network_statistics()
    
    print(f"   • Total IEDs: {stats['total_ieds']}")
    print(f"   • Total Links: {stats['total_links']}")
    print(f"   • Network Density: {stats['network_density']:.3f}")
    print(f"   • Average Degree: {stats['average_degree']:.1f}")
    
    print(f"\n   IED Types:")
    for ied_type, count in stats['ied_types'].items():
        print(f"     • {ied_type}: {count}")
    
    print(f"\n   Link Types:")
    for link_type, count in stats['link_types'].items():
        print(f"     • {link_type}: {count}")
    
    # Step 4: Show output files
    print("\n📁 Demo output files:")
    if demo_dir.exists():
        for file in demo_dir.iterdir():
            if file.is_file():
                size = file.stat().st_size
                print(f"   • {file.name} ({size:,} bytes)")
    
    print("\n" + "=" * 60)
    print("✅ Demo completed successfully!")
    print("=" * 60)
    
    print("\n🚀 Next steps:")
    print("   • Try the web interface: python -m scd_parser.web_app")
    print("   • Use CLI tools: python -m scd_parser.cli --help")
    print("   • Upload your own SCD files for analysis")
    
    return True

if __name__ == "__main__":
    success = run_demo()
    sys.exit(0 if success else 1)