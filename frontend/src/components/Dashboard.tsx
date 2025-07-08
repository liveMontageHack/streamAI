import React, { useState } from 'react';
import { 
  Play, 
  Square, 
  Settings, 
  Mic, 
  Video, 
  Users, 
  Activity, 
  Bell,
  Twitch,
  Youtube,
  MessageCircle,
  BarChart3,
  Zap,
  Radio,
  Pause,
  Edit3,
  Hash,
  Type,
  ChevronDown,
  Plus,
  X,
  Check,
  AlertTriangle
} from 'lucide-react';
import { useAppMode } from '../hooks/useAppMode';

const Dashboard: React.FC = () => {
  const { apiUrl, isDemo, features } = useAppMode();
  const [twitchEnabled, setTwitchEnabled] = useState(true);
  const [youtubeEnabled, setYoutubeEnabled] = useState(false);
  const [discordEnabled, setDiscordEnabled] = useState(true);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [transcriptionEnabled, setTranscriptionEnabled] = useState(true);
  
  // Stream preparation fields
  const [streamTitle, setStreamTitle] = useState('');
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [showCategoryDropdown, setShowCategoryDropdown] = useState(false);
  const [newCategoryInput, setNewCategoryInput] = useState('');
  const [isAddingCategory, setIsAddingCategory] = useState(false);

  const [defaultCategories] = useState([
    'Gaming', 'Just Chatting', 'Music', 'Art', 'Programming', 'Education', 
    'Sports', 'Travel & Outdoors', 'Food & Drink', 'Science & Technology',
    'Politics', 'ASMR', 'Fitness & Health', 'Beauty & Makeup'
  ]);

  const [customCategories, setCustomCategories] = useState<string[]>([]);

  const allCategories = [...defaultCategories, ...customCategories];

  const handleStartStream = () => {
    if (!twitchEnabled && !youtubeEnabled && !discordEnabled) {
      alert('Please enable at least one platform to start streaming');
      return;
    }
    if (!streamTitle.trim()) {
      alert('Please enter a stream title');
      return;
    }
    setIsStreaming(!isStreaming);
  };

  const handleStartRecord = async () => {
    if (!streamTitle.trim()) {
      alert('Please enter a stream title before starting recording');
      return;
    }

    // Demo mode limitation
    if (isDemo) {
      alert('🚀 Mode Démo: L\'enregistrement réel n\'est pas disponible. Installez la version locale pour cette fonctionnalité.');
      return;
    }

    try {
      if (isRecording) {
        // Stop recording
        const response = await fetch(`${apiUrl}/api/recording/stop`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        const result = await response.json();
        
        if (result.success) {
          setIsRecording(false);
          console.log('Recording stopped successfully');
        } else {
          console.error('Failed to stop recording:', result.message);
          alert('Failed to stop recording: ' + result.message);
        }
      } else {
        // Start recording with stream title as session name
        const response = await fetch(`${apiUrl}/api/recording/start`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            sessionName: streamTitle.trim()
          }),
        });

        const result = await response.json();
        
        if (result.success) {
          setIsRecording(true);
          console.log('Recording started successfully with session:', streamTitle);
        } else {
          console.error('Failed to start recording:', result.message);
          alert('Failed to start recording: ' + result.message);
        }
      }
    } catch (error) {
      console.error('Error communicating with API:', error);
      if (isDemo) {
        alert('🚀 Mode Démo: Impossible de se connecter au serveur local. Cette fonctionnalité nécessite l\'installation locale.');
      } else {
        alert('Error: Could not connect to StreamAI API server. Make sure it\'s running on port 5001.');
      }
    }
  };

  const getEnabledPlatforms = () => {
    const platforms = [];
    if (twitchEnabled) platforms.push('Twitch');
    if (youtubeEnabled) platforms.push('YouTube');
    if (discordEnabled) platforms.push('Discord');
    return platforms;
  };

  const handleCategoryToggle = (category: string) => {
    setSelectedCategories(prev => 
      prev.includes(category) 
        ? prev.filter(c => c !== category)
        : [...prev, category]
    );
  };

  const handleAddCustomCategory = () => {
    if (newCategoryInput.trim() && !allCategories.includes(newCategoryInput.trim())) {
      const newCategory = newCategoryInput.trim();
      setCustomCategories(prev => [...prev, newCategory]);
      setSelectedCategories(prev => [...prev, newCategory]);
      setNewCategoryInput('');
      setIsAddingCategory(false);
    }
  };

  const handleDeleteCategory = (categoryToDelete: string) => {
    // Remove from custom categories if it's a custom one
    if (customCategories.includes(categoryToDelete)) {
      setCustomCategories(prev => prev.filter(c => c !== categoryToDelete));
    }
    // Remove from selected categories
    setSelectedCategories(prev => prev.filter(c => c !== categoryToDelete));
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleAddCustomCategory();
    } else if (e.key === 'Escape') {
      setIsAddingCategory(false);
      setNewCategoryInput('');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-blue-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2 flex items-center space-x-3">
              <Zap className="w-10 h-10 text-purple-400" />
              <span>StreamAI</span>
            </h1>
            <p className="text-gray-300">AI-Powered Discord Multi-Platform Streaming</p>
          </div>
          <div className="flex items-center space-x-4">
            <button className="bg-white/10 backdrop-blur-md border border-white/20 text-white px-4 py-2 rounded-lg hover:bg-white/20 transition-all duration-200 flex items-center space-x-2">
              <Bell className="w-4 h-4" />
              <span>Notifications</span>
            </button>
            <button className="bg-white/10 backdrop-blur-md border border-white/20 text-white px-4 py-2 rounded-lg hover:bg-white/20 transition-all duration-200 flex items-center space-x-2">
              <Settings className="w-4 h-4" />
              <span>Settings</span>
            </button>
          </div>
        </div>

        {/* Stream Preparation */}
        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-8 mb-8">
          <h2 className="text-2xl font-semibold text-white mb-6 flex items-center space-x-2">
            <Edit3 className="w-6 h-6" />
            <span>Stream Preparation</span>
          </h2>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Stream Title */}
            <div className="space-y-2">
              <label className="block text-white font-medium flex items-center space-x-2">
                <Type className="w-4 h-4" />
                <span>Stream Title</span>
              </label>
              <input
                type="text"
                value={streamTitle}
                onChange={(e) => setStreamTitle(e.target.value)}
                placeholder="Enter your stream title..."
                className="w-full bg-white/5 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200"
              />
              <p className="text-gray-400 text-sm">This will be used across all enabled platforms</p>
            </div>

            {/* Enhanced Category Selection */}
            <div className="space-y-2">
              <label className="block text-white font-medium flex items-center space-x-2">
                <Hash className="w-4 h-4" />
                <span>Categories</span>
              </label>
              
              {/* Selected Categories Display */}
              {selectedCategories.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-2">
                  {selectedCategories.map((category) => (
                    <div key={category} className="bg-purple-600/20 text-purple-400 px-3 py-1 rounded-full text-sm flex items-center space-x-2 group">
                      <span>{category}</span>
                      <button
                        onClick={() => handleDeleteCategory(category)}
                        className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 hover:text-red-400"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </div>
                  ))}
                </div>
              )}

              <div className="relative">
                <button
                  onClick={() => setShowCategoryDropdown(!showCategoryDropdown)}
                  className="w-full bg-white/5 border border-white/20 rounded-lg px-4 py-3 text-left text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200 flex items-center justify-between"
                >
                  <span className={selectedCategories.length > 0 ? 'text-white' : 'text-gray-400'}>
                    {selectedCategories.length > 0 
                      ? `${selectedCategories.length} categor${selectedCategories.length > 1 ? 'ies' : 'y'} selected`
                      : 'Select categories...'}
                  </span>
                  <ChevronDown className={`w-4 h-4 transition-transform duration-200 ${showCategoryDropdown ? 'rotate-180' : ''}`} />
                </button>
                
                {showCategoryDropdown && (
                  <div className="absolute top-full left-0 right-0 mt-2 bg-gray-800/95 backdrop-blur-md border border-white/20 rounded-lg shadow-xl z-[9999] max-h-80 overflow-y-auto">
                    {/* Add Custom Category Section */}
                    <div className="p-3 border-b border-white/10">
                      {isAddingCategory ? (
                        <div className="flex items-center space-x-2">
                          <input
                            type="text"
                            value={newCategoryInput}
                            onChange={(e) => setNewCategoryInput(e.target.value)}
                            onKeyDown={handleKeyPress}
                            placeholder="Enter new category..."
                            className="flex-1 bg-white/10 border border-white/20 rounded px-3 py-2 text-white text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
                            autoFocus
                          />
                          <button
                            onClick={handleAddCustomCategory}
                            className="bg-green-600 hover:bg-green-700 text-white p-2 rounded transition-all duration-200"
                          >
                            <Check className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => {
                              setIsAddingCategory(false);
                              setNewCategoryInput('');
                            }}
                            className="bg-gray-600 hover:bg-gray-700 text-white p-2 rounded transition-all duration-200"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => setIsAddingCategory(true)}
                          className="w-full flex items-center space-x-2 px-3 py-2 text-purple-400 hover:bg-white/10 rounded transition-all duration-200"
                        >
                          <Plus className="w-4 h-4" />
                          <span className="text-sm">Add custom category</span>
                        </button>
                      )}
                    </div>

                    {/* Default Categories */}
                    {defaultCategories.length > 0 && (
                      <div>
                        <div className="px-3 py-2 text-xs text-gray-400 font-medium uppercase tracking-wider">
                          Default Categories
                        </div>
                        {defaultCategories.map((category) => (
                          <button
                            key={category}
                            onClick={() => handleCategoryToggle(category)}
                            className={`w-full px-4 py-3 text-left transition-all duration-200 flex items-center justify-between ${
                              selectedCategories.includes(category)
                                ? 'bg-purple-600/20 text-purple-400'
                                : 'text-white hover:bg-white/10'
                            }`}
                          >
                            <span>{category}</span>
                            {selectedCategories.includes(category) && (
                              <Check className="w-4 h-4" />
                            )}
                          </button>
                        ))}
                      </div>
                    )}

                    {/* Custom Categories */}
                    {customCategories.length > 0 && (
                      <div>
                        <div className="px-3 py-2 text-xs text-gray-400 font-medium uppercase tracking-wider border-t border-white/10">
                          Custom Categories
                        </div>
                        {customCategories.map((category) => (
                          <div
                            key={category}
                            className={`flex items-center justify-between px-4 py-3 transition-all duration-200 group ${
                              selectedCategories.includes(category)
                                ? 'bg-purple-600/20 text-purple-400'
                                : 'text-white hover:bg-white/10'
                            }`}
                          >
                            <button
                              onClick={() => handleCategoryToggle(category)}
                              className="flex-1 text-left flex items-center justify-between"
                            >
                              <span>{category}</span>
                              {selectedCategories.includes(category) && (
                                <Check className="w-4 h-4" />
                              )}
                            </button>
                            <button
                              onClick={() => handleDeleteCategory(category)}
                              className="opacity-0 group-hover:opacity-100 ml-2 p-1 text-red-400 hover:text-red-300 transition-all duration-200"
                            >
                              <X className="w-3 h-3" />
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
              <p className="text-gray-400 text-sm">Select multiple categories or create custom ones</p>
            </div>
          </div>

          {/* Stream Preview */}
          {(streamTitle || selectedCategories.length > 0) && (
            <div className="mt-6 bg-white/5 border border-white/10 rounded-xl p-4">
              <h3 className="text-white font-medium mb-3">Stream Preview</h3>
              <div className="space-y-2">
                {streamTitle && (
                  <div className="flex items-center space-x-2">
                    <span className="text-gray-400 text-sm">Title:</span>
                    <span className="text-white font-medium">{streamTitle}</span>
                  </div>
                )}
                {selectedCategories.length > 0 && (
                  <div className="flex items-start space-x-2">
                    <span className="text-gray-400 text-sm mt-1">Categories:</span>
                    <div className="flex flex-wrap gap-1">
                      {selectedCategories.map((category) => (
                        <span key={category} className="bg-purple-600/20 text-purple-400 px-2 py-1 rounded-full text-sm">
                          {category}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                <div className="flex items-center space-x-2">
                  <span className="text-gray-400 text-sm">Platforms:</span>
                  <div className="flex space-x-1">
                    {getEnabledPlatforms().map((platform) => (
                      <span key={platform} className="bg-blue-600/20 text-blue-400 px-2 py-1 rounded-full text-xs">
                        {platform}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Platform Selection */}
        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-8 mb-8">
          <h2 className="text-2xl font-semibold text-white mb-6 flex items-center space-x-2">
            <Radio className="w-6 h-6" />
            <span>Platform Selection</span>
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Twitch Toggle */}
            <div className="bg-white/5 border border-white/10 rounded-xl p-6 hover:bg-white/10 transition-all duration-200">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 bg-purple-600 rounded-lg flex items-center justify-center">
                    <Twitch className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-white font-semibold">Twitch</h3>
                    <p className="text-gray-400 text-sm">Live streaming platform</p>
                  </div>
                </div>
                <button
                  onClick={() => setTwitchEnabled(!twitchEnabled)}
                  className={`relative inline-flex h-8 w-14 items-center rounded-full transition-colors focus:outline-none ${
                    twitchEnabled ? 'bg-purple-600' : 'bg-gray-600'
                  }`}
                >
                  <span
                    className={`inline-block h-6 w-6 transform rounded-full bg-white transition-transform ${
                      twitchEnabled ? 'translate-x-7' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>
              {twitchEnabled && (
                <div className="text-green-400 text-sm flex items-center space-x-1">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span>Ready to stream</span>
                </div>
              )}
            </div>

            {/* YouTube Toggle */}
            <div className="bg-white/5 border border-white/10 rounded-xl p-6 hover:bg-white/10 transition-all duration-200">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 bg-red-600 rounded-lg flex items-center justify-center">
                    <Youtube className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-white font-semibold">YouTube</h3>
                    <p className="text-gray-400 text-sm">Video platform</p>
                  </div>
                </div>
                <button
                  onClick={() => setYoutubeEnabled(!youtubeEnabled)}
                  className={`relative inline-flex h-8 w-14 items-center rounded-full transition-colors focus:outline-none ${
                    youtubeEnabled ? 'bg-red-600' : 'bg-gray-600'
                  }`}
                >
                  <span
                    className={`inline-block h-6 w-6 transform rounded-full bg-white transition-transform ${
                      youtubeEnabled ? 'translate-x-7' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>
              {youtubeEnabled && (
                <div className="text-green-400 text-sm flex items-center space-x-1">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span>Ready to stream</span>
                </div>
              )}
            </div>

            {/* Discord Toggle */}
            <div className="bg-white/5 border border-white/10 rounded-xl p-6 hover:bg-white/10 transition-all duration-200">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center">
                    <MessageCircle className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-white font-semibold">Discord</h3>
                    <p className="text-gray-400 text-sm">Voice chat platform</p>
                  </div>
                </div>
                <button
                  onClick={() => setDiscordEnabled(!discordEnabled)}
                  className={`relative inline-flex h-8 w-14 items-center rounded-full transition-colors focus:outline-none ${
                    discordEnabled ? 'bg-blue-600' : 'bg-gray-600'
                  }`}
                >
                  <span
                    className={`inline-block h-6 w-6 transform rounded-full bg-white transition-transform ${
                      discordEnabled ? 'translate-x-7' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>
              {discordEnabled && (
                <div className="text-green-400 text-sm flex items-center space-x-1">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span>Connected to voice channel</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Stream Control Center */}
        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-8 mb-8">
          <h2 className="text-2xl font-semibold text-white mb-6 flex items-center space-x-2">
            <Video className="w-6 h-6" />
            <span>Stream Control Center</span>
          </h2>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Stream Status */}
            <div className="space-y-6">
              <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                <h3 className="text-white font-medium mb-4">Current Status</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Stream Status</span>
                    <div className="flex items-center space-x-2">
                      <div className={`w-3 h-3 rounded-full ${isStreaming ? 'bg-green-500 animate-pulse' : 'bg-gray-500'}`}></div>
                      <span className="text-white">{isStreaming ? 'Live' : 'Offline'}</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Recording</span>
                    <div className="flex items-center space-x-2">
                      <div className={`w-3 h-3 rounded-full ${isRecording ? 'bg-red-500 animate-pulse' : 'bg-gray-500'}`}></div>
                      <span className="text-white">{isRecording ? 'Recording' : 'Stopped'}</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Active Platforms</span>
                    <span className="text-white">{getEnabledPlatforms().join(', ') || 'None'}</span>
                  </div>
                  {isStreaming && (
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Duration</span>
                      <span className="text-white">00:24:15</span>
                    </div>
                  )}
                </div>
              </div>

              {/* AI Transcription */}
              <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-white font-medium flex items-center space-x-2">
                    <Mic className="w-5 h-5" />
                    <span>AI Transcription</span>
                  </h3>
                  <button
                    onClick={() => setTranscriptionEnabled(!transcriptionEnabled)}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none ${
                      transcriptionEnabled ? 'bg-green-600' : 'bg-gray-600'
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        transcriptionEnabled ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>
                <p className="text-gray-400 text-sm">Real-time voice-to-text conversion with AI enhancement</p>
                {transcriptionEnabled && (
                  <div className="mt-3 text-green-400 text-sm flex items-center space-x-1">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <span>AI transcription active</span>
                  </div>
                )}
              </div>
            </div>

            {/* Control Buttons */}
            <div className="flex flex-col justify-center space-y-6">
              {/* Main Stream Button */}
              <button
                onClick={handleStartStream}
                disabled={(!twitchEnabled && !youtubeEnabled && !discordEnabled) || !streamTitle.trim()}
                className={`w-full py-8 px-8 rounded-2xl font-bold text-2xl transition-all duration-300 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center space-x-4 ${
                  isStreaming
                    ? 'bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white shadow-lg shadow-red-500/25'
                    : 'bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white shadow-lg shadow-green-500/25'
                }`}
              >
                {isStreaming ? (
                  <>
                    <Square className="w-8 h-8" />
                    <span>Stop Stream</span>
                  </>
                ) : (
                  <>
                    <Play className="w-8 h-8" />
                    <span>Start Stream</span>
                  </>
                )}
              </button>

              {/* Record Button */}
              <button
                onClick={handleStartRecord}
                className={`w-full py-6 px-6 rounded-xl font-semibold text-lg transition-all duration-300 transform hover:scale-105 flex items-center justify-center space-x-3 ${
                  isRecording
                    ? 'bg-gradient-to-r from-red-600 to-pink-600 hover:from-red-700 hover:to-pink-700 text-white shadow-lg shadow-red-500/25'
                    : 'bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white shadow-lg shadow-purple-500/25'
                }`}
              >
                {isRecording ? (
                  <>
                    <Pause className="w-6 h-6" />
                    <span>Stop Recording</span>
                  </>
                ) : (
                  <>
                    <Radio className="w-6 h-6" />
                    <span>Start Recording</span>
                  </>
                )}
              </button>

              {/* Platform Info */}
              <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                <h4 className="text-white font-medium mb-2">Enabled Platforms</h4>
                <div className="flex flex-wrap gap-2">
                  {twitchEnabled && (
                    <span className="bg-purple-600/20 text-purple-400 px-3 py-1 rounded-full text-sm">Twitch</span>
                  )}
                  {youtubeEnabled && (
                    <span className="bg-red-600/20 text-red-400 px-3 py-1 rounded-full text-sm">YouTube</span>
                  )}
                  {discordEnabled && (
                    <span className="bg-blue-600/20 text-blue-400 px-3 py-1 rounded-full text-sm">Discord</span>
                  )}
                  {!twitchEnabled && !youtubeEnabled && !discordEnabled && (
                    <span className="bg-gray-600/20 text-gray-400 px-3 py-1 rounded-full text-sm">No platforms enabled</span>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-xl p-6">
            <div className="flex items-center space-x-3 mb-2">
              <Users className="w-5 h-5 text-blue-400" />
              <span className="text-gray-400 text-sm">Total Viewers</span>
            </div>
            <div className="text-2xl font-bold text-white">2,139</div>
            <div className="text-green-400 text-sm">+12% from last stream</div>
          </div>

          <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-xl p-6">
            <div className="flex items-center space-x-3 mb-2">
              <MessageCircle className="w-5 h-5 text-green-400" />
              <span className="text-gray-400 text-sm">Chat Messages</span>
            </div>
            <div className="text-2xl font-bold text-white">1,582</div>
            <div className="text-green-400 text-sm">+8% engagement</div>
          </div>

          <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-xl p-6">
            <div className="flex items-center space-x-3 mb-2">
              <BarChart3 className="w-5 h-5 text-purple-400" />
              <span className="text-gray-400 text-sm">Stream Quality</span>
            </div>
            <div className="text-2xl font-bold text-white">1080p</div>
            <div className="text-blue-400 text-sm">60 FPS</div>
          </div>

          <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-xl p-6">
            <div className="flex items-center space-x-3 mb-2">
              <Activity className="w-5 h-5 text-orange-400" />
              <span className="text-gray-400 text-sm">Uptime</span>
            </div>
            <div className="text-2xl font-bold text-white">99.8%</div>
            <div className="text-green-400 text-sm">Excellent</div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6">
          <h3 className="text-xl font-semibold text-white mb-6 flex items-center space-x-2">
            <Activity className="w-5 h-5" />
            <span>Recent Activity</span>
          </h3>
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-white text-sm">StreamAI bot connected to Discord</span>
              <span className="text-gray-400 text-xs ml-auto">2m ago</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span className="text-white text-sm">AI transcription model loaded</span>
              <span className="text-gray-400 text-xs ml-auto">5m ago</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
              <span className="text-white text-sm">Twitch stream key validated</span>
              <span className="text-gray-400 text-xs ml-auto">12m ago</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
              <span className="text-white text-sm">Platform connections verified</span>
              <span className="text-gray-400 text-xs ml-auto">1h ago</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
