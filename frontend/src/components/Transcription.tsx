import React, { useState, useEffect } from 'react';
import { RefreshCw, Save, Mic, MicOff, User, Bot, Trash2, Download } from 'lucide-react';

interface Message {
  id: string;
  type: 'raw' | 'refined';
  content: string;
  timestamp: Date;
}

interface TranscriptionProps {}

const Transcription: React.FC<TranscriptionProps> = () => {
  const [promptMessage, setPromptMessage] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isRefining, setIsRefining] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [renderError, setRenderError] = useState<string | null>(null);

  const API_BASE_URL = 'http://localhost:5001'; // Adjust this to your API server URL

  // Error boundary-like error handling
  const handleError = (error: Error, context: string) => {
    console.error(`[ERROR] ${context}:`, error);
    setRenderError(`Error in ${context}: ${error.message}`);
  };

  // Load saved prompt on component mount
  useEffect(() => {
    const initializeComponent = async () => {
      try {
        await loadSavedPrompt();
        await checkListeningStatus();
      } catch (error) {
        console.error('[DEBUG] Error during initialization:', error);
        handleError(error as Error, 'component initialization');
      }
    };
    
    initializeComponent();
    
    // Set up polling for new transcriptions - always poll, not just when listening
    const interval = setInterval(pollForTranscriptions, 1000);
    return () => clearInterval(interval);
  }, []);

  // Set a default prompt if none is loaded
  const setDefaultPrompt = () => {
    const defaultPrompt = "You are a transcription editor. Clean up this audio transcription by fixing grammar, spelling, and punctuation errors. Make the text more coherent and readable while preserving the original meaning. Respond ONLY with the corrected transcription text. Do not ask questions, add commentary, or provide explanations.";
    setPromptMessage(defaultPrompt);
  };

  const checkListeningStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/transcription/listening/status`);
      if (response.ok) {
        const data = await response.json();
        console.log('[DEBUG] Current listening status:', data);
        setIsListening(data.is_listening || false);
      }
    } catch (error) {
      console.error('[DEBUG] Error checking listening status:', error);
    }
  };

  const loadSavedPrompt = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/transcription/prompt`);
      if (response.ok) {
        const data = await response.json();
        setPromptMessage(data.prompt || '');
      }
    } catch (error) {
      console.error('Error loading saved prompt:', error);
    }
  };

  const pollForTranscriptions = async () => {
    // Always poll for transcriptions, add debug logging
    try {
      console.log('[DEBUG] Polling for transcriptions...');
      const response = await fetch(`${API_BASE_URL}/api/transcription/poll`);
      console.log('[DEBUG] Poll response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('[DEBUG] Poll response data:', data);
        
        if (data.transcription && typeof data.transcription === 'object') {
          // Handle structured message from API
          const message = data.transcription;
          console.log('[DEBUG] New structured transcription received:', message);
          
          if (message.content && message.content.trim()) {
            if (message.type === 'raw') {
              addRawMessage(message.content.trim());
            } else if (message.type === 'refined') {
              // Add refined message directly
              const refinedMessage: Message = {
                id: `refined_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
                type: 'refined',
                content: message.content.trim(),
                timestamp: new Date()
              };
              setMessages(prev => [...prev, refinedMessage]);
            }
          }
        } else if (data.transcription && typeof data.transcription === 'string' && data.transcription.trim()) {
          // Handle simple string transcription (legacy)
          console.log('[DEBUG] New simple transcription received:', data.transcription);
          addRawMessage(data.transcription.trim());
        } else {
          console.log('[DEBUG] No new transcription or empty transcription');
        }
      } else {
        console.error('[DEBUG] Poll failed with status:', response.status);
        // Don't log every 404 - it's normal when no transcription is available
        if (response.status !== 404) {
          const errorText = await response.text().catch(() => 'Unknown error');
          console.error('[DEBUG] Poll error details:', errorText);
        }
      }
    } catch (error) {
      console.error('[DEBUG] Error polling for transcriptions:', error);
      // Don't crash the app, just log the error
    }
  };

  const addRawMessage = (content: string) => {
    console.log('[DEBUG] Adding raw message:', content);
    
    try {
      const newMessage: Message = {
        id: `raw_${Date.now()}`,
        type: 'raw',
        content,
        timestamp: new Date()
      };
      
      setMessages(prev => {
        const updated = [...prev, newMessage];
        console.log('[DEBUG] Messages updated, count:', updated.length);
        return updated;
      });
      
      // Trigger refinement after a small delay to ensure state is updated
      if (promptMessage && promptMessage.trim()) {
        console.log('[DEBUG] Triggering refinement with prompt');
        setTimeout(() => {
          refineMessage(content).catch(error => {
            console.error('[DEBUG] Refinement failed:', error);
            handleError(error, 'refinement');
          });
        }, 200);
      } else {
        console.log('[DEBUG] No prompt available for auto-refinement');
      }
      
    } catch (error) {
      console.error('[DEBUG] Error in addRawMessage:', error);
      handleError(error as Error, 'adding raw message');
    }
  };

  const refineMessage = async (rawContent: string) => {
    if (!promptMessage.trim()) {
      console.log('[DEBUG] No prompt message available for refinement');
      return;
    }
    
    console.log('[DEBUG] Starting refinement process...');
    setIsRefining(true);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/transcription/refine`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          raw_text: rawContent,
          prompt: promptMessage.trim()
        }),
      });

      console.log('[DEBUG] Refinement response status:', response.status);

      if (response.ok) {
        const data = await response.json();
        console.log('[DEBUG] Refinement successful:', data.refined_text?.substring(0, 50) + '...');
        
        const refinedMessage: Message = {
          id: `refined_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          type: 'refined',
          content: data.refined_text || 'No refined text received',
          timestamp: new Date()
        };
        
        setMessages(prev => {
          console.log('[DEBUG] Adding refined message to', prev.length, 'existing messages');
          return [...prev, refinedMessage];
        });
      } else {
        const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
        console.error('[DEBUG] Refinement error:', errorData.error);
        
        // Check if it's a Groq capacity issue
        if (errorData.error && errorData.error.includes('over capacity')) {
          console.log('[DEBUG] Groq API is over capacity, skipping refinement for now');
          // Don't show error message for capacity issues - just skip refinement
          return;
        }
        
        const errorMessage: Message = {
          id: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          type: 'refined',
          content: `Refinement failed: ${errorData.error}`,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('[DEBUG] Error refining transcription:', error);
      
      // Check if it's a network timeout or capacity issue
      const errorStr = error instanceof Error ? error.message : 'Unknown error';
      if (errorStr.includes('over capacity') || errorStr.includes('503')) {
        console.log('[DEBUG] Groq API capacity issue detected, skipping refinement');
        return;
      }
      
      const errorMessage: Message = {
        id: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        type: 'refined',
        content: `Refinement error: ${errorStr}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      console.log('[DEBUG] Refinement process completed');
      setIsRefining(false);
    }
  };

  const savePrompt = async () => {
    if (!promptMessage.trim()) return;
    
    setIsSaving(true);
    setSaveStatus('idle');
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/transcription/prompt`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt: promptMessage }),
      });

      if (response.ok) {
        setSaveStatus('success');
        setTimeout(() => setSaveStatus('idle'), 2000);
      } else {
        setSaveStatus('error');
      }
    } catch (error) {
      console.error('Error saving prompt:', error);
      setSaveStatus('error');
    } finally {
      setIsSaving(false);
    }
  };

  const clearAllMessages = () => {
    setMessages([]);
  };

  const downloadTranscription = () => {
    if (messages.length === 0) return;
    
    const transcriptionText = messages.map(message => {
      const timeStr = message.timestamp.toLocaleString();
      const typeStr = message.type === 'raw' ? 'Raw Transcription' : 'Refined Transcription';
      return `[${timeStr}] ${typeStr}:\n${message.content}\n`;
    }).join('\n');
    
    const blob = new Blob([transcriptionText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `transcription-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };



  const toggleListening = async () => {
    const newListeningState = !isListening;
    
    try {
      const endpoint = newListeningState 
        ? '/api/transcription/listening/start' 
        : '/api/transcription/listening/stop';
      
      console.log(`[DEBUG] ${newListeningState ? 'Starting' : 'Stopping'} listening...`);
      
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('[DEBUG] Listening state changed:', data);
        setIsListening(newListeningState);
        
        if (newListeningState) {
          console.log('[DEBUG] Started real-time audio transcription');
        } else {
          console.log('[DEBUG] Stopped real-time audio transcription');
        }
      } else {
        console.error('[DEBUG] Failed to change listening state:', response.status);
        const errorData = await response.json();
        console.error('[DEBUG] Error details:', errorData);
      }
    } catch (error) {
      console.error('[DEBUG] Error toggling listening state:', error);
    }
  };

  const getSaveButtonColor = () => {
    switch (saveStatus) {
      case 'success':
        return 'bg-green-600 hover:bg-green-700';
      case 'error':
        return 'bg-red-600 hover:bg-red-700';
      default:
        return 'bg-blue-600 hover:bg-blue-700';
    }
  };

  const getSaveButtonText = () => {
    if (isSaving) return 'Saving...';
    switch (saveStatus) {
      case 'success':
        return 'Saved!';
      case 'error':
        return 'Error';
      default:
        return 'Save Prompt';
    }
  };

  const formatTime = (date: Date) => {
    try {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch (error) {
      console.error('[DEBUG] Error formatting time:', error);
      return 'Unknown time';
    }
  };

  // Add debugging for re-renders
  console.log('[DEBUG] Transcription component render - messages count:', messages.length, 'isListening:', isListening);

  return (
    <div className="space-y-6">
      {renderError && (
        <div className="bg-red-600/20 border border-red-500/30 rounded-lg p-4 mb-4">
          <h3 className="text-red-400 font-semibold mb-2">Error Detected</h3>
          <p className="text-red-300 text-sm">{renderError}</p>
          <button 
            onClick={() => setRenderError(null)}
            className="mt-2 px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-white text-sm"
          >
            Dismiss
          </button>
        </div>
      )}
      <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/20">
        <h2 className="text-2xl font-bold text-white mb-6">Real-time Transcription Chat</h2>
        
        {/* Prompt Message Field - Top Left */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <label htmlFor="promptMessage" className="block text-sm font-medium text-white">
              Refinement Prompt Message
            </label>
            <div className="flex gap-2">
              <button
                onClick={setDefaultPrompt}
                className="px-3 py-1 bg-purple-600 hover:bg-purple-700 rounded-md text-white text-sm font-medium transition-colors flex items-center gap-2"
              >
                Use Default
              </button>
              <button
                onClick={toggleListening}
                className={`px-3 py-1 rounded-md text-white text-sm font-medium transition-colors flex items-center gap-2 ${
                  isListening ? 'bg-red-600 hover:bg-red-700' : 'bg-gray-600 hover:bg-gray-700'
                }`}
              >
                {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                {isListening ? 'Stop Listening' : 'Start Listening'}
              </button>
              <button
                onClick={savePrompt}
                disabled={isSaving || !promptMessage.trim()}
                className={`px-3 py-1 rounded-md text-white text-sm font-medium transition-colors flex items-center gap-2 disabled:opacity-50 ${getSaveButtonColor()}`}
              >
                <Save className="w-4 h-4" />
                {getSaveButtonText()}
              </button>
            </div>
          </div>
          <textarea
            id="promptMessage"
            value={promptMessage}
            onChange={(e) => setPromptMessage(e.target.value)}
            className="w-full h-20 p-3 bg-white/5 border border-white/30 rounded-lg text-white placeholder-white/60 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            placeholder="Enter your refinement prompt here (e.g., 'Clean up this transcription, fix grammar and spelling errors, and make it more coherent. Provide only the corrected transcription without asking questions or adding commentary.')"
          />
          <p className="text-sm text-white/60 mt-1">
            This prompt will be used to refine raw transcriptions using LLaMA via Groq API. Be specific about wanting only the corrected transcription without questions or commentary.
          </p>
        </div>

        {/* Communication Bubbles */}
        <div className="bg-white/5 rounded-lg p-4 min-h-[400px] max-h-[600px] overflow-y-auto">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">Transcription Chat</h3>
            <div className="flex gap-2">
              <button
                onClick={downloadTranscription}
                disabled={messages.length === 0}
                className="px-3 py-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:opacity-50 rounded-md text-white text-sm font-medium transition-colors flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                Download
              </button>
              <button
                onClick={clearAllMessages}
                className="px-3 py-1 bg-gray-600 hover:bg-gray-700 rounded-md text-white text-sm font-medium transition-colors flex items-center gap-2"
              >
                <Trash2 className="w-4 h-4" />
                Clear All
              </button>
            </div>
          </div>
          
          {messages.length === 0 ? (
            <div className="text-center text-white/60 py-12">
              <Mic className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p className="text-lg">No messages yet</p>
              <p className="text-sm">Start listening to see transcriptions appear here</p>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.filter(Boolean).map((message) => {
                if (!message || !message.id || !message.content) {
                  console.warn('[DEBUG] Skipping invalid message:', message);
                  return null;
                }
                
                return (
                  <div
                    key={message.id}
                    className={`flex ${message.type === 'raw' ? 'justify-start' : 'justify-end'}`}
                  >
                    <div
                      className={`max-w-[70%] rounded-lg p-3 ${
                        message.type === 'raw'
                          ? 'bg-blue-600/20 border border-blue-500/30 text-blue-100'
                          : 'bg-purple-600/20 border border-purple-500/30 text-purple-100'
                      }`}
                    >
                      <div className="flex items-start gap-2">
                        <div className="flex-shrink-0 mt-1">
                          {message.type === 'raw' ? (
                            <User className="w-4 h-4" />
                          ) : (
                            <Bot className="w-4 h-4" />
                          )}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs font-medium opacity-80">
                              {message.type === 'raw' ? 'Me (Raw)' : 'LLaMA (Refined)'}
                            </span>
                            <span className="text-xs opacity-60">
                              {message.timestamp ? formatTime(message.timestamp) : 'Unknown time'}
                            </span>
                          </div>
                          <p className="text-sm leading-relaxed">{message.content}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
              
              
              {isRefining && (
                <div className="flex justify-end">
                  <div className="max-w-[70%] rounded-lg p-3 bg-purple-600/20 border border-purple-500/30 text-purple-100">
                    <div className="flex items-start gap-2">
                      <div className="flex-shrink-0 mt-1">
                        <Bot className="w-4 h-4" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs font-medium opacity-80">LLaMA (Refined)</span>
                          <RefreshCw className="w-3 h-3 animate-spin opacity-60" />
                        </div>
                        <p className="text-sm leading-relaxed opacity-60">Processing...</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Status and Instructions */}
        <div className="mt-6 space-y-4">
          <div className="flex items-center justify-between p-3 bg-gray-900/30 rounded-lg">
            <div className="flex items-center gap-3">
              <div className={`w-3 h-3 rounded-full ${isListening ? 'bg-red-500 animate-pulse' : 'bg-gray-500'}`}></div>
              <span className="text-sm text-white">
                {isListening ? 'Listening for audio...' : 'Audio capture stopped'}
              </span>
            </div>
            <div className="text-sm text-white/60">
              {messages.length} messages
            </div>
          </div>

          <div className="p-4 bg-blue-900/20 rounded-lg border border-blue-500/30">
            <h3 className="text-lg font-semibold text-white mb-2">How it works:</h3>
            <ul className="text-sm text-white/80 space-y-1">
              <li>• <strong>Blue bubbles</strong> show raw transcriptions from Whisper model</li>
              <li>• <strong>Purple bubbles</strong> show refined text from LLaMA model via Groq API</li>
              <li>• Set your refinement prompt above to customize how the AI improves transcriptions</li>
              <li>• Click "Start Listening" to begin real-time transcription</li>
              <li>• Raw transcriptions are automatically refined using your prompt</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Transcription;
