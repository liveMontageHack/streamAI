/**
 * Service API pour communiquer avec le serveur de traitement vidéo IA
 * Supporte le mode mock pour le développement local
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://45.32.145.22';
const MOCK_MODE = import.meta.env.VITE_MOCK_MODE === 'true';
const LOCAL_PROCESSING = import.meta.env.VITE_LOCAL_PROCESSING === 'true';

export interface UploadOptions {
  subtitle_model?: 'base' | 'small' | 'medium' | 'large';
  priority?: number;
}

export interface TaskStatus {
  task_id: string;
  status: 'uploaded' | 'processing' | 'completed' | 'completed_simple' | 'error';
  progress?: number;
  message?: string;
  result?: string;
  filename?: string;
  size?: number;
  config?: {
    subtitle_model: string;
    priority: number;
  };
}

export interface UploadResponse {
  task_id: string;
  status: string;
  filename: string;
  size: number;
  message: string;
  config: {
    subtitle_model: string;
    priority: number;
  };
}

export interface ProcessedResults {
  task_id: string;
  original_video: string;
  processed_video?: string;
  subtitles?: string;
  highlights?: string[];
  thumbnail?: string;
  duration?: string;
  processing_time?: string;
}

class VideoProcessingAPI {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Test de connectivité avec l'API
   */
  async testConnection(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/test`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        return data.test === 'success';
      }
      return false;
    } catch (error) {
      console.error('Erreur de connexion à l\'API:', error);
      return false;
    }
  }

  /**
   * Upload d'une vidéo pour traitement
   */
  async uploadVideoForProcessing(
    file: File, 
    options: UploadOptions = {}
  ): Promise<UploadResponse> {
    if (MOCK_MODE && LOCAL_PROCESSING) {
      return this.processVideoLocally(file, options);
    }

    const formData = new FormData();
    formData.append('file', file, file.name);
    formData.append('subtitle_model', options.subtitle_model || 'base');
    formData.append('priority', (options.priority || 1).toString());

    try {
      const response = await fetch(`${this.baseUrl}/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Erreur HTTP: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Erreur lors de l\'upload:', error);
      throw error;
    }
  }

  /**
   * Récupération du statut d'une tâche
   */
  async getTaskStatus(taskId: string): Promise<TaskStatus> {
    // Mode mock : récupérer depuis localStorage
    if (MOCK_MODE && LOCAL_PROCESSING && taskId.startsWith('local_')) {
      const localState = this.getLocalProcessingState(taskId);
      if (localState) {
        return localState;
      }
      // Si pas trouvé, retourner un état d'erreur
      return {
        task_id: taskId,
        status: 'error',
        message: 'Tâche locale non trouvée'
      };
    }

    try {
      const response = await fetch(`${this.baseUrl}/status/${taskId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Erreur HTTP: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Erreur lors de la récupération du statut:', error);
      throw error;
    }
  }

  /**
   * Polling du statut d'une tâche avec callback
   */
  async pollTaskProgress(
    taskId: string,
    onProgress: (status: TaskStatus) => void,
    onComplete: (status: TaskStatus) => void,
    onError: (error: Error) => void,
    intervalMs: number = 5000
  ): Promise<() => void> {
    let isPolling = true;

    const poll = async () => {
      if (!isPolling) return;

      try {
        const status = await this.getTaskStatus(taskId);
        onProgress(status);

        if (status.status === 'completed' || status.status === 'completed_simple') {
          isPolling = false;
          onComplete(status);
        } else if (status.status === 'error') {
          isPolling = false;
          onError(new Error(status.message || 'Erreur de traitement'));
        } else {
          // Continuer le polling
          setTimeout(poll, intervalMs);
        }
      } catch (error) {
        isPolling = false;
        onError(error as Error);
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
   * Récupération des informations de l'API
   */
  async getAPIInfo(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Erreur lors de la récupération des infos API:', error);
      throw error;
    }
  }

  /**
   * Génération d'URL pour les résultats (si disponibles)
   */
  getResultUrl(taskId: string, type: 'video' | 'subtitles' | 'thumbnail' = 'video'): string {
    return `${this.baseUrl}/results/${taskId}/${type}`;
  }

  /**
   * Estimation du temps de traitement basé sur la taille du fichier
   */
  estimateProcessingTime(fileSizeBytes: number): string {
    // Estimation approximative : 1 minute de traitement par 100MB
    const fileSizeMB = fileSizeBytes / (1024 * 1024);
    const estimatedMinutes = Math.ceil(fileSizeMB / 100);
    
    if (estimatedMinutes < 1) {
      return 'Moins d\'1 minute';
    } else if (estimatedMinutes < 60) {
      return `${estimatedMinutes} minute${estimatedMinutes > 1 ? 's' : ''}`;
    } else {
      const hours = Math.floor(estimatedMinutes / 60);
      const minutes = estimatedMinutes % 60;
      return `${hours}h${minutes > 0 ? ` ${minutes}min` : ''}`;
    }
  }

  /**
   * Formatage de la taille de fichier
   */
  formatFileSize(bytes: number): string {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  }

  /**
   * Traitement vidéo local (mode mock)
   */
  private async processVideoLocally(file: File, options: UploadOptions): Promise<UploadResponse> {
    const taskId = `local_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    try {
      // Sauvegarder le fichier localement
      const uploadDir = 'recordings/mock_uploads';
      const fileName = `${taskId}_${file.name}`;
      
      // Créer un blob URL pour simuler la sauvegarde
      const arrayBuffer = await file.arrayBuffer();
      const blob = new Blob([arrayBuffer], { type: file.type });
      
      // Simuler la sauvegarde (en réalité, on utiliserait l'API File System ou un serveur local)
      console.log(`[MOCK] Sauvegarde de ${fileName} dans ${uploadDir}`);
      
      // Lancer le traitement en arrière-plan
      this.startLocalProcessing(taskId, fileName, options);
      
      return {
        task_id: taskId,
        status: 'uploaded',
        filename: fileName,
        size: file.size,
        message: 'Fichier uploadé en mode local - traitement en cours',
        config: {
          subtitle_model: options.subtitle_model || 'base',
          priority: options.priority || 1
        }
      };
    } catch (error) {
      console.error('Erreur lors du traitement local:', error);
      throw new Error(`Erreur de traitement local: ${error}`);
    }
  }

  /**
   * Démarrer le traitement local en arrière-plan
   */
  private async startLocalProcessing(taskId: string, fileName: string, options: UploadOptions) {
    // Simuler les étapes de traitement
    const steps = [
      { progress: 10, message: 'Initialisation du processeur Whisper...' },
      { progress: 25, message: 'Extraction audio...' },
      { progress: 40, message: 'Transcription en cours...' },
      { progress: 60, message: 'Analyse du contenu...' },
      { progress: 80, message: 'Édition de la vidéo...' },
      { progress: 95, message: 'Génération des sous-titres...' },
      { progress: 100, message: 'Traitement terminé' }
    ];

    // Sauvegarder l'état initial
    let processingState: any = {
      task_id: taskId,
      status: 'processing',
      progress: 0,
      message: 'Démarrage du traitement...',
      filename: fileName,
      config: {
        subtitle_model: options.subtitle_model || 'base',
        priority: options.priority || 1
      }
    };

    this.saveProcessingState(taskId, processingState);

    // Simuler le traitement progressif
    for (const step of steps) {
      await new Promise(resolve => setTimeout(resolve, 2000)); // 2 secondes par étape
      
      processingState.progress = step.progress;
      processingState.message = step.message;
      
      if (step.progress === 100) {
        processingState.status = 'completed';
        processingState.result = `Traitement terminé - Vidéo éditée disponible`;
      }
      
      this.saveProcessingState(taskId, processingState);
    }

    console.log(`[MOCK] Traitement terminé pour ${taskId}`);
  }

  /**
   * Sauvegarder l'état de traitement (simulation avec localStorage)
   */
  private saveProcessingState(taskId: string, state: any) {
    if (typeof window !== 'undefined') {
      localStorage.setItem(`processing_${taskId}`, JSON.stringify(state));
    }
  }

  /**
   * Récupérer l'état de traitement local
   */
  private getLocalProcessingState(taskId: string): TaskStatus | null {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem(`processing_${taskId}`);
      if (stored) {
        return JSON.parse(stored);
      }
    }
    return null;
  }
}

// Instance singleton
export const videoProcessingAPI = new VideoProcessingAPI();
