import React from 'react';
import { 
  Download, 
  Play, 
  FileText, 
  Scissors, 
  Eye, 
  ExternalLink,
  Copy,
  CheckCircle,
  Clock,
  Film,
  Subtitles
} from 'lucide-react';
import { TaskStatus, videoProcessingAPI } from '../services/videoProcessingAPI';

interface ProcessedResultsProps {
  taskStatus: TaskStatus;
  onClose?: () => void;
}

const ProcessedResults: React.FC<ProcessedResultsProps> = ({
  taskStatus,
  onClose
}) => {
  const [copiedUrl, setCopiedUrl] = React.useState<string | null>(null);

  const handleCopyUrl = async (url: string, type: string) => {
    try {
      await navigator.clipboard.writeText(url);
      setCopiedUrl(type);
      setTimeout(() => setCopiedUrl(null), 2000);
    } catch (error) {
      console.error('Erreur lors de la copie:', error);
    }
  };

  const handleDownload = (url: string, filename: string) => {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getVideoUrl = () => videoProcessingAPI.getResultUrl(taskStatus.task_id, 'video');
  const getSubtitlesUrl = () => videoProcessingAPI.getResultUrl(taskStatus.task_id, 'subtitles');
  const getThumbnailUrl = () => videoProcessingAPI.getResultUrl(taskStatus.task_id, 'thumbnail');

  const isCompleted = taskStatus.status === 'completed' || taskStatus.status === 'completed_simple';

  if (!isCompleted) {
    return (
      <div className="bg-white/5 border border-white/10 rounded-xl p-6">
        <div className="text-center">
          <Clock className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h4 className="text-white font-medium mb-2">Traitement en cours</h4>
          <p className="text-gray-400 text-sm">
            Les résultats seront disponibles une fois le traitement terminé.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h4 className="text-xl font-semibold text-white mb-2">Résultats du traitement</h4>
          <p className="text-gray-400 text-sm">
            Votre vidéo a été traitée avec succès par l'IA
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <CheckCircle className="w-5 h-5 text-green-400" />
          <span className="text-green-400 text-sm font-medium">Terminé</span>
        </div>
      </div>

      {/* Task Info */}
      <div className="bg-white/5 border border-white/10 rounded-xl p-4">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-400">ID de tâche:</span>
            <p className="text-white font-mono text-xs mt-1">{taskStatus.task_id}</p>
          </div>
          <div>
            <span className="text-gray-400">Fichier original:</span>
            <p className="text-white truncate mt-1" title={taskStatus.filename}>
              {taskStatus.filename}
            </p>
          </div>
          {taskStatus.size && (
            <div>
              <span className="text-gray-400">Taille:</span>
              <p className="text-white mt-1">
                {(taskStatus.size / (1024 * 1024)).toFixed(1)} MB
              </p>
            </div>
          )}
          {taskStatus.config && (
            <div>
              <span className="text-gray-400">Modèle utilisé:</span>
              <p className="text-white capitalize mt-1">{taskStatus.config.subtitle_model}</p>
            </div>
          )}
        </div>
      </div>

      {/* Video Preview */}
      <div className="bg-white/5 border border-white/10 rounded-xl p-6">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-10 h-10 bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg flex items-center justify-center">
            <Film className="w-5 h-5 text-white" />
          </div>
          <div>
            <h5 className="text-white font-medium">Vidéo traitée</h5>
            <p className="text-gray-400 text-sm">Vidéo avec sous-titres intégrés</p>
          </div>
        </div>

        {/* Video Thumbnail/Preview */}
        <div className="relative bg-black rounded-lg overflow-hidden mb-4">
          <div className="aspect-video flex items-center justify-center bg-gradient-to-br from-gray-800 to-gray-900">
            <div className="text-center">
              <Play className="w-16 h-16 text-white/60 mx-auto mb-4" />
              <p className="text-white/80 text-sm">Aperçu de la vidéo traitée</p>
              <p className="text-white/60 text-xs mt-1">Cliquez pour ouvrir dans un nouvel onglet</p>
            </div>
          </div>
          <button
            onClick={() => window.open(getVideoUrl(), '_blank')}
            className="absolute inset-0 bg-black/40 hover:bg-black/20 transition-all duration-200 flex items-center justify-center opacity-0 hover:opacity-100"
          >
            <div className="bg-white/20 backdrop-blur-md border border-white/30 text-white p-4 rounded-full">
              <ExternalLink className="w-6 h-6" />
            </div>
          </button>
        </div>

        {/* Video Actions */}
        <div className="flex items-center space-x-3">
          <button
            onClick={() => window.open(getVideoUrl(), '_blank')}
            className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center space-x-2"
          >
            <Play className="w-4 h-4" />
            <span>Voir la vidéo</span>
          </button>
          
          <button
            onClick={() => handleDownload(getVideoUrl(), `processed_${taskStatus.filename || 'video.mp4'}`)}
            className="bg-white/10 hover:bg-white/20 border border-white/20 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center space-x-2"
          >
            <Download className="w-4 h-4" />
            <span>Télécharger</span>
          </button>

          <button
            onClick={() => handleCopyUrl(getVideoUrl(), 'video')}
            className="bg-white/10 hover:bg-white/20 border border-white/20 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center space-x-2"
          >
            {copiedUrl === 'video' ? (
              <>
                <CheckCircle className="w-4 h-4 text-green-400" />
                <span className="text-green-400">Copié!</span>
              </>
            ) : (
              <>
                <Copy className="w-4 h-4" />
                <span>Copier le lien</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Subtitles */}
      <div className="bg-white/5 border border-white/10 rounded-xl p-6">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-cyan-600 rounded-lg flex items-center justify-center">
            <Subtitles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h5 className="text-white font-medium">Sous-titres générés</h5>
            <p className="text-gray-400 text-sm">Transcription automatique avec timestamps</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => window.open(getSubtitlesUrl(), '_blank')}
            className="bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center space-x-2"
          >
            <Eye className="w-4 h-4" />
            <span>Voir les sous-titres</span>
          </button>
          
          <button
            onClick={() => handleDownload(getSubtitlesUrl(), `subtitles_${taskStatus.task_id}.srt`)}
            className="bg-white/10 hover:bg-white/20 border border-white/20 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center space-x-2"
          >
            <Download className="w-4 h-4" />
            <span>Télécharger SRT</span>
          </button>

          <button
            onClick={() => handleCopyUrl(getSubtitlesUrl(), 'subtitles')}
            className="bg-white/10 hover:bg-white/20 border border-white/20 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center space-x-2"
          >
            {copiedUrl === 'subtitles' ? (
              <>
                <CheckCircle className="w-4 h-4 text-green-400" />
                <span className="text-green-400">Copié!</span>
              </>
            ) : (
              <>
                <Copy className="w-4 h-4" />
                <span>Copier le lien</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Additional Features */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Highlights */}
        <div className="bg-white/5 border border-white/10 rounded-xl p-4">
          <div className="flex items-center space-x-3 mb-3">
            <div className="w-8 h-8 bg-gradient-to-r from-orange-600 to-red-600 rounded-lg flex items-center justify-center">
              <Scissors className="w-4 h-4 text-white" />
            </div>
            <div>
              <h6 className="text-white font-medium text-sm">Highlights</h6>
              <p className="text-gray-400 text-xs">Moments clés extraits</p>
            </div>
          </div>
          <p className="text-gray-400 text-xs mb-3">
            Les moments les plus intéressants ont été identifiés automatiquement.
          </p>
          <button className="bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-700 hover:to-red-700 text-white px-3 py-1.5 rounded text-xs font-medium transition-all duration-200">
            Voir les highlights
          </button>
        </div>

        {/* Thumbnail */}
        <div className="bg-white/5 border border-white/10 rounded-xl p-4">
          <div className="flex items-center space-x-3 mb-3">
            <div className="w-8 h-8 bg-gradient-to-r from-green-600 to-teal-600 rounded-lg flex items-center justify-center">
              <FileText className="w-4 h-4 text-white" />
            </div>
            <div>
              <h6 className="text-white font-medium text-sm">Miniature</h6>
              <p className="text-gray-400 text-xs">Image de couverture</p>
            </div>
          </div>
          <p className="text-gray-400 text-xs mb-3">
            Miniature générée automatiquement pour votre vidéo.
          </p>
          <button
            onClick={() => window.open(getThumbnailUrl(), '_blank')}
            className="bg-gradient-to-r from-green-600 to-teal-600 hover:from-green-700 hover:to-teal-700 text-white px-3 py-1.5 rounded text-xs font-medium transition-all duration-200"
          >
            Voir la miniature
          </button>
        </div>
      </div>

      {/* URLs for Integration */}
      <div className="bg-white/5 border border-white/10 rounded-xl p-4">
        <h6 className="text-white font-medium mb-3 text-sm">Liens directs</h6>
        <div className="space-y-2 text-xs">
          <div className="flex items-center justify-between p-2 bg-white/5 rounded">
            <span className="text-gray-400">Vidéo:</span>
            <div className="flex items-center space-x-2">
              <code className="text-white font-mono text-xs bg-black/30 px-2 py-1 rounded">
                {getVideoUrl()}
              </code>
              <button
                onClick={() => handleCopyUrl(getVideoUrl(), 'video-url')}
                className="text-gray-400 hover:text-white transition-colors duration-200"
              >
                {copiedUrl === 'video-url' ? (
                  <CheckCircle className="w-3 h-3 text-green-400" />
                ) : (
                  <Copy className="w-3 h-3" />
                )}
              </button>
            </div>
          </div>
          
          <div className="flex items-center justify-between p-2 bg-white/5 rounded">
            <span className="text-gray-400">Sous-titres:</span>
            <div className="flex items-center space-x-2">
              <code className="text-white font-mono text-xs bg-black/30 px-2 py-1 rounded">
                {getSubtitlesUrl()}
              </code>
              <button
                onClick={() => handleCopyUrl(getSubtitlesUrl(), 'subtitles-url')}
                className="text-gray-400 hover:text-white transition-colors duration-200"
              >
                {copiedUrl === 'subtitles-url' ? (
                  <CheckCircle className="w-3 h-3 text-green-400" />
                ) : (
                  <Copy className="w-3 h-3" />
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProcessedResults;
