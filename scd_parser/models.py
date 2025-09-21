"""
Data models for SCD parsing and visualization
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class IED:
    """Intelligent Electronic Device model"""
    name: str
    type: str
    manufacturer: str = ""
    config_version: str = ""
    desc: str = ""
    logical_devices: List[str] = None
    access_points: List[str] = None
    
    def __post_init__(self):
        if self.logical_devices is None:
            self.logical_devices = []
        if self.access_points is None:
            self.access_points = []


@dataclass
class LogicalNode:
    """Logical Node model"""
    name: str
    class_name: str
    inst: str
    desc: str = ""
    ied_name: str = ""


@dataclass
class DataSet:
    """DataSet model for GOOSE/SMV"""
    name: str
    desc: str = ""
    fcda_refs: List[str] = None
    
    def __post_init__(self):
        if self.fcda_refs is None:
            self.fcda_refs = []


@dataclass
class LogicalLink:
    """Logical Link between devices"""
    source_ied: str
    target_ied: str
    link_type: str  # GOOSE, SMV, Client-Server
    link_id: str
    multicast_address: str = ""
    vlan_id: str = ""
    app_id: str = ""
    data_set: str = ""
    control_block: str = ""
    
    def __str__(self):
        return f"{self.source_ied} -> {self.target_ied} ({self.link_type})"


@dataclass
class SubNetwork:
    """Communication SubNetwork model"""
    name: str
    type: str = "8-MMS"
    desc: str = ""
    bit_rate: str = ""
    connected_aps: List[str] = None
    
    def __post_init__(self):
        if self.connected_aps is None:
            self.connected_aps = []


@dataclass
class AccessPoint:
    """Access Point model"""
    name: str
    ied_name: str
    desc: str = ""
    router: bool = False
    clock: bool = False
    server_at: Optional[str] = None
    services: List[str] = None
    
    def __post_init__(self):
        if self.services is None:
            self.services = []