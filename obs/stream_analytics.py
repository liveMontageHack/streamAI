#!/usr/bin/env python3
"""
Stream Analytics Module - Advanced data analysis for OBS streams
"""

import json
import asyncio
from datetime import datetime, timedelta
from recording_manager import RecordingManager

class StreamAnalytics:
    """Advanced analytics for stream data"""
    
    def __init__(self):
        self.recording_manager = RecordingManager()
    
    async def get_detailed_analytics(self):
        """Get comprehensive stream analytics"""
        await self.recording_manager.initialize()
        
        if not self.recording_manager.obs_controller.is_connected():
            print("❌ Cannot get analytics: OBS not connected")
            return None
        
        # Get current data
        obs_data = self.recording_manager.get_obs_data()
        
        # Calculate analytics
        analytics = {
            'timestamp': datetime.now().isoformat(),
            'performance_metrics': self._analyze_performance(obs_data),
            'audio_analysis': self._analyze_audio(obs_data),
            'stream_quality': self._analyze_stream_quality(obs_data),
            'recording_analysis': self._analyze_recording(obs_data),
            'recommendations': self._generate_recommendations(obs_data)
        }
        
        await self.recording_manager.cleanup()
        return analytics
    
    def _analyze_performance(self, obs_data):
        """Analyze stream performance metrics"""
        stream_status = obs_data.get('stream_status', {})
        
        if not stream_status.get('active'):
            return {'status': 'not_streaming'}
        
        total_frames = stream_status.get('total_frames', 0)
        skipped_frames = stream_status.get('skipped_frames', 0)
        duration_ms = stream_status.get('duration', 0)
        
        # Calculate metrics
        duration_seconds = duration_ms / 1000 if duration_ms > 0 else 1
        fps = total_frames / duration_seconds if duration_seconds > 0 else 0
        skip_rate = (skipped_frames / total_frames * 100) if total_frames > 0 else 0
        
        return {
            'fps': round(fps, 2),
            'total_frames': total_frames,
            'skipped_frames': skipped_frames,
            'skip_rate_percent': round(skip_rate, 2),
            'duration_seconds': round(duration_seconds, 2),
            'performance_grade': self._grade_performance(skip_rate, fps)
        }
    
    def _analyze_audio(self, obs_data):
        """Analyze audio configuration"""
        audio_sources = obs_data.get('audio_sources', [])
        
        analysis = {
            'total_sources': len(audio_sources),
            'source_types': {},
            'sources': []
        }
        
        for source in audio_sources:
            source_type = source.get('kind', 'unknown')
            analysis['source_types'][source_type] = analysis['source_types'].get(source_type, 0) + 1
            
            analysis['sources'].append({
                'name': source.get('name'),
                'type': source_type,
                'category': self._categorize_audio_source(source_type)
            })
        
        return analysis
    
    def _analyze_stream_quality(self, obs_data):
        """Analyze stream quality metrics"""
        stream_status = obs_data.get('stream_status', {})
        
        if not stream_status.get('active'):
            return {'status': 'not_streaming'}
        
        bytes_sent = stream_status.get('bytes', 0)
        duration_ms = stream_status.get('duration', 0)
        congestion = stream_status.get('congestion', 0)
        
        # Calculate bitrate
        duration_seconds = duration_ms / 1000 if duration_ms > 0 else 1
        bitrate_bps = (bytes_sent * 8) / duration_seconds if duration_seconds > 0 else 0
        bitrate_kbps = bitrate_bps / 1000
        
        return {
            'bitrate_kbps': round(bitrate_kbps, 2),
            'total_bytes': bytes_sent,
            'congestion_percent': round(congestion * 100, 2),
            'connection_quality': self._grade_connection(congestion, bitrate_kbps),
            'data_efficiency': self._calculate_efficiency(bytes_sent, duration_seconds)
        }
    
    def _analyze_recording(self, obs_data):
        """Analyze recording status and configuration"""
        recording_status = obs_data.get('recording_status', {})
        
        return {
            'is_recording': recording_status.get('active', False),
            'recording_duration': recording_status.get('timecode', '00:00:00'),
            'recording_size_bytes': recording_status.get('bytes', 0),
            'recording_folder': obs_data.get('recording_folder'),
            'current_scene': obs_data.get('current_scene'),
            'available_scenes': obs_data.get('scenes_list', [])
        }
    
    def _generate_recommendations(self, obs_data):
        """Generate optimization recommendations"""
        recommendations = []
        
        stream_status = obs_data.get('stream_status', {})
        if stream_status.get('active'):
            # Check frame drops
            skip_rate = 0
            if stream_status.get('total_frames', 0) > 0:
                skip_rate = (stream_status.get('skipped_frames', 0) / stream_status.get('total_frames', 1)) * 100
            
            if skip_rate > 5:
                recommendations.append({
                    'type': 'performance',
                    'priority': 'high',
                    'message': f'High frame drop rate ({skip_rate:.1f}%). Consider reducing stream quality or closing other applications.'
                })
            
            # Check congestion
            congestion = stream_status.get('congestion', 0)
            if congestion > 0.1:
                recommendations.append({
                    'type': 'network',
                    'priority': 'medium',
                    'message': f'Network congestion detected ({congestion*100:.1f}%). Check internet connection.'
                })
        
        # Check audio setup
        audio_sources = obs_data.get('audio_sources', [])
        if len(audio_sources) < 2:
            recommendations.append({
                'type': 'audio',
                'priority': 'low',
                'message': 'Consider adding more audio sources for better stream quality.'
            })
        
        return recommendations
    
    def _grade_performance(self, skip_rate, fps):
        """Grade overall performance"""
        if skip_rate < 1 and fps >= 25:
            return 'A'
        elif skip_rate < 3 and fps >= 20:
            return 'B'
        elif skip_rate < 5 and fps >= 15:
            return 'C'
        else:
            return 'D'
    
    def _grade_connection(self, congestion, bitrate):
        """Grade connection quality"""
        if congestion < 0.05 and bitrate > 1000:
            return 'Excellent'
        elif congestion < 0.1 and bitrate > 500:
            return 'Good'
        elif congestion < 0.2:
            return 'Fair'
        else:
            return 'Poor'
    
    def _categorize_audio_source(self, source_type):
        """Categorize audio source type"""
        if 'input' in source_type:
            return 'Microphone'
        elif 'output' in source_type:
            return 'Desktop Audio'
        else:
            return 'Other'
    
    def _calculate_efficiency(self, bytes_sent, duration):
        """Calculate data efficiency"""
        if duration <= 0:
            return 0
        
        mb_per_minute = (bytes_sent / (1024 * 1024)) / (duration / 60)
        return round(mb_per_minute, 2)

async def main():
    """Run analytics demonstration"""
    analytics = StreamAnalytics()
    
    print("🔍 Getting detailed stream analytics...")
    data = await analytics.get_detailed_analytics()
    
    if data:
        print("\n📊 STREAM ANALYTICS REPORT")
        print("=" * 50)
        
        # Performance metrics
        perf = data['performance_metrics']
        if perf.get('status') != 'not_streaming':
            print(f"\n🎯 Performance Grade: {perf['performance_grade']}")
            print(f"   FPS: {perf['fps']}")
            print(f"   Frame Drop Rate: {perf['skip_rate_percent']}%")
            print(f"   Total Frames: {perf['total_frames']:,}")
        
        # Stream quality
        quality = data['stream_quality']
        if quality.get('status') != 'not_streaming':
            print(f"\n🌐 Connection Quality: {quality['connection_quality']}")
            print(f"   Bitrate: {quality['bitrate_kbps']:.1f} kbps")
            print(f"   Data Sent: {quality['total_bytes'] / (1024*1024):.1f} MB")
            print(f"   Congestion: {quality['congestion_percent']:.1f}%")
        
        # Audio analysis
        audio = data['audio_analysis']
        print(f"\n🎵 Audio Setup: {audio['total_sources']} sources")
        for source in audio['sources']:
            print(f"   - {source['name']} ({source['category']})")
        
        # Recording status
        recording = data['recording_analysis']
        print(f"\n📹 Recording: {'Active' if recording['is_recording'] else 'Inactive'}")
        if recording['is_recording']:
            print(f"   Duration: {recording['recording_duration']}")
            print(f"   Size: {recording['recording_size_bytes'] / (1024*1024):.1f} MB")
        
        # Recommendations
        recommendations = data['recommendations']
        if recommendations:
            print(f"\n💡 Recommendations:")
            for rec in recommendations:
                priority_icon = "🔴" if rec['priority'] == 'high' else "🟡" if rec['priority'] == 'medium' else "🟢"
                print(f"   {priority_icon} {rec['message']}")
        else:
            print(f"\n✅ No issues detected - your stream is running optimally!")
        
        print("\n" + "=" * 50)
    else:
        print("❌ Could not retrieve analytics data")

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
