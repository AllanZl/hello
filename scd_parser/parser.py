"""
SCD File Parser Module

This module provides functionality to parse SCD (Substation Configuration Description) files
and extract IED (Intelligent Electronic Device) information, logical nodes, communication
settings, and logical links.
"""

import logging
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import xml.etree.ElementTree as ET
from lxml import etree

from .models import IED, LogicalNode, LogicalLink, DataSet, SubNetwork, AccessPoint

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SCDParser:
    """SCD file parser for extracting device and communication information"""
    
    # IEC 61850 namespace
    SCL_NAMESPACE = "http://www.iec.ch/61850/2003/SCL"
    
    def __init__(self):
        self.tree = None
        self.root = None
        self.namespaces = {'scl': self.SCL_NAMESPACE}
        
    def load_file(self, file_path: str) -> bool:
        """
        Load and parse SCD file
        
        Args:
            file_path: Path to SCD file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.tree = etree.parse(file_path)
            self.root = self.tree.getroot()
            
            # Update namespaces if different
            if self.root.nsmap:
                # Use default namespace if available
                default_ns = self.root.nsmap.get(None)
                if default_ns:
                    self.namespaces = {'scl': default_ns}
                    
            logger.info(f"Successfully loaded SCD file: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading SCD file {file_path}: {str(e)}")
            return False
    
    def load_from_content(self, content: str) -> bool:
        """
        Load and parse SCD content from string
        
        Args:
            content: SCD file content as string
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.root = etree.fromstring(content.encode('utf-8'))
            self.tree = etree.ElementTree(self.root)
            
            # Update namespaces if different
            if self.root.nsmap:
                default_ns = self.root.nsmap.get(None)
                if default_ns:
                    self.namespaces = {'scl': default_ns}
                    
            logger.info("Successfully loaded SCD content")
            return True
            
        except Exception as e:
            logger.error(f"Error loading SCD content: {str(e)}")
            return False
    
    def extract_ieds(self) -> List[IED]:
        """
        Extract all IED (Intelligent Electronic Device) information
        
        Returns:
            List[IED]: List of IED objects
        """
        ieds = []
        
        if self.root is None:
            logger.warning("No SCD file loaded")
            return ieds
        
        try:
            # Find all IED elements
            ied_elements = self.root.xpath('.//scl:IED', namespaces=self.namespaces)
            
            for ied_elem in ied_elements:
                # Extract basic IED information
                ied_name = ied_elem.get('name', '')
                ied_type = ied_elem.get('type', '')
                manufacturer = ied_elem.get('manufacturer', '')
                config_version = ied_elem.get('configVersion', '')
                desc = ied_elem.get('desc', '')
                
                # Extract logical devices
                logical_devices = []
                ld_elements = ied_elem.xpath('.//scl:LDevice', namespaces=self.namespaces)
                for ld_elem in ld_elements:
                    ld_inst = ld_elem.get('inst', '')
                    if ld_inst:
                        logical_devices.append(ld_inst)
                
                # Extract access points
                access_points = []
                ap_elements = ied_elem.xpath('.//scl:AccessPoint', namespaces=self.namespaces)
                for ap_elem in ap_elements:
                    ap_name = ap_elem.get('name', '')
                    if ap_name:
                        access_points.append(ap_name)
                
                # Create IED object
                ied = IED(
                    name=ied_name,
                    type=ied_type,
                    manufacturer=manufacturer,
                    config_version=config_version,
                    desc=desc,
                    logical_devices=logical_devices,
                    access_points=access_points
                )
                
                ieds.append(ied)
                
            logger.info(f"Extracted {len(ieds)} IEDs")
            return ieds
            
        except Exception as e:
            logger.error(f"Error extracting IEDs: {str(e)}")
            return []
    
    def extract_logical_nodes(self) -> List[LogicalNode]:
        """
        Extract logical nodes from all IEDs
        
        Returns:
            List[LogicalNode]: List of logical node objects
        """
        logical_nodes = []
        
        if self.root is None:
            logger.warning("No SCD file loaded")
            return logical_nodes
        
        try:
            # Find all LN elements
            ln_elements = self.root.xpath('.//scl:LN', namespaces=self.namespaces)
            
            for ln_elem in ln_elements:
                ln_class = ln_elem.get('lnClass', '')
                ln_inst = ln_elem.get('inst', '')
                ln_desc = ln_elem.get('desc', '')
                
                # Find parent IED
                ied_elem = ln_elem.xpath('ancestor::scl:IED', namespaces=self.namespaces)
                ied_name = ied_elem[0].get('name', '') if ied_elem else ''
                
                ln_name = f"{ln_class}{ln_inst}"
                
                logical_node = LogicalNode(
                    name=ln_name,
                    class_name=ln_class,
                    inst=ln_inst,
                    desc=ln_desc,
                    ied_name=ied_name
                )
                
                logical_nodes.append(logical_node)
            
            logger.info(f"Extracted {len(logical_nodes)} logical nodes")
            return logical_nodes
            
        except Exception as e:
            logger.error(f"Error extracting logical nodes: {str(e)}")
            return []
    
    def extract_communication_links(self) -> List[LogicalLink]:
        """
        Extract logical communication links (GOOSE, SMV, Client-Server)
        
        Returns:
            List[LogicalLink]: List of logical link objects
        """
        links = []
        
        if self.root is None:
            logger.warning("No SCD file loaded")
            return links
        
        try:
            # Extract GOOSE links
            goose_links = self._extract_goose_links()
            links.extend(goose_links)
            
            # Extract SMV links
            smv_links = self._extract_smv_links()
            links.extend(smv_links)
            
            # Extract Client-Server links
            client_server_links = self._extract_client_server_links()
            links.extend(client_server_links)
            
            logger.info(f"Extracted {len(links)} logical links")
            return links
            
        except Exception as e:
            logger.error(f"Error extracting communication links: {str(e)}")
            return []
    
    def _extract_goose_links(self) -> List[LogicalLink]:
        """Extract GOOSE communication links"""
        goose_links = []
        
        try:
            # Find all GSEControl elements (GOOSE senders)
            gse_controls = self.root.xpath('.//scl:GSEControl', namespaces=self.namespaces)
            
            for gse_ctrl in gse_controls:
                control_name = gse_ctrl.get('name', '')
                dataset_name = gse_ctrl.get('datSet', '')
                app_id = gse_ctrl.get('appID', '')
                
                # Find parent IED
                ied_elem = gse_ctrl.xpath('ancestor::scl:IED', namespaces=self.namespaces)
                source_ied = ied_elem[0].get('name', '') if ied_elem else ''
                
                # Find corresponding GSE in Communication section
                gse_xpath = f'.//scl:GSE[@ldInst and @cbName="{control_name}"]'
                gse_elements = self.root.xpath(gse_xpath, namespaces=self.namespaces)
                
                for gse_elem in gse_elements:
                    # Find multicast address
                    address_elem = gse_elem.xpath('.//scl:Address/scl:P[@type="MAC-Address"]', 
                                                namespaces=self.namespaces)
                    mac_address = address_elem[0].text if address_elem else ''
                    
                    # Find VLAN ID
                    vlan_elem = gse_elem.xpath('.//scl:Address/scl:P[@type="VLAN-ID"]', 
                                             namespaces=self.namespaces)
                    vlan_id = vlan_elem[0].text if vlan_elem else ''
                    
                    # For GOOSE, we need to find subscribers (this is complex, simplified here)
                    # In practice, you'd analyze Inputs/ExtRef elements to find subscribers
                    target_ied = "ALL_SUBSCRIBERS"  # Placeholder
                    
                    link = LogicalLink(
                        source_ied=source_ied,
                        target_ied=target_ied,
                        link_type="GOOSE",
                        link_id=control_name,
                        multicast_address=mac_address,
                        vlan_id=vlan_id,
                        app_id=app_id,
                        data_set=dataset_name,
                        control_block=control_name
                    )
                    
                    goose_links.append(link)
            
            return goose_links
            
        except Exception as e:
            logger.error(f"Error extracting GOOSE links: {str(e)}")
            return []
    
    def _extract_smv_links(self) -> List[LogicalLink]:
        """Extract SMV (Sampled Measured Values) communication links"""
        smv_links = []
        
        try:
            # Find all SampledValueControl elements
            smv_controls = self.root.xpath('.//scl:SampledValueControl', namespaces=self.namespaces)
            
            for smv_ctrl in smv_controls:
                control_name = smv_ctrl.get('name', '')
                dataset_name = smv_ctrl.get('datSet', '')
                smv_id = smv_ctrl.get('smvID', '')
                
                # Find parent IED
                ied_elem = smv_ctrl.xpath('ancestor::scl:IED', namespaces=self.namespaces)
                source_ied = ied_elem[0].get('name', '') if ied_elem else ''
                
                # Find corresponding SMV in Communication section
                smv_xpath = f'.//scl:SMV[@ldInst and @cbName="{control_name}"]'
                smv_elements = self.root.xpath(smv_xpath, namespaces=self.namespaces)
                
                for smv_elem in smv_elements:
                    # Find multicast address
                    address_elem = smv_elem.xpath('.//scl:Address/scl:P[@type="MAC-Address"]', 
                                                namespaces=self.namespaces)
                    mac_address = address_elem[0].text if address_elem else ''
                    
                    # Find VLAN ID
                    vlan_elem = smv_elem.xpath('.//scl:Address/scl:P[@type="VLAN-ID"]', 
                                             namespaces=self.namespaces)
                    vlan_id = vlan_elem[0].text if vlan_elem else ''
                    
                    target_ied = "SMV_SUBSCRIBERS"  # Placeholder
                    
                    link = LogicalLink(
                        source_ied=source_ied,
                        target_ied=target_ied,
                        link_type="SMV",
                        link_id=control_name,
                        multicast_address=mac_address,
                        vlan_id=vlan_id,
                        app_id=smv_id,
                        data_set=dataset_name,
                        control_block=control_name
                    )
                    
                    smv_links.append(link)
            
            return smv_links
            
        except Exception as e:
            logger.error(f"Error extracting SMV links: {str(e)}")
            return []
    
    def _extract_client_server_links(self) -> List[LogicalLink]:
        """Extract Client-Server communication links"""
        cs_links = []
        
        try:
            # This is a simplified implementation
            # Real implementation would analyze ReportControl, LogControl, etc.
            
            # Find all IEDs with servers
            server_ieds = self.root.xpath('.//scl:IED[.//scl:Server]', namespaces=self.namespaces)
            
            for server_ied in server_ieds:
                server_name = server_ied.get('name', '')
                
                # Find potential clients (IEDs with client access points)
                client_aps = self.root.xpath('.//scl:ConnectedAP', namespaces=self.namespaces)
                
                for client_ap in client_aps:
                    client_ied = client_ap.get('iedName', '')
                    
                    if client_ied != server_name:  # Don't link to self
                        link = LogicalLink(
                            source_ied=client_ied,
                            target_ied=server_name,
                            link_type="Client-Server",
                            link_id=f"{client_ied}_to_{server_name}",
                            multicast_address="",
                            vlan_id="",
                            app_id="",
                            data_set="",
                            control_block=""
                        )
                        
                        cs_links.append(link)
            
            return cs_links
            
        except Exception as e:
            logger.error(f"Error extracting Client-Server links: {str(e)}")
            return []
    
    def get_substation_info(self) -> Dict[str, str]:
        """
        Extract substation basic information
        
        Returns:
            Dict[str, str]: Substation information
        """
        if self.root is None:
            return {}
        
        try:
            substation_elem = self.root.xpath('.//scl:Substation', namespaces=self.namespaces)
            
            if substation_elem:
                substation = substation_elem[0]
                return {
                    'name': substation.get('name', ''),
                    'desc': substation.get('desc', ''),
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error extracting substation info: {str(e)}")
            return {}
    
    def get_communication_info(self) -> Dict[str, any]:
        """
        Extract communication configuration information
        
        Returns:
            Dict: Communication information including subnets and connected APs
        """
        if self.root is None:
            return {}
        
        try:
            comm_info = {
                'subnets': [],
                'connected_aps': []
            }
            
            # Extract SubNetworks
            subnet_elements = self.root.xpath('.//scl:SubNetwork', namespaces=self.namespaces)
            
            for subnet_elem in subnet_elements:
                subnet_name = subnet_elem.get('name', '')
                subnet_type = subnet_elem.get('type', '')
                subnet_desc = subnet_elem.get('desc', '')
                
                # Find connected APs in this subnet
                connected_aps = []
                cap_elements = subnet_elem.xpath('.//scl:ConnectedAP', namespaces=self.namespaces)
                
                for cap_elem in cap_elements:
                    ap_name = cap_elem.get('apName', '')
                    ied_name = cap_elem.get('iedName', '')
                    
                    if ap_name and ied_name:
                        connected_aps.append(f"{ied_name}_{ap_name}")
                
                subnet_info = {
                    'name': subnet_name,
                    'type': subnet_type,
                    'desc': subnet_desc,
                    'connected_aps': connected_aps
                }
                
                comm_info['subnets'].append(subnet_info)
            
            return comm_info
            
        except Exception as e:
            logger.error(f"Error extracting communication info: {str(e)}")
            return {}