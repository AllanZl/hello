"""
Test cases for SCD Parser and Visualizer
"""

import unittest
import tempfile
import json
from pathlib import Path

from scd_parser.parser import SCDParser
from scd_parser.visualizer import LogicalLinkVisualizer
from scd_parser.models import IED, LogicalLink


class TestSCDParser(unittest.TestCase):
    """Test cases for SCD parser functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.parser = SCDParser()
        self.sample_scd_path = Path(__file__).parent.parent / "examples" / "sample_substation.scd"
    
    def test_load_scd_file(self):
        """Test loading SCD file"""
        result = self.parser.load_file(str(self.sample_scd_path))
        self.assertTrue(result)
        self.assertIsNotNone(self.parser.root)
    
    def test_extract_ieds(self):
        """Test IED extraction"""
        self.parser.load_file(str(self.sample_scd_path))
        ieds = self.parser.extract_ieds()
        
        self.assertGreater(len(ieds), 0)
        
        # Check if we have the expected IEDs
        ied_names = [ied.name for ied in ieds]
        expected_ieds = ['ProtIED1', 'ProtIED2', 'MeasIED1', 'ControlIED']
        
        for expected_ied in expected_ieds:
            self.assertIn(expected_ied, ied_names)
        
        # Check IED properties
        prot_ied1 = next((ied for ied in ieds if ied.name == 'ProtIED1'), None)
        self.assertIsNotNone(prot_ied1)
        self.assertEqual(prot_ied1.type, 'Protection')
        self.assertEqual(prot_ied1.manufacturer, 'TestVendor')
    
    def test_extract_logical_links(self):
        """Test logical link extraction"""
        self.parser.load_file(str(self.sample_scd_path))
        links = self.parser.extract_communication_links()
        
        self.assertGreater(len(links), 0)
        
        # Check for GOOSE links
        goose_links = [link for link in links if link.link_type == 'GOOSE']
        self.assertGreater(len(goose_links), 0)
        
        # Check for SMV links
        smv_links = [link for link in links if link.link_type == 'SMV']
        self.assertGreater(len(smv_links), 0)
    
    def test_get_substation_info(self):
        """Test substation information extraction"""
        self.parser.load_file(str(self.sample_scd_path))
        substation_info = self.parser.get_substation_info()
        
        self.assertIn('name', substation_info)
        self.assertEqual(substation_info['name'], 'TestSubstation')


class TestLogicalLinkVisualizer(unittest.TestCase):
    """Test cases for visualizer functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.visualizer = LogicalLinkVisualizer()
        
        # Create sample data
        self.sample_ieds = [
            IED(name="IED1", type="Protection", manufacturer="Vendor1"),
            IED(name="IED2", type="Control", manufacturer="Vendor2"),
            IED(name="IED3", type="Measurement", manufacturer="Vendor3")
        ]
        
        self.sample_links = [
            LogicalLink(
                source_ied="IED1",
                target_ied="IED2", 
                link_type="GOOSE",
                link_id="GOOSE1",
                vlan_id="100"
            ),
            LogicalLink(
                source_ied="IED2",
                target_ied="IED3",
                link_type="SMV",
                link_id="SMV1",
                vlan_id="101"
            )
        ]
    
    def test_set_data(self):
        """Test setting data for visualization"""
        self.visualizer.set_data(self.sample_ieds, self.sample_links)
        
        self.assertEqual(len(self.visualizer.ieds), 3)
        self.assertEqual(len(self.visualizer.links), 2)
        self.assertEqual(self.visualizer.graph.number_of_nodes(), 3)
        self.assertEqual(self.visualizer.graph.number_of_edges(), 2)
    
    def test_generate_graphviz_diagram(self):
        """Test Graphviz diagram generation"""
        self.visualizer.set_data(self.sample_ieds, self.sample_links)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_diagram.png"
            
            try:
                result_path = self.visualizer.generate_graphviz_diagram(
                    output_format='png',
                    output_path=str(output_path)
                )
                
                # Check if file was created
                self.assertTrue(Path(result_path).exists())
                
            except Exception as e:
                # If graphviz is not installed, skip this test
                self.skipTest(f"Graphviz not available: {e}")
    
    def test_generate_matplotlib_diagram(self):
        """Test matplotlib diagram generation"""
        self.visualizer.set_data(self.sample_ieds, self.sample_links)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_diagram_matplotlib.png"
            
            result_path = self.visualizer.generate_matplotlib_diagram(str(output_path))
            
            # Check if file was created
            self.assertTrue(Path(result_path).exists())
    
    def test_get_network_statistics(self):
        """Test network statistics calculation"""
        self.visualizer.set_data(self.sample_ieds, self.sample_links)
        stats = self.visualizer.get_network_statistics()
        
        self.assertEqual(stats['total_ieds'], 3)
        self.assertEqual(stats['total_links'], 2)
        self.assertIn('link_types', stats)
        self.assertIn('ied_types', stats)
        self.assertGreater(stats['network_density'], 0)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete workflow"""
    
    def test_end_to_end_workflow(self):
        """Test complete parsing and visualization workflow"""
        # Parse sample SCD file
        parser = SCDParser()
        sample_scd_path = Path(__file__).parent.parent / "examples" / "sample_substation.scd"
        
        self.assertTrue(parser.load_file(str(sample_scd_path)))
        
        ieds = parser.extract_ieds()
        links = parser.extract_communication_links()
        
        self.assertGreater(len(ieds), 0)
        self.assertGreater(len(links), 0)
        
        # Visualize the data
        visualizer = LogicalLinkVisualizer()
        visualizer.set_data(ieds, links)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "integration_test.png"
            
            try:
                result_path = visualizer.generate_matplotlib_diagram(str(output_path))
                self.assertTrue(Path(result_path).exists())
                
                # Test statistics
                stats = visualizer.get_network_statistics()
                self.assertEqual(stats['total_ieds'], len(ieds))
                self.assertEqual(stats['total_links'], len(links))
                
            except Exception as e:
                self.fail(f"Integration test failed: {e}")


if __name__ == '__main__':
    unittest.main()