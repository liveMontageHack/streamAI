import logging
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import config

class YouTubeAPI:
    """YouTube API integration for streaming platform functionality"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.youtube = None
        self.api_key = config.get_youtube_api_key()
        self.authenticated = False
        
        if self.api_key:
            self._initialize_service()
        else:
            self.logger.warning("YouTube API key not available. YouTube features disabled.")
    
    def _initialize_service(self):
        """Initialize YouTube API service"""
        try:
            self.youtube = build('youtube', 'v3', developerKey=self.api_key)
            self.authenticated = True
            self.logger.info("YouTube API service initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize YouTube API service: {e}")
            self.authenticated = False
    
    def is_authenticated(self):
        """Check if YouTube API is authenticated"""
        return self.authenticated
    
    def get_channel_info(self, channel_id=None):
        """Get channel information"""
        if not self.authenticated:
            self.logger.error("YouTube API not authenticated")
            return None
        
        try:
            # If no channel_id provided, get info for authenticated user's channel
            if channel_id:
                request = self.youtube.channels().list(
                    part='snippet,statistics,status',
                    id=channel_id
                )
            else:
                request = self.youtube.channels().list(
                    part='snippet,statistics,status',
                    mine=True
                )
            
            response = request.execute()
            
            if response['items']:
                channel = response['items'][0]
                channel_info = {
                    'id': channel['id'],
                    'title': channel['snippet']['title'],
                    'description': channel['snippet']['description'],
                    'subscriber_count': channel['statistics'].get('subscriberCount', 0),
                    'video_count': channel['statistics'].get('videoCount', 0),
                    'view_count': channel['statistics'].get('viewCount', 0),
                    'created_date': channel['snippet']['publishedAt']
                }
                self.logger.info(f"Retrieved channel info for: {channel_info['title']}")
                return channel_info
            else:
                self.logger.warning("No channel found")
                return None
                
        except HttpError as e:
            self.logger.error(f"YouTube API error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to get channel info: {e}")
            return None
    
    def search_videos(self, query, max_results=10):
        """Search for videos on YouTube"""
        if not self.authenticated:
            self.logger.error("YouTube API not authenticated")
            return []
        
        try:
            request = self.youtube.search().list(
                part='snippet',
                q=query,
                type='video',
                maxResults=max_results,
                order='relevance'
            )
            
            response = request.execute()
            videos = []
            
            for item in response['items']:
                video_info = {
                    'video_id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'channel_title': item['snippet']['channelTitle'],
                    'published_at': item['snippet']['publishedAt'],
                    'thumbnail_url': item['snippet']['thumbnails']['default']['url']
                }
                videos.append(video_info)
            
            self.logger.info(f"Found {len(videos)} videos for query: {query}")
            return videos
            
        except HttpError as e:
            self.logger.error(f"YouTube API error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Failed to search videos: {e}")
            return []
    
    def get_video_details(self, video_id):
        """Get detailed information about a specific video"""
        if not self.authenticated:
            self.logger.error("YouTube API not authenticated")
            return None
        
        try:
            request = self.youtube.videos().list(
                part='snippet,statistics,status,contentDetails',
                id=video_id
            )
            
            response = request.execute()
            
            if response['items']:
                video = response['items'][0]
                video_details = {
                    'id': video['id'],
                    'title': video['snippet']['title'],
                    'description': video['snippet']['description'],
                    'channel_title': video['snippet']['channelTitle'],
                    'published_at': video['snippet']['publishedAt'],
                    'duration': video['contentDetails']['duration'],
                    'view_count': video['statistics'].get('viewCount', 0),
                    'like_count': video['statistics'].get('likeCount', 0),
                    'comment_count': video['statistics'].get('commentCount', 0),
                    'privacy_status': video['status']['privacyStatus'],
                    'upload_status': video['status']['uploadStatus']
                }
                self.logger.info(f"Retrieved details for video: {video_details['title']}")
                return video_details
            else:
                self.logger.warning(f"No video found with ID: {video_id}")
                return None
                
        except HttpError as e:
            self.logger.error(f"YouTube API error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to get video details: {e}")
            return None
    
    def get_live_streams(self, channel_id=None):
        """Get live streams for a channel"""
        if not self.authenticated:
            self.logger.error("YouTube API not authenticated")
            return []
        
        try:
            if channel_id:
                request = self.youtube.search().list(
                    part='snippet',
                    channelId=channel_id,
                    type='video',
                    eventType='live',
                    maxResults=10
                )
            else:
                request = self.youtube.search().list(
                    part='snippet',
                    type='video',
                    eventType='live',
                    maxResults=10
                )
            
            response = request.execute()
            live_streams = []
            
            for item in response['items']:
                stream_info = {
                    'video_id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'channel_title': item['snippet']['channelTitle'],
                    'channel_id': item['snippet']['channelId'],
                    'published_at': item['snippet']['publishedAt'],
                    'thumbnail_url': item['snippet']['thumbnails']['default']['url']
                }
                live_streams.append(stream_info)
            
            self.logger.info(f"Found {len(live_streams)} live streams")
            return live_streams
            
        except HttpError as e:
            self.logger.error(f"YouTube API error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Failed to get live streams: {e}")
            return []
    
    def create_broadcast(self, title, description, scheduled_start_time=None):
        """Create a YouTube live broadcast (requires OAuth, not API key)"""
        # Note: This functionality requires OAuth authentication, not just API key
        # This is a placeholder for future OAuth implementation
        self.logger.warning("Creating broadcasts requires OAuth authentication, not implemented with API key only")
        return None
    
    def get_quota_usage(self):
        """Get information about API quota usage"""
        # This is informational - actual quota tracking happens on Google's side
        self.logger.info("YouTube API quota usage tracking is handled by Google")
        return {
            'note': 'Quota usage is tracked by Google. Check Google Cloud Console for details.',
            'daily_limit': 10000,  # Default quota limit
            'authenticated': self.authenticated
        }
    
    def validate_api_key(self):
        """Validate the YouTube API key by making a simple request"""
        if not self.api_key:
            return False
        
        try:
            # Make a simple request to validate the API key
            request = self.youtube.search().list(
                part='snippet',
                q='test',
                type='video',
                maxResults=1
            )
            request.execute()
            self.logger.info("YouTube API key validation successful")
            return True
        except HttpError as e:
            self.logger.error(f"YouTube API key validation failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"YouTube API key validation error: {e}")
            return False
