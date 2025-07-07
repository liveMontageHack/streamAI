#!/usr/bin/env python3
"""
Script de démarrage pour le serveur d'enregistrement intégré StreamAI
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# Ajouter le répertoire obs au path pour les imports
sys.path.insert(0, str(Path(__file__).parent))

from integrated_api_server import app, socketio, integrated_service

def setup_logging():
    """Configuration du logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('integrated_server.log')
        ]
    )

def check_dependencies():
    """Vérifier les dépendances nécessaires"""
    try:
        import obsws_python
        import flask
        import flask_socketio
        import flask_cors
        import requests
        print("✅ Toutes les dépendances sont installées")
        return True
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        print("Installez les dépendances avec: pip install -r requirements.txt")
        return False

def check_obs_connection():
    """Vérifier la connexion OBS"""
    try:
        # Test basique de connexion OBS
        from obs_controller import OBSController
        obs = OBSController()
        # Ne pas essayer de se connecter ici, juste vérifier que la classe existe
        print("✅ Module OBS disponible")
        return True
    except Exception as e:
        print(f"⚠️ Attention: {e}")
        print("OBS Studio doit être lancé avec WebSocket activé")
        return True  # Continue quand même

def print_startup_info():
    """Afficher les informations de démarrage"""
    print("\n" + "="*60)
    print("🎬 StreamAI - Serveur d'Enregistrement Intégré")
    print("="*60)
    print("📡 API Server: http://localhost:5002")
    print("🔌 WebSocket: ws://localhost:5002")
    print("📁 Enregistrements: ./recordings/")
    print("📋 Logs: ./integrated_server.log")
    print("="*60)
    print("\n🚀 Fonctionnalités disponibles:")
    print("   • Enregistrement OBS automatique")
    print("   • Upload automatique vers Vultr")
    print("   • WebSocket temps réel")
    print("   • Interface web intégrée")
    print("\n📖 Endpoints principaux:")
    print("   GET  /api/health")
    print("   GET  /api/integrated/status")
    print("   POST /api/integrated/recording/start")
    print("   POST /api/integrated/recording/stop")
    print("   GET  /api/integrated/recordings")
    print("   POST /api/integrated/upload/manual")
    print("\n⚙️ Configuration:")
    print("   • OBS WebSocket: localhost:4455")
    print("   • Vultr API: http://45.32.145.22")
    print("   • Mode Debug: Activé")
    print("\n" + "="*60)

async def initialize_service():
    """Initialiser le service d'enregistrement"""
    try:
        print("🔧 Initialisation du service d'enregistrement...")
        success = await integrated_service.initialize()
        if success:
            print("✅ Service d'enregistrement initialisé")
        else:
            print("⚠️ Échec de l'initialisation du service (continuera quand même)")
        return success
    except Exception as e:
        print(f"⚠️ Erreur d'initialisation: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Démarrage du serveur d'enregistrement intégré StreamAI...")
    
    # Configuration du logging
    setup_logging()
    
    # Vérification des dépendances
    if not check_dependencies():
        sys.exit(1)
    
    # Vérification OBS
    check_obs_connection()
    
    # Affichage des informations
    print_startup_info()
    
    # Initialisation asynchrone du service
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(initialize_service())
    except Exception as e:
        print(f"⚠️ Erreur lors de l'initialisation: {e}")
    
    print("\n🎯 Démarrage du serveur Flask-SocketIO...")
    print("   Appuyez sur Ctrl+C pour arrêter")
    print("\n" + "-"*60)
    
    try:
        # Démarrer le serveur
        socketio.run(
            app, 
            debug=True, 
            host='0.0.0.0', 
            port=5002,
            allow_unsafe_werkzeug=True  # Pour le développement
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt du serveur demandé par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur du serveur: {e}")
    finally:
        print("🧹 Nettoyage des ressources...")
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(integrated_service.cleanup())
        except:
            pass
        print("✅ Serveur arrêté proprement")

if __name__ == '__main__':
    main()
