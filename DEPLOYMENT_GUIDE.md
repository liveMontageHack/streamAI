# Guide de Déploiement StreamAI

Ce guide vous explique comment déployer votre application StreamAI sur le web avec Netlify (frontend) et Railway (backend).

## 🎤 Solution pour l'Audio en Production

### Problème avec `sounddevice`
La bibliothèque `sounddevice` utilisée dans `realtime_audio/audio_capture.py` **ne fonctionne pas en production** car:

- ❌ Les serveurs web n'ont pas accès aux micros/périphériques audio
- ❌ Railway/Netlify/Heroku ne supportent pas l'accès hardware direct
- ❌ Environnements containerisés sans drivers audio système

### ✅ Solution Disponible: Audio Côté Client

**Architecture:**
```
Navigateur Client → Microphone → MediaRecorder → Chunks Audio → Backend API → Groq → Transcription
```

**Statut d'implémentation:**
- ✅ Backend prêt: `obs/api_server_production.py` avec endpoint `/api/transcription/process-audio`
- ✅ Service créé: `frontend/src/services/ClientAudioService.ts` (capture audio client)
- ✅ Composant mis à jour: `frontend/src/components/Transcription.tsx`
- ⚠️ **Audio capture actuel**: Les endpoints listening utilisent des mocks en production

**Fonctionnalités disponibles:**
- ✅ Endpoint pour traiter l'audio uploadé (`/api/transcription/process-audio`)
- ✅ Validation des clés API Groq
- ✅ Raffinement des transcriptions
- ✅ Système de polling pour la communication temps réel
- ✅ Gestion complète des paramètres utilisateur
- ⚠️ Capture audio simulée (prête pour remplacement par solution client)

### 🔧 Changements Techniques

**Frontend (React/TypeScript):**
```typescript
// Remplacement de l'audio serveur par audio client
import { clientAudioService } from '../services/ClientAudioService';

// Démarrage capture audio
await clientAudioService.startListening(onTranscription, groqApiKey);
```

**Backend (Production):**
```python
# Nouveau endpoint pour traiter l'audio uploadé
@app.route('/api/transcription/process-audio', methods=['POST'])
def process_audio():
    # Traite les fichiers audio du frontend
    # Utilise Groq API pour transcription
    # Retourne résultats JSON
```

### 🛠️ Différences Dev vs Prod

| Aspect | Développement Local | Production Web |
|--------|-------------------|----------------|
| **Audio Source** | `sounddevice` (micro serveur) | `MediaRecorder` (micro client) |
| **Processing** | Python local | Upload → Python serveur |
| **Latency** | Très faible | Faible (chunks 2s) |
| **Permissions** | Aucune | Permission navigateur requise |
| **Compatibilité** | Linux/Mac/Windows | Tous navigateurs modernes |

### ⚠️ Considérations Production

**Permissions Navigateur:**
- HTTPS obligatoire pour accès microphone
- Demande autorisation utilisateur automatique
- Gestion des refus d'accès avec messages d'erreur

**Performance:**
- Chunks de 2 secondes pour équilibrer latence/qualité
- Compression audio automatique (WebM/Opus optimal)
- Upload asynchrone non-bloquant

**Compatibilité:**
- Chrome/Edge: Support complet WebM/Opus
- Firefox: Support WebM/MP3
- Safari: Support MP4/AAC (limité)
- Mobile: Support variable selon navigateur

## 📋 Prérequis

- Compte GitHub (gratuit)
- Compte Netlify (gratuit)
- Compte Railway (gratuit)
- Vos clés API (YouTube, Groq, etc.)

## 🚀 Étape 1: Préparer le Repository

1. **Pusher les changements sur GitHub:**
   ```bash
   git add .
   git commit -m "Add deployment configuration"
   git push origin main
   ```

## 🔧 Étape 2: Déployer le Backend sur Railway

### 2.1 Créer un projet Railway

1. Allez sur [railway.app](https://railway.app)
2. Connectez-vous avec GitHub
3. Cliquez sur "New Project"
4. Sélectionnez "Deploy from GitHub repo"
5. Choisissez votre repository `streamAI`

### 2.2 Configurer les variables d'environnement

Dans Railway, allez dans l'onglet "Variables" et ajoutez:

```
FLASK_ENV=production
YOUTUBE_API_KEY=votre_clé_youtube
GROQ_API_KEY=votre_clé_groq
OPENAI_API_KEY=votre_clé_openai
OBS_HOST=localhost
OBS_PORT=4455
OBS_PASSWORD=votre_mot_de_passe_obs
SECRET_KEY=une_clé_secrète_aléatoire
```

### 2.3 Déployer

1. Railway détectera automatiquement le `Procfile`
2. Le déploiement commencera automatiquement
3. Notez l'URL de votre application (ex: `https://streamai-production.up.railway.app`)

## 🌐 Étape 3: Déployer le Frontend sur Netlify

### 3.1 Créer un site Netlify

1. Allez sur [netlify.com](https://netlify.com)
2. Connectez-vous avec GitHub
3. Cliquez sur "New site from Git"
4. Choisissez GitHub et sélectionnez votre repository
5. Configurez les paramètres de build:
   - **Base directory:** `frontend`
   - **Build command:** `npm run build`
   - **Publish directory:** `frontend/dist`

### 3.2 Configurer les variables d'environnement

Dans Netlify, allez dans "Site settings" > "Environment variables" et ajoutez:

```
VITE_API_URL=https://votre-app-railway.up.railway.app
```

⚠️ **Important:** Remplacez `votre-app-railway.up.railway.app` par l'URL réelle de votre backend Railway.

### 3.3 Mettre à jour netlify.toml

Modifiez le fichier `netlify.toml` pour utiliser votre vraie URL Railway:

```toml
[context.production.environment]
  VITE_API_URL = "https://votre-app-railway.up.railway.app"
```

### 3.4 Redéployer

1. Commitez et pushez les changements
2. Netlify redéploiera automatiquement

## 🔄 Étape 4: Mettre à jour les URLs

### 4.1 Mettre à jour le frontend

Modifiez `frontend/.env.production`:
```
VITE_API_URL=https://votre-app-railway.up.railway.app
```

### 4.2 Configurer CORS sur Railway

Ajoutez cette variable d'environnement sur Railway:
```
CORS_ORIGINS=https://votre-app-netlify.netlify.app
```

## ✅ Étape 5: Tester le Déploiement

1. **Visitez votre site Netlify** (ex: `https://streamai-app.netlify.app`)
2. **Vérifiez la connexion API:**
   - Ouvrez les outils de développement (F12)
   - Allez dans l'onglet "Network"
   - Naviguez vers "Recordings"
   - Vérifiez que les requêtes vers Railway fonctionnent

3. **Test de santé du backend:**
   - Visitez `https://votre-app-railway.up.railway.app/api/health`
   - Vous devriez voir: `{"status": "healthy", "timestamp": "..."}`

## 🔧 Dépannage

### Problème: CORS Error
**Solution:** Vérifiez que `CORS_ORIGINS` est configuré sur Railway avec l'URL Netlify.

### Problème: 404 sur les routes frontend
**Solution:** Le fichier `netlify.toml` gère les redirections. Vérifiez qu'il est présent.

### Problème: Variables d'environnement non reconnues
**Solution:** 
- Vérifiez l'orthographe des variables
- Redéployez après avoir ajouté les variables
- Les variables Vite doivent commencer par `VITE_`

### Problème: Build failed sur Netlify
**Solution:**
- Vérifiez que `package.json` est dans le dossier `frontend`
- Vérifiez que la base directory est `frontend`

## 📱 URLs Finales

Après déploiement, vous aurez:

- **Frontend:** `https://votre-app.netlify.app`
- **Backend API:** `https://votre-app.up.railway.app`
- **Health Check:** `https://votre-app.up.railway.app/api/health`

## 🔄 Mises à jour

Pour mettre à jour votre application:

1. Faites vos modifications localement
2. Commitez et pushez sur GitHub
3. Railway et Netlify redéploieront automatiquement

## 💡 Conseils

- **Domaine personnalisé:** Vous pouvez configurer un domaine personnalisé sur Netlify
- **Monitoring:** Railway et Netlify offrent des logs et métriques
- **Scaling:** Railway peut automatiquement scaler votre backend
- **SSL:** HTTPS est automatique sur les deux plateformes

## 🆘 Support

Si vous rencontrez des problèmes:

1. Vérifiez les logs Railway et Netlify
2. Testez les endpoints API individuellement
3. Vérifiez la configuration des variables d'environnement
4. Assurez-vous que les URLs sont correctes

Votre application StreamAI est maintenant déployée et accessible depuis n'importe où dans le monde ! 🌍
