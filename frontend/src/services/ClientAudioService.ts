/**
 * Client-side Audio Capture Service for Production
 * Replaces server-side sounddevice library with browser-based audio capture
 */

export interface AudioConfig {
  sampleRate: number;
  channelCount: number;
  echoCancellation: boolean;
  noiseSuppression: boolean;
  chunkDuration: number; // in milliseconds
}

export interface TranscriptionResult {
  transcript: string;
  confidence?: number;
  timestamp: number;
}

export class ClientAudioService {
  private mediaRecorder: MediaRecorder | null = null;
  private audioStream: MediaStream | null = null;
  private audioChunks: Blob[] = [];
  private isRecording = false;
  private isListening = false;
  private onTranscriptionCallback?: (result: TranscriptionResult) => void;
  private chunkInterval?: number;
  
  private config: AudioConfig = {
    sampleRate: 16000,
    channelCount: 1,
    echoCancellation: true,
    noiseSuppression: true,
    chunkDuration: 2000 // 2 seconds
  };

  constructor(config?: Partial<AudioConfig>) {
    if (config) {
      this.config = { ...this.config, ...config };
    }
  }

  /**
   * Request microphone permission and start audio capture
   */
  async startListening(
    onTranscription: (result: TranscriptionResult) => void,
    groqApiKey: string
  ): Promise<boolean> {
    try {
      console.log('🎤 Requesting microphone access...');
      
      // Request microphone access with specific constraints
      this.audioStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: this.config.sampleRate,
          channelCount: this.config.channelCount,
          echoCancellation: this.config.echoCancellation,
          noiseSuppression: this.config.noiseSuppression,
          autoGainControl: true
        }
      });

      this.onTranscriptionCallback = onTranscription;
      
      // Create MediaRecorder
      const mimeType = this.getSupportedMimeType();
      this.mediaRecorder = new MediaRecorder(this.audioStream, {
        mimeType: mimeType
      });

      // Handle data available
      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data);
        }
      };

      // Handle recording stop
      this.mediaRecorder.onstop = () => {
        this.processAudioChunks(groqApiKey);
      };

      // Start recording
      this.mediaRecorder.start();
      this.isRecording = true;
      this.isListening = true;

      // Set up chunk processing interval
      this.chunkInterval = setInterval(() => {
        if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
          this.mediaRecorder.stop();
          setTimeout(() => {
            if (this.isListening && this.audioStream) {
              this.mediaRecorder = new MediaRecorder(this.audioStream, {
                mimeType: mimeType
              });
              this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                  this.audioChunks.push(event.data);
                }
              };
              this.mediaRecorder.onstop = () => {
                this.processAudioChunks(groqApiKey);
              };
              this.mediaRecorder.start();
            }
          }, 100);
        }
      }, this.config.chunkDuration);

      console.log('✅ Audio capture started successfully');
      return true;

    } catch (error) {
      console.error('❌ Failed to start audio capture:', error);
      
      if (error instanceof DOMException) {
        if (error.name === 'NotAllowedError') {
          throw new Error('Microphone access denied. Please allow microphone access and try again.');
        } else if (error.name === 'NotFoundError') {
          throw new Error('No microphone found. Please check your audio devices.');
        } else if (error.name === 'NotSupportedError') {
          throw new Error('Audio capture not supported in this browser.');
        }
      }
      
      throw new Error(`Audio capture failed: ${error}`);
    }
  }

  /**
   * Stop audio capture
   */
  stopListening(): void {
    console.log('🛑 Stopping audio capture...');
    
    this.isListening = false;
    this.isRecording = false;

    if (this.chunkInterval) {
      clearInterval(this.chunkInterval);
      this.chunkInterval = undefined;
    }

    if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
      this.mediaRecorder.stop();
    }

    if (this.audioStream) {
      this.audioStream.getTracks().forEach(track => track.stop());
      this.audioStream = null;
    }

    this.audioChunks = [];
    this.mediaRecorder = null;
  }

  /**
   * Get supported MIME type for MediaRecorder
   */
  private getSupportedMimeType(): string {
    const types = [
      'audio/webm;codecs=opus',
      'audio/webm',
      'audio/mp4',
      'audio/ogg;codecs=opus',
      'audio/wav'
    ];

    for (const type of types) {
      if (MediaRecorder.isTypeSupported(type)) {
        console.log(`📄 Using MIME type: ${type}`);
        return type;
      }
    }

    console.warn('⚠️  No supported MIME type found, using default');
    return 'audio/webm';
  }

  /**
   * Process accumulated audio chunks
   */
  private async processAudioChunks(groqApiKey: string): Promise<void> {
    if (this.audioChunks.length === 0) {
      return;
    }

    try {
      // Combine chunks into a single blob
      const audioBlob = new Blob(this.audioChunks, { 
        type: this.mediaRecorder?.mimeType || 'audio/webm' 
      });

      // Clear chunks for next round
      this.audioChunks = [];

      // Skip processing if blob is too small (likely silence)
      if (audioBlob.size < 1000) { // Less than 1KB
        return;
      }

      console.log(`🎵 Processing audio chunk: ${audioBlob.size} bytes`);

      // Send to backend for transcription
      const result = await this.sendAudioToBackend(audioBlob, groqApiKey);
      
      if (result && result.transcript && result.transcript.trim()) {
        this.onTranscriptionCallback?.({
          transcript: result.transcript,
          timestamp: Date.now()
        });
      }

    } catch (error) {
      console.error('❌ Error processing audio chunks:', error);
    }
  }

  /**
   * Send audio blob to backend for processing
   */
  private async sendAudioToBackend(audioBlob: Blob, groqApiKey: string): Promise<any> {
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'audio_chunk.webm');
      formData.append('groq_api_key', groqApiKey);

      const response = await fetch('/api/transcription/process-audio', {
        method: 'POST',
        body: formData,
        headers: {
          'X-Groq-API-Key': groqApiKey
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP ${response.status}`);
      }

      const result = await response.json();
      return result;

    } catch (error) {
      console.error('❌ Error sending audio to backend:', error);
      throw error;
    }
  }

  /**
   * Check if the browser supports audio capture
   */
  static isSupported(): boolean {
    return !!(
      navigator.mediaDevices &&
      typeof navigator.mediaDevices.getUserMedia === 'function' &&
      window.MediaRecorder
    );
  }

  /**
   * Get current listening status
   */
  getStatus() {
    return {
      isListening: this.isListening,
      isRecording: this.isRecording,
      isSupported: ClientAudioService.isSupported(),
      config: this.config
    };
  }
}

// Export singleton instance
export const clientAudioService = new ClientAudioService();
