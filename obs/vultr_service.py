#!/usr/bin/env python3
"""
Vultr Upload Service

Service for uploading video files to Vultr server for processing.
"""

import requests
import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any
from config import config

class VultrUploadService:
    """Service for uploading files to Vultr server"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.vultr_config = config.get_vultr_config()
        self.api_url = self.vultr_config['api_url']
        self.upload_endpoint = self.vultr_config['upload_endpoint']
        self.auto_upload = self.vultr_config['auto_upload']
        
        # Task counter for unique task IDs
        self.task_counter = 0
    
    def is_configured(self) -> bool:
        """Check if Vultr service is properly configured"""
        return bool(self.api_url and self.upload_endpoint)
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to Vultr server"""
        if not self.is_configured():
            return {
                "success": False,
                "error": "Vultr service not configured"
            }
        
        try:
            # Try to ping the server
            response = requests.get(f"{self.api_url}/health", timeout=10)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Vultr server is reachable",
                    "server_info": response.json() if response.headers.get('content-type', '').startswith('application/json') else None
                }
            else:
                return {
                    "success": False,
                    "error": f"Server returned status code: {response.status_code}"
                }
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to connect to Vultr server: {e}")
            return {
                "success": False,
                "error": f"Connection failed: {str(e)}"
            }
    
    def upload_file(self, file_path: Path, session_name: str = None, auto_process: bool = False) -> Dict[str, Any]:
        """
        Upload a file to Vultr server
        
        Args:
            file_path: Path to the file to upload
            session_name: Optional session name for organization
            auto_process: Whether to automatically start processing
            
        Returns:
            Dictionary with upload result
        """
        if not self.is_configured():
            return {
                "success": False,
                "error": "Vultr service not configured"
            }
        
        if not file_path.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        try:
            # Generate unique task ID
            self.task_counter += 1
            task_id = f"task_{self.task_counter}_{int(time.time())}"
            
            # Prepare upload data
            upload_url = f"{self.api_url}{self.upload_endpoint}"
            
            # Prepare file for upload
            with open(file_path, 'rb') as file:
                files = {
                    'file': (file_path.name, file, 'video/mp4')
                }
                
                # Additional data
                data = {
                    'task_id': task_id,
                    'session_name': session_name or file_path.stem,
                    'auto_process': str(auto_process).lower(),
                    'upload_time': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                
                self.logger.info(f"Uploading file to Vultr: {file_path.name}")
                self.logger.info(f"Upload URL: {upload_url}")
                
                # Upload the file
                response = requests.post(
                    upload_url,
                    files=files,
                    data=data,
                    timeout=300  # 5 minutes timeout for large files
                )
                
                if response.status_code == 200:
                    result = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                    
                    self.logger.info(f"File uploaded successfully: {task_id}")
                    
                    return {
                        "success": True,
                        "task_id": task_id,
                        "file_name": file_path.name,
                        "file_size": file_path.stat().st_size,
                        "upload_time": time.strftime('%Y-%m-%d %H:%M:%S'),
                        "message": result.get('message', 'File uploaded successfully'),
                        "server_response": result
                    }
                else:
                    error_msg = f"Upload failed with status code: {response.status_code}"
                    try:
                        error_detail = response.json().get('error', response.text)
                        error_msg += f" - {error_detail}"
                    except:
                        error_msg += f" - {response.text}"
                    
                    self.logger.error(error_msg)
                    return {
                        "success": False,
                        "error": error_msg
                    }
                    
        except requests.exceptions.Timeout:
            error_msg = "Upload timeout - file may be too large or connection too slow"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
        except requests.exceptions.RequestException as e:
            error_msg = f"Upload failed: {str(e)}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
        except Exception as e:
            error_msg = f"Unexpected error during upload: {str(e)}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def get_upload_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the status of an upload/processing task
        
        Args:
            task_id: The task ID returned from upload_file
            
        Returns:
            Dictionary with task status
        """
        if not self.is_configured():
            return {
                "success": False,
                "error": "Vultr service not configured"
            }
        
        try:
            status_url = f"{self.api_url}/status/{task_id}"
            response = requests.get(status_url, timeout=10)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "status": response.json()
                }
            elif response.status_code == 404:
                return {
                    "success": False,
                    "error": "Task not found"
                }
            else:
                return {
                    "success": False,
                    "error": f"Status check failed: {response.status_code}"
                }
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get upload status: {e}")
            return {
                "success": False,
                "error": f"Status check failed: {str(e)}"
            }
    
    def list_uploads(self, limit: int = 10) -> Dict[str, Any]:
        """
        List recent uploads
        
        Args:
            limit: Maximum number of uploads to return
            
        Returns:
            Dictionary with list of uploads
        """
        if not self.is_configured():
            return {
                "success": False,
                "error": "Vultr service not configured"
            }
        
        try:
            list_url = f"{self.api_url}/uploads"
            params = {"limit": limit}
            response = requests.get(list_url, params=params, timeout=10)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "uploads": response.json()
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to list uploads: {response.status_code}"
                }
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to list uploads: {e}")
            return {
                "success": False,
                "error": f"List uploads failed: {str(e)}"
            }
    
    def get_config_info(self) -> Dict[str, Any]:
        """Get current Vultr configuration info"""
        return {
            "configured": self.is_configured(),
            "api_url": self.api_url,
            "upload_endpoint": self.upload_endpoint,
            "auto_upload": self.auto_upload
        }

# Global service instance
vultr_service = VultrUploadService()
