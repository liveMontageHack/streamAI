#!/usr/bin/env python3
"""
Script de test pour l'enregistrement intégré StreamAI
Teste les fonctionnalités principales sans OBS
"""

import asyncio
import requests
import json
import time
from datetime import datetime

class IntegratedRecordingTester:
    def __init__(self, base_url="http://localhost:5002"):
        self.base_url = base_url
        self.session_name = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def print_header(self, title):
        print(f"\n{'='*60}")
        print(f"🧪 {title}")
        print('='*60)
    
    def print_step(self, step, description):
        print(f"\n{step}. {description}")
        print("-" * 40)
    
    def test_health_check(self):
        """Test du health check"""
        self.print_step("1", "Test de santé du serveur")
        
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Serveur en ligne: {data.get('status')}")
                print(f"   Timestamp: {data.get('timestamp')}")
                return True
            else:
                print(f"❌ Erreur HTTP {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Impossible de se connecter au serveur: {e}")
            print("   Assurez-vous que le serveur intégré est démarré:")
            print("   cd obs/ && python start_integrated_server.py")
            return False
    
    def test_service_status(self):
        """Test du statut du service"""
        self.print_step("2", "Vérification du statut du service")
        
        try:
            response = requests.get(f"{self.base_url}/api/integrated/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Service initialisé: {data.get('service_initialized')}")
                
                recording_status = data.get('recording_status', {})
                print(f"   Enregistrement actif: {recording_status.get('active', False)}")
                
                recent_recordings = data.get('recent_recordings', [])
                print(f"   Enregistrements récents: {len(recent_recordings)}")
                
                return True
            else:
                print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur de connexion: {e}")
            return False
    
    def test_recording_status(self):
        """Test du statut d'enregistrement"""
        self.print_step("3", "Vérification du statut d'enregistrement")
        
        try:
            response = requests.get(f"{self.base_url}/api/integrated/recording/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Statut récupéré:")
                print(f"   Actif: {data.get('active', False)}")
                if data.get('active'):
                    print(f"   Session: {data.get('sessionName')}")
                    print(f"   Début: {data.get('startTime')}")
                    print(f"   Auto-upload: {data.get('autoUpload')}")
                else:
                    print(f"   Message: {data.get('message', 'Aucun enregistrement actif')}")
                return True
            else:
                print(f"❌ Erreur HTTP {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur: {e}")
            return False
    
    def test_start_recording(self):
        """Test de démarrage d'enregistrement"""
        self.print_step("4", f"Test de démarrage d'enregistrement: {self.session_name}")
        
        payload = {
            "sessionName": self.session_name,
            "autoUpload": False  # Pas d'upload pour le test
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/integrated/recording/start",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ Enregistrement démarré:")
                    print(f"   Session: {data.get('session_name')}")
                    print(f"   Chemin: {data.get('session_path')}")
                    print(f"   Auto-upload: {data.get('auto_upload')}")
                    return True
                else:
                    print(f"❌ Échec: {data.get('message')}")
                    return False
            else:
                error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
                print(f"❌ Erreur HTTP {response.status_code}: {error_data.get('error', response.text)}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur de connexion: {e}")
            return False
    
    def test_recording_active_status(self):
        """Test du statut pendant l'enregistrement"""
        self.print_step("5", "Vérification du statut pendant l'enregistrement")
        
        try:
            response = requests.get(f"{self.base_url}/api/integrated/recording/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('active'):
                    print(f"✅ Enregistrement confirmé actif:")
                    print(f"   Session: {data.get('sessionName')}")
                    print(f"   Début: {data.get('startTime')}")
                    
                    obs_status = data.get('obsStatus', {})
                    if obs_status:
                        print(f"   OBS actif: {obs_status.get('active')}")
                        print(f"   Timecode: {obs_status.get('timecode', 'N/A')}")
                        print(f"   Taille: {obs_status.get('bytes', 0)} bytes")
                    else:
                        print("   ⚠️ Statut OBS non disponible (normal si OBS n'est pas connecté)")
                    
                    return True
                else:
                    print(f"❌ Enregistrement non actif: {data.get('message')}")
                    return False
            else:
                print(f"❌ Erreur HTTP {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur: {e}")
            return False
    
    def test_stop_recording(self):
        """Test d'arrêt d'enregistrement"""
        self.print_step("6", "Test d'arrêt d'enregistrement")
        
        try:
            response = requests.post(
                f"{self.base_url}/api/integrated/recording/stop",
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ Enregistrement arrêté:")
                    print(f"   Session: {data.get('session_name')}")
                    print(f"   Chemin: {data.get('session_path')}")
                    
                    # Vérifier si upload automatique
                    upload_result = data.get('upload_result')
                    if upload_result:
                        if upload_result.get('success'):
                            print(f"   ✅ Upload réussi: {upload_result.get('task_id')}")
                        else:
                            print(f"   ❌ Upload échoué: {upload_result.get('message')}")
                    else:
                        print("   ℹ️ Pas d'upload automatique (comme configuré)")
                    
                    return True
                else:
                    print(f"❌ Échec: {data.get('message')}")
                    return False
            else:
                error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
                print(f"❌ Erreur HTTP {response.status_code}: {error_data.get('error', response.text)}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur de connexion: {e}")
            return False
    
    def test_list_recordings(self):
        """Test de listage des enregistrements"""
        self.print_step("7", "Test de listage des enregistrements")
        
        try:
            response = requests.get(f"{self.base_url}/api/integrated/recordings?limit=5", timeout=5)
            if response.status_code == 200:
                data = response.json()
                recordings = data.get('recordings', [])
                print(f"✅ {data.get('count', 0)} enregistrements trouvés:")
                
                for i, recording in enumerate(recordings[:3], 1):
                    print(f"   {i}. {recording.get('name', 'N/A')}")
                    print(f"      Créé: {recording.get('created', 'N/A')}")
                    print(f"      Fichiers: {len(recording.get('files', []))}")
                
                return True
            else:
                print(f"❌ Erreur HTTP {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur: {e}")
            return False
    
    def test_formatted_recordings(self):
        """Test des enregistrements formatés pour le frontend"""
        self.print_step("8", "Test des enregistrements formatés")
        
        try:
            response = requests.get(f"{self.base_url}/api/frontend/recordings/formatted", timeout=5)
            if response.status_code == 200:
                data = response.json()
                recordings = data.get('recordings', [])
                print(f"✅ {data.get('count', 0)} enregistrements formatés:")
                
                for i, recording in enumerate(recordings[:2], 1):
                    print(f"   {i}. {recording.get('title', 'N/A')}")
                    print(f"      ID: {recording.get('id', 'N/A')}")
                    print(f"      Date: {recording.get('date', 'N/A')}")
                    print(f"      Taille: {recording.get('size', 'N/A')}")
                    print(f"      Plateformes: {', '.join(recording.get('platforms', []))}")
                
                return True
            else:
                print(f"❌ Erreur HTTP {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur: {e}")
            return False
    
    def run_all_tests(self):
        """Exécuter tous les tests"""
        self.print_header("Tests d'Enregistrement Intégré StreamAI")
        
        print(f"🎯 URL de test: {self.base_url}")
        print(f"📝 Session de test: {self.session_name}")
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Service Status", self.test_service_status),
            ("Recording Status", self.test_recording_status),
            ("Start Recording", self.test_start_recording),
            ("Active Status", self.test_recording_active_status),
            ("Stop Recording", self.test_stop_recording),
            ("List Recordings", self.test_list_recordings),
            ("Formatted Recordings", self.test_formatted_recordings),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
                
                # Pause entre les tests
                if test_name in ["Start Recording", "Active Status"]:
                    print("   ⏳ Pause de 2 secondes...")
                    time.sleep(2)
                    
            except Exception as e:
                print(f"❌ Erreur inattendue dans {test_name}: {e}")
                results.append((test_name, False))
        
        # Résumé
        self.print_header("Résumé des Tests")
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        print(f"📊 Résultats: {passed}/{total} tests réussis")
        print()
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {status} {test_name}")
        
        if passed == total:
            print(f"\n🎉 Tous les tests sont passés ! L'intégration fonctionne correctement.")
            print(f"   Vous pouvez maintenant utiliser l'interface web sur http://localhost:5173")
        else:
            print(f"\n⚠️ {total - passed} test(s) ont échoué.")
            print(f"   Vérifiez les logs du serveur et la configuration OBS.")
        
        return passed == total

def main():
    """Fonction principale"""
    print("🚀 Démarrage des tests d'enregistrement intégré...")
    
    # Vérifier les arguments
    import sys
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5002"
    
    tester = IntegratedRecordingTester(base_url)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
