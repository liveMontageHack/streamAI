# StreamAI - Enregistrement Intégré OBS + Vultr

## 🎯 Vue d'ensemble

Cette implémentation ajoute un système d'enregistrement intégré à StreamAI qui combine :
- **OBS Studio** pour l'enregistrement vidéo
- **Upload automatique vers Vultr** pour le traitement IA
- **Interface web temps réel** avec WebSocket
- **Gestion complète des sessions** d'enregistrement

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

## 📁 Structure des Fichiers

```
streamAI/
├── obs/                                    # Backend Python
│   ├── integrated_recording_service.py    # Service principal
│   ├── integrated_api_server.py          # API Flask + SocketIO
│   ├── start_integrated_server.py        # Script de démarrage
│   ├── recording_manager.py              # Gestion des sessions
│   ├── obs_controller.py                 # Contrôle OBS
│   └── config.py                         # Configuration
│
├── frontend/src/                          # Frontend React
│   ├── services/
│   │   └── integratedRecordingService.ts  # Service TypeScript
│   └── components/
│       ├── IntegratedRecording.tsx        # Composant principal
│       └── Dashboard.tsx                  # Dashboard modifié
│
├── start_integrated_system.py            # Lanceur complet
├── test_integrated_recording.py          # Tests d'intégration
├── INTEGRATED_RECORDING_GUIDE.md         # Guide détaillé
└── README_INTEGRATED_RECORDING.md        # Ce fichier
```

## 🚀 Démarrage Rapide

### Option 1 : Lanceur Automatique (Recommandé)
```bash
python start_integrated_system.py
```

### Option 2 : Démarrage Manuel
```bash
# Terminal 1 - Serveur intégré
cd obs/
python start_integrated_server.py

# Terminal 2 - Frontend
cd frontend/
npm run dev

# Terminal 3 - Tests (optionnel)
python test_integrated_recording.py
```

## 🎬 Fonctionnalités Principales

### 1. Enregistrement Automatique
- ✅ Démarrage/arrêt via interface web
- ✅ Sessions nommées personnalisées
- ✅ Surveillance temps réel (durée, taille)
- ✅ Métadonnées automatiques
- ✅ Gestion des erreurs robuste

### 2. Upload Automatique
- ✅ Upload vers Vultr après enregistrement
- ✅ Configuration du modèle de sous-titres
- ✅ Gestion des priorités de traitement
- ✅ Suivi des tâches avec Task ID
- ✅ Upload manuel pour sessions existantes

### 3. Interface Temps Réel
- ✅ WebSocket pour mises à jour live
- ✅ Statut d'enregistrement en direct
- ✅ Notifications d'événements
- ✅ Synchronisation multi-clients
- ✅ Indicateurs visuels de connexion

### 4. Gestion des Sessions
- ✅ Historique des enregistrements
- ✅ Métadonnées enrichies
- ✅ Formatage pour interface frontend
- ✅ Calcul automatique des tailles
- ✅ Statuts d'upload intégrés

## 🔧 Configuration

### OBS Studio
1. **Activer WebSocket Server**
   - Outils → WebSocket Server Settings
   - Enable WebSocket server
   - Server Port: `4455`
   - Server Password: (laisser vide)

2. **Configuration d'enregistrement**
   - Format: MKV (recommandé)
   - Qualité: Haute qualité, taille moyenne
   - Chemin: Configuré automatiquement

### Vultr API
- URL: `http://45.32.145.22`
- Endpoints: `/upload`, `/status`, `/results`
- Modèles: `base`, `small`, `medium`, `large`

## 📡 API Endpoints

### Contrôle d'enregistrement
```http
POST /api/integrated/recording/start
{
  "sessionName": "Ma_Session_2025",
  "autoUpload": true
}

POST /api/integrated/recording/stop
```

### Statut et monitoring
```http
GET /api/health
GET /api/integrated/status
GET /api/integrated/recording/status
```

### Gestion des enregistrements
```http
GET /api/integrated/recordings?limit=10
GET /api/frontend/recordings/formatted
POST /api/integrated/upload/manual
```

## 🔌 WebSocket Events

### Événements reçus
- `recording_started` - Enregistrement démarré
- `recording_stopped` - Enregistrement arrêté
- `recording_status_update` - Mise à jour du statut
- `manual_upload_completed` - Upload manuel terminé
- `error` - Erreurs diverses

### Événements émis
- `join_recording_updates` - Rejoindre les mises à jour
- `leave_recording_updates` - Quitter les mises à jour

## 🧪 Tests

### Tests Automatiques
```bash
python test_integrated_recording.py
```

### Tests Manuels
1. Ouvrir http://localhost:5173
2. Aller au Dashboard
3. Section "Enregistrement Intégré"
4. Tester start/stop avec différentes configurations

## 🔍 Dépannage

### Problèmes Courants

#### 1. Serveur ne démarre pas
```bash
# Vérifier les dépendances
pip install -r obs/requirements.txt
cd frontend && npm install
```

#### 2. OBS non connecté
- Vérifier que OBS est lancé
- Activer WebSocket Server (port 4455)
- Pas de mot de passe requis

#### 3. Upload Vultr échoue
- Vérifier la connectivité : `curl http://45.32.145.22/health`
- Vérifier la taille du fichier (limite serveur)
- Consulter les logs du serveur

#### 4. Frontend ne se connecte pas
- Vérifier que le serveur intégré est sur port 5002
- Vérifier les CORS dans la console navigateur
- Tester la connexion WebSocket manuellement

### Logs et Debugging
```bash
# Logs du serveur intégré
tail -f obs/integrated_server.log

# Logs du frontend
# Ouvrir DevTools → Console dans le navigateur

# Test de connectivité
curl http://localhost:5002/api/health
curl http://localhost:5002/api/integrated/status
```

## 📈 Métriques et Monitoring

### Statuts Surveillés
- Connexion OBS WebSocket
- État d'enregistrement (actif/inactif)
- Durée et taille en temps réel
- Statut des uploads Vultr
- Santé des services

### Indicateurs Interface
- 🟢 Vert : Service connecté et fonctionnel
- 🔴 Rouge : Enregistrement en cours
- 🟡 Jaune : Avertissement ou upload en cours
- ⚫ Gris : Service déconnecté

## 🔮 Évolutions Futures

### Fonctionnalités Prévues
- [ ] Support multi-caméras OBS
- [ ] Streaming simultané + enregistrement
- [ ] Intégration Discord pour notifications
- [ ] Sauvegarde cloud automatique
- [ ] Édition vidéo basique intégrée
- [ ] Analytics d'utilisation
- [ ] API REST complète
- [ ] Support mobile/tablette

### Améliorations Techniques
- [ ] Clustering pour haute disponibilité
- [ ] Cache Redis pour les métadonnées
- [ ] Queue système pour uploads
- [ ] Monitoring Prometheus/Grafana
- [ ] Tests automatisés CI/CD
- [ ] Documentation API OpenAPI
- [ ] Support Docker/Kubernetes

## 🤝 Contribution

### Structure du Code
- **Backend** : Python 3.8+ avec AsyncIO
- **Frontend** : React 18+ avec TypeScript
- **Communication** : REST API + WebSocket
- **Tests** : Pytest + Jest
- **Style** : Black + Prettier

### Workflow de Développement
1. Fork du repository
2. Branche feature/nom-fonctionnalité
3. Tests unitaires et d'intégration
4. Pull Request avec description détaillée
5. Review et merge

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## 📞 Support

- **Issues** : GitHub Issues
- **Documentation** : INTEGRATED_RECORDING_GUIDE.md
- **Tests** : test_integrated_recording.py
- **Exemples** : Voir le dossier examples/

---

**StreamAI Team** - Enregistrement Intégré v1.0
*Dernière mise à jour : 07/07/2025*
