"""
Command Line Interface for SCD Parser and Visualizer
"""

import argparse
import json
import sys
import logging
from pathlib import Path
from typing import Optional

from .parser import SCDParser
from .visualizer import LogicalLinkVisualizer


def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def parse_scd_file(input_file: str, output_dir: str, verbose: bool = False):
    """Parse SCD file and extract information"""
    setup_logging(verbose)
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize parser
        parser = SCDParser()
        
        # Load SCD file
        if not parser.load_file(input_file):
            logger.error(f"Failed to load SCD file: {input_file}")
            return False
        
        # Extract information
        logger.info("Extracting IEDs...")
        ieds = parser.extract_ieds()
        
        logger.info("Extracting logical links...")
        links = parser.extract_communication_links()
        
        logger.info("Extracting substation info...")
        substation_info = parser.get_substation_info()
        
        logger.info("Extracting communication info...")
        comm_info = parser.get_communication_info()
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save IED information
        ied_data = [
            {
                'name': ied.name,
                'type': ied.type,
                'manufacturer': ied.manufacturer,
                'config_version': ied.config_version,
                'desc': ied.desc,
                'logical_devices': ied.logical_devices,
                'access_points': ied.access_points
            }
            for ied in ieds
        ]
        
        ied_file = output_path / 'ieds.json'
        with open(ied_file, 'w', encoding='utf-8') as f:
            json.dump(ied_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved IED information to: {ied_file}")
        
        # Save link information
        link_data = [
            {
                'source_ied': link.source_ied,
                'target_ied': link.target_ied,
                'link_type': link.link_type,
                'link_id': link.link_id,
                'multicast_address': link.multicast_address,
                'vlan_id': link.vlan_id,
                'app_id': link.app_id,
                'data_set': link.data_set,
                'control_block': link.control_block
            }
            for link in links
        ]
        
        link_file = output_path / 'links.json'
        with open(link_file, 'w', encoding='utf-8') as f:
            json.dump(link_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved link information to: {link_file}")
        
        # Save summary information
        summary = {
            'substation': substation_info,
            'communication': comm_info,
            'statistics': {
                'total_ieds': len(ieds),
                'total_links': len(links),
                'ied_types': {},
                'link_types': {}
            }
        }
        
        # Count types
        for ied in ieds:
            ied_type = ied.type or 'Unknown'
            summary['statistics']['ied_types'][ied_type] = \
                summary['statistics']['ied_types'].get(ied_type, 0) + 1
        
        for link in links:
            link_type = link.link_type
            summary['statistics']['link_types'][link_type] = \
                summary['statistics']['link_types'].get(link_type, 0) + 1
        
        summary_file = output_path / 'summary.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved summary information to: {summary_file}")
        
        # Print summary to console
        print(f"\nSCD Parsing Results:")
        print(f"==================")
        print(f"Input file: {input_file}")
        print(f"Output directory: {output_dir}")
        print(f"Substation: {substation_info.get('name', 'Unknown')}")
        print(f"Total IEDs: {len(ieds)}")
        print(f"Total Links: {len(links)}")
        print(f"\nIED Types:")
        for ied_type, count in summary['statistics']['ied_types'].items():
            print(f"  {ied_type}: {count}")
        print(f"\nLink Types:")
        for link_type, count in summary['statistics']['link_types'].items():
            print(f"  {link_type}: {count}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error parsing SCD file: {str(e)}")
        return False


def visualize_links(input_dir: str, output_file: str, format_type: str = 'png', 
                   style: str = 'modern', verbose: bool = False):
    """Generate visualization from parsed data"""
    setup_logging(verbose)
    logger = logging.getLogger(__name__)
    
    try:
        input_path = Path(input_dir)
        
        # Load IED data
        ied_file = input_path / 'ieds.json'
        if not ied_file.exists():
            logger.error(f"IED data file not found: {ied_file}")
            return False
        
        with open(ied_file, 'r', encoding='utf-8') as f:
            ied_data = json.load(f)
        
        # Load link data
        link_file = input_path / 'links.json'
        if not link_file.exists():
            logger.error(f"Link data file not found: {link_file}")
            return False
        
        with open(link_file, 'r', encoding='utf-8') as f:
            link_data = json.load(f)
        
        # Convert to objects
        from .models import IED, LogicalLink
        
        ieds = [
            IED(
                name=ied['name'],
                type=ied['type'],
                manufacturer=ied['manufacturer'],
                config_version=ied['config_version'],
                desc=ied['desc'],
                logical_devices=ied['logical_devices'],
                access_points=ied['access_points']
            )
            for ied in ied_data
        ]
        
        links = [
            LogicalLink(
                source_ied=link['source_ied'],
                target_ied=link['target_ied'],
                link_type=link['link_type'],
                link_id=link['link_id'],
                multicast_address=link['multicast_address'],
                vlan_id=link['vlan_id'],
                app_id=link['app_id'],
                data_set=link['data_set'],
                control_block=link['control_block']
            )
            for link in link_data
        ]
        
        # Create visualizer
        visualizer = LogicalLinkVisualizer()
        visualizer.set_data(ieds, links)
        
        # Generate visualization
        if format_type.lower() == 'svg':
            result_path = visualizer.export_to_svg(output_file)
        elif format_type.lower() == 'pdf':
            result_path = visualizer.export_to_pdf(output_file)
        elif format_type.lower() == 'matplotlib':
            result_path = visualizer.generate_matplotlib_diagram(output_file)
        else:  # default to PNG
            result_path = visualizer.export_to_png(output_file)
        
        logger.info(f"Generated visualization: {result_path}")
        
        # Print statistics
        stats = visualizer.get_network_statistics()
        print(f"\nVisualization Results:")
        print(f"====================")
        print(f"Output file: {result_path}")
        print(f"Format: {format_type.upper()}")
        print(f"Style: {style}")
        print(f"Network density: {stats['network_density']:.3f}")
        print(f"Average degree: {stats['average_degree']:.1f}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error generating visualization: {str(e)}")
        return False


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description='SCD Parser and Logical Link Visualizer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Parse SCD file
  scd-parser parse input.scd --output ./output
  
  # Generate visualization
  scd-parser visualize ./output --output diagram.png --format png
  
  # Parse and visualize in one command
  scd-parser all input.scd --output ./output --diagram diagram.svg --format svg
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Parse command
    parse_parser = subparsers.add_parser('parse', help='Parse SCD file')
    parse_parser.add_argument('input', help='Input SCD file path')
    parse_parser.add_argument('--output', '-o', required=True,
                            help='Output directory for parsed data')
    parse_parser.add_argument('--verbose', '-v', action='store_true',
                            help='Enable verbose logging')
    
    # Visualize command
    viz_parser = subparsers.add_parser('visualize', help='Generate visualization')
    viz_parser.add_argument('input', help='Input directory with parsed data')
    viz_parser.add_argument('--output', '-o', required=True,
                           help='Output file for visualization')
    viz_parser.add_argument('--format', '-f', choices=['png', 'svg', 'pdf', 'matplotlib'],
                           default='png', help='Output format')
    viz_parser.add_argument('--style', '-s', choices=['modern', 'classic', 'minimal'],
                           default='modern', help='Visualization style')
    viz_parser.add_argument('--verbose', '-v', action='store_true',
                           help='Enable verbose logging')
    
    # All-in-one command
    all_parser = subparsers.add_parser('all', help='Parse and visualize')
    all_parser.add_argument('input', help='Input SCD file path')
    all_parser.add_argument('--output', '-o', required=True,
                           help='Output directory for parsed data')
    all_parser.add_argument('--diagram', '-d', required=True,
                           help='Output file for visualization')
    all_parser.add_argument('--format', '-f', choices=['png', 'svg', 'pdf', 'matplotlib'],
                           default='png', help='Output format')
    all_parser.add_argument('--style', '-s', choices=['modern', 'classic', 'minimal'],
                           default='modern', help='Visualization style')
    all_parser.add_argument('--verbose', '-v', action='store_true',
                           help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    success = False
    
    if args.command == 'parse':
        success = parse_scd_file(args.input, args.output, args.verbose)
    
    elif args.command == 'visualize':
        success = visualize_links(args.input, args.output, args.format, 
                                args.style, args.verbose)
    
    elif args.command == 'all':
        # First parse
        success = parse_scd_file(args.input, args.output, args.verbose)
        
        # Then visualize if parsing succeeded
        if success:
            success = visualize_links(args.output, args.diagram, args.format,
                                    args.style, args.verbose)
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())