import React, { useState } from 'react';
import { 
  Twitch, 
  Youtube, 
  Key, 
  Webhook, 
  Bell, 
  Mic, 
  Shield,
  Link,
  Check,
  X
} from 'lucide-react';

const Settings: React.FC = () => {
  const [twitchConnected, setTwitchConnected] = useState(true);
  const [youtubeConnected, setYoutubeConnected] = useState(false);
  const [webhookUrl, setWebhookUrl] = useState('https://discord.com/api/webhooks/...');
  const [autoNotifications, setAutoNotifications] = useState(true);
  const [transcriptionLanguage, setTranscriptionLanguage] = useState('en');

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold text-white mb-2">Settings</h2>
        <p className="text-gray-400">Configure your streaming and Discord bot settings</p>
      </div>

      {/* Platform Connections */}
      <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6">
        <h3 className="text-xl font-semibold text-white mb-6 flex items-center space-x-2">
          <Link className="w-5 h-5" />
          <span>Platform Connections</span>
        </h3>
        
        <div className="space-y-6">
          {/* Twitch Connection */}
          <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg border border-white/10">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-purple-600 rounded-lg flex items-center justify-center">
                <Twitch className="w-6 h-6 text-white" />
              </div>
              <div>
                <h4 className="text-white font-medium">Twitch</h4>
                <p className="text-gray-400 text-sm">
                  {twitchConnected ? 'Connected as streamername' : 'Not connected'}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              {twitchConnected && (
                <div className="flex items-center space-x-1 text-green-500">
                  <Check className="w-4 h-4" />
                  <span className="text-sm">Connected</span>
                </div>
              )}
              <button
                onClick={() => setTwitchConnected(!twitchConnected)}
                className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                  twitchConnected
                    ? 'bg-red-600 hover:bg-red-700 text-white'
                    : 'bg-purple-600 hover:bg-purple-700 text-white'
                }`}
              >
                {twitchConnected ? 'Disconnect' : 'Connect'}
              </button>
            </div>
          </div>

          {/* YouTube Connection */}
          <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg border border-white/10">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-red-600 rounded-lg flex items-center justify-center">
                <Youtube className="w-6 h-6 text-white" />
              </div>
              <div>
                <h4 className="text-white font-medium">YouTube</h4>
                <p className="text-gray-400 text-sm">
                  {youtubeConnected ? 'Connected as channelname' : 'Not connected'}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              {youtubeConnected && (
                <div className="flex items-center space-x-1 text-green-500">
                  <Check className="w-4 h-4" />
                  <span className="text-sm">Connected</span>
                </div>
              )}
              <button
                onClick={() => setYoutubeConnected(!youtubeConnected)}
                className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                  youtubeConnected
                    ? 'bg-red-600 hover:bg-red-700 text-white'
                    : 'bg-red-600 hover:bg-red-700 text-white'
                }`}
              >
                {youtubeConnected ? 'Disconnect' : 'Connect'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Discord Bot Settings */}
      <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6">
        <h3 className="text-xl font-semibold text-white mb-6 flex items-center space-x-2">
          <Shield className="w-5 h-5" />
          <span>Discord Bot Configuration</span>
        </h3>
        
        <div className="space-y-6">
          <div>
            <label className="block text-white font-medium mb-2">Bot Token</label>
            <div className="relative">
              <input
                type="password"
                className="w-full bg-white/5 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="Your Discord bot token"
                defaultValue="••••••••••••••••••••••••••••••••••••••••"
              />
              <Key className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            </div>
          </div>

          <div>
            <label className="block text-white font-medium mb-2">Webhook URL</label>
            <div className="relative">
              <input
                type="url"
                value={webhookUrl}
                onChange={(e) => setWebhookUrl(e.target.value)}
                className="w-full bg-white/5 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="Discord webhook URL for notifications"
              />
              <Webhook className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            </div>
          </div>
        </div>
      </div>

      {/* Notification Settings */}
      <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6">
        <h3 className="text-xl font-semibold text-white mb-6 flex items-center space-x-2">
          <Bell className="w-5 h-5" />
          <span>Notification Settings</span>
        </h3>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="text-white font-medium">Auto Stream Notifications</h4>
              <p className="text-gray-400 text-sm">Automatically notify Discord when stream starts</p>
            </div>
            <button
              onClick={() => setAutoNotifications(!autoNotifications)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none ${
                autoNotifications ? 'bg-green-600' : 'bg-gray-600'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  autoNotifications ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        </div>
      </div>

      {/* Transcription Settings */}
      <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6">
        <h3 className="text-xl font-semibold text-white mb-6 flex items-center space-x-2">
          <Mic className="w-5 h-5" />
          <span>Transcription Settings</span>
        </h3>
        
        <div className="space-y-6">
          <div>
            <label className="block text-white font-medium mb-2">Language</label>
            <select
              value={transcriptionLanguage}
              onChange={(e) => setTranscriptionLanguage(e.target.value)}
              className="w-full bg-white/5 border border-white/20 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="en">English</option>
              <option value="es">Spanish</option>
              <option value="fr">French</option>
              <option value="de">German</option>
              <option value="it">Italian</option>
              <option value="pt">Portuguese</option>
              <option value="ru">Russian</option>
              <option value="ja">Japanese</option>
              <option value="ko">Korean</option>
              <option value="zh">Chinese</option>
            </select>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-white/5 border border-white/10 rounded-lg p-4">
              <h4 className="text-white font-medium mb-2">Voice Chat Transcription</h4>
              <p className="text-gray-400 text-sm mb-3">Transcribe Discord voice channels</p>
              <button className="w-full py-2 px-4 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-all duration-200">
                Enable
              </button>
            </div>
            <div className="bg-white/5 border border-white/10 rounded-lg p-4">
              <h4 className="text-white font-medium mb-2">Stream Audio Transcription</h4>
              <p className="text-gray-400 text-sm mb-3">Transcribe stream audio content</p>
              <button className="w-full py-2 px-4 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-all duration-200">
                Enable
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end">
        <button className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-medium py-3 px-8 rounded-lg transition-all duration-200">
          Save Settings
        </button>
      </div>
    </div>
  );
};

export default Settings;