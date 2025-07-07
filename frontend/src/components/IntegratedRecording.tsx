/**
 * Composant d'enregistrement intégré StreamAI
 * Interface pour l'enregistrement OBS + upload automatique vers Vultr
 */

import React, { useState, useEffect, useCallback } from 'react';
import { integratedRecordingService, RecordingStatus } from '../services/integratedRecordingService';

interface IntegratedRecordingProps {
  onRecordingStarted?: (data: any) => void;
  onRecordingStopped?: (data: any) => void;
  onError?: (error: string) => void;
}

const IntegratedRecording: React.FC<IntegratedRecordingProps> = ({
  onRecordingStarted,
  onRecordingStopped,
  onError
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingStatus, setRecordingStatus] = useState<RecordingStatus | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionName, setSessionName] = useState('');
  const [autoUpload, setAutoUpload] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState<string | null>(null);

  // Initialiser la connexion WebSocket
  useEffect(() => {
    const initializeService = async () => {
      try {
        await integratedRecordingService.initializeWebSocket();
        setIsConnected(true);
        
        // Configurer les callbacks
        integratedRecordingService.onRecordingStarted = (data) => {
          console.log('🎬 Enregistrement démarré:', data);
          setIsRecording(true);
          setError(null);
          onRecordingStarted?.(data);
        };

        integratedRecordingService.onRecordingStopped = (data) => {
          console.log('⏹️ Enregistrement arrêté:', data);
          setIsRecording(false);
          
          // Vérifier si upload automatique
          if (data.result?.upload_result) {
            if (data.result.upload_result.success) {
              setUploadProgress(`✅ Upload réussi - Task ID: ${data.result.upload_result.task_id}`);
            } else {
              setUploadProgress(`❌ Échec upload: ${data.result.upload_result.message}`);
            }
          }
          
          onRecordingStopped?.(data);
        };

        integratedRecordingService.onStatusUpdate = (status) => {
          setRecordingStatus(status);
          setIsRecording(status.active);
        };

        integratedRecordingService.onError = (errorData) => {
          const errorMsg = errorData.message || 'Erreur inconnue';
          setError(errorMsg);
          onError?.(errorMsg);
        };

        // Vérifier le statut initial
        const status = await integratedRecordingService.getRecordingStatus();
        setRecordingStatus(status);
        setIsRecording(status.active);

      } catch (error) {
        console.error('Erreur d\'initialisation:', error);
        setError('Impossible de se connecter au service d\'enregistrement');
        setIsConnected(false);
      }
    };

    initializeService();

    // Nettoyage
    return () => {
      integratedRecordingService.disconnect();
    };
  }, [onRecordingStarted, onRecordingStopped, onError]);

  // Démarrer l'enregistrement
  const handleStartRecording = useCallback(async () => {
    if (isLoading || isRecording) return;

    setIsLoading(true);
    setError(null);
    setUploadProgress(null);

    try {
      const result = await integratedRecordingService.startRecording({
        sessionName: sessionName.trim() || undefined,
        autoUpload
      });

      if (result.success) {
        setIsRecording(true);
        console.log('✅ Enregistrement démarré avec succès');
      } else {
        throw new Error(result.message || 'Échec du démarrage');
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Erreur inconnue';
      setError(errorMsg);
      onError?.(errorMsg);
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, isRecording, sessionName, autoUpload, onError]);

  // Arrêter l'enregistrement
  const handleStopRecording = useCallback(async () => {
    if (isLoading || !isRecording) return;

    setIsLoading(true);
    setError(null);

    try {
      const result = await integratedRecordingService.stopRecording();

      if (result.success) {
        setIsRecording(false);
        console.log('✅ Enregistrement arrêté avec succès');
        
        // Afficher le résultat de l'upload si disponible
        if (result.upload_result) {
          if (result.upload_result.success) {
            setUploadProgress(`✅ Upload réussi - Task ID: ${result.upload_result.task_id}`);
          } else {
            setUploadProgress(`❌ Échec upload: ${result.upload_result.message}`);
          }
        }
      } else {
        throw new Error(result.message || 'Échec de l\'arrêt');
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Erreur inconnue';
      setError(errorMsg);
      onError?.(errorMsg);
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, isRecording, onError]);

  // Formater la durée
  const formatDuration = (timecode?: string) => {
    if (!timecode || timecode === '00:00:00') return '00:00:00';
    return timecode;
  };

  // Formater la taille
  const formatSize = (bytes?: number) => {
    if (!bytes || bytes === 0) return '0 MB';
    return integratedRecordingService.formatFileSize(bytes);
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-gray-800">
          🎬 Enregistrement Intégré
        </h2>
        <div className="flex items-center space-x-2">
          <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
          <span className="text-sm text-gray-600">
            {isConnected ? 'Connecté' : 'Déconnecté'}
          </span>
        </div>
      </div>

      {/* Configuration */}
      {!isRecording && (
        <div className="mb-4 space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nom de session (optionnel)
            </label>
            <input
              type="text"
              value={sessionName}
              onChange={(e) => setSessionName(e.target.value)}
              placeholder="Ex: Présentation_2025"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            />
          </div>
          
          <div className="flex items-center">
            <input
              type="checkbox"
              id="autoUpload"
              checked={autoUpload}
              onChange={(e) => setAutoUpload(e.target.checked)}
              className="mr-2"
              disabled={isLoading}
            />
            <label htmlFor="autoUpload" className="text-sm text-gray-700">
              Upload automatique vers Vultr après enregistrement
            </label>
          </div>
        </div>
      )}

      {/* Statut de l'enregistrement */}
      {recordingStatus && recordingStatus.active && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-red-800">
                🔴 Enregistrement en cours
              </p>
              <p className="text-xs text-red-600">
                Session: {recordingStatus.sessionName}
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm font-mono text-red-800">
                {formatDuration(recordingStatus.obsStatus?.timecode)}
              </p>
              <p className="text-xs text-red-600">
                {formatSize(recordingStatus.obsStatus?.bytes)}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Messages d'erreur */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-800">❌ {error}</p>
        </div>
      )}

      {/* Progression de l'upload */}
      {uploadProgress && (
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
          <p className="text-sm text-blue-800">{uploadProgress}</p>
        </div>
      )}

      {/* Boutons de contrôle */}
      <div className="flex space-x-3">
        {!isRecording ? (
          <button
            onClick={handleStartRecording}
            disabled={isLoading || !isConnected}
            className={`flex-1 px-4 py-2 rounded-md font-medium transition-colors ${
              isLoading || !isConnected
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-red-600 text-white hover:bg-red-700'
            }`}
          >
            {isLoading ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Démarrage...
              </span>
            ) : (
              '🎬 Démarrer l\'enregistrement'
            )}
          </button>
        ) : (
          <button
            onClick={handleStopRecording}
            disabled={isLoading}
            className={`flex-1 px-4 py-2 rounded-md font-medium transition-colors ${
              isLoading
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-gray-600 text-white hover:bg-gray-700'
            }`}
          >
            {isLoading ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Arrêt...
              </span>
            ) : (
              '⏹️ Arrêter l\'enregistrement'
            )}
          </button>
        )}

        {/* Bouton de test de connexion */}
        <button
          onClick={async () => {
            const connected = await integratedRecordingService.testConnection();
            setIsConnected(connected);
          }}
          className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors"
          disabled={isLoading}
        >
          🔄 Test
        </button>
      </div>

      {/* Informations supplémentaires */}
      <div className="mt-4 text-xs text-gray-500">
        <p>• L'enregistrement utilise OBS Studio</p>
        <p>• {autoUpload ? 'Upload automatique activé' : 'Upload manuel uniquement'}</p>
        <p>• Serveur: localhost:5002</p>
      </div>
    </div>
  );
};

export default IntegratedRecording;
