import React from 'react';
import { useAppMode } from '../hooks/useAppMode';

const DemoBanner: React.FC = () => {
  const { isDemo } = useAppMode();

  if (!isDemo) return null;

  const handleInstallClick = () => {
    window.open('https://github.com/liveMontageHack/streamAI#installation', '_blank');
  };

  return (
    <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-3 shadow-lg">
      <div className="max-w-7xl mx-auto flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🚀</span>
            <div>
              <h3 className="font-semibold text-lg">Mode Démo - StreamAI</h3>
              <p className="text-blue-100 text-sm">
                Fonctionnalités limitées • Données simulées • Pas de contrôle OBS
              </p>
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="hidden sm:block text-right">
            <p className="text-sm text-blue-100">
              Voulez-vous toutes les fonctionnalités ?
            </p>
            <p className="text-xs text-blue-200">
              Installation locale requise
            </p>
          </div>
          
          <button
            onClick={handleInstallClick}
            className="bg-white text-blue-600 px-4 py-2 rounded-lg font-semibold hover:bg-blue-50 transition-colors duration-200 shadow-md"
          >
            📥 Installer localement
          </button>
        </div>
      </div>
      
      {/* Features comparison */}
      <div className="max-w-7xl mx-auto mt-3 pt-3 border-t border-blue-400/30">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div className="flex items-center gap-2">
            <span className="text-green-300">✅</span>
            <span>Interface complète</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-green-300">✅</span>
            <span>Transcription AI</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-red-300">❌</span>
            <span>Contrôle OBS</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-red-300">❌</span>
            <span>Enregistrement réel</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DemoBanner;
