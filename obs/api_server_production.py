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

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Initialize SocketIO with CORS enabled
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global variables
current_refinement_prompt = ""
processing_jobs = {}
job_counter = 0

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

@app.route('/api/transcription/refine', methods=['POST'])
def refine_transcription():
    """Refine transcription using AI"""
    try:
        data = request.get_json() or {}
        raw_text = data.get('raw_text', '')
        prompt = data.get('prompt', current_refinement_prompt)
        
        if not raw_text:
            return jsonify({"error": "No raw text provided"}), 400
        
        if not prompt:
            return jsonify({"error": "No refinement prompt provided"}), 400
        
        # Try to use OpenAI for refinement
        try:
            import openai
            
            api_key = os.environ.get('OPENAI_API_KEY')
            if not api_key:
                return jsonify({"error": "OpenAI API key not configured"}), 500
            
            client = openai.OpenAI(api_key=api_key)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"You are a transcription refinement assistant. {prompt}"},
                    {"role": "user", "content": f"Please refine this transcription: {raw_text}"}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            refined_text = response.choices[0].message.content.strip()
            
            return jsonify({
                "success": True,
                "refined_text": refined_text,
                "original_text": raw_text,
                "prompt_used": prompt
            })
            
        except Exception as e:
            return jsonify({"error": f"AI refinement failed: {str(e)}"}), 500
            
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

# WebSocket events
@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    print(f"Starting StreamAI Production Server on port {port}")
    socketio.run(app, debug=debug, host='0.0.0.0', port=port)
