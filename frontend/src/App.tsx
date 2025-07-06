import React, { useState } from 'react';
import Navigation from './components/Navigation';
import Dashboard from './components/Dashboard';
import Settings from './components/Settings';
import DiscordIntegration from './components/DiscordIntegration';
import StreamAnalytics from './components/StreamAnalytics';
import Recordings from './components/Recordings';

function App() {
  const [activeSection, setActiveSection] = useState('dashboard');

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
        return <div className="text-white">Transcription management coming soon...</div>;
      case 'discord':
        return <DiscordIntegration />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-blue-900">
      <Navigation activeSection={activeSection} setActiveSection={setActiveSection} />
      <div className="lg:ml-64 min-h-screen">
        <div className="p-6 pt-16 lg:pt-6">
          {renderActiveSection()}
        </div>
      </div>
    </div>
  );
}

export default App;