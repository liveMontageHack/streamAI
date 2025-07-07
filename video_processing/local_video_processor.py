#!/usr/bin/env python3
"""
Mock Local Video Processor for StreamAI
A simplified version that simulates video processing functionality
"""

import asyncio
import os
import shutil
import time
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class LocalProcessingConfig:
    """Configuration for video processing"""
    subtitle_model: str = "base"
    subtitle_language: str = "en"
    silence_threshold: float = -30
    min_silence_duration: float = 1.0
    min_segment_duration: float = 2.0
    max_gap_merge: float = 3.0
    hesitation_threshold: float = 0.5
    filler_threshold: float = 0.4
    confidence_threshold: float = 0.3
    min_text_length: int = 10
    detect_silence: bool = True
    detect_hesitations: bool = True
    detect_filler_words: bool = True
    detect_low_confidence: bool = True
    custom_hesitation_words: Optional[list] = None
    custom_filler_words: Optional[list] = None
    output_quality: str = "medium"
    create_project_folder: bool = True
    keep_temp_files: bool = False

class LocalVideoProcessor:
    """Mock video processor that simulates the functionality"""
    
    def __init__(self, config: LocalProcessingConfig):
        self.config = config
        
    async def initialize(self):
        """Initialize the processor"""
        return True
    
    async def process_video_locally(
        self, 
        video_path: str, 
        output_dir: str
    ) -> Dict[str, Any]:
        """
        Mock video processing that simulates editing
        In a real implementation, this would use FFmpeg and AI models
        """
        
        # Simulate processing time based on video length
        video_file = Path(video_path)
        if not video_file.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Create output directory structure
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        video_dir = output_path / "video"
        subtitles_dir = output_path / "subtitles"
        reports_dir = output_path / "reports"
        
        video_dir.mkdir(exist_ok=True)
        subtitles_dir.mkdir(exist_ok=True)
        reports_dir.mkdir(exist_ok=True)
        
        # Simulate processing steps
        await asyncio.sleep(1)  # Initialization
        
        # Mock video file size for timing estimation
        file_size_mb = video_file.stat().st_size / (1024 * 1024)
        estimated_processing_time = min(max(file_size_mb / 10, 5), 30)  # 5-30 seconds
        
        # Simulate processing with progress updates
        steps = 10
        for i in range(steps):
            await asyncio.sleep(estimated_processing_time / steps)
            progress = int((i + 1) / steps * 100)
            # Progress would be reported via callback in real implementation
        
        # Create output video (copy original for now - in real implementation this would be edited)
        output_video = video_dir / f"{video_file.stem}_edited{video_file.suffix}"
        shutil.copy2(video_path, output_video)
        
        # Create mock subtitle file
        subtitle_file = subtitles_dir / f"{video_file.stem}.srt"
        with open(subtitle_file, 'w', encoding='utf-8') as f:
            f.write("1\n00:00:00,000 --> 00:00:05,000\nProcessed with StreamAI Video Editor\n\n")
            f.write("2\n00:00:05,000 --> 00:00:10,000\nSilence and hesitations removed\n\n")
        
        # Create processing report
        report_file = reports_dir / "processing_report.json"
        import json
        report = {
            "preset": getattr(self.config, 'preset_name', 'custom'),
            "original_duration": "00:10:30",  # Mock duration
            "edited_duration": "00:08:45",    # Mock edited duration
            "time_saved": 105,  # seconds
            "compression_ratio": 83.3,  # percentage
            "segments_removed": 15,
            "silence_removed": "01:25",
            "hesitations_removed": "00:20"
        }
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Calculate mock statistics
        original_duration = 630  # 10:30 in seconds
        edited_duration = 525    # 8:45 in seconds
        time_saved = original_duration - edited_duration
        compression_ratio = (time_saved / original_duration) * 100
        
        return {
            "edited_video": str(output_video),
            "subtitle_files": [str(subtitle_file)],
            "reports": [str(report_file)],
            "processing_summary": {
                "original_duration": original_duration,
                "edited_duration": edited_duration,
                "time_saved": time_saved,
                "compression_ratio": compression_ratio,
                "segments_removed": 15,
                "preset_used": getattr(self.config, 'preset_name', 'custom')
            }
        }
