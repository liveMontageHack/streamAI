#!/usr/bin/env python3
"""
Service de traitement vidéo pour StreamAI utilisant AIVIDEO
Intègre le processeur local d'AIVIDEO dans l'écosystème StreamAI
"""

import os
import sys
import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Ajouter le chemin AIVIDEO au Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'AIVIDEO'))

# Import du processeur local AIVIDEO
from local_video_processor import LocalVideoProcessor, LocalProcessingConfig, VideoSegment

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StreamAIVideoProcessor:
    """Service de traitement vidéo pour StreamAI utilisant AIVIDEO"""
    
    def __init__(self, recordings_dir: str = "./recordings", output_dir: str = "./processed_videos"):
        self.recordings_dir = Path(recordings_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Configuration optimisée pour StreamAI
        self.config = LocalProcessingConfig(
            subtitle_model="base",  # Modèle Whisper rapide
            subtitle_language="auto",  # Détection automatique
            silence_threshold=-35,  # Plus sensible aux silences
            min_silence_duration=0.8,  # Couper les silences plus courts
            min_segment_duration=1.5,  # Segments plus courts acceptés
            max_gap_merge=2.0,  # Fusion plus agressive
            output_quality="medium",  # Qualité équilibrée
            hesitation_threshold=0.4,  # Plus agressif sur les hésitations
            filler_threshold=0.3,  # Plus agressif sur les mots de remplissage
            confidence_threshold=0.2,  # Seuil de confiance plus bas
            min_text_length=5,  # Texte plus court accepté
            min_duration_threshold=0.8,  # Durée minimale plus courte
            detect_silence=True,
            detect_hesitations=True,
            detect_filler_words=True,
            detect_low_confidence=True,
            create_project_folder=True,  # Organisation en dossiers
            keep_temp_files=False  # Nettoyer les fichiers temporaires
        )
        
        self.processor = None
        
    async def initialize(self):
        """Initialiser le processeur AIVIDEO"""
        try:
            logger.info("Initialisation du processeur vidéo StreamAI...")
            self.processor = LocalVideoProcessor(self.config)
            await self.processor.initialize()
            logger.info("Processeur vidéo StreamAI initialisé avec succès")
        except Exception as e:
            logger.error(f"Erreur d'initialisation: {e}")
            raise
    
    def scan_recordings(self) -> List[Dict]:
        """Scanner les enregistrements disponibles"""
        recordings = []
        
        try:
            if not self.recordings_dir.exists():
                logger.warning(f"Dossier recordings non trouvé: {self.recordings_dir}")
                return recordings
            
            for session_dir in self.recordings_dir.iterdir():
                if session_dir.is_dir():
                    for video_file in session_dir.iterdir():
                        if video_file.suffix.lower() in ['.mp4', '.mkv', '.avi', '.mov', '.wmv']:
                            # Vérifier si déjà traité
                            processed_info = self.get_processing_status(str(video_file))
                            
                            recording_info = {
                                'id': f"rec_{session_dir.name}_{video_file.stem}",
                                'session_name': session_dir.name,
                                'filename': video_file.name,
                                'filepath': str(video_file),
                                'size': self._format_file_size(video_file.stat().st_size),
                                'date': datetime.fromtimestamp(video_file.stat().st_mtime).strftime('%Y-%m-%d'),
                                'processed': processed_info['processed'],
                                'processing_status': processed_info['status']
                            }
                            
                            if processed_info['processed']:
                                recording_info.update(processed_info['result'])
                            
                            recordings.append(recording_info)
            
            logger.info(f"Trouvé {len(recordings)} enregistrements")
            return recordings
            
        except Exception as e:
            logger.error(f"Erreur lors du scan des enregistrements: {e}")
            return recordings
    
    def get_processing_status(self, video_path: str) -> Dict:
        """Vérifier le statut de traitement d'une vidéo"""
        video_file = Path(video_path)
        base_name = video_file.stem
        
        # Chercher dans le dossier de sortie
        for project_dir in self.output_dir.iterdir():
            if project_dir.is_dir() and base_name in project_dir.name:
                # Vérifier si le traitement est terminé
                video_dir = project_dir / "video"
                reports_dir = project_dir / "reports"
                
                if video_dir.exists() and reports_dir.exists():
                    # Chercher la vidéo éditée
                    edited_videos = list(video_dir.glob(f"{base_name}_edited.*"))
                    report_files = list(reports_dir.glob(f"{base_name}_report.json"))
                    
                    if edited_videos and report_files:
                        try:
                            with open(report_files[0], 'r', encoding='utf-8') as f:
                                report = json.load(f)
                            
                            return {
                                'processed': True,
                                'status': 'completed',
                                'result': {
                                    'edited_video': str(edited_videos[0]),
                                    'project_dir': str(project_dir),
                                    'time_saved': report['summary']['time_saved'],
                                    'compression_ratio': report['summary']['compression_ratio'],
                                    'processing_date': report['timestamp']
                                }
                            }
                        except Exception as e:
                            logger.error(f"Erreur lecture rapport: {e}")
                            return {'processed': False, 'status': 'error'}
        
        return {'processed': False, 'status': 'not_processed'}
    
    async def process_video(self, video_path: str, priority: int = 1) -> Dict:
        """Traiter une vidéo avec AIVIDEO"""
        try:
            if not self.processor:
                await self.initialize()
            
            logger.info(f"Début du traitement: {video_path}")
            
            # Vérifier que le fichier existe
            if not Path(video_path).exists():
                raise FileNotFoundError(f"Fichier vidéo non trouvé: {video_path}")
            
            # Traitement avec AIVIDEO
            result = await self.processor.process_video_locally(
                video_path=video_path,
                output_dir=str(self.output_dir)
            )
            
            # Enrichir le résultat avec des infos StreamAI
            result.update({
                'processing_service': 'StreamAI + AIVIDEO',
                'priority': priority,
                'processed_at': datetime.now().isoformat(),
                'status': 'completed'
            })
            
            logger.info(f"Traitement terminé: {video_path}")
            logger.info(f"Temps économisé: {result['processing_summary']['time_saved']:.2f}s")
            logger.info(f"Ratio de compression: {result['processing_summary']['compression_ratio']:.1f}%")
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur de traitement pour {video_path}: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'processed_at': datetime.now().isoformat()
            }
    
    async def process_recording_by_id(self, recording_id: str) -> Dict:
        """Traiter un enregistrement par son ID"""
        recordings = self.scan_recordings()
        recording = next((r for r in recordings if r['id'] == recording_id), None)
        
        if not recording:
            raise ValueError(f"Enregistrement non trouvé: {recording_id}")
        
        if recording['processed']:
            return {
                'status': 'already_processed',
                'message': 'Cet enregistrement a déjà été traité',
                'result': recording
            }
        
        return await self.process_video(recording['filepath'])
    
    def get_processed_video_url(self, recording_id: str) -> Optional[str]:
        """Obtenir l'URL de la vidéo traitée"""
        recordings = self.scan_recordings()
        recording = next((r for r in recordings if r['id'] == recording_id), None)
        
        if recording and recording['processed']:
            # Retourner le chemin relatif pour l'API
            edited_video_path = recording.get('edited_video', '')
            if edited_video_path:
                return edited_video_path.replace(str(self.output_dir), '/processed')
        
        return None
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Formater la taille de fichier"""
        if size_bytes >= 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
        elif size_bytes >= 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        elif size_bytes >= 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes} B"

# Service global
video_processor_service = StreamAIVideoProcessor()

async def main():
    """Test du service"""
    try:
        await video_processor_service.initialize()
        
        # Scanner les enregistrements
        recordings = video_processor_service.scan_recordings()
        print(f"Enregistrements trouvés: {len(recordings)}")
        
        for recording in recordings:
            print(f"- {recording['filename']} ({recording['size']}) - Traité: {recording['processed']}")
        
        # Traiter le premier enregistrement non traité
        unprocessed = [r for r in recordings if not r['processed']]
        if unprocessed:
            print(f"\nTraitement de: {unprocessed[0]['filename']}")
            result = await video_processor_service.process_recording_by_id(unprocessed[0]['id'])
            print(f"Résultat: {result['status']}")
        
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    asyncio.run(main())
