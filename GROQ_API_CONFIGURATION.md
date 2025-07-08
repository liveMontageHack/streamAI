# Groq API Key Configuration Guide

This guide explains how to properly configure the Groq API key for transcription refinement in both development and production environments.

## Environment Overview

The application supports multiple ways to configure the Groq API key, with a fallback hierarchy for maximum flexibility:

1. **Settings UI** (Primary) - Configured through the web interface
2. **Environment Variables** (Fallback) - Set at the OS/deployment level
3. **Default** (None) - Graceful degradation when no key is available

## Development Environment

### Method 1: Using the Settings UI (Recommended)

1. Start the development server:
   ```bash
   cd obs
   python api_server.py
   ```

2. Open the frontend and navigate to Settings
3. Enter your Groq API key in the "API Keys" section
4. Click "Validate" to test the key
5. Click "Save Settings" to store it

### Method 2: Using Environment Variables

1. Create a `.env` file in the project root:
   ```bash
   GROQ_API_KEY=your_actual_groq_api_key_here
   API_BASE_URL=http://localhost:5001
   ```

2. Or set it directly in your shell:
   ```bash
   # Windows PowerShell
   $env:GROQ_API_KEY="your_actual_groq_api_key_here"
   
   # Windows CMD
   set GROQ_API_KEY=your_actual_groq_api_key_here
   
   # Linux/macOS
   export GROQ_API_KEY="your_actual_groq_api_key_here"
   ```

## Production Environment (Railway/Vercel/etc.)

### Method 1: Environment Variables (Recommended for Production)

Set these environment variables in your deployment platform:

```bash
GROQ_API_KEY=your_actual_groq_api_key_here
API_BASE_URL=https://your-app-domain.com
WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook
AUTO_NOTIFICATIONS=true
TRANSCRIPTION_LANGUAGE=en
```

#### Railway Deployment
1. Go to your Railway project dashboard
2. Navigate to "Variables" tab
3. Add the environment variables above
4. Redeploy your application

#### Vercel Deployment
1. Go to your Vercel project dashboard
2. Navigate to "Settings" → "Environment Variables"
3. Add the environment variables above
4. Redeploy your application

### Method 2: Settings UI (Runtime Configuration)

Even in production, you can configure the API key through the settings UI:

1. Navigate to `/settings` in your deployed application
2. Enter your Groq API key
3. Click "Validate" and "Save Settings"

## Key Features and Fallback Behavior

### Automatic Fallback Chain

The system follows this priority order:

1. **Settings API** - Key stored via Settings UI
2. **Environment Variable** - `GROQ_API_KEY`
3. **Graceful Degradation** - Transcription works without refinement

### Environment-Aware Configuration

- **Development**: Uses `http://localhost:5001` by default
- **Production**: Uses `API_BASE_URL` environment variable
- **Auto-detection**: Falls back to localhost if no URL specified

### Security Features

- API keys are masked in the UI (shown as `••••••••••••••••••••••••••••••••••••••••`)
- Keys are not logged or exposed in error messages
- Validation endpoint tests keys without storing them
- Production server sanitizes settings responses

## Troubleshooting

### Common Issues

1. **"No Groq API key available"**
   - Verify the key is set in Settings or environment variables
   - Check that the API server has the `/api/settings` endpoint

2. **"Invalid Groq API key"**
   - Verify the key is correct and active
   - Use the validation button in Settings to test

3. **"Connection failed" in production**
   - Check that `API_BASE_URL` is set correctly
   - Ensure the production server is running and accessible

4. **Refinement not working**
   - Check browser console for API errors
   - Verify the Settings UI shows the key as configured
   - Test with the validation button

### Testing Configuration

You can test your configuration by:

1. **Validation Button**: Use the "Validate API Key" button in Settings
2. **Manual Test**: Try transcribing some audio and check for refined output
3. **Console Logs**: Check browser console for API communication errors

## Getting a Groq API Key

1. Visit [console.groq.com](https://console.groq.com)
2. Sign up or log in to your account
3. Navigate to "API Keys" section
4. Create a new API key
5. Copy the key (it will only be shown once)

## Security Best Practices

### Development
- Use `.env` files for local development
- Never commit API keys to version control
- Add `.env` to your `.gitignore` file

### Production
- Always use environment variables for sensitive data
- Rotate API keys regularly
- Monitor API usage and set up alerts
- Use the Settings UI only for non-sensitive configuration

## Supported Deployment Platforms

This configuration approach works with:

- ✅ Railway
- ✅ Vercel
- ✅ Heroku
- ✅ AWS (EC2, Lambda, ECS)
- ✅ Google Cloud Platform
- ✅ Azure
- ✅ DigitalOcean
- ✅ Local development servers

The environment variable approach ensures maximum compatibility across platforms.
