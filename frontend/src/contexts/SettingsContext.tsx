import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface Settings {
  groqApiKey: string;
  webhookUrl: string;
  autoNotifications: boolean;
  transcriptionLanguage: string;
}

interface SettingsContextType {
  settings: Settings;
  updateSettings: (newSettings: Partial<Settings>) => void;
  loadSettings: () => Promise<void>;
  saveSettings: () => Promise<boolean>;
  isLoading: boolean;
  hasUnsavedChanges: boolean;
}

const defaultSettings: Settings = {
  groqApiKey: '',
  webhookUrl: 'https://discord.com/api/webhooks/...',
  autoNotifications: true,
  transcriptionLanguage: 'en',
};

const SettingsContext = createContext<SettingsContextType | undefined>(undefined);

export const useSettings = () => {
  const context = useContext(SettingsContext);
  if (context === undefined) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }
  return context;
};

interface SettingsProviderProps {
  children: ReactNode;
}

export const SettingsProvider: React.FC<SettingsProviderProps> = ({ children }) => {
  const [settings, setSettings] = useState<Settings>(defaultSettings);
  const [originalSettings, setOriginalSettings] = useState<Settings>(defaultSettings);
  const [isLoading, setIsLoading] = useState(false);

  // Calculate if there are unsaved changes
  const hasUnsavedChanges = JSON.stringify(settings) !== JSON.stringify(originalSettings);

  const loadSettings = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/settings');
      if (response.ok) {
        const data = await response.json();
        const loadedSettings = {
          groqApiKey: data.settings.groq_api_key || '',
          webhookUrl: data.settings.webhook_url || defaultSettings.webhookUrl,
          autoNotifications: data.settings.auto_notifications ?? defaultSettings.autoNotifications,
          transcriptionLanguage: data.settings.transcription_language || defaultSettings.transcriptionLanguage,
        };
        setSettings(loadedSettings);
        setOriginalSettings(loadedSettings);
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const updateSettings = (newSettings: Partial<Settings>) => {
    setSettings(prev => ({ ...prev, ...newSettings }));
  };

  const saveSettings = async (): Promise<boolean> => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/settings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          groq_api_key: settings.groqApiKey,
          webhook_url: settings.webhookUrl,
          auto_notifications: settings.autoNotifications,
          transcription_language: settings.transcriptionLanguage,
        }),
      });

      if (response.ok) {
        // Update the original settings to reflect the saved state
        setOriginalSettings({ ...settings });
        return true;
      } else {
        console.error('Failed to save settings:', response.status, response.statusText);
        return false;
      }
    } catch (error) {
      console.error('Failed to save settings:', error);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  // Load settings when the provider mounts
  useEffect(() => {
    loadSettings();
  }, []);

  const value: SettingsContextType = {
    settings,
    updateSettings,
    loadSettings,
    saveSettings,
    isLoading,
    hasUnsavedChanges,
  };

  return (
    <SettingsContext.Provider value={value}>
      {children}
    </SettingsContext.Provider>
  );
};
