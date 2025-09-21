"""
Flask Web Interface for SCD Parser and Visualizer
"""

import os
import tempfile
import json
from pathlib import Path
from flask import Flask, request, render_template, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
import logging

from .parser import SCDParser
from .visualizer import LogicalLinkVisualizer
from .models import IED, LogicalLink

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'scd_parser_secret_key_change_in_production'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Upload folder configuration
UPLOAD_FOLDER = tempfile.mkdtemp()
ALLOWED_EXTENSIONS = {'scd', 'xml', 'icd', 'cid'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Handle SCD file upload and parsing"""
    if request.method == 'POST':
        # Check if file was uploaded
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            try:
                # Save uploaded file
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                # Parse SCD file
                parser = SCDParser()
                if not parser.load_file(file_path):
                    flash('Error loading SCD file. Please check the file format.')
                    return redirect(request.url)
                
                # Extract information
                ieds = parser.extract_ieds()
                links = parser.extract_communication_links()
                substation_info = parser.get_substation_info()
                comm_info = parser.get_communication_info()
                
                # Prepare data for display
                ied_data = [
                    {
                        'name': ied.name,
                        'type': ied.type,
                        'manufacturer': ied.manufacturer,
                        'config_version': ied.config_version,
                        'desc': ied.desc,
                        'logical_devices_count': len(ied.logical_devices),
                        'access_points_count': len(ied.access_points)
                    }
                    for ied in ieds
                ]
                
                link_data = [
                    {
                        'source_ied': link.source_ied,
                        'target_ied': link.target_ied,
                        'link_type': link.link_type,
                        'link_id': link.link_id,
                        'vlan_id': link.vlan_id,
                        'app_id': link.app_id
                    }
                    for link in links
                ]
                
                # Store data in session or temporary file for visualization
                session_data = {
                    'ieds': [
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
                    ],
                    'links': [
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
                }
                
                # Save session data to temp file
                session_file = os.path.join(app.config['UPLOAD_FOLDER'], 
                                          f"{filename}_session.json")
                with open(session_file, 'w', encoding='utf-8') as f:
                    json.dump(session_data, f, indent=2, ensure_ascii=False)
                
                # Calculate statistics
                stats = {
                    'total_ieds': len(ieds),
                    'total_links': len(links),
                    'ied_types': {},
                    'link_types': {}
                }
                
                for ied in ieds:
                    ied_type = ied.type or 'Unknown'
                    stats['ied_types'][ied_type] = stats['ied_types'].get(ied_type, 0) + 1
                
                for link in links:
                    link_type = link.link_type
                    stats['link_types'][link_type] = stats['link_types'].get(link_type, 0) + 1
                
                return render_template('results.html',
                                     filename=filename,
                                     substation_info=substation_info,
                                     ieds=ied_data,
                                     links=link_data,
                                     stats=stats,
                                     session_file=f"{filename}_session.json")
                
            except Exception as e:
                logger.error(f"Error processing file: {str(e)}")
                flash(f'Error processing file: {str(e)}')
                return redirect(request.url)
        
        else:
            flash('Invalid file type. Please upload SCD, XML, ICD, or CID files.')
            return redirect(request.url)
    
    return render_template('upload.html')


@app.route('/visualize/<session_file>')
def visualize(session_file):
    """Generate and display network visualization"""
    try:
        # Load session data
        session_path = os.path.join(app.config['UPLOAD_FOLDER'], session_file)
        
        if not os.path.exists(session_path):
            flash('Session data not found. Please upload file again.')
            return redirect(url_for('upload_file'))
        
        with open(session_path, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        # Convert to objects
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
            for ied in session_data['ieds']
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
            for link in session_data['links']
        ]
        
        # Create visualizer
        visualizer = LogicalLinkVisualizer()
        visualizer.set_data(ieds, links)
        
        # Generate SVG for web display
        svg_path = os.path.join(app.config['UPLOAD_FOLDER'], 
                              f"{session_file}_diagram.svg")
        visualizer.export_to_svg(svg_path)
        
        # Generate network statistics
        stats = visualizer.get_network_statistics()
        
        # Read SVG content
        with open(svg_path, 'r', encoding='utf-8') as f:
            svg_content = f.read()
        
        return render_template('visualization.html',
                             svg_content=svg_content,
                             stats=stats,
                             session_file=session_file)
        
    except Exception as e:
        logger.error(f"Error generating visualization: {str(e)}")
        flash(f'Error generating visualization: {str(e)}')
        return redirect(url_for('upload_file'))


@app.route('/download/<session_file>/<format_type>')
def download_diagram(session_file, format_type):
    """Download diagram in specified format"""
    try:
        # Load session data
        session_path = os.path.join(app.config['UPLOAD_FOLDER'], session_file)
        
        if not os.path.exists(session_path):
            flash('Session data not found.')
            return redirect(url_for('upload_file'))
        
        with open(session_path, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        # Convert to objects
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
            for ied in session_data['ieds']
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
            for link in session_data['links']
        ]
        
        # Create visualizer
        visualizer = LogicalLinkVisualizer()
        visualizer.set_data(ieds, links)
        
        # Generate file in requested format
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], 
                                 f"{session_file}_download.{format_type}")
        
        if format_type == 'svg':
            visualizer.export_to_svg(output_path)
        elif format_type == 'png':
            visualizer.export_to_png(output_path)
        elif format_type == 'pdf':
            visualizer.export_to_pdf(output_path)
        elif format_type == 'matplotlib':
            output_path = output_path.replace('.matplotlib', '.png')
            visualizer.generate_matplotlib_diagram(output_path)
        else:
            flash('Unsupported format')
            return redirect(url_for('visualize', session_file=session_file))
        
        return send_file(output_path, as_attachment=True)
        
    except Exception as e:
        logger.error(f"Error downloading diagram: {str(e)}")
        flash(f'Error downloading diagram: {str(e)}')
        return redirect(url_for('visualize', session_file=session_file))


@app.route('/api/parse', methods=['POST'])
def api_parse():
    """API endpoint for parsing SCD files"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Read file content
        content = file.read().decode('utf-8')
        
        # Parse SCD content
        parser = SCDParser()
        if not parser.load_from_content(content):
            return jsonify({'error': 'Error parsing SCD content'}), 400
        
        # Extract information
        ieds = parser.extract_ieds()
        links = parser.extract_communication_links()
        substation_info = parser.get_substation_info()
        
        # Prepare response data
        response_data = {
            'substation': substation_info,
            'ieds': [
                {
                    'name': ied.name,
                    'type': ied.type,
                    'manufacturer': ied.manufacturer,
                    'config_version': ied.config_version,
                    'desc': ied.desc,
                    'logical_devices_count': len(ied.logical_devices),
                    'access_points_count': len(ied.access_points)
                }
                for ied in ieds
            ],
            'links': [
                {
                    'source_ied': link.source_ied,
                    'target_ied': link.target_ied,
                    'link_type': link.link_type,
                    'link_id': link.link_id,
                    'vlan_id': link.vlan_id,
                    'app_id': link.app_id
                }
                for link in links
            ],
            'statistics': {
                'total_ieds': len(ieds),
                'total_links': len(links)
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"API parse error: {str(e)}")
        return jsonify({'error': str(e)}), 500


def create_app():
    """Application factory"""
    return app


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)