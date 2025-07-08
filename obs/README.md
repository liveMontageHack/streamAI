# StreamAI - Guide de démarrage rapide

## 🚀 Lancement de l'application

### Prérequis

1. **Python 3.8+** installé
2. **OBS Studio** installé et configuré
3. **WebSocket OBS** activé dans OBS (Outils → WebSocket Server Settings)

### Installation rapide

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Configurer l'environnement
cp .env.example .env
# Éditer .env avec vos paramètres

# 3. Lancer le système complet (RECOMMANDÉ)
python launch_all.py
```

## ⚙️ Configuration

### Fichier `.env` (obligatoire)

```bash
# YouTube API (optionnel)
YOUTUBE_API_KEY=votre_cle_youtube

# OBS WebSocket (obligatoire)
OBS_HOST=localhost
OBS_PORT=4455
OBS_PASSWORD=votre_mot_de_passe_obs

# Enregistrements
RECORDINGS_PATH=./recordings
LOG_LEVEL=INFO

# Vultr (optionnel - pour upload automatique)
VULTR_API_URL=http://45.32.145.22
VULTR_UPLOAD_ENDPOINT=/upload
VULTR_AUTO_UPLOAD=true
```

### Configuration OBS

1. Ouvrir OBS Studio
2. Aller dans **Outils** → **WebSocket Server Settings**
3. Cocher **Enable WebSocket server**
4. Définir un mot de passe
5. Noter le port (par défaut 4455)

## 🎯 Lancement

### Méthode 1 : Lancement global (RECOMMANDÉ) 🚀

```bash
cd obs
python launch_all.py
```

**Lance automatiquement :**
- 🌐 Serveur Vultr (traitement vidéo)
- 📱 Application StreamAI (interface web)
- 🔄 Auto-upload entre les deux

**Interfaces disponibles :**
- Interface StreamAI : http://localhost:5000
- Serveur Vultr : http://45.32.145.22

### Méthode 2 : StreamAI seulement

```bash
cd obs
python start_integrated_system.py
```

**Interface web disponible sur :** http://localhost:5000

### Méthode 3 : API seulement

```bash
cd obs
python api_server.py
```

### Méthode 4 : Ligne de commande

```bash
cd obs
python main.py record --session-name "mon_enregistrement"
```

## 📱 Utilisation

### Via l'interface web (http://localhost:5000)

1. **Démarrer un enregistrement**
   - Cliquer sur "Start Recording"
   - Donner un nom à la session

2. **Arrêter l'enregistrement**
   - Cliquer sur "Stop Recording"
   - L'upload Vultr se fait automatiquement (si activé)

3. **Consulter les enregistrements**
   - Onglet "Recordings"
   - Télécharger, visualiser, gérer

### Via l'API REST

```bash
# Démarrer un enregistrement
curl -X POST http://localhost:5000/api/recording/start \
  -H "Content-Type: application/json" \
  -d '{"sessionName": "test"}'

# Arrêter l'enregistrement
curl -X POST http://localhost:5000/api/recording/stop

# Lister les enregistrements
curl http://localhost:5000/api/recordings

# Statut du système
curl http://localhost:5000/api/status
```

## 🔧 Endpoints API principaux

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/status` | GET | Statut du système |
| `/api/recording/start` | POST | Démarrer enregistrement |
| `/api/recording/stop` | POST | Arrêter enregistrement |
| `/api/recordings` | GET | Liste des enregistrements |
| `/api/vultr/status` | GET | Statut Vultr |
| `/api/vultr/upload` | POST | Upload vers Vultr |

## 🧪 Tests

### Test complet du système

```bash
cd obs
python test_vultr_integration.py
```

### Test de connexion OBS

```bash
cd obs
python -c "from obs_controller import OBSController; obs = OBSController(); print('✅ OBS OK' if obs.connect() else '❌ OBS KO')"
```

## 📁 Structure des fichiers

```
obs/
├── start_integrated_system.py  # 🚀 LANCER ICI
├── main.py                     # CLI principal
├── api_server.py              # Serveur web
├── recording_manager.py       # Gestion enregistrements
├── obs_controller.py          # Contrôle OBS
├── vultr_service.py           # Service Vultr
├── config.py                  # Configuration
├── .env                       # Variables d'environnement
├── requirements.txt           # Dépendances Python
├── recordings/                # Dossier enregistrements
└── logs/                      # Logs système
```

## 🐛 Dépannage

### Problèmes courants

1. **"OBS not connected"**
   ```bash
   # Vérifier qu'OBS est ouvert
   # Vérifier WebSocket activé dans OBS
   # Vérifier mot de passe dans .env
   ```

2. **"Port 5000 already in use"**
   ```bash
   # Tuer le processus existant
   sudo lsof -ti:5000 | xargs kill -9
   ```

3. **"Module not found"**
   ```bash
   # Réinstaller les dépendances
   pip install -r requirements.txt
   ```

4. **"Vultr connection failed"**
   ```bash
   # Vérifier VULTR_API_URL dans .env
   # Tester : curl http://45.32.145.22/health
   ```

### Logs utiles

```bash
# Logs en temps réel
tail -f logs/streamai_integrated.log

# Logs OBS
grep "obs_controller" logs/streamai_integrated.log

# Logs Vultr
grep "vultr_service" logs/streamai_integrated.log
```

## 🎮 Workflow typique

1. **Démarrage global**
   ```bash
   cd obs
   python launch_all.py
   ```

2. **Vérification** (dans un autre terminal)
   ```bash
   # Test StreamAI
   curl http://localhost:5000/api/status
   
   # Test serveur Vultr
   curl http://45.32.145.22/health
   ```

3. **Enregistrement**
   - Via web : http://localhost:5000
   - Via API : `curl -X POST http://localhost:5000/api/recording/start`

4. **Arrêt et upload automatique**
   - L'upload vers Vultr se fait automatiquement
   - Traitement sur le serveur Vultr
   - Vérifier dans les logs ou via `/api/vultr/status`

## 🔄 Auto-upload Vultr

Si `VULTR_AUTO_UPLOAD=true` dans `.env` :

- ✅ Upload automatique après chaque enregistrement
- ✅ Suivi des tâches d'upload
- ✅ Métadonnées enrichies
- ✅ Logs détaillés

## 📞 Support

En cas de problème :

1. Consulter les logs : `tail -f logs/streamai_integrated.log`
2. Tester les composants : `python test_vultr_integration.py`
3. Vérifier la config : `cat .env`
4. Redémarrer OBS et relancer l'app

---

## 🎉 Démarrage en une commande

```bash
cd obs && python start_integrated_system.py
```

**Interface web :** http://localhost:5000

**C'est parti ! 🚀**
