import React, { useState } from 'react';
import { 
  BarChart3, 
  TrendingUp, 
  Users, 
  Clock, 
  MessageCircle,
  Heart,
  Share,
  Eye,
  Calendar,
  Filter
} from 'lucide-react';

interface StreamMetrics {
  platform: 'twitch' | 'youtube' | 'discord';
  viewers: number;
  peakViewers: number;
  duration: string;
  messages: number;
  engagement: number;
}

const StreamAnalytics: React.FC = () => {
  const [timeRange, setTimeRange] = useState('7d');
  const [selectedPlatform, setSelectedPlatform] = useState('all');

  const currentMetrics: StreamMetrics[] = [
    { platform: 'twitch', viewers: 1247, peakViewers: 1856, duration: '2:34:12', messages: 892, engagement: 78 },
    { platform: 'youtube', viewers: 892, peakViewers: 1203, duration: '2:34:12', messages: 456, engagement: 65 },
    { platform: 'discord', viewers: 12, peakViewers: 18, duration: '2:34:12', messages: 234, engagement: 92 }
  ];

  const weeklyStats = [
    { day: 'Mon', viewers: 1200, engagement: 75 },
    { day: 'Tue', viewers: 1450, engagement: 82 },
    { day: 'Wed', viewers: 1100, engagement: 68 },
    { day: 'Thu', viewers: 1650, engagement: 85 },
    { day: 'Fri', viewers: 1890, engagement: 91 },
    { day: 'Sat', viewers: 2100, engagement: 88 },
    { day: 'Sun', viewers: 1750, engagement: 79 }
  ];

  const topMessages = [
    { user: 'StreamFan123', message: 'Amazing stream today!', platform: 'twitch', likes: 45 },
    { user: 'GamerPro', message: 'Can you play that song again?', platform: 'youtube', likes: 32 },
    { user: 'DiscordUser', message: 'Great explanation of the strategy', platform: 'discord', likes: 28 },
    { user: 'ViewerX', message: 'When is the next stream?', platform: 'twitch', likes: 19 }
  ];

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2">Stream Analytics</h2>
          <p className="text-gray-400">Detailed insights across all your streaming platforms</p>
        </div>
        <div className="flex items-center space-x-4">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="bg-white/10 border border-white/20 text-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
          </select>
          <select
            value={selectedPlatform}
            onChange={(e) => setSelectedPlatform(e.target.value)}
            className="bg-white/10 border border-white/20 text-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="all">All Platforms</option>
            <option value="twitch">Twitch</option>
            <option value="youtube">YouTube</option>
            <option value="discord">Discord</option>
          </select>
        </div>
      </div>

      {/* Current Stream Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {currentMetrics.map((metric) => (
          <div key={metric.platform} className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-white font-semibold capitalize">{metric.platform}</h3>
              <div className={`w-3 h-3 rounded-full bg-green-500 animate-pulse`}></div>
            </div>
            
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400 text-sm">Current Viewers</span>
                <span className="text-white font-medium">{metric.viewers.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400 text-sm">Peak Viewers</span>
                <span className="text-white font-medium">{metric.peakViewers.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400 text-sm">Duration</span>
                <span className="text-white font-medium">{metric.duration}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400 text-sm">Messages</span>
                <span className="text-white font-medium">{metric.messages}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400 text-sm">Engagement</span>
                <span className="text-green-400 font-medium">{metric.engagement}%</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Weekly Performance Chart */}
      <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6">
        <h3 className="text-xl font-semibold text-white mb-6 flex items-center space-x-2">
          <BarChart3 className="w-5 h-5" />
          <span>Weekly Performance</span>
        </h3>
        
        <div className="grid grid-cols-7 gap-4 mb-6">
          {weeklyStats.map((stat, index) => (
            <div key={index} className="text-center">
              <div className="bg-white/5 rounded-lg p-4 mb-2">
                <div 
                  className="bg-gradient-to-t from-purple-600 to-blue-600 rounded-lg mx-auto mb-2"
                  style={{ 
                    height: `${(stat.viewers / 2500) * 100}px`,
                    minHeight: '20px',
                    width: '100%'
                  }}
                ></div>
                <div className="text-white text-sm font-medium">{stat.viewers}</div>
                <div className="text-gray-400 text-xs">{stat.engagement}%</div>
              </div>
              <div className="text-gray-400 text-sm">{stat.day}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Engagement Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6">
          <h3 className="text-xl font-semibold text-white mb-6 flex items-center space-x-2">
            <TrendingUp className="w-5 h-5" />
            <span>Engagement Trends</span>
          </h3>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
              <div className="flex items-center space-x-3">
                <Heart className="w-5 h-5 text-red-500" />
                <span className="text-white">Likes/Reactions</span>
              </div>
              <div className="text-right">
                <div className="text-white font-medium">2,847</div>
                <div className="text-green-400 text-sm">+12%</div>
              </div>
            </div>
            
            <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
              <div className="flex items-center space-x-3">
                <MessageCircle className="w-5 h-5 text-blue-500" />
                <span className="text-white">Chat Messages</span>
              </div>
              <div className="text-right">
                <div className="text-white font-medium">1,582</div>
                <div className="text-green-400 text-sm">+8%</div>
              </div>
            </div>
            
            <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
              <div className="flex items-center space-x-3">
                <Share className="w-5 h-5 text-green-500" />
                <span className="text-white">Shares</span>
              </div>
              <div className="text-right">
                <div className="text-white font-medium">234</div>
                <div className="text-green-400 text-sm">+15%</div>
              </div>
            </div>
            
            <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
              <div className="flex items-center space-x-3">
                <Clock className="w-5 h-5 text-yellow-500" />
                <span className="text-white">Avg. Watch Time</span>
              </div>
              <div className="text-right">
                <div className="text-white font-medium">24m 32s</div>
                <div className="text-green-400 text-sm">+5%</div>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6">
          <h3 className="text-xl font-semibold text-white mb-6 flex items-center space-x-2">
            <MessageCircle className="w-5 h-5" />
            <span>Top Chat Messages</span>
          </h3>
          
          <div className="space-y-4">
            {topMessages.map((msg, index) => (
              <div key={index} className="p-4 bg-white/5 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="text-white font-medium text-sm">{msg.user}</span>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      msg.platform === 'twitch' ? 'bg-purple-600/20 text-purple-400' :
                      msg.platform === 'youtube' ? 'bg-red-600/20 text-red-400' :
                      'bg-blue-600/20 text-blue-400'
                    }`}>
                      {msg.platform}
                    </span>
                  </div>
                  <div className="flex items-center space-x-1 text-gray-400">
                    <Heart className="w-3 h-3" />
                    <span className="text-xs">{msg.likes}</span>
                  </div>
                </div>
                <p className="text-gray-300 text-sm">{msg.message}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default StreamAnalytics;