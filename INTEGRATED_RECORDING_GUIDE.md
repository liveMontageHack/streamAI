# Guide d'Enregistrement Intégré StreamAI

## Vue d'ensemble

L'enregistrement intégré StreamAI combine OBS Studio avec l'upload automatique vers Vultr pour un workflow de traitement vidéo complet et automatisé.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │  Backend Python  │    │   OBS Studio    │
│   React/TS      │◄──►│  Flask+SocketIO  │◄──►│   WebSocket     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Vultr API     │
                       │  (Processing)   │
                       └─────────────────┘
```

## Fonctionnalités

### 🎬 Enregistrement Automatique
- Démarrage/arrêt via interface web
- Gestion des sessions nommées
- Surveillance temps réel (durée, taille)
- Métadonnées automatiques

### 📤 Upload Automatique
- Upload vers Vultr après enregistrement
- Configuration du modèle de sous-titres
- Gestion des priorités
- Suivi des tâches de traitement

### 🔄 Temps Réel
- WebSocket pour mises à jour live
- Statut d'enregistrement en direct
- Notifications d'événements
- Synchronisation multi-clients

## Installation

### 1. Prérequis

#### OBS Studio
```bash
# Ubuntu/Debian
sudo apt install obs-studio

# Windows: Télécharger depuis https://obsproject.com/
```

#### Python Dependencies
```bash
cd obs/
pip install -r requirements.txt
```

#### Frontend Dependencies
```bash
cd frontend/
npm install socket.io-client
```

### 2. Configuration OBS

1. **Activer WebSocket Server**
   - Outils → WebSocket Server Settings
   - Enable WebSocket server
   - Server Port: `4455`
   - Server Password: (laisser vide pour le développement)

2. **Configuration d'enregistrement**
   - Paramètres → Sortie
   - Mode de sortie: Avancé
   - Format d'enregistrement: mkv (recommandé)
   - Qualité: Haute qualité, taille de fichier moyenne

### 3. Configuration Vultr

Vérifiez que l'API Vultr est accessible :
```bash
curl http://45.32.145.22/health
```

## Utilisation

### 1. Démarrer le serveur intégré

```bash
cd obs/
python start_integrated_server.py
```

Le serveur sera disponible sur :
- API: http://localhost:5002
- WebSocket: ws://localhost:5002

### 2. Démarrer le frontend

```bash
cd frontend/
npm run dev
```

Interface disponible sur : http://localhost:5173

### 3. Utilisation de l'interface

#### Démarrer un enregistrement
1. Ouvrir le Dashboard StreamAI
2. Section "Enregistrement Intégré"
3. Configurer :
   - Nom de session (optionnel)
   - Upload automatique (recommandé)
4. Cliquer "Démarrer l'enregistrement"

#### Arrêter un enregistrement
1. Cliquer "Arrêter l'enregistrement"
2. L'upload vers Vultr se lance automatiquement
3. Suivre le Task ID pour le traitement

## API Endpoints

### Status et Santé
```http
GET /api/health
GET /api/integrated/status
GET /api/integrated/recording/status
```

### Contrôle d'enregistrement
```http
POST /api/integrated/recording/start
Content-Type: application/json
{
  "sessionName": "Ma_Session_2025",
  "autoUpload": true
}

POST /api/integrated/recording/stop
```

### Gestion des enregistrements
```http
GET /api/integrated/recordings?limit=10
GET /api/frontend/recordings/formatted

POST /api/integrated/upload/manual
Content-Type: application/json
{
  "sessionName": "recording_session_20250107_123456",
  "subtitleModel": "base",
  "priority": 1
}
```

## WebSocket Events

### Côté Client (Écoute)
```javascript
socket.on('recording_started', (data) => {
  console.log('Enregistrement démarré:', data);
});

socket.on('recording_stopped', (data) => {
  console.log('Enregistrement arrêté:', data);
  if (data.result.upload_result) {
    console.log('Upload:', data.result.upload_result);
  }
});

socket.on('recording_status_update', (data) => {
  console.log('Statut:', data.status);
});

socket.on('manual_upload_completed', (data) => {
  console.log('Upload manuel terminé:', data);
});
```

### Côté Client (Émission)
```javascript
socket.emit('join_recording_updates');
socket.emit('leave_recording_updates');
```

## Structure des Fichiers

```
streamAI/
├── obs/
│   ├── integrated_recording_service.py    # Service principal
│   ├── integrated_api_server.py          # Serveur Flask+SocketIO
│   ├── start_integrated_server.py        # Script de démarrage
│   ├── recording_manager.py              # Gestion des sessions
│   ├── obs_controller.py                 # Contrôle OBS
│   └── recordings/                       # Enregistrements locaux
│
├── frontend/
│   ├── src/
│   │   ├── services/
│   │   │   └── integratedRecordingService.ts
│   │   └── components/
│   │       ├── IntegratedRecording.tsx
│   │       └── Dashboard.tsx
│   └── package.json
│
└── INTEGRATED_RECORDING_GUIDE.md
```

## Workflow Complet

### 1. Préparation
```mermaid
graph TD
    A[Lancer OBS Studio] --> B[Activer WebSocket]
    B --> C[Démarrer serveur intégré]
