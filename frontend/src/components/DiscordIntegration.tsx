import React, { useState, useEffect } from 'react';
import { 
  MessageCircle, 
  Mic, 
  Users, 
  Play, 
  Square, 
  Settings,
  Volume2,
  Radio,
  Link,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

interface VoiceChannel {
  id: string;
  name: string;
  userCount: number;
  isStreaming: boolean;
}

interface DiscordServer {
  id: string;
  name: string;
  icon: string;
  channels: VoiceChannel[];
  connected: boolean;
}

const DiscordIntegration: React.FC = () => {
  const [servers, setServers] = useState<DiscordServer[]>([
    {
      id: '1',
      name: 'Mon Serveur',
      icon: '🎮',
      connected: true,
      channels: [
        { id: '1', name: 'Général', userCount: 3, isStreaming: false },
        { id: '2', name: 'Stream', userCount: 1, isStreaming: true },
        { id: '3', name: 'Gaming', userCount: 0, isStreaming: false }
      ]
    }
  ]);

  const [selectedChannel, setSelectedChannel] = useState<string>('');
  const [streamingToTwitch, setStreamingToTwitch] = useState(false);
  const [streamingToYoutube, setStreamingToYoutube] = useState(false);
  const [audioQuality, setAudioQuality] = useState('high');

  const startStreaming = (platform: 'twitch' | 'youtube' | 'both') => {
    if (platform === 'twitch' || platform === 'both') {
      setStreamingToTwitch(true);
    }
    if (platform === 'youtube' || platform === 'both') {
      setStreamingToYoutube(true);
    }
  };

  const stopStreaming = () => {
    setStreamingToTwitch(false);
    setStreamingToYoutube(false);
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold text-white mb-2">Discord Integration</h2>
        <p className="text-gray-400">Connect and stream from Discord voice channels to multiple platforms</p>
      </div>

      {/* Discord Servers */}
      <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6">
        <h3 className="text-xl font-semibold text-white mb-6 flex items-center space-x-2">
          <MessageCircle className="w-5 h-5" />
          <span>Connected Discord Servers</span>
        </h3>

        <div className="space-y-4">
          {servers.map((server) => (
            <div key={server.id} className="bg-white/5 border border-white/10 rounded-lg p-4">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center text-lg">
                    {server.icon}
                  </div>
                  <div>
                    <h4 className="text-white font-medium">{server.name}</h4>
                    <div className="flex items-center space-x-2">
                      {server.connected ? (
                        <div className="flex items-center space-x-1 text-green-500">
                          <CheckCircle className="w-4 h-4" />
                          <span className="text-sm">Connected</span>
                        </div>
                      ) : (
                        <div className="flex items-center space-x-1 text-red-500">
                          <AlertCircle className="w-4 h-4" />
                          <span className="text-sm">Disconnected</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <h5 className="text-white font-medium text-sm mb-2">Voice Channels</h5>
                {server.channels.map((channel) => (
                  <div key={channel.id} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Volume2 className="w-4 h-4 text-gray-400" />
                      <span className="text-white">{channel.name}</span>
                      <div className="flex items-center space-x-1 text-gray-400">
                        <Users className="w-3 h-3" />
                        <span className="text-xs">{channel.userCount}</span>
                      </div>
                      {channel.isStreaming && (
                        <div className="flex items-center space-x-1 text-red-500">
                          <Radio className="w-3 h-3" />
                          <span className="text-xs">Live</span>
                        </div>
                      )}
                    </div>
                    <button
                      onClick={() => setSelectedChannel(channel.id)}
                      className={`px-3 py-1 rounded-lg text-sm transition-all duration-200 ${
                        selectedChannel === channel.id
                          ? 'bg-purple-600 text-white'
                          : 'bg-white/10 text-gray-400 hover:bg-white/20 hover:text-white'
                      }`}
                    >
                      {selectedChannel === channel.id ? 'Selected' : 'Select'}
                    </button>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Stream Control */}
      {selectedChannel && (
        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6">
          <h3 className="text-xl font-semibold text-white mb-6 flex items-center space-x-2">
            <Radio className="w-5 h-5" />
            <span>Stream Control</span>
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            {/* Audio Settings */}
            <div className="space-y-4">
              <h4 className="text-white font-medium">Audio Settings</h4>
              <div>
                <label className="block text-gray-400 text-sm mb-2">Audio Quality</label>
                <select
                  value={audioQuality}
                  onChange={(e) => setAudioQuality(e.target.value)}
                  className="w-full bg-white/5 border border-white/20 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="low">Low (64kbps)</option>
                  <option value="medium">Medium (128kbps)</option>
                  <option value="high">High (320kbps)</option>
                </select>
              </div>
            </div>

            {/* Stream Status */}
            <div className="space-y-4">
              <h4 className="text-white font-medium">Current Status</h4>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Twitch</span>
                  <div className={`w-3 h-3 rounded-full ${streamingToTwitch ? 'bg-green-500 animate-pulse' : 'bg-gray-500'}`}></div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">YouTube</span>
                  <div className={`w-3 h-3 rounded-full ${streamingToYoutube ? 'bg-green-500 animate-pulse' : 'bg-gray-500'}`}></div>
                </div>
              </div>
            </div>
          </div>

          {/* Stream Controls */}
          <div className="flex flex-wrap gap-4">
            <button
              onClick={() => startStreaming('both')}
              disabled={streamingToTwitch && streamingToYoutube}
              className="flex items-center space-x-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-6 py-3 rounded-lg font-medium transition-all duration-200"
            >
              <Play className="w-4 h-4" />
              <span>Start Multi-Stream</span>
            </button>

            <button
              onClick={() => startStreaming('twitch')}
              disabled={streamingToTwitch}
              className="flex items-center space-x-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-6 py-3 rounded-lg font-medium transition-all duration-200"
            >
              <Play className="w-4 h-4" />
              <span>Twitch Only</span>
            </button>

            <button
              onClick={() => startStreaming('youtube')}
              disabled={streamingToYoutube}
              className="flex items-center space-x-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-6 py-3 rounded-lg font-medium transition-all duration-200"
            >
              <Play className="w-4 h-4" />
              <span>YouTube Only</span>
            </button>

            <button
              onClick={stopStreaming}
              disabled={!streamingToTwitch && !streamingToYoutube}
              className="flex items-center space-x-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-6 py-3 rounded-lg font-medium transition-all duration-200"
            >
              <Square className="w-4 h-4" />
              <span>Stop All Streams</span>
            </button>
          </div>
        </div>
      )}

      {/* Live Transcription */}
      <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6">
        <h3 className="text-xl font-semibold text-white mb-6 flex items-center space-x-2">
          <Mic className="w-5 h-5" />
          <span>Live Transcription</span>
        </h3>

        <div className="bg-black/20 border border-white/10 rounded-lg p-4 h-32 overflow-y-auto">
          <div className="space-y-2 text-sm">
            <div className="text-blue-400">[12:34] User1: Salut tout le monde!</div>
            <div className="text-green-400">[12:35] User2: Comment ça va?</div>
            <div className="text-purple-400">[12:36] User3: On commence le stream?</div>
            <div className="text-gray-400">[12:37] System: Transcription active...</div>
          </div>
        </div>

        <div className="flex items-center justify-between mt-4">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-green-400 text-sm">Live transcription active</span>
          </div>
          <button className="bg-white/10 hover:bg-white/20 border border-white/20 text-white px-4 py-2 rounded-lg transition-all duration-200">
            Export Transcript
          </button>
        </div>
      </div>

      {/* Bot Setup Instructions */}
      <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6">
        <h3 className="text-xl font-semibold text-white mb-6 flex items-center space-x-2">
          <Link className="w-5 h-5" />
          <span>Bot Setup Instructions</span>
        </h3>

        <div className="space-y-4">
          <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
            <h4 className="text-blue-400 font-medium mb-2">Step 1: Invite Bot to Server</h4>
            <p className="text-gray-300 text-sm mb-3">Add the streaming bot to your Discord server with the necessary permissions.</p>
            <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm transition-all duration-200">
              Invite Bot
            </button>
          </div>

          <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
            <h4 className="text-green-400 font-medium mb-2">Step 2: Configure Permissions</h4>
            <p className="text-gray-300 text-sm">Ensure the bot has permissions to:</p>
            <ul className="text-gray-400 text-sm mt-2 space-y-1">
              <li>• Connect to voice channels</li>
              <li>• Use voice activity</li>
              <li>• Send messages</li>
              <li>• Manage webhooks</li>
            </ul>
          </div>

          <div className="bg-purple-500/10 border border-purple-500/20 rounded-lg p-4">
            <h4 className="text-purple-400 font-medium mb-2">Step 3: Link Streaming Accounts</h4>
            <p className="text-gray-300 text-sm">Connect your Twitch and YouTube accounts in the Settings section.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DiscordIntegration;