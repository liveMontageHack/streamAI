#!/usr/bin/env python3
"""
StreamAI Integrated System Launcher

This script starts the complete StreamAI system with all integrations:
- OBS WebSocket connection
- YouTube API integration
- Vultr upload service
- Web API server
- Real-time transcription (if available)
"""

import asyncio
import logging
import signal
import sys
import threading
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/streamai_integrated.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Import our services
from main import StreamAIApp
from api_server import app, socketio
from vultr_service import vultr_service
from config import config

class IntegratedStreamAISystem:
    """Main system coordinator"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.stream_app = StreamAIApp()
        self.api_server_thread = None
        self.running = False
        
    async def initialize(self):
        """Initialize all system components"""
        self.logger.info("🚀 Starting StreamAI Integrated System")
        self.logger.info("=" * 60)
        
        # Create logs directory
        Path('logs').mkdir(exist_ok=True)
        
        # Initialize main StreamAI app
        self.logger.info("📡 Initializing StreamAI Core...")
        success = await self.stream_app.initialize()
        if not success:
            self.logger.error("❌ Failed to initialize StreamAI Core")
            return False
        
        self.logger.info("✅ StreamAI Core initialized successfully")
        
        # Test Vultr integration
        self.logger.info("🌐 Testing Vultr Integration...")
        if vultr_service.is_configured():
            connection_test = vultr_service.test_connection()
            if connection_test['success']:
                self.logger.info("✅ Vultr service connected and ready")
                vultr_config = config.get_vultr_config()
                if vultr_config['auto_upload']:
                    self.logger.info("🔄 Auto-upload to Vultr is ENABLED")
                else:
                    self.logger.info("⚠️ Auto-upload to Vultr is DISABLED")
            else:
                self.logger.warning(f"⚠️ Vultr connection failed: {connection_test['error']}")
        else:
            self.logger.warning("⚠️ Vultr service not configured")
        
        # Get system status
        status = self.stream_app.recording_manager.get_system_status()
        self.logger.info("📊 System Status:")
        self.logger.info(f"   • OBS Connected: {'✅' if status['obs_connected'] else '❌'}")
        self.logger.info(f"   • YouTube API: {'✅' if status['youtube_authenticated'] else '❌'}")
        self.logger.info(f"   • Recordings Path: {status['recordings_path']}")
        
        return True
    
    def start_api_server(self):
        """Start the Flask API server in a separate thread"""
        def run_server():
            try:
                self.logger.info("🌐 Starting Web API Server on http://localhost:5000")
                socketio.run(app, debug=False, host='0.0.0.0', port=5000, use_reloader=False)
            except Exception as e:
                self.logger.error(f"❌ API Server error: {e}")
        
        self.api_server_thread = threading.Thread(target=run_server, daemon=True)
        self.api_server_thread.start()
        
        # Wait a moment for server to start
        time.sleep(2)
        self.logger.info("✅ Web API Server started successfully")
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.logger.info(f"\n🛑 Received signal {signum}, shutting down gracefully...")
            asyncio.create_task(self.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def run(self):
        """Main run loop"""
        try:
            # Initialize system
            if not await self.initialize():
                return False
            
            # Start API server
            self.start_api_server()
            
            # Setup signal handlers
            self.setup_signal_handlers()
            
            self.running = True
            
            self.logger.info("🎉 StreamAI Integrated System is now running!")
            self.logger.info("=" * 60)
            self.logger.info("📱 Web Interface: http://localhost:5000")
            self.logger.info("🔧 API Endpoints:")
            self.logger.info("   • System Status: GET /api/status")
            self.logger.info("   • Start Recording: POST /api/recording/start")
            self.logger.info("   • Stop Recording: POST /api/recording/stop")
            self.logger.info("   • List Recordings: GET /api/recordings")
            self.logger.info("   • Vultr Status: GET /api/vultr/status")
            self.logger.info("   • Upload to Vultr: POST /api/vultr/upload")
            self.logger.info("🔄 Auto-upload to Vultr: " + ("ENABLED" if config.get_vultr_config()['auto_upload'] else "DISABLED"))
            self.logger.info("=" * 60)
            self.logger.info("Press Ctrl+C to stop the system")
            
            # Keep the system running
            while self.running:
                await asyncio.sleep(1)
                
                # Periodic health check (every 30 seconds)
                if int(time.time()) % 30 == 0:
                    await self.health_check()
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ System error: {e}")
            return False
    
    async def health_check(self):
        """Periodic health check"""
        try:
            # Check if OBS is still connected
            if not self.stream_app.recording_manager.obs_controller.is_connected():
                self.logger.warning("⚠️ OBS connection lost, attempting to reconnect...")
                await self.stream_app.recording_manager.obs_controller.connect()
            
            # Check Vultr service if configured
            if vultr_service.is_configured():
                # Quick connection test (non-blocking)
                pass  # Could add periodic Vultr health check here
                
        except Exception as e:
            self.logger.error(f"Health check error: {e}")
    
    async def shutdown(self):
        """Graceful shutdown"""
        self.logger.info("🔄 Shutting down StreamAI Integrated System...")
        
        self.running = False
        
        # Cleanup StreamAI app
        if self.stream_app:
            await self.stream_app.cleanup()
        
        self.logger.info("✅ StreamAI Integrated System shutdown complete")
        
        # Exit the program
        import os
        os._exit(0)

async def main():
    """Main entry point"""
    system = IntegratedStreamAISystem()
    
    try:
        success = await system.run()
        return 0 if success else 1
    except KeyboardInterrupt:
        logger.info("\n🛑 System interrupted by user")
        await system.shutdown()
        return 0
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    # Ensure we're in the right directory
    import os
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Run the system
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 System stopped by user")
        sys.exit(0)
