#!/usr/bin/env python3
"""
Advanced example with full control over detection settings
"""

import asyncio
from local_video_processor import LocalVideoProcessor, LocalProcessingConfig

async def example_conservative_editing(video_path: str):
    """Conservative editing - keeps more content"""
    print("🔧 CONSERVATIVE EDITING EXAMPLE")
    print("=" * 50)
    
    config = LocalProcessingConfig(
        # Basic settings
        subtitle_model="base",
        subtitle_language="fr",
        
        # Conservative silence detection
        silence_threshold=-35,  # Less aggressive (quieter sounds kept)
        min_silence_duration=2.0,  # Longer silences required to cut
        min_segment_duration=1.5,  # Shorter segments allowed
        max_gap_merge=5.0,  # Merge segments with larger gaps
        
        # Conservative hesitation detection
        hesitation_threshold=0.7,  # 70% hesitation words needed
        filler_threshold=0.6,  # 60% filler words needed
        confidence_threshold=0.2,  # Lower confidence threshold
        min_text_length=5,  # Shorter text allowed
        
        # Detection flags
        detect_silence=True,
        detect_hesitations=True,
        detect_filler_words=True,
        detect_low_confidence=False,  # Keep low confidence segments
        
        # Output settings
        output_quality="high",
        create_project_folder=True,
        keep_temp_files=True
    )
    
    processor = LocalVideoProcessor(config)
    await processor.initialize()
    
    #video_path = "/home/avgilles/Documents/github/lab/ytb/downloads/gilles.mp4"
    video_path = "./hesitation.mkv"
    
    result = await processor.process_video_locally(video_path, "output")
    
    print(f"✅ Conservative editing completed!")
    print(f"📁 Project folder: {result['edited_video'].replace('/video/gilles_edited.mp4', '')}")
    print(f"⏱️ Time saved: {result['processing_summary']['time_saved']:.2f}s")
    print(f"📈 Compression: {result['processing_summary']['compression_ratio']:.1f}%")
    print()

async def example_aggressive_editing(video_path: str):
    """Aggressive editing - removes more content"""
    print("⚡ AGGRESSIVE EDITING EXAMPLE")
    print("=" * 50)
    
    config = LocalProcessingConfig(
        # Basic settings
        subtitle_model="base",
        subtitle_language="fr",
        
        # Aggressive silence detection
        silence_threshold=-25,  # More aggressive (louder sounds cut)
        min_silence_duration=0.5,  # Shorter silences cut
        min_segment_duration=3.0,  # Longer segments required
        max_gap_merge=2.0,  # Smaller gaps merged
        
        # Aggressive hesitation detection
        hesitation_threshold=0.3,  # 30% hesitation words enough
        filler_threshold=0.2,  # 20% filler words enough
        confidence_threshold=0.4,  # Higher confidence required
        min_text_length=15,  # Longer text required
        
        # Detection flags
        detect_silence=True,
        detect_hesitations=True,
        detect_filler_words=True,
        detect_low_confidence=True,
        
        # Custom word lists
        custom_hesitation_words=["euh", "euuh", "hm", "hmm", "um", "uh"],
        custom_filler_words=["ben", "alors", "donc", "voilà", "quoi", "like", "you know"],
        
        # Output settings
        output_quality="medium",
        create_project_folder=True,
        keep_temp_files=False
    )
    
    processor = LocalVideoProcessor(config)
    await processor.initialize()
    
    result = await processor.process_video_locally(video_path, "output")
    
    print(f"✅ Aggressive editing completed!")
    print(f"📁 Project folder: {result['edited_video'].replace('/video/gilles_edited.mp4', '')}")
    print(f"⏱️ Time saved: {result['processing_summary']['time_saved']:.2f}s")
    print(f"📈 Compression: {result['processing_summary']['compression_ratio']:.1f}%")
    print()

async def example_custom_detection(video_path: str):
    """Custom detection with specific settings"""
    print("🎯 CUSTOM DETECTION EXAMPLE")
    print("=" * 50)
    
    config = LocalProcessingConfig(
        # Basic settings
        subtitle_model="base",
        subtitle_language="fr",
        
        # Custom silence settings
        silence_threshold=-28,  # Balanced
        min_silence_duration=1.2,  # Custom duration
        min_segment_duration=2.5,  # Custom segment length
        max_gap_merge=4.0,  # Custom gap merging
        
        # Custom detection thresholds
        hesitation_threshold=0.4,  # 40% threshold
        filler_threshold=0.3,  # 30% threshold
        confidence_threshold=0.35,  # 35% confidence
        min_text_length=12,  # 12 characters minimum
        
        # Selective detection
        detect_silence=True,
        detect_hesitations=True,
        detect_filler_words=False,  # Disable filler word detection
        detect_low_confidence=True,
        
        # Custom word lists for French content
        custom_hesitation_words=[
            "euh", "euuh", "euuuh", "euuuuh",
            "hm", "hmm", "hmmm", "hmmmm",
            "mmm", "mmmm", "mmmmm"
        ],
        custom_filler_words=[
            "ben", "alors", "donc", "voilà", "quoi", "enfin",
            "disons", "comment dire", "tu vois", "genre"
        ],
        
        # Output settings
        output_quality="high",
        create_project_folder=True,
        keep_temp_files=True
    )
    
    processor = LocalVideoProcessor(config)
    await processor.initialize()
    
    result = await processor.process_video_locally(video_path, "output")
    
    print(f"✅ Custom detection completed!")
    print(f"📁 Project folder: {result['edited_video'].replace('/video/gilles_edited.mp4', '')}")
    print(f"⏱️ Time saved: {result['processing_summary']['time_saved']:.2f}s")
    print(f"📈 Compression: {result['processing_summary']['compression_ratio']:.1f}%")
    print()

async def example_silence_only(video_path: str):
    """Only remove silence, keep all speech"""
    print("🔇 SILENCE-ONLY EDITING EXAMPLE")
    print("=" * 50)
    
    config = LocalProcessingConfig(
        # Basic settings
        subtitle_model="base",
        subtitle_language="fr",
        
        # Silence-only settings
        silence_threshold=-30,
        min_silence_duration=1.5,
        min_segment_duration=1.0,
        max_gap_merge=10.0,  # Large gap merging
        
        # Disable all speech filtering
        hesitation_threshold=1.0,  # Never trigger (100%)
        filler_threshold=1.0,  # Never trigger (100%)
        confidence_threshold=0.0,  # Accept all confidence
        min_text_length=1,  # Accept very short text
        
        # Detection flags - only silence
        detect_silence=True,
        detect_hesitations=False,  # Disabled
        detect_filler_words=False,  # Disabled
        detect_low_confidence=False,  # Disabled
        
        # Output settings
        output_quality="medium",
        create_project_folder=True,
        keep_temp_files=False
    )
    
    processor = LocalVideoProcessor(config)
    await processor.initialize()
    
    result = await processor.process_video_locally(video_path, "output")
    
    print(f"✅ Silence-only editing completed!")
    print(f"📁 Project folder: {result['edited_video'].replace('/video/gilles_edited.mp4', '')}")
    print(f"⏱️ Time saved: {result['processing_summary']['time_saved']:.2f}s")
    print(f"📈 Compression: {result['processing_summary']['compression_ratio']:.1f}%")
    print()

async def main():
    """Run all examples"""
    print("🚀 ADVANCED LOCAL VIDEO PROCESSOR EXAMPLES")
    print("=" * 60)
    print()
    
    try:
        # Run different editing styles

        #video_path = "./test.mp4"
        video_path = "./hesitation.mkv"

        # await example_conservative_editing(video_path)
        await example_aggressive_editing(video_path)
        await example_custom_detection(video_path)
        await example_silence_only(video_path)

        print("🎉 All examples completed successfully!")
        print()
        print("📁 Check the 'output' folder for organized results:")
        print("   📂 gilles_YYYYMMDD_HHMMSS/")
        print("      ├── 📂 video/           # Edited video files")
        print("      ├── 📂 subtitles/      # SRT subtitle files")
        print("      ├── 📂 reports/        # Processing reports & config")
        print("      └── 📂 debug/          # Debug information")
        print()
        print("🔧 Configuration options:")
        print("   • silence_threshold: -35 (conservative) to -25 (aggressive)")
        print("   • min_silence_duration: 0.5s (aggressive) to 2.0s (conservative)")
        print("   • hesitation_threshold: 0.3 (aggressive) to 0.7 (conservative)")
        print("   • filler_threshold: 0.2 (aggressive) to 0.6 (conservative)")
        print("   • Detection flags: Enable/disable specific detection types")
        print("   • Custom word lists: Define your own hesitation/filler words")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())