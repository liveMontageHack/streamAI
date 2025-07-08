import React, { useState, useEffect } from 'react';
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
  Settings as SettingsIcon
} from 'lucide-react';
import { useSettings } from '../contexts/SettingsContext';

const Settings: React.FC = () => {
  const { settings, updateSettings, saveSettings: contextSaveSettings } = useSettings();
  const [twitchConnected, setTwitchConnected] = useState(true);
  const [youtubeConnected, setYoutubeConnected] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [isValidating, setIsValidating] = useState(false);
  const [validationStatus, setValidationStatus] = useState<'idle' | 'valid' | 'invalid' | 'error'>('idle');

  // Load settings on component mount
  useEffect(() => {
    // Settings are automatically loaded by the context
  }, []);

  const validateGroqApiKey = async () => {
    if (!settings.groqApiKey.trim()) {
      setValidationStatus('error');
      setTimeout(() => setValidationStatus('idle'), 3000);
      return;
    }

    setIsValidating(true);
    setValidationStatus('idle');
    
    try {
      // Use the dedicated validation endpoint
      const response = await fetch('/api/transcription/validate-key', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          api_key: settings.groqApiKey
        }),
      });

      console.log('Validation response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('Validation response data:', data);
        
        if (data.success && data.valid) {
          setValidationStatus('valid');
        } else if (data.success && !data.valid) {
          setValidationStatus('invalid');
        } else {
          setValidationStatus('error');
        }
      } else {
        console.error('Validation request failed:', response.status, response.statusText);
        setValidationStatus('error');
      }
      
      setTimeout(() => setValidationStatus('idle'), 5000);
    } catch (error) {
      console.error('Failed to validate API key:', error);
      setValidationStatus('error');
      setTimeout(() => setValidationStatus('idle'), 3000);
    } finally {
      setIsValidating(false);
    }
  };

  const removeApiKey = async () => {
    setIsSaving(true);
    setSaveStatus('idle');
    
    try {
      updateSettings({ groqApiKey: '' });
      const success = await contextSaveSettings();
      
      if (success) {
        setSaveStatus('success');
        setValidationStatus('idle');
        setTimeout(() => setSaveStatus('idle'), 3000);
      } else {
        setSaveStatus('error');
        setTimeout(() => setSaveStatus('idle'), 3000);
      }
    } catch (error) {
      console.error('Failed to remove API key:', error);
      setSaveStatus('error');
      setTimeout(() => setSaveStatus('idle'), 3000);
    } finally {
      setIsSaving(false);
    }
  };

  const saveSettings = async () => {
    setIsSaving(true);
    setSaveStatus('idle');
    
    try {
      const success = await contextSaveSettings();
      
      if (success) {
        setSaveStatus('success');
        setTimeout(() => setSaveStatus('idle'), 3000);
      } else {
        setSaveStatus('error');
        setTimeout(() => setSaveStatus('idle'), 3000);
      }
    } catch (error) {
      console.error('Failed to save settings:', error);
      setSaveStatus('error');
      setTimeout(() => setSaveStatus('idle'), 3000);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold text-white mb-2">Settings</h2>
        <p className="text-gray-400">Configure your streaming and Discord bot settings</p>
      </div>

      {/* API Keys Section */}
      <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6">
        <h3 className="text-xl font-semibold text-white mb-6 flex items-center space-x-2">
          <SettingsIcon className="w-5 h-5" />
          <span>API Keys</span>
        </h3>
        
        <div className="space-y-6">
          <div>
            <label className="block text-white font-medium mb-2">Groq API Key</label>
            <div className="space-y-3">
              <div className="relative">
                <input
                  type="password"
                  value={settings.groqApiKey}
                  onChange={(e) => updateSettings({ groqApiKey: e.target.value })}
                  className="w-full bg-white/5 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="Enter your Groq API key for transcription refinement"
                />
                <Key className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              </div>
              
              {/* Validation Button */}
              <div className="flex items-center space-x-3">
                <button
                  onClick={validateGroqApiKey}
                  disabled={isValidating || !settings.groqApiKey.trim()}
                  className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                    validationStatus === 'valid'
                      ? 'bg-green-600 hover:bg-green-700 text-white'
                      : validationStatus === 'invalid'
                      ? 'bg-red-600 hover:bg-red-700 text-white'
                      : validationStatus === 'error'
                      ? 'bg-yellow-600 hover:bg-yellow-700 text-white'
                      : isValidating
                      ? 'bg-gray-600 cursor-not-allowed text-gray-300'
                      : 'bg-blue-600 hover:bg-blue-700 text-white disabled:bg-gray-600 disabled:cursor-not-allowed disabled:text-gray-300'
                  }`}
                >
                  {isValidating ? 'Validating...' : 
                   validationStatus === 'valid' ? '✅ Valid' :
                   validationStatus === 'invalid' ? '❌ Invalid' :
                   validationStatus === 'error' ? '⚠️ Error' :
                   'Validate Key'}
                </button>
                
                {/* Remove API Key Button - only show when we have a stored key */}
                {settings.groqApiKey && (
                  <button
                    onClick={removeApiKey}
                    className="px-4 py-2 rounded-lg font-medium text-red-400 border border-red-400/50 hover:bg-red-400/10 transition-all duration-200"
                  >
                    Remove Key
                  </button>
                )}
                
                {validationStatus === 'valid' && (
                  <span className="text-green-400 text-sm">API key is working correctly!</span>
                )}
                {validationStatus === 'invalid' && (
                  <span className="text-red-400 text-sm">Invalid API key. Please check your key.</span>
                )}
                {validationStatus === 'error' && (
                  <span className="text-yellow-400 text-sm">Error validating. Please try again.</span>
                )}
              </div>
            </div>
            
            <p className="text-gray-400 text-xs mt-2">
              Required for AI-powered transcription refinement. Get your key from{' '}
              <a 
                href="https://console.groq.com" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-purple-400 hover:text-purple-300 underline"
              >
                console.groq.com
              </a>
              {settings.groqApiKey && (
                <span className="block mt-1 text-green-400">
                  ✓ API key is currently saved and ready to use
                </span>
              )}
            </p>
          </div>
        </div>
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
                value={settings.webhookUrl}
                onChange={(e) => updateSettings({ webhookUrl: e.target.value })}
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
              onClick={() => updateSettings({ autoNotifications: !settings.autoNotifications })}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none ${
                settings.autoNotifications ? 'bg-green-600' : 'bg-gray-600'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  settings.autoNotifications ? 'translate-x-6' : 'translate-x-1'
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
              value={settings.transcriptionLanguage}
              onChange={(e) => updateSettings({ transcriptionLanguage: e.target.value })}
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
        <button 
          onClick={saveSettings}
          disabled={isSaving}
          className={`bg-gradient-to-r font-medium py-3 px-8 rounded-lg transition-all duration-200 ${
            saveStatus === 'success' 
              ? 'from-green-600 to-green-700 text-white'
              : saveStatus === 'error'
              ? 'from-red-600 to-red-700 text-white'
              : isSaving
              ? 'from-gray-600 to-gray-700 text-gray-300 cursor-not-allowed'
              : 'from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white'
          }`}
        >
          {isSaving ? 'Saving...' : saveStatus === 'success' ? 'Saved!' : saveStatus === 'error' ? 'Error!' : 'Save Settings'}
        </button>
      </div>
    </div>
  );
};

export default Settings;