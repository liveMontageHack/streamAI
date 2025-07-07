#!/usr/bin/env python3
"""
Script wrapper pour traitement vidéo local avec AIVIDEO
Utilisé en mode développement pour traiter les vidéos localement
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path
from datetime import datetime

# Ajouter le chemin AIVIDEO au Python path
current_dir = Path(__file__).parent.parent
aivideo_path = current_dir / 'AIVIDEO'
sys.path.append(str(aivideo_path))

try:
    from local_video_processor import LocalVideoProcessor, LocalProcessingConfig
except ImportError as e:
    print(f"Erreur: Impossible d'importer AIVIDEO: {e}")
    print("Assurez-vous que les dépendances AIVIDEO sont installées")
    sys.exit(1)

class StreamAILocalProcessor:
    """Wrapper pour traitement local StreamAI"""
    
    def __init__(self):
        self.config = LocalProcessingConfig(
            subtitle_model="base",
            subtitle_language="auto",
            silence_threshold=-35,
            min_silence_duration=0.8,
            min_segment_duration=1.5,
            max_gap_merge=2.0,
            output_quality="medium",
            hesitation_threshold=0.4,
            filler_threshold=0.3,
            confidence_threshold=0.2,
            min_text_length=5,
            min_duration_threshold=0.8,
            detect_silence=True,
            detect_hesitations=True,
            detect_filler_words=True,
            detect_low_confidence=True,
            create_project_folder=True,
            keep_temp_files=False
        )
        self.processor = None
    
    async def initialize(self):
        """Initialiser le processeur AIVIDEO"""
        try:
            self.processor = LocalVideoProcessor(self.config)
            await self.processor.initialize()
            return True
        except Exception as e:
            print(f"Erreur d'initialisation: {e}")
            return False
    
    async def process_video(self, input_path: str, output_dir: str, task_id: str):
        """Traiter une vidéo et retourner les résultats"""
        try:
            if not self.processor:
                if not await self.initialize():
                    raise Exception("Impossible d'initialiser le processeur")
            
            # Créer le dossier de sortie spécifique à la tâche
            task_output_dir = Path(output_dir) / task_id
            task_output_dir.mkdir(parents=True, exist_ok=True)
            
            print(f"Début du traitement: {input_path}")
            print(f"Dossier de sortie: {task_output_dir}")
            
            # Traitement avec AIVIDEO
            result = await self.processor.process_video_locally(
                video_path=input_path,
                output_dir=str(task_output_dir)
            )
            
            # Adapter le résultat pour StreamAI
            streamai_result = {
                "task_id": task_id,
                "status": "completed",
                "original_video": input_path,
                "edited_video": result.get("edited_video"),
                "subtitles_fr": result.get("subtitles_fr"),
                "subtitles_en": result.get("subtitles_en"),
                "report": result.get("report"),
                "processing_summary": result.get("processing_summary", {}),
                "processed_at": datetime.now().isoformat(),
                "processing_service": "StreamAI Local + AIVIDEO"
            }
            
            # Sauvegarder le résultat
            result_file = task_output_dir / "result.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(streamai_result, f, indent=2, ensure_ascii=False)
            
            print(f"Traitement terminé avec succès")
            print(f"Temps économisé: {result['processing_summary'].get('time_saved', 0):.2f}s")
            print(f"Ratio de compression: {result['processing_summary'].get('compression_ratio', 0):.1f}%")
            
            return streamai_result
            
        except Exception as e:
            error_result = {
                "task_id": task_id,
                "status": "error",
                "error": str(e),
                "processed_at": datetime.now().isoformat()
            }
            
            # Sauvegarder l'erreur
            if 'task_output_dir' in locals():
                error_file = task_output_dir / "error.json"
                with open(error_file, 'w', encoding='utf-8') as f:
                    json.dump(error_result, f, indent=2, ensure_ascii=False)
            
            print(f"Erreur de traitement: {e}")
            return error_result

async def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(description='Traitement vidéo local StreamAI')
    parser.add_argument('input_path', help='Chemin vers la vidéo à traiter')
    parser.add_argument('output_dir', help='Dossier de sortie')
    parser.add_argument('task_id', help='ID de la tâche')
    parser.add_argument('--config', help='Fichier de configuration JSON (optionnel)')
    
    args = parser.parse_args()
    
    # Vérifier que le fichier d'entrée existe
    if not Path(args.input_path).exists():
        print(f"Erreur: Fichier non trouvé: {args.input_path}")
        sys.exit(1)
    
    # Créer le processeur
    processor = StreamAILocalProcessor()
    
    # Traiter la vidéo
    result = await processor.process_video(
        input_path=args.input_path,
        output_dir=args.output_dir,
        task_id=args.task_id
    )
    
    # Afficher le résultat
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Code de sortie
    sys.exit(0 if result["status"] == "completed" else 1)

if __name__ == "__main__":
    asyncio.run(main())
