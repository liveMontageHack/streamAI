# StreamAI - Enregistrement Intégré OBS + Vultr

## 🎯 Vue d'ensemble

StreamAI est un système d'enregistrement intégré qui combine OBS Studio avec l'upload automatique vers Vultr pour un workflow de traitement vidéo complet et automatisé.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        StreamAI Frontend                        │
│                     (React + TypeScript)                       │
└─────────────────────┬───────────────────────────────────────────┘
                      │ HTTP/WebSocket
┌─────────────────────▼───────────────────────────────────────────┐
│                 Serveur Intégré Python                         │
│              (Flask + SocketIO + AsyncIO)                      │
└─────────────────────┬───────────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ OBS Studio  │ │ Vultr API   │ │ Système     │
│ WebSocket   │ │ Processing  │ │ Fichiers    │
└─────────────┘ └─────────────┘ └─────────────┘
```

## 📁 Structure du Projet

```
streamAI/
├── obs/                                    # Backend Python
│   ├── integrated_recording_service.py    # Service principal
│   ├── integrated_api_server.py          # API Flask + SocketIO
│   ├── start_integrated_server.py        # Script de démarrage
│   ├── start_integrated_system.py        # Lanceur complet
│   ├── test_integrated_recording.py      # Tests d'intégration
│   ├── recording_manager.py              # Gestion des sessions
│   ├── obs_controller.py                 # Contrôle OBS
│   └── config.py                         # Configuration
│
├── frontend/                              # Frontend React
│   ├── src/
│   │   ├── services/
│   │   │   └── integratedRecordingService.ts
│   │   └── components/
│   │       ├── IntegratedRecording.tsx
│   │       └── Dashboard.tsx
│   └── package.json
│
├── recordings/                            # Enregistrements locaux
└── README.md                             # Ce fichier
```

## 🚀 Démarrage Rapide

### Prérequis
- Python 3.8+
- Node.js 16+
- OBS Studio
- Git

### Installation et Démarrage

#### Option 1 : Démarrage Simple (Recommandé)
```bash
python start.py
```

#### Option 2 : Lanceur Complet
```bash
cd obs/
python start_integrated_system.py
```

#### Option 3 : Démarrage Manuel
```bash
# Terminal 1 - Serveur intégré
cd obs/
python start_integrated_server.py

# Terminal 2 - Frontend
cd frontend/
npm install
npm run dev

# Terminal 3 - Tests (optionnel)
cd obs/
python test_integrated_recording.py
```

### Configuration OBS
1. **Activer WebSocket Server**
   - Outils → WebSocket Server Settings
   - Enable WebSocket server
   - Server Port: `4455`
   - Server Password: (laisser vide)

2. **Configuration d'enregistrement**
   - Format: MKV (recommandé)
   - Qualité: Haute qualité, taille moyenne

## 🎬 Fonctionnalités

### ✅ Enregistrement Automatique
- Démarrage/arrêt via interface web
- Sessions nommées personnalisées
- Surveillance temps réel (durée, taille)
- Métadonnées automatiques

### ✅ Upload Automatique
- Upload vers Vultr après enregistrement
- Configuration du modèle de sous-titres
- Gestion des priorités de traitement
- Suivi des tâches avec Task ID

### ✅ Interface Temps Réel
- WebSocket pour mises à jour live
- Statut d'enregistrement en direct
- Notifications d'événements
- Synchronisation multi-clients

### ✅ Gestion des Sessions
- Historique des enregistrements
- Métadonnées enrichies
- Upload manuel pour sessions existantes
- Calcul automatique des tailles

## 🌐 Accès aux Services

Une fois démarré, les services sont disponibles sur :
- **Frontend React** : http://localhost:5173
- **API Backend** : http://localhost:5002
- **WebSocket** : ws://localhost:5002

## 📡 API Endpoints Principaux

```http
# Contrôle d'enregistrement
POST /api/integrated/recording/start
POST /api/integrated/recording/stop

# Statut et monitoring
GET /api/health
GET /api/integrated/status
GET /api/integrated/recording/status

# Gestion des enregistrements
GET /api/integrated/recordings
POST /api/integrated/upload/manual
```

## 🧪 Tests

```bash
cd obs/
python test_integrated_recording.py
```

## 🔧 Configuration

### Variables d'environnement (obs/.env)
```bash
# OBS Configuration
OBS_HOST=localhost
OBS_PORT=4455
OBS_PASSWORD=

# Vultr API Configuration
VULTR_API_URL=http://45.32.145.22
VULTR_UPLOAD_ENDPOINT=/upload
VULTR_STATUS_ENDPOINT=/status

# Recording Configuration
RECORDINGS_DIR=./recordings
DEFAULT_SUBTITLE_MODEL=base
```

## 🔍 Dépannage

### Problèmes Courants

#### Serveur ne démarre pas
```bash
cd obs/
pip install -r requirements.txt
```

#### OBS non connecté
- Vérifier qu'OBS est lancé
- Activer WebSocket Server (port 4455)
- Pas de mot de passe requis

#### Upload Vultr échoue
```bash
curl http://45.32.145.22/health
```

### Logs
```bash
# Logs du serveur intégré
tail -f obs/integrated_server.log

# Test de connectivité
curl http://localhost:5002/api/health
```

## 🤝 Contribution

1. Fork du repository
2. Créer une branche feature
3. Commit des changements
4. Push vers la branche
5. Créer une Pull Request

## 📄 Licence

Ce projet est sous licence MIT.

---

**StreamAI Team** - Enregistrement Intégré v1.0
