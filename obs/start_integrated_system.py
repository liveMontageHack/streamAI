#!/usr/bin/env python3
"""
Script de démarrage complet pour l'écosystème StreamAI intégré
Lance tous les services nécessaires
"""

import subprocess
import sys
import time
import os
import signal
from pathlib import Path
import threading
import requests

class StreamAILauncher:
    def __init__(self):
        self.processes = []
        self.base_dir = Path(__file__).parent
        self.running = True
        
    def print_header(self, title):
        print(f"\n{'='*60}")
        print(f"🚀 {title}")
        print('='*60)
    
    def print_step(self, step, description):
        print(f"\n{step}. {description}")
        print("-" * 40)
    
    def check_dependencies(self):
        """Vérifier les dépendances"""
        self.print_step("1", "Vérification des dépendances")
        
        # Vérifier Python
        print(f"✅ Python: {sys.version}")
        
        # Vérifier Node.js
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Node.js: {result.stdout.strip()}")
            else:
                print("❌ Node.js non trouvé")
                return False
        except FileNotFoundError:
            print("❌ Node.js non installé")
            return False
        
        # Vérifier npm
        try:
            result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ npm: {result.stdout.strip()}")
            else:
                print("❌ npm non trouvé")
                return False
        except FileNotFoundError:
            print("❌ npm non installé")
            return False
        
        return True
    
    def install_python_deps(self):
        """Installer les dépendances Python"""
        self.print_step("2", "Installation des dépendances Python")
        
        # Le script est déjà dans le dossier obs/
        requirements_file = self.base_dir / "requirements.txt"
        
        if requirements_file.exists():
            print("📦 Installation des dépendances OBS...")
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
                ], check=True, cwd=self.base_dir)
                print("✅ Dépendances Python installées")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Erreur d'installation Python: {e}")
                return False
        else:
            print("⚠️ Fichier requirements.txt non trouvé")
            return True
    
    def install_frontend_deps(self):
        """Installer les dépendances frontend"""
        self.print_step("3", "Installation des dépendances Frontend")
        
        # Le frontend est au niveau parent
        frontend_dir = self.base_dir.parent / "frontend"
        package_json = frontend_dir / "package.json"
        
        if package_json.exists():
            print("📦 Installation des dépendances npm...")
            try:
                subprocess.run(["npm", "install"], check=True, cwd=frontend_dir)
                print("✅ Dépendances Frontend installées")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Erreur d'installation npm: {e}")
                return False
        else:
            print("⚠️ Fichier package.json non trouvé")
            return False
    
    def start_integrated_server(self):
        """Démarrer le serveur intégré"""
        self.print_step("4", "Démarrage du serveur intégré")
        
        # Le script est déjà dans le dossier obs/
        start_script = self.base_dir / "start_integrated_server.py"
        
        if start_script.exists():
            print("🔧 Démarrage du serveur d'enregistrement intégré...")
            try:
                process = subprocess.Popen([
                    sys.executable, str(start_script)
                ], cwd=self.base_dir)
                
                self.processes.append(("Serveur Intégré", process))
                
                # Attendre que le serveur soit prêt
                print("⏳ Attente du démarrage du serveur...")
                for i in range(30):  # 30 secondes max
                    try:
                        response = requests.get("http://localhost:5002/api/health", timeout=2)
                        if response.status_code == 200:
                            print("✅ Serveur intégré démarré sur http://localhost:5002")
                            return True
                    except:
                        pass
                    time.sleep(1)
                
                print("⚠️ Serveur intégré démarré mais pas encore prêt")
                return True
                
            except Exception as e:
                print(f"❌ Erreur de démarrage du serveur: {e}")
                return False
        else:
            print("❌ Script de démarrage non trouvé")
            return False
    
    def start_frontend(self):
        """Démarrer le frontend"""
        self.print_step("5", "Démarrage du frontend")
        
        # Le frontend est au niveau parent
        frontend_dir = self.base_dir.parent / "frontend"
        
        if (frontend_dir / "package.json").exists():
            print("🎨 Démarrage du serveur de développement frontend...")
            try:
                process = subprocess.Popen([
                    "npm", "run", "dev"
                ], cwd=frontend_dir)
                
                self.processes.append(("Frontend", process))
                
                # Attendre un peu pour le démarrage
                time.sleep(3)
                print("✅ Frontend démarré sur http://localhost:5173")
                return True
                
            except Exception as e:
                print(f"❌ Erreur de démarrage du frontend: {e}")
                return False
        else:
            print("❌ Projet frontend non trouvé")
            return False
    
    def run_tests(self):
        """Exécuter les tests"""
        self.print_step("6", "Exécution des tests")
        
        test_script = self.base_dir / "test_integrated_recording.py"
        
        if test_script.exists():
            print("🧪 Exécution des tests d'intégration...")
            try:
                # Attendre un peu que tous les services soient prêts
                time.sleep(5)
                
                result = subprocess.run([
                    sys.executable, str(test_script)
                ], cwd=self.base_dir)
                
                if result.returncode == 0:
                    print("✅ Tous les tests sont passés")
                    return True
                else:
                    print("⚠️ Certains tests ont échoué (voir détails ci-dessus)")
                    return False
                    
            except Exception as e:
                print(f"❌ Erreur lors des tests: {e}")
                return False
        else:
            print("⚠️ Script de test non trouvé")
            return True
    
    def print_status(self):
        """Afficher le statut des services"""
        self.print_header("Statut des Services")
        
        print("🌐 Services actifs:")
        print("   • Serveur Intégré: http://localhost:5002")
        print("   • Frontend React: http://localhost:5173")
        print("   • WebSocket: ws://localhost:5002")
        
        print("\n📋 Endpoints principaux:")
        print("   • GET  /api/health")
        print("   • GET  /api/integrated/status")
        print("   • POST /api/integrated/recording/start")
        print("   • POST /api/integrated/recording/stop")
        
        print("\n🎯 Utilisation:")
        print("   1. Ouvrir http://localhost:5173 dans votre navigateur")
        print("   2. Aller dans le Dashboard")
        print("   3. Utiliser la section 'Enregistrement Intégré'")
        print("   4. Configurer OBS Studio avec WebSocket sur port 4455")
        
        print("\n⚙️ Configuration OBS:")
        print("   • Outils → WebSocket Server Settings")
        print("   • Enable WebSocket server")
        print("   • Server Port: 4455")
        print("   • Server Password: (laisser vide)")
    
    def signal_handler(self, signum, frame):
        """Gestionnaire de signal pour arrêt propre"""
        print(f"\n\n🛑 Signal {signum} reçu, arrêt des services...")
        self.running = False
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """Nettoyer les processus"""
        print("\n🧹 Nettoyage des processus...")
        
        for name, process in self.processes:
            if process.poll() is None:  # Processus encore actif
                print(f"   Arrêt de {name}...")
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print(f"   Force l'arrêt de {name}...")
                    process.kill()
                except:
                    pass
        
        print("✅ Nettoyage terminé")
    
    def run(self):
        """Exécuter le lanceur complet"""
        self.print_header("StreamAI - Lanceur Intégré")
        
        # Configurer les gestionnaires de signaux
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            # Étapes de démarrage
            steps = [
                ("Dépendances", self.check_dependencies),
                ("Python Deps", self.install_python_deps),
                ("Frontend Deps", self.install_frontend_deps),
                ("Serveur Intégré", self.start_integrated_server),
                ("Frontend", self.start_frontend),
                ("Tests", self.run_tests),
            ]
            
            for step_name, step_func in steps:
                if not step_func():
                    print(f"\n❌ Échec de l'étape: {step_name}")
                    print("   Vérifiez les erreurs ci-dessus et réessayez")
                    return False
            
            # Afficher le statut
            self.print_status()
            
            # Boucle principale
            print(f"\n{'='*60}")
            print("🎉 Système StreamAI démarré avec succès !")
            print("   Appuyez sur Ctrl+C pour arrêter tous les services")
            print('='*60)
            
            # Attendre l'arrêt
            while self.running:
                time.sleep(1)
                
                # Vérifier si les processus sont encore actifs
                active_processes = []
                for name, process in self.processes:
                    if process.poll() is None:
                        active_processes.append((name, process))
                
                if not active_processes and self.running:
                    print("\n⚠️ Tous les processus se sont arrêtés")
                    break
                
                self.processes = active_processes
            
            return True
            
        except KeyboardInterrupt:
            print("\n\n🛑 Arrêt demandé par l'utilisateur")
            return True
        except Exception as e:
            print(f"\n❌ Erreur inattendue: {e}")
            return False
        finally:
            self.cleanup()

def main():
    """Fonction principale"""
    launcher = StreamAILauncher()
    success = launcher.run()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
