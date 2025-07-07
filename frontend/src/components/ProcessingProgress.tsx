import React from 'react';
import { 
  Upload, 
  Cpu, 
  CheckCircle, 
  XCircle, 
  Clock, 
  X,
  AlertCircle,
  Loader2
} from 'lucide-react';
import { TaskStatus } from '../services/videoProcessingAPI';

interface ProcessingProgressProps {
  isOpen: boolean;
  onClose: () => void;
  taskStatus: TaskStatus | null;
  uploadProgress: number;
  estimatedTime?: string;
  onCancel?: () => void;
}

const ProcessingProgress: React.FC<ProcessingProgressProps> = ({
  isOpen,
  onClose,
  taskStatus,
  uploadProgress,
  estimatedTime,
  onCancel
}) => {
  if (!isOpen) return null;

  const getStatusInfo = () => {
    if (!taskStatus) {
      return {
        title: 'Préparation...',
        description: 'Initialisation du traitement',
        progress: 0,
        icon: <Loader2 className="w-6 h-6 animate-spin" />,
        color: 'text-blue-400'
      };
    }

    switch (taskStatus.status) {
      case 'uploaded':
        return {
          title: 'Upload terminé',
          description: 'Fichier uploadé avec succès, traitement en attente',
          progress: uploadProgress,
          icon: <Upload className="w-6 h-6" />,
          color: 'text-green-400'
        };
      case 'processing':
        return {
          title: 'Traitement en cours',
          description: 'L\'IA traite votre vidéo...',
          progress: taskStatus.progress || 50,
          icon: <Cpu className="w-6 h-6" />,
          color: 'text-purple-400'
        };
      case 'completed':
      case 'completed_simple':
        return {
          title: 'Traitement terminé',
          description: 'Votre vidéo a été traitée avec succès !',
          progress: 100,
          icon: <CheckCircle className="w-6 h-6" />,
          color: 'text-green-400'
        };
      case 'error':
        return {
          title: 'Erreur de traitement',
          description: taskStatus.message || 'Une erreur est survenue',
          progress: 0,
          icon: <XCircle className="w-6 h-6" />,
          color: 'text-red-400'
        };
      default:
        return {
          title: 'Statut inconnu',
          description: 'Vérification du statut...',
          progress: 0,
          icon: <AlertCircle className="w-6 h-6" />,
          color: 'text-yellow-400'
        };
    }
  };

  const statusInfo = getStatusInfo();
  const isCompleted = taskStatus?.status === 'completed' || taskStatus?.status === 'completed_simple';
  const isError = taskStatus?.status === 'error';
  const canCancel = taskStatus && !isCompleted && !isError;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-6">
      <div className="bg-gray-900/95 backdrop-blur-md border border-white/20 rounded-2xl max-w-md w-full">
        <div className="p-8">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-2xl font-bold text-white">AutoMontage IA</h3>
            {(isCompleted || isError) && (
              <button
                onClick={onClose}
                className="bg-white/10 hover:bg-white/20 border border-white/20 text-white p-2 rounded-lg transition-all duration-200"
              >
                <X className="w-5 h-5" />
              </button>
            )}
          </div>

          {/* Status Icon and Title */}
          <div className="text-center mb-6">
            <div className={`inline-flex items-center justify-center w-16 h-16 rounded-full bg-white/10 mb-4 ${statusInfo.color}`}>
              {statusInfo.icon}
            </div>
            <h4 className="text-xl font-semibold text-white mb-2">{statusInfo.title}</h4>
            <p className="text-gray-400 text-sm">{statusInfo.description}</p>
          </div>

          {/* Progress Bar */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-400">Progression</span>
              <span className="text-sm text-white font-medium">{Math.round(statusInfo.progress)}%</span>
            </div>
            <div className="w-full h-3 bg-white/10 rounded-full overflow-hidden">
              <div 
                className={`h-full transition-all duration-500 ease-out ${
                  isError 
                    ? 'bg-red-500' 
                    : isCompleted 
                      ? 'bg-green-500' 
                      : 'bg-gradient-to-r from-purple-600 to-blue-600'
                }`}
                style={{ width: `${statusInfo.progress}%` }}
              />
            </div>
          </div>

          {/* Task Details */}
          {taskStatus && (
            <div className="bg-white/5 border border-white/10 rounded-xl p-4 mb-6">
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">ID de tâche:</span>
                  <span className="text-white font-mono text-xs">{taskStatus.task_id}</span>
                </div>
                {taskStatus.filename && (
                  <div className="flex justify-between">
                    <span className="text-gray-400">Fichier:</span>
                    <span className="text-white truncate ml-2" title={taskStatus.filename}>
                      {taskStatus.filename}
                    </span>
                  </div>
                )}
                {taskStatus.size && (
                  <div className="flex justify-between">
                    <span className="text-gray-400">Taille:</span>
                    <span className="text-white">
                      {(taskStatus.size / (1024 * 1024)).toFixed(1)} MB
                    </span>
                  </div>
                )}
                {taskStatus.config && (
                  <div className="flex justify-between">
                    <span className="text-gray-400">Modèle:</span>
                    <span className="text-white capitalize">{taskStatus.config.subtitle_model}</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Estimated Time */}
          {estimatedTime && !isCompleted && !isError && (
            <div className="flex items-center justify-center space-x-2 text-gray-400 text-sm mb-6">
              <Clock className="w-4 h-4" />
              <span>Temps estimé: {estimatedTime}</span>
            </div>
          )}

          {/* Processing Steps */}
          {taskStatus && !isError && (
            <div className="space-y-3 mb-6">
              <div className={`flex items-center space-x-3 ${
                uploadProgress >= 100 ? 'text-green-400' : 'text-gray-400'
              }`}>
                <div className={`w-2 h-2 rounded-full ${
                  uploadProgress >= 100 ? 'bg-green-400' : 'bg-gray-600'
                }`} />
                <span className="text-sm">Upload du fichier</span>
                {uploadProgress >= 100 && <CheckCircle className="w-4 h-4" />}
              </div>
              
              <div className={`flex items-center space-x-3 ${
                taskStatus.status === 'processing' || isCompleted ? 'text-purple-400' : 'text-gray-400'
              }`}>
                <div className={`w-2 h-2 rounded-full ${
                  taskStatus.status === 'processing' || isCompleted ? 'bg-purple-400' : 'bg-gray-600'
                }`} />
                <span className="text-sm">Traitement IA</span>
                {isCompleted && <CheckCircle className="w-4 h-4" />}
                {taskStatus.status === 'processing' && <Loader2 className="w-4 h-4 animate-spin" />}
              </div>
              
              <div className={`flex items-center space-x-3 ${
                isCompleted ? 'text-green-400' : 'text-gray-400'
              }`}>
                <div className={`w-2 h-2 rounded-full ${
                  isCompleted ? 'bg-green-400' : 'bg-gray-600'
                }`} />
                <span className="text-sm">Finalisation</span>
                {isCompleted && <CheckCircle className="w-4 h-4" />}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex items-center justify-between">
            {canCancel && onCancel && (
              <button
                onClick={onCancel}
                className="bg-white/10 hover:bg-white/20 border border-white/20 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
              >
                Annuler
              </button>
            )}
            
            {isCompleted && (
              <button
                onClick={onClose}
                className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white px-6 py-2 rounded-lg text-sm font-medium transition-all duration-200 ml-auto"
              >
                Voir les résultats
              </button>
            )}
            
            {isError && (
              <button
                onClick={onClose}
                className="bg-red-600 hover:bg-red-700 text-white px-6 py-2 rounded-lg text-sm font-medium transition-all duration-200 ml-auto"
              >
                Fermer
              </button>
            )}
            
            {!canCancel && !isCompleted && !isError && (
              <div className="flex-1" />
            )}
          </div>

          {/* Error Details */}
          {isError && taskStatus?.message && (
            <div className="mt-4 p-4 bg-red-600/10 border border-red-600/20 rounded-lg">
              <div className="flex items-start space-x-3">
                <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                <div>
                  <h5 className="text-red-400 font-medium mb-1">Détails de l'erreur</h5>
                  <p className="text-red-300 text-sm">{taskStatus.message}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProcessingProgress;
