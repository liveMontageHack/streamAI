import queue
import threading
import whisper
import numpy as np
import requests
import json


class Transcription:
    def __init__(self, sample_rate=16000, buffer_duration=1, api_url="http://localhost:5001"):
        self.sample_rate = sample_rate
        self.buffer_duration = buffer_duration  # seconds of audio before transcribing
        self.api_url = api_url

        print("Loading Whisper model...")
        self.model = whisper.load_model("tiny")
        print("Whisper model loaded.")

        self.audio_queue = queue.Queue()
        self.refinement_queue = queue.Queue()

        self.running = True
        self.worker_thread = threading.Thread(target=self._work_loop, daemon=True)
        self.worker_thread.start()

    def add_audio(self, audio_np):
        self.audio_queue.put(audio_np)

    def _work_loop(self):
        buffer = []
        total_samples = 0
        min_samples = self.sample_rate * self.buffer_duration

        while self.running:
            try:
                chunk = self.audio_queue.get(timeout=1)
                if chunk is not None:
                    buffer.append(chunk)
                    total_samples += len(chunk)

                if total_samples >= min_samples:
                    full_audio = np.concatenate(buffer)
                    buffer = []
                    total_samples = 0

                    result = self.model.transcribe(full_audio, fp16=False)
                    transcription = result.get("text", "").strip()

                    if transcription:
                        print("[Me] Raw:", transcription)
                        self.refinement_queue.put(transcription)
                        
                        # Send raw transcription to API server
                        self._send_raw_to_api(transcription)
                        
                        # Automatically refine and send refined version
                        self._auto_refine_and_send(transcription)

            except queue.Empty:
                continue

    def _send_raw_to_api(self, transcription):
        """Send raw transcription to API server queue"""
        try:
            response = requests.post(
                f"{self.api_url}/api/transcription/add",
                json={
                    "transcription": transcription,
                    "type": "raw",
                    "timestamp": json.dumps(requests.utils.default_user_agent(), default=str)
                },
                headers={"Content-Type": "application/json"},
                timeout=1
            )
            if not response.ok:
                print(f"[API] Failed to send raw transcription: {response.status_code}")
        except Exception as e:
            print(f"[API] Error sending raw transcription: {e}")
    
    def _auto_refine_and_send(self, raw_transcription):
        """Automatically refine transcription and send to API"""
        def refine_async():
            try:
                # Get the current refinement prompt from API
                response = requests.get(
                    f"{self.api_url}/api/transcription/prompt",
                    timeout=2
                )
                
                if response.ok:
                    prompt_data = response.json()
                    prompt = prompt_data.get('prompt', '')
                    
                    if prompt:
                        try:
                            # Import refinement function
                            from refinement import refine_transcription
                            
                            # Refine the transcription
                            refined_text = refine_transcription(raw_transcription, prompt)
                            print("[Groq] Refined:", refined_text)
                            
                            # Send refined transcription to API
                            response = requests.post(
                                f"{self.api_url}/api/transcription/add",
                                json={
                                    "transcription": refined_text,
                                    "type": "refined",
                                    "original": raw_transcription,
                                    "timestamp": json.dumps(requests.utils.default_user_agent(), default=str)
                                },
                                headers={"Content-Type": "application/json"},
                                timeout=2
                            )
                            
                            if not response.ok:
                                print(f"[API] Failed to send refined transcription: {response.status_code}")
                                
                        except Exception as groq_error:
                            error_msg = str(groq_error)
                            if "over capacity" in error_msg or "503" in error_msg:
                                print(f"[Groq] API over capacity, skipping refinement for: {raw_transcription[:50]}...")
                            else:
                                print(f"[Groq] Refinement error: {error_msg}")
                    else:
                        print("[Groq] No refinement prompt set, skipping refinement")
                else:
                    print(f"[API] Failed to get refinement prompt: {response.status_code}")
                    
            except Exception as e:
                print(f"[Refinement] Error: {e}")
        
        # Run refinement in a separate thread to avoid blocking
        refinement_thread = threading.Thread(target=refine_async, daemon=True)
        refinement_thread.start()

    def get_next_transcription(self):
        try:
            return self.refinement_queue.get_nowait()
        except queue.Empty:
            return None

    def stop(self):
        self.running = False
