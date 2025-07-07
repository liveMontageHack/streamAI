#!/usr/bin/env python3
"""
StreamAI API Server

Flask web server with WebSocket support to provide REST API endpoints 
and real-time communication for the frontend.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import asyncio
import json
import threading
import time
from datetime import datetime
from recording_manager import RecordingManager
from main import StreamAIApp

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Initialize SocketIO with CORS enabled
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global app instance
stream_app = StreamAIApp()

# Global variables for live updates
live_update_thread = None
live_update_active = False

# Global variable to store the current refinement prompt
current_refinement_prompt = ""

# Global queue for transcriptions (in production, use a proper queue system like Redis)
import queue
transcription_queue = queue.Queue()

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    try:
        # Since Flask doesn't handle async well, we'll need to run async code in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        success = loop.run_until_complete(stream_app.initialize())
        if not success:
            return jsonify({"error": "Failed to initialize application"}), 500
            
        status = stream_app.recording_manager.get_system_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        loop.close()

@app.route('/api/recording/start', methods=['POST'])
def start_recording():
    """Start recording session"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        success = loop.run_until_complete(stream_app.initialize())
        if not success:
            return jsonify({"error": "Failed to initialize application"}), 500
        
        # Get session name from request body
        data = request.get_json() or {}
        session_name = data.get('sessionName')
        
        result = loop.run_until_complete(stream_app.start_recording(session_name, continuous=False))
        return jsonify({"success": result, "message": "Recording started" if result else "Failed to start recording"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        loop.close()

@app.route('/api/recording/stop', methods=['POST'])
def stop_recording():
    """Stop recording session"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        success = loop.run_until_complete(stream_app.initialize())
        if not success:
            return jsonify({"error": "Failed to initialize application"}), 500
            
        result = loop.run_until_complete(stream_app.stop_recording())
        return jsonify({"success": result, "message": "Recording stopped" if result else "Failed to stop recording"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        loop.close()

@app.route('/api/recordings', methods=['GET'])
def list_recordings():
    """List all recording sessions"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        success = loop.run_until_complete(stream_app.initialize())
        if not success:
            return jsonify({"error": "Failed to initialize application"}), 500
            
        recordings = loop.run_until_complete(stream_app.list_sessions())
        return jsonify({"recordings": recordings})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        loop.close()

@app.route('/api/obs/data', methods=['GET'])
def get_obs_data():
    """Get current OBS data"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        success = loop.run_until_complete(stream_app.initialize())
        if not success:
            return jsonify({"error": "Failed to initialize application"}), 500
            
        obs_data = loop.run_until_complete(stream_app.get_obs_data())
        return jsonify(obs_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        loop.close()

@app.route('/api/youtube/data', methods=['GET'])
def get_youtube_data():
    """Get YouTube data"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        success = loop.run_until_complete(stream_app.initialize())
        if not success:
            return jsonify({"error": "Failed to initialize application"}), 500
            
        youtube_data = loop.run_until_complete(stream_app.get_youtube_data())
        return jsonify(youtube_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        loop.close()

@app.route('/api/transcription/prompt', methods=['POST'])
def save_transcription_prompt():
    """Save transcription refinement prompt"""
    global current_refinement_prompt
    try:
        data = request.get_json() or {}
        prompt = data.get('prompt', '')
        
        # Save the prompt globally (in production, you'd save this to a database)
        current_refinement_prompt = prompt
        
        return jsonify({"success": True, "message": "Refinement prompt saved successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/transcription/prompt', methods=['GET'])
def get_transcription_prompt():
    """Get current transcription refinement prompt"""
    global current_refinement_prompt
    return jsonify({"prompt": current_refinement_prompt})

@app.route('/api/transcription/refine', methods=['POST'])
def refine_transcription():
    """Refine transcription using the saved prompt"""
    global current_refinement_prompt
    try:
        data = request.get_json() or {}
        raw_text = data.get('raw_text', '')
        
        if not raw_text:
            return jsonify({"error": "No raw text provided"}), 400
        
        if not current_refinement_prompt:
            return jsonify({"error": "No refinement prompt set"}), 400
        
        # Import and use the refinement function
        try:
            import sys
            import os
            # Add the realtime_audio directory to the path
            realtime_audio_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'realtime_audio')
            if realtime_audio_path not in sys.path:
                sys.path.append(realtime_audio_path)
            
            from refinement import refine_transcription
            
            refined_text = refine_transcription(raw_text, current_refinement_prompt)
            
            return jsonify({
                "success": True,
                "refined_text": refined_text,
                "original_text": raw_text,
                "prompt_used": current_refinement_prompt
            })
        except ImportError as e:
            return jsonify({"error": f"Could not import refinement module: {str(e)}"}), 500
        except Exception as e:
            return jsonify({"error": f"Refinement failed: {str(e)}"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/api/transcription/poll', methods=['GET'])
def poll_transcriptions():
    """Poll for new transcriptions from the queue"""
    global transcription_queue
    try:
        # Try to get a transcription from the queue (non-blocking)
        try:
            transcription = transcription_queue.get_nowait()
            return jsonify({"transcription": transcription, "timestamp": datetime.now().isoformat()})
        except queue.Empty:
            return jsonify({"transcription": None})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/transcription/add', methods=['POST'])
def add_transcription():
    """Add a new transcription to the queue (for testing or external integration)"""
    global transcription_queue
    try:
        data = request.get_json() or {}
        transcription = data.get('transcription', '')
        
        if not transcription:
            return jsonify({"error": "No transcription provided"}), 400
        
        # Add to queue
        transcription_queue.put(transcription)
        
        return jsonify({"success": True, "message": "Transcription added to queue"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/transcription/listening/start', methods=['POST'])
def start_listening():
    """Start real-time audio transcription"""
    try:
        # Import the transcription service
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        
        try:
            from realtime_audio.realtime_transcription_service import transcription_service
            
            if not transcription_service.is_running:
                # Initialize and start the service
                if transcription_service.start_service():
                    result = transcription_service.start_listening()
                else:
                    return jsonify({"error": "Failed to start transcription service"}), 500
            else:
                result = transcription_service.start_listening()
            
            if result:
                return jsonify({
                    "success": True, 
                    "message": "Started listening for audio transcription",
                    "status": transcription_service.get_listening_status()
                })
            else:
                return jsonify({"error": "Failed to start listening"}), 500
                
        except ImportError:
            return jsonify({"error": "Transcription service not available"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/transcription/listening/stop', methods=['POST'])
def stop_listening():
    """Stop real-time audio transcription"""
    try:
        # Import the transcription service
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        
        try:
            from realtime_audio.realtime_transcription_service import transcription_service
            
            result = transcription_service.stop_listening()
            
            return jsonify({
                "success": True, 
                "message": "Stopped listening for audio transcription",
                "status": transcription_service.get_listening_status()
            })
                
        except ImportError:
            return jsonify({"error": "Transcription service not available"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/transcription/listening/status', methods=['GET'])
def get_listening_status():
    """Get current listening status"""
    try:
        # Import the transcription service
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        
        try:
            from realtime_audio.realtime_transcription_service import transcription_service
            return jsonify(transcription_service.get_listening_status())
                
        except ImportError:
            return jsonify({
                "is_running": False,
                "is_listening": False,
                "error": "Transcription service not available"
            })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected: {request.sid}")
    emit('status', {'message': 'Connected to StreamAI server', 'timestamp': datetime.now().isoformat()})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected: {request.sid}")

@socketio.on('join_live_updates')
def handle_join_live_updates():
    """Join live updates room"""
    join_room('live_updates')
    print(f"Client {request.sid} joined live updates")
    emit('joined', {'room': 'live_updates'})
    
    # Start live updates if not already running
    global live_update_active, live_update_thread
    if not live_update_active:
        live_update_active = True
        live_update_thread = threading.Thread(target=send_live_updates)
        live_update_thread.daemon = True
        live_update_thread.start()

@socketio.on('leave_live_updates')
def handle_leave_live_updates():
    """Leave live updates room"""
    leave_room('live_updates')
    print(f"Client {request.sid} left live updates")
    emit('left', {'room': 'live_updates'})

@socketio.on('join_transcription')
def handle_join_transcription():
    """Join transcription room"""
    join_room('transcription')
    print(f"Client {request.sid} joined transcription")
    emit('joined', {'room': 'transcription'})

@socketio.on('leave_transcription')
def handle_leave_transcription():
    """Leave transcription room"""
    leave_room('transcription')
    print(f"Client {request.sid} left transcription")
    emit('left', {'room': 'transcription'})

@socketio.on('transcription_message')
def handle_transcription_message(data):
    """Handle incoming transcription message"""
    print(f"Received transcription message: {data}")
    # Broadcast to all clients in transcription room
    socketio.emit('transcription_update', {
        'message': data.get('message', ''),
        'user': data.get('user', 'Unknown'),
        'timestamp': datetime.now().isoformat()
    }, room='transcription')

def send_live_updates():
    """Send live updates to connected clients"""
    global live_update_active
    
    while live_update_active:
        try:
            # Get current system status
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            success = loop.run_until_complete(stream_app.initialize())
            if success:
                # Get OBS data
                obs_data = loop.run_until_complete(stream_app.get_obs_data())
                
                # Send live update
                socketio.emit('live_update', {
                    'timestamp': datetime.now().isoformat(),
                    'obs_data': obs_data,
                    'recording_status': obs_data.get('recording_status', {}),
                    'stream_status': obs_data.get('stream_status', {})
                }, room='live_updates')
            
            loop.close()
            
        except Exception as e:
            print(f"Error in live updates: {e}")
            socketio.emit('error', {
                'message': f'Live update error: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }, room='live_updates')
        
        # Wait 5 seconds before next update
        time.sleep(5)

if __name__ == '__main__':
    print("Starting StreamAI API Server with WebSocket support...")
    print("API will be available at: http://localhost:5001")
    print("WebSocket will be available at: ws://localhost:5001")
    
    # Stop live updates when server shuts down
    try:
        socketio.run(app, debug=True, host='0.0.0.0', port=5001)
    finally:
        live_update_active = False
