#!/usr/bin/env node
/**
 * Script de test pour le mode mock StreamAI
 * Vérifie que toutes les configurations sont correctes
 */

const fs = require('fs');
const path = require('path');

console.log('🧪 Test du Mode Mock StreamAI\n');

// Vérifier les fichiers de configuration
const checks = [
  {
    name: 'Configuration développement',
    file: 'frontend/.env.development',
    required: ['VITE_MOCK_MODE=true', 'VITE_LOCAL_PROCESSING=true']
  },
  {
    name: 'Configuration production',
    file: 'frontend/.env.production',
    required: ['VITE_MOCK_MODE=false', 'VITE_API_BASE_URL=http://45.32.145.22']
  },
  {
    name: 'Script de traitement local',
    file: 'scripts/process_video_local.py',
    required: ['StreamAILocalProcessor', 'async def process_video']
  },
  {
    name: 'Configuration API',
    file: 'frontend/src/config/api.ts',
    required: ['API_CONFIG', 'MOCK_MODE', 'LOCAL_PROCESSING']
  },
  {
    name: 'Service API vidéo',
    file: 'frontend/src/services/videoProcessingAPI.ts',
    required: ['processVideoLocally', 'startLocalProcessing', 'MOCK_MODE']
  },
  {
    name: 'Service enregistrements',
    file: 'frontend/src/services/recordingsService.ts',
    required: ['getMockRecordings', 'getProcessedRecordings', 'MOCK_MODE']
  }
];

// Vérifier les dossiers
const directories = [
  'recordings/mock_uploads',
  'processed_videos',
  'scripts'
];

let allPassed = true;

// Test des fichiers
console.log('📁 Vérification des fichiers...\n');

checks.forEach(check => {
  const filePath = check.file;
  const exists = fs.existsSync(filePath);
  
  if (!exists) {
    console.log(`❌ ${check.name}: Fichier manquant (${filePath})`);
    allPassed = false;
    return;
  }
  
  const content = fs.readFileSync(filePath, 'utf8');
  const missingRequirements = check.required.filter(req => !content.includes(req));
  
  if (missingRequirements.length > 0) {
    console.log(`⚠️  ${check.name}: Éléments manquants`);
    missingRequirements.forEach(req => console.log(`   - ${req}`));
    allPassed = false;
  } else {
    console.log(`✅ ${check.name}: OK`);
  }
});

// Test des dossiers
console.log('\n📂 Vérification des dossiers...\n');

directories.forEach(dir => {
  const exists = fs.existsSync(dir);
  if (exists) {
    console.log(`✅ ${dir}: OK`);
  } else {
    console.log(`❌ ${dir}: Dossier manquant`);
    allPassed = false;
  }
});

// Test de la configuration
console.log('\n⚙️  Test de configuration...\n');

try {
  // Simuler le chargement des variables d'environnement
  const devEnv = fs.readFileSync('frontend/.env.development', 'utf8');
  const prodEnv = fs.readFileSync('frontend/.env.production', 'utf8');
  
  const devMockMode = devEnv.includes('VITE_MOCK_MODE=true');
  const prodMockMode = prodEnv.includes('VITE_MOCK_MODE=false');
  
  console.log(`   Dev mock mode: ${devMockMode}`);
  console.log(`   Prod mock mode disabled: ${prodMockMode}`);
  
  if (devMockMode && prodMockMode) {
    console.log('✅ Configuration des modes: OK');
  } else {
    console.log('❌ Configuration des modes: Incorrecte');
    if (!devMockMode) console.log('   - Mode mock non activé en développement');
    if (!prodMockMode) console.log('   - Mode mock non désactivé en production');
    allPassed = false;
  }
  
} catch (error) {
  console.log('❌ Erreur lors du test de configuration:', error.message);
  allPassed = false;
}

// Résumé
console.log('\n' + '='.repeat(50));
if (allPassed) {
  console.log('🎉 Tous les tests sont passés !');
  console.log('\n📋 Prochaines étapes:');
  console.log('1. cd frontend && npm run dev');
  console.log('2. Ouvrir http://localhost:3000');
  console.log('3. Tester l\'upload d\'une vidéo');
  console.log('4. Vérifier la progression simulée');
  console.log('\n📖 Voir MOCK_MODE_GUIDE.md pour plus d\'infos');
} else {
  console.log('❌ Certains tests ont échoué');
  console.log('\n🔧 Actions requises:');
  console.log('1. Vérifier les fichiers manquants');
  console.log('2. Corriger les configurations');
  console.log('3. Relancer ce test');
}
console.log('='.repeat(50));

process.exit(allPassed ? 0 : 1);
