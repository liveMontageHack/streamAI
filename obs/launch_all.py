#!/usr/bin/env python3
"""
Lanceur global StreamAI + Serveur Vultr

Ce script lance simultanément :
1. Le serveur Vultr (serveur de traitement)
2. L'application StreamAI (client + interface web)
"""

import asyncio
import logging
import subprocess
import sys
import time
import threading
import signal
import os
from pathlib import Path

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/launch_all.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class GlobalLauncher:
    """Lanceur global pour StreamAI + Serveur Vultr"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.vultr_process = None
        self.streamai_process = None
        self.running = False
        
        # Chemins
        self.obs_dir = Path(__file__).parent
        self.parent_dir = self.obs_dir.parent
        
    def setup_signal_handlers(self):
        """Configuration des signaux pour arrêt propre"""
        def signal_handler(signum, frame):
            self.logger.info(f"\n🛑 Signal {signum} reçu, arrêt en cours...")
            self.shutdown()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def start_vultr_server(self):
        """Démarrer le serveur Vultr"""
        try:
            self.logger.info("🌐 Démarrage du serveur Vultr...")
            
            # Chercher le serveur Vultr dans le répertoire parent
            vultr_script = self.parent_dir / "videodb_processor.py"
            
            if not vultr_script.exists():
                self.logger.warning(f"⚠️ Serveur Vultr non trouvé à : {vultr_script}")
                self.logger.info("   Continuons sans le serveur Vultr...")
                return False
            
            # Démarrer le serveur Vultr
            cmd = [sys.executable, str(vultr_script)]
            self.vultr_process = subprocess.Popen(
                cmd,
                cwd=str(self.parent_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Attendre un peu pour voir si le serveur démarre
            time.sleep(2)
            
            if self.vultr_process.poll() is None:
                self.logger.info("✅ Serveur Vultr démarré avec succès")
                
                # Thread pour logger la sortie du serveur Vultr
                def log_vultr_output():
                    for line in iter(self.vultr_process.stdout.readline, ''):
                        if line.strip():
                            self.logger.info(f"[VULTR] {line.strip()}")
                
                vultr_thread = threading.Thread(target=log_vultr_output, daemon=True)
                vultr_thread.start()
                
                return True
            else:
                self.logger.error("❌ Échec du démarrage du serveur Vultr")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erreur lors du démarrage du serveur Vultr : {e}")
            return False
    
    def start_streamai_app(self):
        """Démarrer l'application StreamAI"""
        try:
            self.logger.info("🚀 Démarrage de l'application StreamAI...")
            
            streamai_script = self.obs_dir / "start_integrated_system.py"
            
            if not streamai_script.exists():
                self.logger.error(f"❌ Application StreamAI non trouvée : {streamai_script}")
                return False
            
            # Démarrer StreamAI
            cmd = [sys.executable, str(streamai_script)]
            self.streamai_process = subprocess.Popen(
                cmd,
                cwd=str(self.obs_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Attendre un peu pour voir si l'app démarre
            time.sleep(3)
            
            if self.streamai_process.poll() is None:
                self.logger.info("✅ Application StreamAI démarrée avec succès")
                
                # Thread pour logger la sortie de StreamAI
                def log_streamai_output():
                    for line in iter(self.streamai_process.stdout.readline, ''):
                        if line.strip():
                            self.logger.info(f"[STREAMAI] {line.strip()}")
                
                streamai_thread = threading.Thread(target=log_streamai_output, daemon=True)
                streamai_thread.start()
                
                return True
            else:
                self.logger.error("❌ Échec du démarrage de l'application StreamAI")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erreur lors du démarrage de StreamAI : {e}")
            return False
    
    def check_services_health(self):
        """Vérifier la santé des services"""
        try:
            import requests
            
            # Test du serveur Vultr
            vultr_ok = False
            try:
                response = requests.get("http://45.32.145.22/health", timeout=5)
                vultr_ok = response.status_code == 200
            except:
                pass
            
            # Test de StreamAI
            streamai_ok = False
            try:
                response = requests.get("http://localhost:5000/api/status", timeout=5)
                streamai_ok = response.status_code == 200
            except:
                pass
            
            return vultr_ok, streamai_ok
            
        except Exception as e:
            self.logger.error(f"Erreur lors du test de santé : {e}")
            return False, False
    
    def run(self):
        """Lancer tous les services"""
        try:
            self.logger.info("🎬 LANCEMENT GLOBAL StreamAI + Serveur Vultr")
            self.logger.info("=" * 60)
            
            # Créer le dossier logs
            Path('logs').mkdir(exist_ok=True)
            
            # Configuration des signaux
            self.setup_signal_handlers()
            
            # 1. Démarrer le serveur Vultr
            vultr_started = self.start_vultr_server()
            
            # 2. Attendre un peu puis démarrer StreamAI
            if vultr_started:
                self.logger.info("⏳ Attente de 3 secondes avant de démarrer StreamAI...")
                time.sleep(3)
            
            streamai_started = self.start_streamai_app()
            
            if not streamai_started:
                self.logger.error("❌ Impossible de démarrer StreamAI")
                return False
            
            # 3. Attendre que les services soient prêts
            self.logger.info("⏳ Attente que les services soient prêts...")
            time.sleep(5)
            
            # 4. Vérifier la santé des services
            vultr_health, streamai_health = self.check_services_health()
            
            self.logger.info("📊 État des services :")
            self.logger.info(f"   • Serveur Vultr : {'✅ OK' if vultr_health else '❌ KO'}")
            self.logger.info(f"   • StreamAI App : {'✅ OK' if streamai_health else '❌ KO'}")
            
            if not streamai_health:
                self.logger.error("❌ StreamAI n'est pas accessible")
                return False
            
            # 5. Système prêt !
            self.running = True
            
            self.logger.info("🎉 SYSTÈME COMPLET OPÉRATIONNEL !")
            self.logger.info("=" * 60)
            self.logger.info("🌐 Serveur Vultr : http://45.32.145.22")
            self.logger.info("📱 Interface StreamAI : http://localhost:5000")
            self.logger.info("🔧 API StreamAI : http://localhost:5000/api/")
            self.logger.info("=" * 60)
            self.logger.info("Fonctionnalités disponibles :")
            self.logger.info("  • Enregistrement OBS avec interface web")
            self.logger.info("  • Upload automatique vers serveur Vultr")
            self.logger.info("  • Traitement vidéo sur serveur Vultr")
            self.logger.info("  • API REST complète")
            self.logger.info("=" * 60)
            self.logger.info("Appuyez sur Ctrl+C pour arrêter tous les services")
            
            # 6. Boucle principale - surveiller les processus
            while self.running:
                time.sleep(5)
                
                # Vérifier que les processus tournent toujours
                if self.vultr_process and self.vultr_process.poll() is not None:
                    self.logger.warning("⚠️ Le serveur Vultr s'est arrêté")
                
                if self.streamai_process and self.streamai_process.poll() is not None:
                    self.logger.error("❌ L'application StreamAI s'est arrêtée")
                    break
            
            return True
            
        except KeyboardInterrupt:
            self.logger.info("\n🛑 Arrêt demandé par l'utilisateur")
            return True
        except Exception as e:
            self.logger.error(f"❌ Erreur lors du lancement : {e}")
            return False
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Arrêt propre de tous les services"""
        self.logger.info("🔄 Arrêt des services en cours...")
        
        self.running = False
        
        # Arrêter StreamAI
        if self.streamai_process:
            try:
                self.logger.info("🛑 Arrêt de StreamAI...")
                self.streamai_process.terminate()
                self.streamai_process.wait(timeout=10)
                self.logger.info("✅ StreamAI arrêté")
            except Exception as e:
                self.logger.warning(f"Forçage de l'arrêt de StreamAI : {e}")
                self.streamai_process.kill()
        
        # Arrêter le serveur Vultr
        if self.vultr_process:
            try:
                self.logger.info("🛑 Arrêt du serveur Vultr...")
                self.vultr_process.terminate()
                self.vultr_process.wait(timeout=10)
                self.logger.info("✅ Serveur Vultr arrêté")
            except Exception as e:
                self.logger.warning(f"Forçage de l'arrêt du serveur Vultr : {e}")
                self.vultr_process.kill()
        
        self.logger.info("✅ Tous les services sont arrêtés")

def main():
    """Point d'entrée principal"""
    launcher = GlobalLauncher()
    
    try:
        success = launcher.run()
        return 0 if success else 1
    except Exception as e:
        logger.error(f"❌ Erreur fatale : {e}")
        return 1

if __name__ == "__main__":
    # S'assurer qu'on est dans le bon répertoire
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Lancer le système
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé par l'utilisateur")
        sys.exit(0)
