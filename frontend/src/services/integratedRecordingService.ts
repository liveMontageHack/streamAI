/**
 * Service d'enregistrement intégré StreamAI
 * Gère l'enregistrement OBS + upload automatique vers Vultr
 */

import { io, Socket } from 'socket.io-client';

export interface RecordingSession {
  id: string;
  name: string;
  startTime: string;
  endTime?: string;
  status: 'recording' | 'stopped' | 'uploading' | 'completed';
  autoUpload: boolean;
  sessionPath: string;
  vultrTaskId?: string;
  uploadStatus?: string;
  uploadTime?: string;
}

export interface RecordingStatus {
  active: boolean;
  sessionName?: string;
  startTime?: string;
  autoUpload?: boolean;
  obsStatus?: {
    active: boolean;
    paused: boolean;
    timecode: string;
    bytes: number;
  };
  sessionPath?: string;
  message?: string;
}

export interface StartRecordingOptions {
  sessionName?: string;
  autoUpload?: boolean;
}

export interface UploadOptions {
  sessionName: string;
  subtitleModel?: 'base' | 'small' | 'medium' | 'large';
  priority?: number;
}

class IntegratedRecordingService {
  private baseUrl: string;
  private socket: Socket | null = null;
  private isConnected = false;

  constructor(baseUrl: string = 'http://localhost:5002') {
    this.baseUrl = baseUrl;
  }

  /**
   * Initialiser la connexion WebSocket
   */
  initializeWebSocket(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.socket = io(this.baseUrl, {
          transports: ['websocket', 'polling']
        });

        this.socket.on('connect', () => {
          console.log('🔌 Connecté au serveur d\'enregistrement intégré');
          this.isConnected = true;
          
          // Rejoindre la room des mises à jour d'enregistrement
          this.socket?.emit('join_recording_updates');
          resolve();
        });

        this.socket.on('disconnect', () => {
          console.log('🔌 Déconnecté du serveur d\'enregistrement intégré');
          this.isConnected = false;
        });

        this.socket.on('connect_error', (error: Error) => {
          console.error('❌ Erreur de connexion WebSocket:', error);
          reject(error);
        });

        // Écouter les événements d'enregistrement
        this.setupEventListeners();

      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * Configurer les écouteurs d'événements WebSocket
   */
  private setupEventListeners() {
    if (!this.socket) return;

    this.socket.on('recording_started', (data) => {
      console.log('🎬 Enregistrement démarré:', data);
      this.onRecordingStarted?.(data);
    });

    this.socket.on('recording_stopped', (data) => {
      console.log('⏹️ Enregistrement arrêté:', data);
      this.onRecordingStopped?.(data);
    });

    this.socket.on('recording_status_update', (data) => {
      this.onStatusUpdate?.(data.status);
    });

    this.socket.on('manual_upload_completed', (data) => {
      console.log('📤 Upload manuel terminé:', data);
      this.onUploadCompleted?.(data);
    });

    this.socket.on('error', (data) => {
      console.error('❌ Erreur WebSocket:', data);
      this.onError?.(data);
    });
  }

  /**
   * Callbacks pour les événements (à définir par l'utilisateur)
   */
  onRecordingStarted?: (data: any) => void;
  onRecordingStopped?: (data: any) => void;
  onStatusUpdate?: (status: RecordingStatus) => void;
  onUploadCompleted?: (data: any) => void;
  onError?: (error: any) => void;

  /**
   * Vérifier l'état du service
   */
  async checkServiceStatus(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/api/integrated/status`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Erreur lors de la vérification du statut:', error);
      throw error;
    }
  }

  /**
   * Démarrer un enregistrement
   */
  async startRecording(options: StartRecordingOptions = {}): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/api/integrated/recording/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          sessionName: options.sessionName,
          autoUpload: options.autoUpload ?? true
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      console.log('🎬 Enregistrement démarré:', result);
      return result;
    } catch (error) {
      console.error('Erreur lors du démarrage de l\'enregistrement:', error);
      throw error;
    }
  }

  /**
   * Arrêter l'enregistrement
   */
  async stopRecording(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/api/integrated/recording/stop`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      console.log('⏹️ Enregistrement arrêté:', result);
      return result;
    } catch (error) {
      console.error('Erreur lors de l\'arrêt de l\'enregistrement:', error);
      throw error;
    }
  }

  /**
   * Obtenir le statut de l'enregistrement en cours
   */
  async getRecordingStatus(): Promise<RecordingStatus> {
    try {
      const response = await fetch(`${this.baseUrl}/api/integrated/recording/status`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Erreur lors de la récupération du statut:', error);
      throw error;
    }
  }

  /**
   * Lister les enregistrements
   */
  async getRecordings(limit: number = 10): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/api/integrated/recordings?limit=${limit}`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Erreur lors de la récupération des enregistrements:', error);
      throw error;
    }
  }

  /**
   * Obtenir les enregistrements formatés pour le frontend
   */
  async getFormattedRecordings(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/api/frontend/recordings/formatted`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Erreur lors de la récupération des enregistrements formatés:', error);
      throw error;
    }
  }

  /**
   * Upload manuel d'un enregistrement
   */
  async manualUpload(options: UploadOptions): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/api/integrated/upload/manual`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          sessionName: options.sessionName,
          subtitleModel: options.subtitleModel || 'base',
          priority: options.priority || 1
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      console.log('📤 Upload manuel:', result);
      return result;
    } catch (error) {
      console.error('Erreur lors de l\'upload manuel:', error);
      throw error;
    }
  }

  /**
   * Vérifier la connectivité
   */
  async testConnection(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/health`);
      return response.ok;
    } catch (error) {
      console.error('Test de connexion échoué:', error);
      return false;
    }
  }

  /**
   * Fermer la connexion WebSocket
   */
  disconnect() {
    if (this.socket) {
      this.socket.emit('leave_recording_updates');
      this.socket.disconnect();
      this.socket = null;
      this.isConnected = false;
    }
  }

  /**
   * Vérifier si WebSocket est connecté
   */
  get isWebSocketConnected(): boolean {
    return this.isConnected && this.socket?.connected === true;
  }

  /**
   * Polling du statut d'enregistrement
   */
  async pollRecordingStatus(
    onUpdate: (status: RecordingStatus) => void,
    onError: (error: Error) => void,
    intervalMs: number = 2000
  ): Promise<() => void> {
    let isPolling = true;

    const poll = async () => {
      if (!isPolling) return;

      try {
        const status = await this.getRecordingStatus();
        onUpdate(status);

        if (isPolling) {
          setTimeout(poll, intervalMs);
        }
      } catch (error) {
        onError(error as Error);
        if (isPolling) {
          setTimeout(poll, intervalMs * 2); // Retry with longer interval
        }
      }
    };

    // Démarrer le polling
    poll();

    // Retourner une fonction pour arrêter le polling
    return () => {
      isPolling = false;
    };
  }

  /**
   * Formater la durée d'enregistrement
   */
  formatDuration(timecode: string): string {
    if (!timecode || timecode === '00:00:00') return '00:00:00';
    return timecode;
  }

  /**
   * Formater la taille de fichier
   */
  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
}

// Instance singleton
export const integratedRecordingService = new IntegratedRecordingService();

export default IntegratedRecordingService;
