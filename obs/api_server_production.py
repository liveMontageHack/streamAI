#!/usr/bin/env python3
"""
StreamAI API Server - Production Version

Simplified Flask web server for Railway deployment.
Removes problematic imports and focuses on core functionality.
"""

from flask import Flask, jsonify, request, send_file, abort
from flask_cors import CORS
from flask_socketio import SocketIO
import os
import json
import time
from pathlib import Path
from datetime import datetime
import queue
from werkzeug.utils import secure_filename
import tempfile

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Initialize SocketIO with CORS enabled
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global variables
current_refinement_prompt = ""
processing_jobs = {}
job_counter = 0

# Global queue for transcription polling (simple in-memory implementation)
transcription_queue = queue.Queue()

# Initialize app settings with environment variable fallbacks
app_settings = {
    "groq_api_key": os.environ.get("GROQ_API_KEY", ""),
    "webhook_url": os.environ.get("WEBHOOK_URL", ""),
    "auto_notifications": os.environ.get("AUTO_NOTIFICATIONS", "true").lower() == "true",
    "transcription_language": os.environ.get("TRANSCRIPTION_LANGUAGE", "en")
}

# Mock data for development/testing
mock_recordings = [
    {
        "id": "mock_recording_1",
        "title": "Sample Stream Recording",
        "date": "2025-01-07",
        "duration": "1:23:45",
        "size": "2.1 GB",
        "views": 156,
        "thumbnail": "https://images.pexels.com/photos/442576/pexels-photo-442576.jpeg?auto=compress&cs=tinysrgb&w=400",
        "platforms": ["Local Recording"],
        "status": "ready",
        "hasTranscription": True,
        "hasHighlights": False,
        "hasShorts": False,
        "categories": ["Gaming", "Just Chatting"],
        "technical": {
            "session_path": "recordings/sample_stream",
            "local_recordings": ["sample_stream/recording.mp4"],
            "file_size_bytes": 2147483648
        }
    },
    {
        "id": "mock_recording_2", 
        "title": "Tutorial Session",
        "date": "2025-01-06",
        "duration": "0:45:30",
        "size": "1.2 GB",
        "views": 89,
        "thumbnail": "https://images.pexels.com/photos/1181673/pexels-photo-1181673.jpeg?auto=compress&cs=tinysrgb&w=400",
        "platforms": ["Local Recording"],
        "status": "processing",
        "hasTranscription": False,
        "hasHighlights": True,
        "hasShorts": False,
        "categories": ["Education", "Programming"],
        "technical": {
            "session_path": "recordings/tutorial_session",
            "local_recordings": ["tutorial_session/recording.mp4"],
            "file_size_bytes": 1288490189
        }
    }
]

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get current application settings"""
    # Don't return sensitive data like API keys in full
    safe_settings = app_settings.copy()
    if safe_settings.get("groq_api_key"):
        safe_settings["groq_api_key"] = "••••••••••••••••••••••••••••••••••••••••"
    
    return jsonify({"success": True, "settings": safe_settings})

@app.route('/api/settings', methods=['POST'])
def save_settings():
    """Save application settings"""
    global app_settings
    try:
        data = request.get_json() or {}
        
        # Update settings with provided data
        if 'groq_api_key' in data:
            app_settings['groq_api_key'] = data['groq_api_key']
        if 'webhook_url' in data:
            app_settings['webhook_url'] = data['webhook_url']
        if 'auto_notifications' in data:
            app_settings['auto_notifications'] = data['auto_notifications']
        if 'transcription_language' in data:
            app_settings['transcription_language'] = data['transcription_language']
        
        return jsonify({"success": True, "message": "Settings saved successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0-production",
        "environment": "railway"
    })

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    return jsonify({
        "status": "running",
        "mode": "production",
        "features": {
            "recording": False,  # Disabled in production
            "transcription": True,
            "video_processing": True,
            "obs_integration": False  # Disabled in production
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/recordings', methods=['GET'])
def list_recordings():
    """List all recording sessions"""
    try:
        # In production, this would connect to a real database
        # For now, return mock data
        return jsonify({
            "success": True, 
            "recordings": mock_recordings,
            "total": len(mock_recordings)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/recording/start', methods=['POST'])
def start_recording():
    """Start recording session - Disabled in production"""
    return jsonify({
        "success": False, 
        "error": "Recording functionality is disabled in production deployment. Use local installation for recording."
    }), 501

@app.route('/api/recording/stop', methods=['POST'])
def stop_recording():
    """Stop recording session - Disabled in production"""
    return jsonify({
        "success": False, 
        "error": "Recording functionality is disabled in production deployment. Use local installation for recording."
    }), 501

@app.route('/api/obs/data', methods=['GET'])
def get_obs_data():
    """Get current OBS data - Disabled in production"""
    return jsonify({
        "error": "OBS integration is disabled in production deployment. Use local installation for OBS features."
    }), 501

@app.route('/api/youtube/data', methods=['GET'])
def get_youtube_data():
    """Get YouTube data"""
    try:
        # Mock YouTube data for production
        return jsonify({
            "channel": {
                "name": "StreamAI Demo",
                "subscribers": "1.2K",
                "views": "15.6K",
                "videos": 42
            },
            "recent_videos": [
                {
                    "title": "Latest Stream Highlights",
                    "views": "234",
                    "duration": "5:23",
                    "published": "2 days ago"
                }
            ]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/transcription/prompt', methods=['POST'])
def save_transcription_prompt():
    """Save transcription refinement prompt"""
    global current_refinement_prompt
    try:
        data = request.get_json() or {}
        prompt = data.get('prompt', '')
        current_refinement_prompt = prompt
        return jsonify({"success": True, "message": "Refinement prompt saved successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/transcription/prompt', methods=['GET'])
def get_transcription_prompt():
    """Get current transcription refinement prompt"""
    global current_refinement_prompt
    return jsonify({"prompt": current_refinement_prompt})

@app.route('/api/transcription/validate-key', methods=['POST'])
def validate_groq_api_key():
    """Validate a Groq API key without saving it"""
    try:
        data = request.get_json() or {}
        test_api_key = data.get('api_key', '')
        
        if not test_api_key:
            return jsonify({"error": "No API key provided for validation"}), 400
        
        # Try to use Groq for a simple test
        try:
            from groq import Groq
            
            client = Groq(api_key=test_api_key)
            
            # Simple test message
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        'role': 'system',
                        'content': 'You are a test assistant. Respond with exactly: "API key validated successfully"'
                    },
                    {
                        'role': 'user',
                        'content': 'Test message'
                    }
                ],
                model='llama-3.1-8b-instant',
                max_tokens=20
            )
            
            response_text = chat_completion.choices[0].message.content.strip()
            
            return jsonify({
                "success": True,
                "valid": True,
                "message": "API key is valid and working correctly"
            })
            
        except Exception as e:
            error_msg = str(e).lower()
            
            # Check for specific Groq API errors
            if "invalid api key" in error_msg or "unauthorized" in error_msg or "401" in error_msg:
                return jsonify({
                    "success": True,
                    "valid": False,
                    "message": "Invalid API key"
                }), 200  # Return 200 for successful validation check, even if key is invalid
            elif "rate limit" in error_msg or "429" in error_msg:
                return jsonify({
                    "success": True,
                    "valid": True,
                    "message": "API key is valid but rate limited"
                }), 200
            elif "over capacity" in error_msg or "503" in error_msg:
                return jsonify({
                    "success": True,
                    "valid": True,
                    "message": "API key is valid but service is over capacity"
                }), 200
            else:
                return jsonify({
                    "success": False,
                    "error": f"Validation failed: {str(e)}"
                }), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/transcription/refine', methods=['POST'])
def refine_transcription_endpoint():
    """Refine transcription using Groq AI"""
    global app_settings
    try:
        data = request.get_json() or {}
        raw_text = data.get('raw_text', '')
        prompt = data.get('prompt', current_refinement_prompt)
        
        if not raw_text:
            return jsonify({"error": "No raw text provided"}), 400
        
        if not prompt:
            return jsonify({"error": "No refinement prompt provided"}), 400
        
        # Check if Groq API key is configured
        # Allow temporary key for validation, otherwise use stored key
        groq_api_key = data.get('groq_api_key') or app_settings.get('groq_api_key') or os.environ.get('GROQ_API_KEY')
        if not groq_api_key:
            return jsonify({"error": "Groq API key not configured. Please set it in Settings."}), 400
        
        # Try to use Groq for refinement
        try:
            from groq import Groq
            
            client = Groq(api_key=groq_api_key)
            
            system_message = f"""You are a professional transcription editor. Your task is to clean up audio transcriptions.

{prompt}

IMPORTANT RULES:
- Respond ONLY with the corrected transcription text
- Do NOT ask questions or provide explanations
- Do NOT add commentary or analysis
- Keep the original meaning intact
- Focus only on grammar, spelling, punctuation, and clarity improvements"""

            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        'role': 'system',
                        'content': system_message
                    },
                    {
                        'role': 'user',
                        'content': f"Please clean up this transcription: {raw_text}"
                    }
                ],
                model='llama-3.1-8b-instant'
            )
            
            refined_text = chat_completion.choices[0].message.content.strip()
            
            return jsonify({
                "success": True,
                "refined_text": refined_text,
                "original_text": raw_text,
                "prompt_used": prompt
            })
            
        except Exception as e:
            error_msg = str(e).lower()
            
            # Check for specific Groq API errors
            if "invalid api key" in error_msg or "unauthorized" in error_msg or "401" in error_msg:
                return jsonify({"error": "Invalid Groq API key. Please check your API key in Settings."}), 401
            elif "rate limit" in error_msg or "429" in error_msg:
                return jsonify({"error": "Groq API rate limit exceeded. Please try again later."}), 429
            elif "over capacity" in error_msg or "503" in error_msg:
                return jsonify({"error": "Groq API is over capacity. Please try again in a moment."}), 503
            elif "connection" in error_msg or "network" in error_msg or "timeout" in error_msg:
                return jsonify({"error": "Network error connecting to Groq API. Please check your internet connection."}), 503
            else:
                return jsonify({"error": f"Groq AI refinement failed: {str(e)}"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/transcription/add', methods=['POST'])
def add_transcription():
    """Add transcription data - Updated for polling support"""
    global transcription_queue
    try:
        data = request.get_json() or {}
        transcription = data.get('transcription', '')
        transcription_type = data.get('type', 'raw')
        timestamp = data.get('timestamp', datetime.now().isoformat())
        original = data.get('original', '')
        
        print(f"[Transcription] {transcription_type.upper()}: {transcription}")
        
        # Create transcription object for polling
        transcription_obj = {
            'content': transcription,
            'type': transcription_type,
            'timestamp': timestamp
        }
        if original:
            transcription_obj['original'] = original
        
        # Add to polling queue
        transcription_queue.put(transcription_obj)
        
        # Also emit via WebSocket for real-time updates
        socketio.emit('new_transcription', {
            'text': transcription,
            'type': transcription_type,
            'timestamp': timestamp
        })
        
        return jsonify({"success": True, "message": "Transcription added"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/video/presets', methods=['GET'])
def get_video_presets():
    """Get available video processing presets"""
    presets = {
        "fast": {
            "name": "Fast Processing",
            "description": "Quick processing with basic editing",
            "features": ["Basic cuts", "Simple transitions"]
        },
        "balanced": {
            "name": "Balanced Quality",
            "description": "Good balance of speed and quality",
            "features": ["Smart cuts", "Audio enhancement", "Basic effects"]
        },
        "high_quality": {
            "name": "High Quality",
            "description": "Best quality with advanced features",
            "features": ["Advanced cuts", "Audio enhancement", "Visual effects", "Color correction"]
        }
    }
    return jsonify({"success": True, "presets": presets})

@app.route('/api/video/process', methods=['POST'])
def process_video():
    """Start video processing - Mock implementation"""
    global processing_jobs, job_counter
    
    try:
        data = request.get_json() or {}
        recording_id = data.get('recording_id')
        preset = data.get('preset', 'balanced')
        
        if not recording_id:
            return jsonify({"error": "No recording ID provided"}), 400
        
        # Create mock job
        job_counter += 1
        job_id = f"job_{job_counter}_{int(time.time())}"
        
        processing_jobs[job_id] = {
            "id": job_id,
            "recording_id": recording_id,
            "preset": preset,
            "status": "processing",
            "progress": 0,
            "message": "Starting video processing...",
            "start_time": time.time()
        }
        
        # Simulate processing progress
        def simulate_progress():
            import threading
            import time
            
            def progress_worker():
                for progress in range(0, 101, 10):
                    if job_id in processing_jobs:
                        processing_jobs[job_id]["progress"] = progress
                        if progress < 100:
                            processing_jobs[job_id]["message"] = f"Processing... {progress}%"
                        else:
                            processing_jobs[job_id]["status"] = "completed"
                            processing_jobs[job_id]["message"] = "Processing completed!"
                    time.sleep(2)
            
            thread = threading.Thread(target=progress_worker)
            thread.daemon = True
            thread.start()
        
        simulate_progress()
        
        return jsonify({
            "success": True,
            "job_id": job_id,
            "message": "Video processing started",
            "status": processing_jobs[job_id]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/video/status/<job_id>', methods=['GET'])
def get_processing_status(job_id):
    """Get the status of a video processing job"""
    try:
        if job_id not in processing_jobs:
            return jsonify({"error": "Job not found"}), 404
        
        job_status = processing_jobs[job_id].copy()
        job_status["elapsed_time"] = time.time() - job_status["start_time"]
        
        return jsonify({"success": True, "status": job_status})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/recordings/<recording_id>/thumbnail', methods=['GET'])
def serve_recording_thumbnail(recording_id):
    """Serve thumbnail for recording - Mock implementation"""
    # Return a placeholder image URL
    return jsonify({
        "thumbnail_url": "https://images.pexels.com/photos/442576/pexels-photo-442576.jpeg?auto=compress&cs=tinysrgb&w=400"
    })

@app.route('/api/recordings/<recording_id>/download', methods=['GET'])
def download_recording_video(recording_id):
    """Download recording - Mock implementation"""
    return jsonify({
        "error": "Video download is not available in production deployment. Use local installation for full video features."
    }), 501

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

@app.route('/api/transcription/listening/start', methods=['POST'])
def start_listening():
    """Start real-time audio transcription - Mock implementation for production"""
    try:
        # In production, this would start your audio capture service
        # For now, return success to maintain API compatibility
        return jsonify({
            "success": True, 
            "message": "Started listening for audio transcription (mock)",
            "status": {"is_listening": True, "is_running": True}
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/transcription/listening/stop', methods=['POST'])
def stop_listening():
    """Stop real-time audio transcription - Mock implementation for production"""
    try:
        # In production, this would stop your audio capture service
        return jsonify({
            "success": True, 
            "message": "Stopped listening for audio transcription (mock)",
            "status": {"is_listening": False, "is_running": False}
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/transcription/listening/status', methods=['GET'])
def get_listening_status():
    """Get current listening status - Mock implementation for production"""
    try:
        # In production, this would return actual status from your audio service
        return jsonify({
            "is_listening": False,
            "is_running": False,
            "message": "Audio transcription service not available in production"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/transcription/process-audio', methods=['POST'])
def process_audio():
    """Process uploaded audio file from frontend"""
    try:
        # Check if audio file is in the request
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        groq_api_key = request.headers.get('X-Groq-API-Key') or request.form.get('groq_api_key')
        
        if not groq_api_key:
            return jsonify({'error': 'Groq API key required in headers (X-Groq-API-Key) or form data'}), 400
        
        if audio_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        allowed_extensions = {'wav', 'mp3', 'ogg', 'webm', 'm4a'}
        file_extension = audio_file.filename.rsplit('.', 1)[1].lower() if '.' in audio_file.filename else ''
        
        if file_extension not in allowed_extensions:
            return jsonify({'error': f'Unsupported file type. Allowed: {", ".join(allowed_extensions)}'}), 400
        
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as temp_file:
            audio_file.save(temp_file.name)
            temp_path = temp_file.name
        
        try:
            # Import and use the production audio service
            sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'realtime_audio'))
            
            try:
                from production_audio_service import get_production_service
                audio_service = get_production_service()
                
                # Start service if not running
                if not audio_service.is_running:
                    if not audio_service.start_service():
                        return jsonify({'error': 'Failed to start audio processing service'}), 500
                
                # Process the audio file
                transcript = audio_service.process_audio_file(temp_path, groq_api_key)
                
                if transcript:
                    return jsonify({
                        'success': True,
                        'transcript': transcript,
                        'message': 'Audio processed successfully'
                    })
                else:
                    return jsonify({
                        'success': True,
                        'transcript': '',
                        'message': 'No speech detected in audio'
                    })
                    
            except ImportError as e:
                # Fallback: basic audio processing without the service
                return jsonify({'error': f'Audio processing service not available: {str(e)}'}), 500
                
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
    except Exception as e:
        return jsonify({'error': f'Audio processing failed: {str(e)}'}), 500

# WebSocket events
@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = False  # Always disable debug in production
    
    print(f"Starting StreamAI Production Server on port {port}")
    print(f"Railway Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'local')}")
    
    try:
        socketio.run(
            app, 
            debug=debug, 
            host='0.0.0.0', 
            port=port,
            allow_unsafe_werkzeug=True,
            log_output=True
        )
    except Exception as e:
        print(f"Error starting server: {e}")
        raise
