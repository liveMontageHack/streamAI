#!/usr/bin/env python3
"""
API Server Intégré StreamAI
Serveur Flask avec support WebSocket pour l'enregistrement OBS + upload Vultr
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import asyncio
import json
import threading
import time
from datetime import datetime
from pathlib import Path
from integrated_recording_service import integrated_service

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Initialize SocketIO with CORS enabled
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global variables for live updates
live_update_thread = None
live_update_active = False

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/api/integrated/status', methods=['GET'])
def get_integrated_status():
    """Get integrated recording service status"""
    loop = None
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        success = loop.run_until_complete(integrated_service.initialize())
        if not success:
            return jsonify({"error": "Failed to initialize integrated service"}), 500
        
        # Get recording status
        recording_status = integrated_service.get_recording_status()
        
        # Get recent recordings
        recent_recordings = integrated_service.get_recent_recordings(limit=5)
        
        response_data = {
            "service_initialized": True,
            "recording_status": recording_status,
            "recent_recordings": recent_recordings,
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(response_data), 200
    except Exception as e:
        error_response = {"error": str(e), "timestamp": datetime.now().isoformat()}
        return jsonify(error_response), 500
    finally:
        if loop:
            loop.close()

@app.route('/api/integrated/recording/start', methods=['POST'])
def start_integrated_recording():
    """Start integrated recording (OBS + auto upload)"""
    loop = None
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        success = loop.run_until_complete(integrated_service.initialize())
        if not success:
            error_response = {"error": "Failed to initialize integrated service", "timestamp": datetime.now().isoformat()}
            return jsonify(error_response), 500
        
        # Get parameters from request
        data = request.get_json() or {}
        session_name = data.get('sessionName')
        auto_upload = data.get('autoUpload', True)
        
        # Start recording
        result = loop.run_until_complete(
            integrated_service.start_recording(session_name, auto_upload)
        )
        
        # Emit WebSocket event for real-time updates
        socketio.emit('recording_started', {
            'result': result,
            'timestamp': datetime.now().isoformat()
        }, room='recording_updates')
        
        return jsonify(result), 200
    except Exception as e:
        error_response = {"error": str(e), "timestamp": datetime.now().isoformat()}
        return jsonify(error_response), 500
    finally:
        if loop:
            loop.close()

@app.route('/api/integrated/recording/stop', methods=['POST'])
def stop_integrated_recording():
    """Stop integrated recording and trigger upload if configured"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        success = loop.run_until_complete(integrated_service.initialize())
        if not success:
            return jsonify({"error": "Failed to initialize integrated service"}), 500
        
        # Stop recording
        result = loop.run_until_complete(integrated_service.stop_recording())
        
        # Emit WebSocket event for real-time updates
        socketio.emit('recording_stopped', {
            'result': result,
            'timestamp': datetime.now().isoformat()
        }, room='recording_updates')
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        loop.close()

@app.route('/api/integrated/recordings', methods=['GET'])
def list_integrated_recordings():
    """List all recordings with upload status"""
    try:
        limit = request.args.get('limit', 10, type=int)
        recordings = integrated_service.get_recent_recordings(limit)
        
        return jsonify({
            "recordings": recordings,
            "count": len(recordings),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/integrated/upload/manual', methods=['POST'])
def manual_upload():
    """Manual upload of existing recording"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        data = request.get_json() or {}
        session_name = data.get('sessionName')
        subtitle_model = data.get('subtitleModel', 'base')
        priority = data.get('priority', 1)
        
        if not session_name:
            return jsonify({"error": "Session name is required"}), 400
        
        # Perform manual upload
        result = loop.run_until_complete(
            integrated_service.manual_upload(session_name, subtitle_model, priority)
        )
        
        # Emit WebSocket event
        socketio.emit('manual_upload_completed', {
            'session_name': session_name,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }, room='recording_updates')
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        loop.close()

@app.route('/api/integrated/recording/status', methods=['GET'])
def get_recording_status():
    """Get current recording status"""
    try:
        status = integrated_service.get_recording_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected: {request.sid}")
    emit('status', {
        'message': 'Connected to StreamAI Integrated Server',
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected: {request.sid}")

@socketio.on('join_recording_updates')
def handle_join_recording_updates():
    """Join recording updates room"""
    join_room('recording_updates')
    print(f"Client {request.sid} joined recording updates")
    emit('joined', {'room': 'recording_updates'})
    
    # Start live updates if not already running
    global live_update_active, live_update_thread
    if not live_update_active:
        live_update_active = True
        live_update_thread = threading.Thread(target=send_recording_updates)
        live_update_thread.daemon = True
        live_update_thread.start()

@socketio.on('leave_recording_updates')
def handle_leave_recording_updates():
    """Leave recording updates room"""
    leave_room('recording_updates')
    print(f"Client {request.sid} left recording updates")
    emit('left', {'room': 'recording_updates'})

def send_recording_updates():
    """Send live recording updates to connected clients"""
    global live_update_active
    
    while live_update_active:
        try:
            # Get current recording status
            status = integrated_service.get_recording_status()
            
            # Send live update
            socketio.emit('recording_status_update', {
                'timestamp': datetime.now().isoformat(),
                'status': status
            }, room='recording_updates')
            
        except Exception as e:
            print(f"Error in recording updates: {e}")
            socketio.emit('error', {
                'message': f'Recording update error: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }, room='recording_updates')
        
        # Wait 2 seconds before next update
        time.sleep(2)

# Additional endpoints for frontend integration

@app.route('/api/frontend/recordings/formatted', methods=['GET'])
def get_formatted_recordings():
    """Get recordings formatted for frontend display"""
    try:
        recordings = integrated_service.get_recent_recordings(limit=20)
        
        # Format for frontend
        formatted_recordings = []
        for recording in recordings:
            formatted = {
                'id': recording['name'],
                'title': recording['name'].replace('recording_session_', 'Session '),
                'date': recording['created'].strftime('%Y-%m-%d') if hasattr(recording['created'], 'strftime') else str(recording['created']),
                'duration': '00:00:00',  # Will be calculated from metadata if available
                'size': '0 MB',  # Will be calculated from files
                'views': 0,
                'thumbnail': None,
                'platforms': ['Local Recording'],
                'status': 'ready',
                'hasTranscription': False,
                'hasHighlights': False,
                'hasShorts': False,
                'categories': ['Recording'],
                'isManualUpload': False,
                'filePath': recording['path']
            }
            
            # Add upload info if available
            if 'vultr_upload' in recording:
                upload_info = recording['vultr_upload']
                formatted['vultr_task_id'] = upload_info.get('task_id')
                formatted['upload_status'] = upload_info.get('status')
                formatted['upload_time'] = upload_info.get('upload_time')
                formatted['platforms'].append('Vultr Processing')
            
            # Calculate file size if files exist
            total_size = 0
            for file_name in recording.get('files', []):
                try:
                    file_path = Path(recording['path']) / file_name
                    if file_path.exists():
                        total_size += file_path.stat().st_size
                except:
                    pass
            
            if total_size > 0:
                # Convert to human readable format
                if total_size > 1024**3:  # GB
                    formatted['size'] = f"{total_size / (1024**3):.1f} GB"
                elif total_size > 1024**2:  # MB
                    formatted['size'] = f"{total_size / (1024**2):.1f} MB"
                else:  # KB
                    formatted['size'] = f"{total_size / 1024:.1f} KB"
            
            formatted_recordings.append(formatted)
        
        return jsonify({
            'recordings': formatted_recordings,
            'count': len(formatted_recordings)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting StreamAI Integrated API Server...")
    print("API will be available at: http://localhost:5002")
    print("WebSocket will be available at: ws://localhost:5002")
    
    # Stop live updates when server shuts down
    try:
        socketio.run(app, debug=True, host='0.0.0.0', port=5002)
    finally:
        live_update_active = False
