# Intégration Vultr - Documentation

## Vue d'ensemble

L'intégration Vultr permet d'uploader automatiquement les enregistrements vers un serveur Vultr pour traitement et analyse. Cette fonctionnalité est particulièrement utile pour :

- **Traitement automatique** des vidéos après enregistrement
- **Sauvegarde cloud** des enregistrements
- **Analyse avancée** des contenus vidéo
- **Intégration** avec des pipelines de traitement externes

## Configuration

### 1. Variables d'environnement

Ajoutez ces variables à votre fichier `.env` :

```bash
# Vultr Configuration
VULTR_API_URL=http://45.32.145.22
VULTR_UPLOAD_ENDPOINT=/upload
VULTR_AUTO_UPLOAD=true
```

### 2. Configuration détaillée

- **VULTR_API_URL** : URL de base du serveur Vultr
- **VULTR_UPLOAD_ENDPOINT** : Endpoint pour l'upload des fichiers
- **VULTR_AUTO_UPLOAD** : Active/désactive l'upload automatique après enregistrement

## Fonctionnalités

### 1. Upload automatique

Quand `VULTR_AUTO_UPLOAD=true`, les enregistrements sont automatiquement uploadés vers Vultr après l'arrêt de l'enregistrement.

### 2. Upload manuel via API

```bash
# Upload d'un enregistrement spécifique
POST /api/vultr/upload
{
  "recording_id": "123456789",
  "auto_process": true
}
```

### 3. Suivi des uploads

```bash
# Statut d'un upload
GET /api/vultr/upload/status/{task_id}

# Liste des uploads récents
GET /api/vultr/uploads?limit=10

# Test de connexion
GET /api/vultr/test
```

### 4. Statut du service

```bash
# Informations sur la configuration Vultr
GET /api/vultr/status
```

## Utilisation

### Via l'interface web

1. **Démarrer un enregistrement** via l'interface
2. **Arrêter l'enregistrement** - l'upload se fait automatiquement si activé
3. **Consulter les uploads** dans la section Vultr de l'interface

### Via l'API

```python
import requests

# Upload manuel d'un enregistrement
response = requests.post('http://localhost:5000/api/vultr/upload', json={
    'recording_id': 'your_recording_id',
    'auto_process': True
})

if response.json()['success']:
    task_id = response.json()['task_id']
    print(f"Upload démarré: {task_id}")
```

### Via la ligne de commande

```bash
# Test de l'intégration
python test_vultr_integration.py

# Démarrer un enregistrement avec upload automatique
python main.py record --session-name "test_vultr"
```

## Architecture technique

### Services impliqués

1. **VultrUploadService** (`vultr_service.py`)
   - Gestion des uploads
   - Communication avec l'API Vultr
   - Suivi des tâches

2. **RecordingManager** (`recording_manager.py`)
   - Intégration de l'auto-upload
   - Métadonnées des sessions

3. **API Server** (`api_server.py`)
   - Endpoints REST pour Vultr
   - Interface web

### Flux de données

```
Enregistrement OBS → RecordingManager → VultrService → Serveur Vultr
                                    ↓
                              Métadonnées session
```

## Métadonnées des sessions

Les uploads Vultr sont trackés dans les métadonnées des sessions :

```json
{
  "vultr_uploads": [
    {
      "task_id": "task_1_1751930958",
      "file_name": "recording.mkv",
      "upload_time": "2025-07-08 01:29:18",
      "file_size": 654321
    }
  ],
  "platforms": ["OBS Recording", "Vultr Processing"],
  "auto_upload_completed": true
}
```

## Dépannage

### Problèmes courants

1. **Connexion échouée**
   ```
   ❌ Connection failed: Connection refused
   ```
   - Vérifiez que le serveur Vultr est démarré
   - Vérifiez l'URL dans VULTR_API_URL

2. **Upload échoué**
   ```
   ❌ Upload failed: 500 Internal Server Error
   ```
   - Vérifiez l'espace disque sur le serveur
   - Vérifiez les logs du serveur Vultr

3. **Auto-upload ne fonctionne pas**
   - Vérifiez `VULTR_AUTO_UPLOAD=true` dans .env
   - Vérifiez que le service est configuré correctement

### Logs utiles

```bash
# Logs du service principal
tail -f logs/streamai.log

# Test de l'intégration
python test_vultr_integration.py
```

### Commandes de diagnostic

```bash
# Test de connexion
curl http://45.32.145.22/health

# Statut via API
curl http://localhost:5000/api/vultr/status
```

## Sécurité

### Bonnes pratiques

1. **Réseau** : Utilisez HTTPS en production
2. **Authentification** : Ajoutez une authentification si nécessaire
3. **Validation** : Les fichiers sont validés avant upload
4. **Timeouts** : Timeouts configurés pour éviter les blocages

### Configuration sécurisée

```bash
# Production
VULTR_API_URL=https://your-secure-server.com
VULTR_UPLOAD_ENDPOINT=/api/v1/upload
VULTR_API_KEY=your_secure_api_key  # Si authentification requise
```

## Performance

### Optimisations

- **Upload asynchrone** : N'interrompt pas l'enregistrement
- **Compression** : Les fichiers peuvent être compressés avant upload
- **Retry logic** : Retry automatique en cas d'échec temporaire
- **Timeouts** : 5 minutes de timeout pour les gros fichiers

### Monitoring

```python
# Suivi des performances d'upload
upload_result = vultr_service.upload_file(file_path)
print(f"Upload time: {upload_result['upload_time']}")
print(f"File size: {upload_result['file_size']} bytes")
```

## Développement

### Ajouter de nouvelles fonctionnalités

1. **Modifier VultrUploadService** pour de nouvelles méthodes
2. **Ajouter des endpoints** dans api_server.py
3. **Mettre à jour les tests** dans test_vultr_integration.py

### Tests

```bash
# Test complet de l'intégration
python test_vultr_integration.py

# Test d'un upload spécifique
python -c "from vultr_service import vultr_service; print(vultr_service.test_connection())"
```

## Support

Pour toute question ou problème :

1. Consultez les logs dans `logs/streamai.log`
2. Exécutez `python test_vultr_integration.py` pour diagnostiquer
3. Vérifiez la configuration dans `.env`
4. Consultez la documentation de l'API Vultr

---

*Dernière mise à jour : 2025-07-08*
