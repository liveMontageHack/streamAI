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
                        
                        # Also send to API server queue for frontend consumption
                        self._send_to_api(transcription)

            except queue.Empty:
                continue

    def _send_to_api(self, transcription):
        """Send transcription to API server queue"""
        try:
            response = requests.post(
                f"{self.api_url}/api/transcription/add",
                json={"transcription": transcription},
                headers={"Content-Type": "application/json"},
                timeout=1  # Quick timeout to avoid blocking
            )
            if not response.ok:
                print(f"[API] Failed to send transcription: {response.status_code}")
        except Exception as e:
            print(f"[API] Error sending transcription: {e}")

    def get_next_transcription(self):
        try:
            return self.refinement_queue.get_nowait()
        except queue.Empty:
            return None

    def stop(self):
        self.running = False
