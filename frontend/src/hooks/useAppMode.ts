import { useMemo } from 'react';

export type AppMode = 'demo' | 'local';

export interface AppModeConfig {
  mode: AppMode;
  apiUrl: string;
  isDemo: boolean;
  isLocal: boolean;
  features: {
    obsControl: boolean;
    recording: boolean;
    realVideoProcessing: boolean;
    realTranscription: boolean;
  };
}

export const useAppMode = (): AppModeConfig => {
  return useMemo(() => {
    const hostname = window.location.hostname;
    const isDemo = hostname !== 'localhost' && hostname !== '127.0.0.1';
    
    const mode: AppMode = isDemo ? 'demo' : 'local';
    const apiUrl = isDemo 
      ? 'https://web-production-1c18.up.railway.app'
      : 'http://localhost:5001';

    return {
      mode,
      apiUrl,
      isDemo,
      isLocal: !isDemo,
      features: {
        obsControl: !isDemo,
        recording: !isDemo,
        realVideoProcessing: !isDemo,
        realTranscription: true, // Available in both modes
      }
    };
  }, []);
};
