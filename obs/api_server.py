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
import shutil
import cv2
from pathlib import Path
from datetime import datetime
from recording_manager import RecordingManager
from main import StreamAIApp
from video_processor import StreamAIVideoProcessor
from vultr_service import vultr_service

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Initialize SocketIO with CORS enabled
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global app instance
stream_app = StreamAIApp()

# Initialize video processor
video_processor = StreamAIVideoProcessor()

# Global variables for live updates
live_update_thread = None
live_update_active = False

# Global variable to store the current refinement prompt
current_refinement_prompt = ""

# Global queue for transcriptions (in production, use a proper queue system like Redis)
import queue
transcription_queue = queue.Queue()

# Global dictionary to track processing jobs
processing_jobs = {}
job_counter = 0

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

# Video Processing Endpoints

@app.route('/api/video/presets', methods=['GET'])
def get_video_presets():
    """Get available video processing presets"""
    try:
        presets = video_processor.get_presets()
        return jsonify({"success": True, "presets": presets})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/video/process', methods=['POST'])
def process_video():
    """Start video processing with specified preset"""
    global processing_jobs, job_counter
    
    try:
        data = request.get_json() or {}
        recording_id = data.get('recording_id')
        preset = data.get('preset', 'balanced')
        language = data.get('language', 'en')
        
        if not recording_id:
            return jsonify({"error": "No recording ID provided"}), 400
        
        # Get the recording
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        success = loop.run_until_complete(stream_app.initialize())
        if not success:
            return jsonify({"error": "Failed to initialize application"}), 500
        
        recordings = loop.run_until_complete(stream_app.list_sessions())
        recording = None
        
        for rec in recordings:
            if rec.get('id') == recording_id:
                recording = rec
                break
        
        if not recording:
            return jsonify({"error": "Recording not found"}), 404
        
        # Get video path
        video_path = None
        if recording.get('technical', {}).get('local_recordings'):
            relative_path = recording['technical']['local_recordings'][0]
            recordings_dir = Path(__file__).parent / 'recordings'
            video_path = recordings_dir / relative_path
            
            if not video_path.exists():
                session_name = recording['title']
                filename = relative_path.split('/')[-1]
                video_path = recordings_dir / session_name / filename
            
            if not video_path.exists() and recording['technical'].get('obs_recordings'):
                video_path = Path(recording['technical']['obs_recordings'][0])
        
        if not video_path or not video_path.exists():
            return jsonify({"error": "Video file not found"}), 404
        
        # Create job ID
        job_counter += 1
        job_id = f"job_{job_counter}_{int(time.time())}"
        
        # Create output directory
        output_dir = Path(__file__).parent / 'processed_videos' / f"{recording_id}_{job_id}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize job status
        processing_jobs[job_id] = {
            "id": job_id,
            "recording_id": recording_id,
            "recording_title": recording.get('title', 'Unknown'),
            "preset": preset,
            "language": language,
            "status": "starting",
            "progress": 0,
            "message": "Initializing video processing...",
            "start_time": time.time(),
            "video_path": str(video_path),
            "output_dir": str(output_dir),
            "result": None,
            "error": None
        }
        
        # Start processing in a separate thread
        def process_video_async():
            try:
                # Create new event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Progress callback
                def progress_callback(progress, message):
                    if job_id in processing_jobs:
                        processing_jobs[job_id]["progress"] = progress
                        processing_jobs[job_id]["message"] = message
                        if progress == -1:
                            processing_jobs[job_id]["status"] = "error"
                            processing_jobs[job_id]["error"] = message
                        elif progress == 100:
                            processing_jobs[job_id]["status"] = "completed"
                        else:
                            processing_jobs[job_id]["status"] = "processing"
                
                # Process the video
                result = loop.run_until_complete(
                    video_processor.process_video(
                        str(video_path),
                        preset=preset,
                        output_dir=str(output_dir),
                        language=language,
                        progress_callback=progress_callback
                    )
                )
                
                if job_id in processing_jobs:
                    processing_jobs[job_id]["result"] = result
                    processing_jobs[job_id]["status"] = "completed"
                    processing_jobs[job_id]["progress"] = 100
                    processing_jobs[job_id]["message"] = "Video processing completed successfully!"
                
            except Exception as e:
                if job_id in processing_jobs:
                    processing_jobs[job_id]["status"] = "error"
                    processing_jobs[job_id]["error"] = str(e)
                    processing_jobs[job_id]["message"] = f"Processing failed: {str(e)}"
            finally:
                loop.close()
        
        # Start the processing thread
        processing_thread = threading.Thread(target=process_video_async)
        processing_thread.daemon = True
        processing_thread.start()
        
        return jsonify({
            "success": True,
            "job_id": job_id,
            "message": "Video processing started",
            "status": processing_jobs[job_id]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        loop.close()

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

@app.route('/api/video/download/<job_id>', methods=['GET'])
def download_processed_video(job_id):
    """Download the processed video file"""
    try:
        if job_id not in processing_jobs:
            return jsonify({"error": "Job not found"}), 404
        
        job = processing_jobs[job_id]
        
        if job["status"] != "completed":
            return jsonify({"error": "Processing not completed"}), 400
        
        if not job["result"]:
            return jsonify({"error": "No result available"}), 400
        
        # Get the processed video path
        edited_video_path = job["result"]["edited_video"]
        
        if not os.path.exists(edited_video_path):
            return jsonify({"error": "Processed video file not found"}), 404
        
        # Generate download filename
        recording_title = job["recording_title"]
        preset = job["preset"]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        download_filename = f"{recording_title}_{preset}_edited_{timestamp}.mp4"
        
        return send_file(
            edited_video_path,
            as_attachment=True,
            download_name=download_filename,
            mimetype='video/mp4'
        )
        
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

# Vultr Upload Endpoints

@app.route('/api/vultr/status', methods=['GET'])
def get_vultr_status():
    """Get Vultr service status and configuration"""
    try:
        config_info = vultr_service.get_config_info()
        connection_test = vultr_service.test_connection()
        
        return jsonify({
            "success": True,
            "config": config_info,
            "connection": connection_test
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/vultr/upload', methods=['POST'])
def upload_to_vultr():
    """Upload a recording to Vultr server"""
    try:
        data = request.get_json() or {}
        recording_id = data.get('recording_id')
        auto_process = data.get('auto_process', False)
        
        if not recording_id:
            return jsonify({"error": "No recording ID provided"}), 400
        
        # Get the recording
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        success = loop.run_until_complete(stream_app.initialize())
        if not success:
            return jsonify({"error": "Failed to initialize application"}), 500
        
        recordings = loop.run_until_complete(stream_app.list_sessions())
        recording = None
        
        for rec in recordings:
            if rec.get('id') == recording_id:
                recording = rec
                break
        
        if not recording:
            return jsonify({"error": "Recording not found"}), 404
        
        # Get video path
        video_path = None
        if recording.get('technical', {}).get('local_recordings'):
            relative_path = recording['technical']['local_recordings'][0]
            recordings_dir = Path(__file__).parent / 'recordings'
            video_path = recordings_dir / relative_path
            
            if not video_path.exists():
                session_name = recording['title']
                filename = relative_path.split('/')[-1]
                video_path = recordings_dir / session_name / filename
            
            if not video_path.exists() and recording['technical'].get('obs_recordings'):
                video_path = Path(recording['technical']['obs_recordings'][0])
        
        if not video_path or not video_path.exists():
            return jsonify({"error": "Video file not found"}), 404
        
        # Upload to Vultr
        session_name = recording.get('title', 'Unknown')
        upload_result = vultr_service.upload_file(
            video_path, 
            session_name=session_name,
            auto_process=auto_process
        )
        
        return jsonify(upload_result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        loop.close()

@app.route('/api/vultr/upload/status/<task_id>', methods=['GET'])
def get_vultr_upload_status(task_id):
    """Get the status of a Vultr upload/processing task"""
    try:
        result = vultr_service.get_upload_status(task_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/vultr/uploads', methods=['GET'])
def list_vultr_uploads():
    """List recent Vultr uploads"""
    try:
        limit = request.args.get('limit', 10, type=int)
        result = vultr_service.list_uploads(limit)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/vultr/test', methods=['GET'])
def test_vultr_connection():
    """Test connection to Vultr server"""
    try:
        result = vultr_service.test_connection()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Get port from environment variable (Railway sets this)
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    socketio.run(app, debug=debug, host='0.0.0.0', port=port)
