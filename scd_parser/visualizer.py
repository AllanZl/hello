"""
Logical Link Visualizer Module

This module provides functionality to visualize logical links between IEDs
using graphviz and networkx libraries. Supports export to multiple formats.
"""

import logging
from typing import List, Dict, Tuple, Optional
import tempfile
from pathlib import Path

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import graphviz
from PIL import Image, ImageDraw, ImageFont

from .models import IED, LogicalLink

# Configure logging
logger = logging.getLogger(__name__)


class LogicalLinkVisualizer:
    """Visualizer for IED logical links and network topology"""
    
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.ieds = []
        self.links = []
        self.layout_engine = 'dot'  # graphviz layout engine
        
    def set_data(self, ieds: List[IED], links: List[LogicalLink]):
        """
        Set IED and link data for visualization
        
        Args:
            ieds: List of IED objects
            links: List of LogicalLink objects
        """
        self.ieds = ieds
        self.links = links
        self._build_graph()
    
    def _build_graph(self):
        """Build NetworkX graph from IEDs and links"""
        self.graph.clear()
        
        # Add IED nodes
        for ied in self.ieds:
            self.graph.add_node(
                ied.name,
                type='IED',
                manufacturer=ied.manufacturer,
                ied_type=ied.type,
                desc=ied.desc,
                logical_devices=len(ied.logical_devices)
            )
        
        # Add links as edges
        for link in self.links:
            # Handle broadcast links (GOOSE, SMV)
            if link.target_ied in ['ALL_SUBSCRIBERS', 'SMV_SUBSCRIBERS']:
                # Create broadcast node if not exists
                if not self.graph.has_node(link.target_ied):
                    self.graph.add_node(
                        link.target_ied,
                        type='BROADCAST',
                        desc=f"{link.link_type} subscribers"
                    )
            
            # Add edge with link attributes
            self.graph.add_edge(
                link.source_ied,
                link.target_ied,
                link_type=link.link_type,
                link_id=link.link_id,
                multicast_address=link.multicast_address,
                vlan_id=link.vlan_id,
                app_id=link.app_id,
                data_set=link.data_set,
                control_block=link.control_block
            )
    
    def generate_graphviz_diagram(self, 
                                output_format: str = 'png',
                                output_path: Optional[str] = None,
                                style: str = 'modern') -> str:
        """
        Generate network diagram using Graphviz
        
        Args:
            output_format: Output format (png, svg, pdf)
            output_path: Output file path (optional)
            style: Diagram style ('modern', 'classic', 'minimal')
            
        Returns:
            str: Path to generated file
        """
        try:
            # Create Graphviz graph
            dot = graphviz.Digraph(comment='IED Logical Links')
            dot.attr(rankdir='TB', size='12,8', dpi='300')
            
            # Set graph attributes based on style
            if style == 'modern':
                dot.attr('graph', 
                        bgcolor='white',
                        fontname='Arial',
                        fontsize='12',
                        splines='ortho',
                        nodesep='1.0',
                        ranksep='1.5')
                dot.attr('node',
                        shape='box',
                        style='filled,rounded',
                        fontname='Arial',
                        fontsize='10',
                        margin='0.3,0.1')
                dot.attr('edge',
                        fontname='Arial',
                        fontsize='8',
                        arrowsize='0.7')
            
            # Add IED nodes
            for ied in self.ieds:
                node_color = self._get_ied_color(ied.type)
                label = self._create_ied_label(ied)
                
                dot.node(ied.name,
                        label=label,
                        fillcolor=node_color,
                        tooltip=f"{ied.manufacturer} {ied.type}")
            
            # Add broadcast nodes
            broadcast_nodes = [node for node in self.graph.nodes() 
                             if self.graph.nodes[node].get('type') == 'BROADCAST']
            
            for node in broadcast_nodes:
                dot.node(node,
                        label=node.replace('_', '\\n'),
                        shape='ellipse',
                        fillcolor='lightgray',
                        style='filled')
            
            # Add edges for links
            link_counters = {}  # To handle multiple links between same nodes
            
            for link in self.links:
                edge_key = f"{link.source_ied}_{link.target_ied}"
                link_counters[edge_key] = link_counters.get(edge_key, 0) + 1
                
                edge_label = self._create_link_label(link)
                edge_color = self._get_link_color(link.link_type)
                
                # Handle multiple edges
                if link_counters[edge_key] > 1:
                    constraint = 'false'
                else:
                    constraint = 'true'
                
                dot.edge(link.source_ied,
                        link.target_ied,
                        label=edge_label,
                        color=edge_color,
                        constraint=constraint,
                        tooltip=f"{link.link_type}: {link.link_id}")
            
            # Generate output
            if output_path is None:
                temp_dir = tempfile.mkdtemp()
                output_path = Path(temp_dir) / f"network_diagram.{output_format}"
            
            output_path = Path(output_path)
            
            # Render diagram
            dot.render(str(output_path.with_suffix('')), 
                      format=output_format, 
                      cleanup=True)
            
            final_path = str(output_path)
            logger.info(f"Generated Graphviz diagram: {final_path}")
            return final_path
            
        except Exception as e:
            logger.error(f"Error generating Graphviz diagram: {str(e)}")
            raise
    
    def generate_matplotlib_diagram(self, 
                                  output_path: Optional[str] = None,
                                  figsize: Tuple[int, int] = (15, 10)) -> str:
        """
        Generate network diagram using matplotlib
        
        Args:
            output_path: Output file path
            figsize: Figure size tuple
            
        Returns:
            str: Path to generated file
        """
        try:
            fig, ax = plt.subplots(figsize=figsize)
            ax.set_aspect('equal')
            
            # Calculate layout using networkx
            pos = nx.spring_layout(self.graph, k=3, iterations=50)
            
            # Draw IED nodes
            ied_nodes = [node for node in self.graph.nodes() 
                        if self.graph.nodes[node].get('type') == 'IED']
            
            for node in ied_nodes:
                x, y = pos[node]
                ied_data = next((ied for ied in self.ieds if ied.name == node), None)
                
                if ied_data:
                    # Create fancy box for IED
                    box = FancyBboxPatch(
                        (x - 0.15, y - 0.08),
                        0.3, 0.16,
                        boxstyle="round,pad=0.02",
                        facecolor=self._get_ied_color_matplotlib(ied_data.type),
                        edgecolor='black',
                        linewidth=1.5
                    )
                    ax.add_patch(box)
                    
                    # Add IED name
                    ax.text(x, y + 0.02, ied_data.name, 
                           ha='center', va='center', 
                           fontsize=9, fontweight='bold')
                    
                    # Add IED type
                    ax.text(x, y - 0.02, ied_data.type, 
                           ha='center', va='center', 
                           fontsize=7, style='italic')
            
            # Draw broadcast nodes
            broadcast_nodes = [node for node in self.graph.nodes() 
                             if self.graph.nodes[node].get('type') == 'BROADCAST']
            
            for node in broadcast_nodes:
                x, y = pos[node]
                circle = plt.Circle((x, y), 0.1, 
                                  facecolor='lightgray', 
                                  edgecolor='black')
                ax.add_patch(circle)
                ax.text(x, y, node.replace('_', '\n'), 
                       ha='center', va='center', fontsize=7)
            
            # Draw edges
            for link in self.links:
                if link.source_ied in pos and link.target_ied in pos:
                    x1, y1 = pos[link.source_ied]
                    x2, y2 = pos[link.target_ied]
                    
                    # Draw arrow
                    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                               arrowprops=dict(
                                   arrowstyle='->',
                                   color=self._get_link_color_matplotlib(link.link_type),
                                   lw=2,
                                   connectionstyle="arc3,rad=0.1"
                               ))
                    
                    # Add link label
                    mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                    ax.text(mid_x + 0.05, mid_y + 0.05, 
                           f"{link.link_type}\\n{link.link_id}", 
                           fontsize=6, 
                           bbox=dict(boxstyle="round,pad=0.3", 
                                   facecolor='white', 
                                   alpha=0.8))
            
            # Set title and clean up axes
            ax.set_title('IED Logical Links Network Diagram', 
                        fontsize=16, fontweight='bold', pad=20)
            ax.set_xlim(-1.5, 1.5)
            ax.set_ylim(-1.5, 1.5)
            ax.axis('off')
            
            # Add legend
            self._add_matplotlib_legend(ax)
            
            # Save figure
            if output_path is None:
                temp_dir = tempfile.mkdtemp()
                output_path = Path(temp_dir) / "network_diagram_matplotlib.png"
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Generated matplotlib diagram: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error generating matplotlib diagram: {str(e)}")
            raise
    
    def _get_ied_color(self, ied_type: str) -> str:
        """Get color for IED based on type (Graphviz)"""
        color_map = {
            'Protection': 'lightblue',
            'Control': 'lightgreen',
            'Measurement': 'lightyellow',
            'Gateway': 'lightcoral',
            'Switch': 'lightgray',
            'Server': 'lightpink'
        }
        
        # Check if type contains any known keywords
        for key, color in color_map.items():
            if key.lower() in ied_type.lower():
                return color
        
        return 'lightsteelblue'  # default color
    
    def _get_ied_color_matplotlib(self, ied_type: str) -> str:
        """Get color for IED based on type (Matplotlib)"""
        color_map = {
            'Protection': '#ADD8E6',
            'Control': '#90EE90',
            'Measurement': '#FFFFE0',
            'Gateway': '#F08080',
            'Switch': '#D3D3D3',
            'Server': '#FFB6C1'
        }
        
        for key, color in color_map.items():
            if key.lower() in ied_type.lower():
                return color
        
        return '#B0C4DE'  # default color
    
    def _get_link_color(self, link_type: str) -> str:
        """Get color for link based on type (Graphviz)"""
        color_map = {
            'GOOSE': 'blue',
            'SMV': 'red',
            'Client-Server': 'green'
        }
        return color_map.get(link_type, 'black')
    
    def _get_link_color_matplotlib(self, link_type: str) -> str:
        """Get color for link based on type (Matplotlib)"""
        color_map = {
            'GOOSE': 'blue',
            'SMV': 'red',
            'Client-Server': 'green'
        }
        return color_map.get(link_type, 'black')
    
    def _create_ied_label(self, ied: IED) -> str:
        """Create label for IED node"""
        label_parts = [ied.name]
        
        if ied.type:
            label_parts.append(f"({ied.type})")
        
        if ied.logical_devices:
            label_parts.append(f"LDs: {len(ied.logical_devices)}")
        
        return "\\n".join(label_parts)
    
    def _create_link_label(self, link: LogicalLink) -> str:
        """Create label for link edge"""
        label_parts = [link.link_type]
        
        if link.link_id:
            label_parts.append(link.link_id)
        
        if link.vlan_id:
            label_parts.append(f"VLAN:{link.vlan_id}")
        
        return "\\n".join(label_parts)
    
    def _add_matplotlib_legend(self, ax):
        """Add legend to matplotlib plot"""
        # Create legend elements
        legend_elements = []
        
        # IED types
        ied_types = set(ied.type for ied in self.ieds if ied.type)
        for ied_type in ied_types:
            color = self._get_ied_color_matplotlib(ied_type)
            legend_elements.append(
                patches.Patch(color=color, label=f'IED: {ied_type}')
            )
        
        # Link types
        link_types = set(link.link_type for link in self.links)
        for link_type in link_types:
            color = self._get_link_color_matplotlib(link_type)
            legend_elements.append(
                patches.Patch(color=color, label=f'Link: {link_type}')
            )
        
        # Add legend
        if legend_elements:
            ax.legend(handles=legend_elements, 
                     loc='upper left', 
                     bbox_to_anchor=(0, 1))
    
    def export_to_svg(self, output_path: str) -> str:
        """
        Export diagram to SVG format using Graphviz
        
        Args:
            output_path: Output SVG file path
            
        Returns:
            str: Path to generated SVG file
        """
        return self.generate_graphviz_diagram('svg', output_path)
    
    def export_to_png(self, output_path: str) -> str:
        """
        Export diagram to PNG format
        
        Args:
            output_path: Output PNG file path
            
        Returns:
            str: Path to generated PNG file
        """
        return self.generate_graphviz_diagram('png', output_path)
    
    def export_to_pdf(self, output_path: str) -> str:
        """
        Export diagram to PDF format using Graphviz
        
        Args:
            output_path: Output PDF file path
            
        Returns:
            str: Path to generated PDF file
        """
        return self.generate_graphviz_diagram('pdf', output_path)
    
    def get_network_statistics(self) -> Dict[str, any]:
        """
        Get network topology statistics
        
        Returns:
            Dict: Network statistics
        """
        stats = {
            'total_ieds': len(self.ieds),
            'total_links': len(self.links),
            'link_types': {},
            'ied_types': {},
            'network_density': 0,
            'average_degree': 0
        }
        
        # Count link types
        for link in self.links:
            link_type = link.link_type
            stats['link_types'][link_type] = stats['link_types'].get(link_type, 0) + 1
        
        # Count IED types
        for ied in self.ieds:
            ied_type = ied.type or 'Unknown'
            stats['ied_types'][ied_type] = stats['ied_types'].get(ied_type, 0) + 1
        
        # Calculate network metrics
        if self.graph.number_of_nodes() > 1:
            stats['network_density'] = nx.density(self.graph)
            degrees = [d for n, d in self.graph.degree()]
            stats['average_degree'] = sum(degrees) / len(degrees) if degrees else 0
        
        return stats