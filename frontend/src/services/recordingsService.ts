import { Recording } from '../types/Recording';

export interface RecordingFile {
  id: string;
  title: string;
  date: string;
  duration: string;
  size: string;
  filePath: string;
  sessionName: string;
  thumbnail?: string;
}

const MOCK_MODE = import.meta.env.VITE_MOCK_MODE === 'true';

class RecordingsService {
  private baseUrl = 'http://localhost:5001/api'; // API locale pour accéder aux fichiers

  async getRecordings(): Promise<Recording[]> {
    if (MOCK_MODE) {
      return this.getMockRecordings();
    }

    try {
      const response = await fetch(`${this.baseUrl}/recordings`);
      if (!response.ok) {
        throw new Error('Failed to fetch recordings');
      }
      
      const recordingFiles: RecordingFile[] = await response.json();
      
      // Convertir les fichiers en format Recording pour l'interface
      return recordingFiles.map(file => ({
        id: file.id,
        title: file.title || file.sessionName,
        date: file.date,
        duration: file.duration,
        size: file.size,
        views: 0, // Nouveau enregistrement, pas encore de vues
        thumbnail: file.thumbnail || this.getDefaultThumbnail(),
        platforms: ['Local Recording'],
        status: 'ready' as const,
        hasTranscription: false,
        hasHighlights: false,
        hasShorts: false,
        categories: this.inferCategories(file.sessionName || file.title),
        isManualUpload: false,
        filePath: file.filePath
      }));
    } catch (error) {
      console.error('Error fetching recordings:', error);
      // Retourner des données de démonstration si l'API n'est pas disponible
      return this.getDemoRecordings();
    }
  }

  async getRecordingFile(recordingId: string): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/recordings/${recordingId}/file`);
    if (!response.ok) {
      throw new Error('Failed to fetch recording file');
    }
    return response.blob();
  }

  async generateThumbnail(recordingId: string): Promise<string> {
    try {
      const response = await fetch(`${this.baseUrl}/recordings/${recordingId}/thumbnail`, {
        method: 'POST'
      });
      if (!response.ok) {
        throw new Error('Failed to generate thumbnail');
      }
      const data = await response.json();
      return data.thumbnailUrl;
    } catch (error) {
      console.error('Error generating thumbnail:', error);
      return this.getDefaultThumbnail();
    }
  }

  private getDefaultThumbnail(): string {
    const thumbnails = [
      'https://images.pexels.com/photos/442576/pexels-photo-442576.jpeg?auto=compress&cs=tinysrgb&w=400',
      'https://images.pexels.com/photos/1181673/pexels-photo-1181673.jpeg?auto=compress&cs=tinysrgb&w=400',
      'https://images.pexels.com/photos/1181677/pexels-photo-1181677.jpeg?auto=compress&cs=tinysrgb&w=400',
      'https://images.pexels.com/photos/1181244/pexels-photo-1181244.jpeg?auto=compress&cs=tinysrgb&w=400'
    ];
    return thumbnails[Math.floor(Math.random() * thumbnails.length)];
  }

  private inferCategories(title: string): string[] {
    const titleLower = title.toLowerCase();
    const categories: string[] = [];

    if (titleLower.includes('gaming') || titleLower.includes('game')) {
      categories.push('Gaming');
    }
    if (titleLower.includes('coding') || titleLower.includes('programming')) {
      categories.push('Programming');
    }
    if (titleLower.includes('tutorial') || titleLower.includes('learn')) {
      categories.push('Education');
    }
    if (titleLower.includes('chat') || titleLower.includes('discussion')) {
      categories.push('Just Chatting');
    }
    if (titleLower.includes('music')) {
      categories.push('Music');
    }
    if (titleLower.includes('art') || titleLower.includes('design')) {
      categories.push('Art');
    }

    // Si aucune catégorie détectée, ajouter une catégorie par défaut
    if (categories.length === 0) {
      categories.push('Entertainment');
    }

    return categories;
  }

  /**
   * Récupérer les enregistrements en mode mock
   * Scanne les dossiers locaux et simule les fichiers
   */
  private async getMockRecordings(): Promise<Recording[]> {
    const recordings: Recording[] = [];

    // Simuler des enregistrements locaux existants
    const mockLocalRecordings = [
      {
        id: 'local_session_1',
        title: 'Session de streaming - Gaming',
        date: new Date().toISOString().split('T')[0],
        duration: '1:23:45',
        size: '2.1 GB',
        filePath: 'recordings/recording_session_20250706_164405/2025-07-06 16-44-05.mkv',
        sessionName: 'recording_session_20250706_164405',
        thumbnail: this.getDefaultThumbnail()
      }
    ];

    // Convertir les enregistrements locaux
    for (const file of mockLocalRecordings) {
      recordings.push({
        id: file.id,
        title: file.title,
        date: file.date,
        duration: file.duration,
        size: file.size,
        views: 0,
        thumbnail: file.thumbnail,
        platforms: ['Local Recording'],
        status: 'ready' as const,
        hasTranscription: false,
        hasHighlights: false,
        hasShorts: false,
        categories: this.inferCategories(file.title),
        isManualUpload: false,
        filePath: file.filePath
      });
    }

    // Ajouter les enregistrements traités (depuis localStorage)
    const processedRecordings = this.getProcessedRecordings();
    recordings.push(...processedRecordings);

    // Ajouter quelques enregistrements de démo pour tester l'interface
    recordings.push(...this.getDemoRecordings());

    return recordings;
  }

  /**
   * Récupérer les enregistrements traités depuis localStorage
   */
  private getProcessedRecordings(): Recording[] {
    if (typeof window === 'undefined') return [];

    const processedRecordings: Recording[] = [];
    
    // Parcourir localStorage pour trouver les tâches terminées
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith('processing_local_')) {
        try {
          const data = JSON.parse(localStorage.getItem(key) || '{}');
          if (data.status === 'completed') {
            processedRecordings.push({
              id: data.task_id,
              title: `Vidéo traitée - ${data.filename}`,
              date: new Date().toISOString().split('T')[0],
              duration: '0:45:30', // Durée simulée
              size: '1.2 GB',
              views: 0,
              thumbnail: this.getDefaultThumbnail(),
              platforms: ['Local Processing'],
              status: 'ready' as const,
              hasTranscription: true,
              hasHighlights: true,
              hasShorts: true,
              categories: ['AI Processed'],
              isManualUpload: true
            });
          }
        } catch (error) {
          console.error('Erreur lors de la lecture des données traitées:', error);
        }
      }
    }

    return processedRecordings;
  }

  private getDemoRecordings(): Recording[] {
    return [
      {
        id: '1',
        title: 'Epic Gaming Session - New Game Release',
        date: '2024-01-15',
        duration: '2:34:12',
        size: '4.2 GB',
        views: 1247,
        thumbnail: 'https://images.pexels.com/photos/442576/pexels-photo-442576.jpeg?auto=compress&cs=tinysrgb&w=400',
        platforms: ['Twitch', 'YouTube'],
        status: 'ready',
        hasTranscription: true,
        hasHighlights: true,
        hasShorts: true,
        categories: ['Gaming', 'Entertainment']
      },
      {
        id: '2',
        title: 'Community Q&A and Discussion',
        date: '2024-01-14',
        duration: '1:45:30',
        size: '2.8 GB',
        views: 892,
        thumbnail: 'https://images.pexels.com/photos/1181673/pexels-photo-1181673.jpeg?auto=compress&cs=tinysrgb&w=400',
        platforms: ['Discord', 'YouTube'],
        status: 'processing',
        hasTranscription: true,
        hasHighlights: false,
        hasShorts: false,
        categories: ['Just Chatting', 'Community']
      }
    ];
  }
}

export const recordingsService = new RecordingsService();
