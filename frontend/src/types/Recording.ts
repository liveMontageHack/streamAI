export interface Recording {
  id: string;
  title: string;
  date: string;
  duration: string;
  size: string;
  views: number;
  thumbnail: string;
  platforms: string[];
  status: 'processing' | 'ready' | 'editing';
  hasTranscription: boolean;
  hasHighlights: boolean;
  hasShorts: boolean;
  categories: string[];
  isManualUpload?: boolean;
  filePath?: string;
}
