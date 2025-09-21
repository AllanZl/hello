"""
SCD Parser and Visualizer Package

This package provides functionality to:
1. Parse SCD (Substation Configuration Description) files
2. Extract IED (Intelligent Electronic Device) information
3. Analyze logical links between devices
4. Generate visualization diagrams
5. Export diagrams in multiple formats
"""

__version__ = "1.0.0"
__author__ = "SCD Parser Team"

from .parser import SCDParser
from .visualizer import LogicalLinkVisualizer
from .models import IED, LogicalLink

__all__ = ['SCDParser', 'LogicalLinkVisualizer', 'IED', 'LogicalLink']