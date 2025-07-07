/**
 * Configuration API pour StreamAI
 * Gère les modes développement/production et mock/réel
 */

export const API_CONFIG = {
  // URLs de base
  VULTR_API_URL: 'http://45.32.145.22',
  LOCAL_API_URL: 'http://localhost:5001/api',
  
  // Modes
  MOCK_MODE: import.meta.env.VITE_MOCK_MODE === 'true',
  LOCAL_PROCESSING: import.meta.env.VITE_LOCAL_PROCESSING === 'true',
  
  // Configuration actuelle basée sur l'environnement
  get API_BASE_URL() {
    return import.meta.env.VITE_API_BASE_URL || this.VULTR_API_URL;
  },
  
  get IS_DEVELOPMENT() {
    return import.meta.env.DEV;
  },
  
  get IS_PRODUCTION() {
    return import.meta.env.PROD;
  },
  
  // Helpers
  get USE_MOCK_PROCESSING() {
    return this.MOCK_MODE && this.LOCAL_PROCESSING;
  },
  
  get USE_VULTR_API() {
    return !this.MOCK_MODE && this.IS_PRODUCTION;
  },
  
  get USE_LOCAL_API() {
    return !this.MOCK_MODE && this.IS_DEVELOPMENT;
  }
};

// Log de la configuration au démarrage (développement uniquement)
if (API_CONFIG.IS_DEVELOPMENT) {
  console.log('🔧 Configuration API StreamAI:', {
    mode: API_CONFIG.MOCK_MODE ? 'MOCK' : 'REAL',
    processing: API_CONFIG.LOCAL_PROCESSING ? 'LOCAL' : 'REMOTE',
    apiUrl: API_CONFIG.API_BASE_URL,
    environment: API_CONFIG.IS_DEVELOPMENT ? 'DEV' : 'PROD'
  });
}

export default API_CONFIG;
