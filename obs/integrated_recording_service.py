#!/usr/bin/env python3
"""
Service d'enregistrement intégré StreamAI
Gère l'enregistrement OBS + upload automatique vers Vultr
"""

import asyncio
import logging
import requests
import json
import os
from datetime import datetime
from pathlib import Path
from recording_manager import RecordingManager
from config import config

class IntegratedRecordingService:
    """Service intégré pour enregistrement et upload automatique"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.recording_manager = RecordingManager()
        self.vultr_api_url = "http://45.32.145.22"
        self.current_recording_info = None
        self.upload_after_recording = True
        
    async def initialize(self):
        """Initialiser le service"""
        self.logger.info("Initialisation du service d'enregistrement intégré...")
        success = await self.recording_manager.initialize()
        if success:
            self.logger.info("Service d'enregistrement intégré initialisé avec succès")
        return success
    
    async def start_recording(self, session_name=None, auto_upload=True):
        """
        Démarrer un enregistrement avec upload automatique
        
        Args:
            session_name: Nom de la session (optionnel)
            auto_upload: Upload automatique vers Vultr après enregistrement
        """
        self.logger.info(f"Démarrage enregistrement - Session: {session_name}, Auto-upload: {auto_upload}")
        
        self.upload_after_recording = auto_upload
        
        # Démarrer l'enregistrement OBS
        success = await self.recording_manager.start_recording_session(session_name)
        
        if success:
            # Stocker les infos de l'enregistrement en cours
            self.current_recording_info = {
                'session': self.recording_manager.current_session,
                'start_time': datetime.now(),
                'auto_upload': auto_upload,
                'status': 'recording'
            }
            
            self.logger.info(f"Enregistrement démarré avec succès: {session_name}")
            return {
                'success': True,
                'session_name': self.recording_manager.current_session['name'],
                'session_path': str(self.recording_manager.current_session['path']),
                'auto_upload': auto_upload,
                'message': 'Enregistrement démarré'
            }
        else:
            self.logger.error("Échec du démarrage de l'enregistrement")
            return {
                'success': False,
                'message': 'Échec du démarrage de l\'enregistrement'
            }
    
    async def stop_recording(self):
        """
        Arrêter l'enregistrement et déclencher l'upload si configuré
        """
        self.logger.info("Arrêt de l'enregistrement...")
        
        if not self.current_recording_info:
            self.logger.warning("Aucun enregistrement actif à arrêter")
            return {
                'success': False,
                'message': 'Aucun enregistrement actif'
            }
        
        # Arrêter l'enregistrement OBS
        success = await self.recording_manager.stop_recording_session()
        
        if success:
            # Mettre à jour les infos
            self.current_recording_info['status'] = 'stopped'
            self.current_recording_info['end_time'] = datetime.now()
            
            # Sauvegarder les métadonnées
            self.recording_manager.save_session_metadata({
                'integrated_service': True,
                'auto_upload_enabled': self.upload_after_recording
            })
            
            result = {
                'success': True,
                'session_name': self.recording_manager.current_session['name'],
                'session_path': str(self.recording_manager.current_session['path']),
                'message': 'Enregistrement arrêté'
            }
            
            # Déclencher l'upload automatique si configuré
            if self.upload_after_recording:
                self.logger.info("Déclenchement de l'upload automatique...")
                upload_result = await self._upload_recording_to_vultr()
                result['upload_result'] = upload_result
            
            # Réinitialiser l'état
            completed_recording = self.current_recording_info
            self.current_recording_info = None
            
            return result
        else:
            self.logger.error("Échec de l'arrêt de l'enregistrement")
            return {
                'success': False,
                'message': 'Échec de l\'arrêt de l\'enregistrement'
            }
    
    async def _upload_recording_to_vultr(self):
        """Upload automatique de l'enregistrement vers l'API Vultr"""
        try:
            self.logger.info("Début de l'upload vers Vultr...")
            
            # Trouver le fichier vidéo le plus récent dans la session
            session_path = Path(self.recording_manager.current_session['path'])
            video_files = []
            
            # Chercher les fichiers vidéo courants
            for ext in ['.mkv', '.mp4', '.avi', '.mov']:
                video_files.extend(session_path.glob(f'*{ext}'))
            
            if not video_files:
                self.logger.error("Aucun fichier vidéo trouvé dans la session")
                return {
                    'success': False,
                    'message': 'Aucun fichier vidéo trouvé'
                }
            
            # Prendre le fichier le plus récent
            latest_video = max(video_files, key=lambda f: f.stat().st_mtime)
            self.logger.info(f"Upload du fichier: {latest_video}")
            
            # Préparer les données pour l'upload
            upload_data = {
                'subtitle_model': 'base',  # Modèle par défaut
                'priority': 1
            }
            
            # Effectuer l'upload
            with open(latest_video, 'rb') as video_file:
                files = {
                    'file': (latest_video.name, video_file, 'video/x-matroska')
                }
                data = {
                    'subtitle_model': upload_data['subtitle_model'],
                    'priority': str(upload_data['priority'])
                }
                
                self.logger.info(f"Envoi vers {self.vultr_api_url}/upload...")
                response = requests.post(
                    f"{self.vultr_api_url}/upload",
                    files=files,
                    data=data,
                    timeout=300  # 5 minutes timeout
                )
            
            if response.status_code == 200:
                upload_response = response.json()
                self.logger.info(f"Upload réussi - Task ID: {upload_response.get('task_id')}")
                
                # Sauvegarder les infos d'upload dans les métadonnées
                upload_metadata = {
                    'vultr_upload': {
                        'task_id': upload_response.get('task_id'),
                        'upload_time': datetime.now().isoformat(),
                        'file_name': latest_video.name,
                        'file_size': latest_video.stat().st_size,
                        'status': upload_response.get('status'),
                        'message': upload_response.get('message')
                    }
                }
                
                self.recording_manager.save_session_metadata(upload_metadata)
                
                return {
                    'success': True,
                    'task_id': upload_response.get('task_id'),
                    'file_name': latest_video.name,
                    'file_size': latest_video.stat().st_size,
                    'message': 'Upload vers Vultr réussi'
                }
            else:
                error_msg = f"Erreur HTTP {response.status_code}: {response.text}"
                self.logger.error(f"Échec de l'upload: {error_msg}")
                return {
                    'success': False,
                    'message': f'Échec de l\'upload: {error_msg}'
                }
                
        except Exception as e:
            self.logger.error(f"Erreur lors de l'upload vers Vultr: {e}")
            return {
                'success': False,
                'message': f'Erreur d\'upload: {str(e)}'
            }
    
    def get_recording_status(self):
        """Obtenir le statut de l'enregistrement en cours"""
        if not self.current_recording_info:
            return {
                'active': False,
                'message': 'Aucun enregistrement actif'
            }
        
        # Obtenir le statut OBS en temps réel
        obs_status = self.recording_manager.obs_controller.get_recording_status()
        
        return {
            'active': True,
            'session_name': self.current_recording_info['session']['name'],
            'start_time': self.current_recording_info['start_time'].isoformat(),
            'auto_upload': self.current_recording_info['auto_upload'],
            'obs_status': obs_status,
            'session_path': str(self.current_recording_info['session']['path'])
        }
    
    def get_recent_recordings(self, limit=10):
        """Obtenir la liste des enregistrements récents"""
        sessions = self.recording_manager.list_sessions()
        
        # Enrichir avec les métadonnées d'upload si disponibles
        enriched_sessions = []
        for session in sessions[:limit]:
            session_path = Path(session['path'])
            metadata_file = session_path / 'session_metadata.json'
            
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    session['metadata'] = metadata
                    
                    # Ajouter les infos d'upload Vultr si disponibles
                    if 'additional' in metadata and 'vultr_upload' in metadata['additional']:
                        session['vultr_upload'] = metadata['additional']['vultr_upload']
                        
                except Exception as e:
                    self.logger.warning(f"Erreur lecture métadonnées {metadata_file}: {e}")
            
            enriched_sessions.append(session)
        
        return enriched_sessions
    
    async def manual_upload(self, session_name, subtitle_model='base', priority=1):
        """Upload manuel d'un enregistrement existant"""
        try:
            self.logger.info(f"Upload manuel de la session: {session_name}")
            
            # Trouver la session
            sessions = self.recording_manager.list_sessions()
            target_session = None
            
            for session in sessions:
                if session['name'] == session_name:
                    target_session = session
                    break
            
            if not target_session:
                return {
                    'success': False,
                    'message': f'Session non trouvée: {session_name}'
                }
            
            # Trouver le fichier vidéo
            session_path = Path(target_session['path'])
            video_files = []
            
            for ext in ['.mkv', '.mp4', '.avi', '.mov']:
                video_files.extend(session_path.glob(f'*{ext}'))
            
            if not video_files:
                return {
                    'success': False,
                    'message': 'Aucun fichier vidéo trouvé dans la session'
                }
            
            # Prendre le fichier le plus récent
            latest_video = max(video_files, key=lambda f: f.stat().st_mtime)
            
            # Effectuer l'upload
            with open(latest_video, 'rb') as video_file:
                files = {
                    'file': (latest_video.name, video_file, 'video/x-matroska')
                }
                data = {
                    'subtitle_model': subtitle_model,
                    'priority': str(priority)
                }
                
                response = requests.post(
                    f"{self.vultr_api_url}/upload",
                    files=files,
                    data=data,
                    timeout=300
                )
            
            if response.status_code == 200:
                upload_response = response.json()
                self.logger.info(f"Upload manuel réussi - Task ID: {upload_response.get('task_id')}")
                
                return {
                    'success': True,
                    'task_id': upload_response.get('task_id'),
                    'file_name': latest_video.name,
                    'file_size': latest_video.stat().st_size,
                    'message': 'Upload manuel réussi'
                }
            else:
                error_msg = f"Erreur HTTP {response.status_code}: {response.text}"
                return {
                    'success': False,
                    'message': f'Échec de l\'upload: {error_msg}'
                }
                
        except Exception as e:
            self.logger.error(f"Erreur lors de l'upload manuel: {e}")
            return {
                'success': False,
                'message': f'Erreur d\'upload: {str(e)}'
            }
    
    async def cleanup(self):
        """Nettoyage des ressources"""
        self.logger.info("Nettoyage du service d'enregistrement intégré...")
        await self.recording_manager.cleanup()
        self.current_recording_info = None

# Instance globale du service
integrated_service = IntegratedRecordingService()
