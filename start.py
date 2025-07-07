#!/usr/bin/env python3
"""
Script de démarrage simple pour StreamAI
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Démarrer le système StreamAI"""
    print("🚀 Démarrage de StreamAI...")
    
    # Chemin vers le script principal
    obs_dir = Path(__file__).parent / "obs"
    start_script = obs_dir / "start_integrated_system.py"
    
    if not start_script.exists():
        print("❌ Script de démarrage non trouvé")
        print(f"   Recherché: {start_script}")
        return 1
    
    try:
        # Exécuter le script principal
        subprocess.run([sys.executable, str(start_script)], cwd=obs_dir)
        return 0
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé par l'utilisateur")
        return 0
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
