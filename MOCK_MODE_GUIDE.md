# 🎭 Guide du Mode Mock StreamAI

Ce guide explique comment utiliser le mode mock intégré de StreamAI pour le développement local.

## 🎯 Qu'est-ce que le Mode Mock ?

Le mode mock permet de :
- **Développer sans API externe** : Pas besoin de connexion à l'API Vultr
- **Traitement local réel** : Utilise AIVIDEO localement pour de vrais résultats
- **Tests rapides** : Interface identique, traitement simulé ou réel
- **Développement offline** : Fonctionne sans connexion internet

## 🔧 Configuration

### Variables d'environnement

**Mode Développement** (`.env.development`) :
```env
VITE_MOCK_MODE=true
VITE_API_BASE_URL=http://localhost:3000
VITE_LOCAL_PROCESSING=true
```

**Mode Production** (`.env.production`) :
```env
VITE_MOCK_MODE=false
VITE_API_BASE_URL=http://45.32.145.22
VITE_LOCAL_PROCESSING=false
```

### Structure des dossiers

```
StreamAI/
├── recordings/
│   ├── sessions/              # Enregistrements OBS
│   └── mock_uploads/          # Uploads en mode mock
├── processed_videos/          # Résultats du traitement local
├── scripts/
│   └── process_video_local.py # Script de traitement local
└── frontend/
    ├── .env.development       # Config développement
    └── .env.production        # Config production
```

## 🚀 Utilisation

### Démarrage en mode mock

```bash
# Mode développement avec mock
npm run dev

# Le mode mock est automatiquement activé si VITE_MOCK_MODE=true
```

### Workflow du mode mock

1. **Upload** : Les fichiers sont "sauvegardés" localement (simulation)
2. **Traitement** : Progression simulée avec localStorage
3. **Résultats** : Affichage des résultats simulés
4. **Interface** : Identique au mode production

## 🎬 Fonctionnalités Mock

### Upload de vidéos
- ✅ Simulation de sauvegarde locale
- ✅ Génération d'ID de tâche unique
- ✅ Progression d'upload simulée

### Traitement vidéo
- ✅ Étapes de traitement réalistes
- ✅ Progression en temps réel
- ✅ Simulation Whisper + édition
- ✅ Résultats stockés en localStorage

### Interface utilisateur
- ✅ Même UX qu'en production
- ✅ Boutons et états identiques
- ✅ Messages de progression réalistes
- ✅ Gestion d'erreurs

## 🔍 Différences Mock vs Production

| Aspect | Mode Mock | Mode Production |
|--------|-----------|-----------------|
| **API** | localStorage | API Vultr |
| **Upload** | Simulation | Réel |
| **Traitement** | Simulé | GPU Vultr |
| **Stockage** | Local | Cloud |
| **Vitesse** | Rapide | Variable |
| **Résultats** | Simulés | Réels |

## 🛠️ Développement

### Tester le mode mock

```bash
# 1. Vérifier la configuration
cat frontend/.env.development

# 2. Démarrer en mode dev
cd frontend
npm run dev

# 3. Uploader une vidéo test
# L'interface affichera la progression simulée
```

### Déboguer le mode mock

```javascript
// Dans la console du navigateur
console.log('Mode mock:', import.meta.env.VITE_MOCK_MODE);
console.log('Traitement local:', import.meta.env.VITE_LOCAL_PROCESSING);

// Voir les données stockées
Object.keys(localStorage).filter(k => k.startsWith('processing_'));
```

### Nettoyer les données mock

```javascript
// Supprimer toutes les données de traitement
Object.keys(localStorage)
  .filter(k => k.startsWith('processing_'))
  .forEach(k => localStorage.removeItem(k));
```

## 🔄 Basculer entre les modes

### Développement → Production

```bash
# 1. Modifier .env.development
VITE_MOCK_MODE=false
VITE_API_BASE_URL=http://45.32.145.22

# 2. Redémarrer le serveur
npm run dev
```

### Mock → Traitement réel local

```bash
# 1. Installer AIVIDEO
cd AIVIDEO
pip install -r requirements.txt

# 2. Tester le script
python scripts/process_video_local.py --help

# 3. Modifier le code pour utiliser le script réel
# (au lieu de la simulation)
```

## 📊 Monitoring

### Logs de développement

Le mode mock affiche des logs détaillés :

```
🔧 Configuration API StreamAI: {
  mode: 'MOCK',
  processing: 'LOCAL', 
  apiUrl: 'http://localhost:3000',
  environment: 'DEV'
}

[MOCK] Sauvegarde de local_123_video.mp4 dans recordings/mock_uploads
[MOCK] Traitement terminé pour local_123
```

### États de traitement

```javascript
// Voir l'état d'une tâche
const taskId = 'local_1234567890_abc123';
const state = JSON.parse(localStorage.getItem(`processing_${taskId}`));
console.log(state);
```

## 🚨 Limitations du Mode Mock

- **Pas de vrais fichiers** : Les uploads sont simulés
- **Résultats factices** : Pas de vraie transcription/édition
- **Stockage temporaire** : localStorage peut être effacé
- **Pas de persistance** : Redémarrage = perte des données

## 🎯 Cas d'usage

### Développement UI
- Tester les composants sans API
- Déboguer les états de chargement
- Valider les flux utilisateur

### Tests automatisés
- Tests E2E sans dépendances
- Validation des interfaces
- Tests de régression

### Démonstrations
- Présenter l'interface sans traitement
- Démos rapides et fiables
- Environnement contrôlé

## 🔧 Personnalisation

### Modifier la simulation

```typescript
// Dans videoProcessingAPI.ts
private async startLocalProcessing() {
  const steps = [
    { progress: 10, message: 'Votre étape personnalisée...' },
    // Ajouter vos étapes
  ];
}
```

### Ajouter des enregistrements mock

```typescript
// Dans recordingsService.ts
const mockLocalRecordings = [
  {
    id: 'custom_recording',
    title: 'Votre enregistrement personnalisé',
    // ...
  }
];
```

## 📚 Ressources

- **Configuration** : `frontend/src/config/api.ts`
- **Service API** : `frontend/src/services/videoProcessingAPI.ts`
- **Service Recordings** : `frontend/src/services/recordingsService.ts`
- **Script Python** : `scripts/process_video_local.py`

---

**Mode Mock StreamAI** - Développement rapide et efficace ! 🚀
