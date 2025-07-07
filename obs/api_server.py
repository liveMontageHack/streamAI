#!/usr/bin/env python3
"""
StreamAI API Server

Flask web server with WebSocket support to provide REST API endpoints 
and real-time communication for the frontend.
"""

from flask import Flask, jsonify, request, send_file, abort
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import asyncio
import json
import threading
import time
import os
import cv2
from pathlib import Path
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
            return jsonify({"success": False, "error": "Failed to initialize application"}), 500
            
        recordings = loop.run_until_complete(stream_app.list_sessions())
        return jsonify({"success": True, "recordings": recordings})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
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
    """Refine transcription using the provided or saved prompt"""
    global current_refinement_prompt
    try:
        data = request.get_json() or {}
        raw_text = data.get('raw_text', '')
        provided_prompt = data.get('prompt', '')  # Accept prompt from request
        
        if not raw_text:
            return jsonify({"error": "No raw text provided"}), 400
        
        # Use provided prompt or fall back to saved prompt
        prompt_to_use = provided_prompt.strip() or current_refinement_prompt
        
        if not prompt_to_use:
            return jsonify({"error": "No refinement prompt provided or saved"}), 400
        
        # Import and use the refinement function
        try:
            import sys
            import os
            # Add the realtime_audio directory to the path
            realtime_audio_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'realtime_audio')
            if realtime_audio_path not in sys.path:
                sys.path.append(realtime_audio_path)
            
            from refinement import refine_transcription
            
            refined_text = refine_transcription(raw_text, prompt_to_use)
            
            return jsonify({
                "success": True,
                "refined_text": refined_text,
                "original_text": raw_text,
                "prompt_used": prompt_to_use
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
        message_type = data.get('type', 'raw')  # 'raw' or 'refined'
        original = data.get('original', '')
        
        if not transcription:
            return jsonify({"error": "No transcription provided"}), 400
        
        # Create a structured message for the frontend
        message = {
            "id": str(datetime.now().timestamp()),
            "type": message_type,
            "content": transcription,
            "timestamp": datetime.now().isoformat()
        }
        
        if message_type == 'refined' and original:
            message["original"] = original
        
        # Add to queue
        transcription_queue.put(message)
        
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

@app.route('/api/recordings/<recording_id>/video', methods=['GET'])
def serve_recording_video(recording_id):
    """Serve the video file for a specific recording"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        success = loop.run_until_complete(stream_app.initialize())
        if not success:
            return jsonify({"error": "Failed to initialize application"}), 500
        
        # Get all recordings to find the one with the matching ID
        recordings = loop.run_until_complete(stream_app.list_sessions())
        recording = None
        
        for rec in recordings:
            if rec.get('id') == recording_id:
                recording = rec
                break
        
        if not recording:
            abort(404)
        
        # Get the video file path from technical metadata
        video_path = None
        if recording.get('technical', {}).get('local_recordings'):
            # Use the first video file
            relative_path = recording['technical']['local_recordings'][0]
            # Convert to absolute path
            recordings_dir = Path(__file__).parent / 'recordings'
            video_path = recordings_dir / relative_path
            
            # If the relative path doesn't work, try building the path differently
            if not video_path.exists():
                # Try: recordings_dir / session_name / filename
                session_name = recording['title']
                filename = relative_path.split('/')[-1]  # Get just the filename
                video_path = recordings_dir / session_name / filename
            
            # If the relative path doesn't work, try the absolute path from obs_recordings
            if not video_path.exists() and recording['technical'].get('obs_recordings'):
                video_path = Path(recording['technical']['obs_recordings'][0])
        
        if not video_path or not video_path.exists():
            abort(404)
        
        return send_file(str(video_path), as_attachment=False, mimetype='video/mp4')
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        loop.close()

@app.route('/api/recordings/<recording_id>/thumbnail', methods=['GET'])
def serve_recording_thumbnail(recording_id):
    """Generate and serve a thumbnail (first frame) for a specific recording"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        success = loop.run_until_complete(stream_app.initialize())
        if not success:
            return jsonify({"error": "Failed to initialize application"}), 500
        
        # Get all recordings to find the one with the matching ID
        recordings = loop.run_until_complete(stream_app.list_sessions())
        recording = None
        
        for rec in recordings:
            if rec.get('id') == recording_id:
                recording = rec
                break
        
        if not recording:
            abort(404)
        
        # Get the video file path
        video_path = None
        if recording.get('technical', {}).get('local_recordings'):
            relative_path = recording['technical']['local_recordings'][0]
            recordings_dir = Path(__file__).parent / 'recordings'
            video_path = recordings_dir / relative_path
            
            # If the relative path doesn't work, try building the path differently
            if not video_path.exists():
                # Try: recordings_dir / session_name / filename
                session_name = recording['title']
                filename = relative_path.split('/')[-1]  # Get just the filename
                video_path = recordings_dir / session_name / filename
            
            # Last resort: try obs_recordings path if available
            if not video_path.exists() and recording['technical'].get('obs_recordings'):
                video_path = Path(recording['technical']['obs_recordings'][0])
        
        if not video_path or not video_path.exists():
            abort(404)
        
        # Generate thumbnail path
        thumbnail_dir = video_path.parent / 'thumbnails'
        thumbnail_dir.mkdir(exist_ok=True)
        thumbnail_path = thumbnail_dir / f"{video_path.stem}_thumbnail.jpg"
        
        # Generate thumbnail if it doesn't exist
        if not thumbnail_path.exists():
            try:
                # Use OpenCV to extract first frame
                cap = cv2.VideoCapture(str(video_path))
                ret, frame = cap.read()
                cap.release()
                
                if ret:
                    # Resize frame to a reasonable thumbnail size
                    height, width = frame.shape[:2]
                    aspect_ratio = width / height
                    thumbnail_width = 320
                    thumbnail_height = int(thumbnail_width / aspect_ratio)
                    
                    resized_frame = cv2.resize(frame, (thumbnail_width, thumbnail_height))
                    cv2.imwrite(str(thumbnail_path), resized_frame)
                else:
                    abort(404)  # Could not extract frame
                    
            except Exception as e:
                print(f"Error generating thumbnail: {e}")
                abort(500)
        
        return send_file(str(thumbnail_path), mimetype='image/jpeg')
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        loop.close()

@app.route('/api/recordings/<recording_id>/download', methods=['GET'])
def download_recording_video(recording_id):
    """Download the video file for a specific recording"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        success = loop.run_until_complete(stream_app.initialize())
        if not success:
            return jsonify({"error": "Failed to initialize application"}), 500
        
        # Get all recordings to find the one with the matching ID
        recordings = loop.run_until_complete(stream_app.list_sessions())
        recording = None
        
        for rec in recordings:
            if rec.get('id') == recording_id:
                recording = rec
                break
        
        if not recording:
            abort(404)
        
        # Get the video file path from technical metadata
        video_path = None
        if recording.get('technical', {}).get('local_recordings'):
            # Use the first video file
            relative_path = recording['technical']['local_recordings'][0]
            # Convert to absolute path
            recordings_dir = Path(__file__).parent / 'recordings'
            video_path = recordings_dir / relative_path
            
            # If the relative path doesn't work, try building the path differently
            if not video_path.exists():
                # Try: recordings_dir / session_name / filename
                session_name = recording['title']
                filename = relative_path.split('/')[-1]  # Get just the filename
                video_path = recordings_dir / session_name / filename
            
            # If the relative path doesn't work, try the absolute path from obs_recordings
            if not video_path.exists() and recording['technical'].get('obs_recordings'):
                video_path = Path(recording['technical']['obs_recordings'][0])
        
        if not video_path or not video_path.exists():
            abort(404)
        
        # Generate a clean filename for download
        session_name = recording.get('title', 'recording')
        timestamp = recording.get('timestamp', '').replace(':', '-').replace(' ', '_')
        download_filename = f"{session_name}_{timestamp}.{video_path.suffix[1:]}"
        
        return send_file(
            str(video_path), 
            as_attachment=True, 
            download_name=download_filename,
            mimetype='video/mp4'
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        loop.close()

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
