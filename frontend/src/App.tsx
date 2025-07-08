import React, { useState } from 'react';
import Navigation from './components/Navigation';
import Dashboard from './components/Dashboard';
import Settings from './components/Settings';
import DiscordIntegration from './components/DiscordIntegration';
import StreamAnalytics from './components/StreamAnalytics';
import Recordings from './components/Recordings';
import Transcription from './components/Transcription';
import DemoBanner from './components/DemoBanner';
import { useAppMode } from './hooks/useAppMode';

function App() {
  const [activeSection, setActiveSection] = useState('dashboard');
  const { mode } = useAppMode();

  const renderActiveSection = () => {
    switch (activeSection) {
      case 'dashboard':
        return <Dashboard />;
      case 'recordings':
        return <Recordings />;
      case 'settings':
        return <Settings />;
      case 'analytics':
        return <StreamAnalytics />;
      case 'schedule':
        return <div className="text-white">Schedule section coming soon...</div>;
      case 'transcription':
        return <Transcription />;
      case 'discord':
        return <DiscordIntegration />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-blue-900">
      <DemoBanner />
      <Navigation activeSection={activeSection} setActiveSection={setActiveSection} />
      <div className="lg:ml-64 min-h-screen">
        <div className="p-6 pt-16 lg:pt-6">
          {renderActiveSection()}
        </div>
      </div>
      
      {/* Mode indicator in bottom right */}
      <div className="fixed bottom-4 right-4 z-50">
        <div className={`px-3 py-1 rounded-full text-xs font-semibold ${
          mode === 'demo' 
            ? 'bg-blue-600 text-white' 
            : 'bg-green-600 text-white'
        }`}>
          {mode === 'demo' ? '🚀 DEMO' : '💻 LOCAL'}
        </div>
      </div>
    </div>
  );
}

export default App;
