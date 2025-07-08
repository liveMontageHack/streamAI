#!/usr/bin/env python3
"""
Video Processing Module for StreamAI
Integrates advanced video editing capabilities using local processing
"""

import asyncio
import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Add video_processing directory to path
video_processing_dir = Path(__file__).parent.parent / "video_processing"
sys.path.append(str(video_processing_dir))

try:
    from local_video_processor import LocalVideoProcessor, LocalProcessingConfig
except ImportError:
    print("Warning: local_video_processor not found. Video processing features will be disabled.")
    LocalVideoProcessor = None
    LocalProcessingConfig = None

@dataclass
class VideoEditingPreset:
    """Predefined video editing presets"""
    name: str
    description: str
    config: Dict[str, Any]

class StreamAIVideoProcessor:
    """Video processor for StreamAI with preset configurations"""
    
    def __init__(self):
        self.presets = {
            "conservative": VideoEditingPreset(
                name="Conservative",
                description="Gentle editing that keeps most content",
                config={
                    "subtitle_model": "base",
                    "subtitle_language": "en",
                    "silence_threshold": -35,
                    "min_silence_duration": 2.0,
                    "min_segment_duration": 1.5,
                    "max_gap_merge": 5.0,
                    "hesitation_threshold": 0.7,
                    "filler_threshold": 0.6,
                    "confidence_threshold": 0.2,
                    "min_text_length": 5,
                    "detect_silence": True,
                    "detect_hesitations": True,
                    "detect_filler_words": True,
                    "detect_low_confidence": False,
                    "output_quality": "high",
                    "create_project_folder": True,
                    "keep_temp_files": False
                }
            ),
            "balanced": VideoEditingPreset(
                name="Balanced",
                description="Balanced editing for general content",
                config={
                    "subtitle_model": "base",
                    "subtitle_language": "en",
                    "silence_threshold": -28,
                    "min_silence_duration": 1.2,
                    "min_segment_duration": 2.5,
                    "max_gap_merge": 4.0,
                    "hesitation_threshold": 0.4,
                    "filler_threshold": 0.3,
                    "confidence_threshold": 0.35,
                    "min_text_length": 12,
                    "detect_silence": True,
                    "detect_hesitations": True,
                    "detect_filler_words": True,
                    "detect_low_confidence": True,
                    "output_quality": "medium",
                    "create_project_folder": True,
                    "keep_temp_files": False
                }
            ),
            "aggressive": VideoEditingPreset(
                name="Aggressive",
                description="Heavy editing that removes more content",
                config={
                    "subtitle_model": "base",
                    "subtitle_language": "en",
                    "silence_threshold": -25,
                    "min_silence_duration": 0.5,
                    "min_segment_duration": 3.0,
                    "max_gap_merge": 2.0,
                    "hesitation_threshold": 0.3,
                    "filler_threshold": 0.2,
                    "confidence_threshold": 0.4,
                    "min_text_length": 15,
                    "detect_silence": True,
                    "detect_hesitations": True,
                    "detect_filler_words": True,
                    "detect_low_confidence": True,
                    "custom_hesitation_words": ["euh", "euuh", "hm", "hmm", "um", "uh"],
                    "custom_filler_words": ["ben", "alors", "donc", "voilà", "quoi", "like", "you know"],
                    "output_quality": "medium",
                    "create_project_folder": True,
                    "keep_temp_files": False
                }
            ),
            "silence_only": VideoEditingPreset(
                name="Silence Only",
                description="Only removes silence, keeps all speech",
                config={
                    "subtitle_model": "base",
                    "subtitle_language": "en",
                    "silence_threshold": -30,
                    "min_silence_duration": 1.5,
                    "min_segment_duration": 1.0,
                    "max_gap_merge": 10.0,
                    "hesitation_threshold": 1.0,
                    "filler_threshold": 1.0,
                    "confidence_threshold": 0.0,
                    "min_text_length": 1,
                    "detect_silence": True,
                    "detect_hesitations": False,
                    "detect_filler_words": False,
                    "detect_low_confidence": False,
                    "output_quality": "medium",
                    "create_project_folder": True,
                    "keep_temp_files": False
                }
            )
        }
    
    async def process_video(
        self, 
        video_path: str, 
        preset: str = "balanced",
        output_dir: Optional[str] = None,
        language: str = "en",
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Process a video with the specified preset
        
        Args:
            video_path: Path to the input video file
            preset: Processing preset ("conservative", "balanced", "aggressive", "silence_only")
            output_dir: Directory for output files (optional)
            language: Language for subtitle processing
            progress_callback: Callback function for progress updates
            
        Returns:
            Dictionary with processing results
        """
        if LocalVideoProcessor is None:
            raise Exception("Video processing dependencies not available")
        
        if preset not in self.presets:
            raise ValueError(f"Unknown preset: {preset}. Available presets: {list(self.presets.keys())}")
        
        # Get preset configuration
        preset_config = self.presets[preset].config.copy()
        preset_config["subtitle_language"] = language
        
        # Create output directory if not specified
        if output_dir is None:
            output_dir = tempfile.mkdtemp(prefix="streamai_video_processing_")
        
        # Create configuration
        config = LocalProcessingConfig(**preset_config)
        config.preset_name = preset  # Add preset name for reporting
        
        # Initialize processor
        processor = LocalVideoProcessor(config)
        await processor.initialize()
        
        try:
            # Process the video
            if progress_callback:
                progress_callback(0, "Starting video processing...")
            
            result = await processor.process_video_locally(video_path, output_dir)
            
            if progress_callback:
                progress_callback(100, "Video processing completed!")
            
            return {
                "success": True,
                "preset": preset,
                "preset_description": self.presets[preset].description,
                "edited_video": result["edited_video"],
                "processing_summary": result["processing_summary"],
                "output_directory": output_dir,
                "subtitle_files": result.get("subtitle_files", []),
                "reports": result.get("reports", [])
            }
            
        except Exception as e:
            if progress_callback:
                progress_callback(-1, f"Error: {str(e)}")
            raise e
    
    def get_presets(self) -> Dict[str, Dict[str, str]]:
        """Get available processing presets"""
        return {
            name: {
                "name": preset.name,
                "description": preset.description
            }
            for name, preset in self.presets.items()
        }
    
    def estimate_processing_time(self, video_path: str) -> Dict[str, Any]:
        """Estimate processing time for a video"""
        try:
            # Get video duration (simple estimate)
            import cv2
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            duration = frame_count / fps if fps > 0 else 0
            cap.release()
            
            # Rough estimate: processing takes 2-5x video duration
            min_time = duration * 2
            max_time = duration * 5
            
            return {
                "video_duration": duration,
                "estimated_min_time": min_time,
                "estimated_max_time": max_time,
                "estimated_avg_time": (min_time + max_time) / 2
            }
        except Exception:
            return {
                "video_duration": 0,
                "estimated_min_time": 60,
                "estimated_max_time": 300,
                "estimated_avg_time": 180
            }
