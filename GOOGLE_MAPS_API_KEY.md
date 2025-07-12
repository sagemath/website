# Google Maps API Key Security

## Overview
The Google Maps API key has been moved from hardcoded HTML to a secure configuration system.

## Changes Made

### 1. Configuration File (`conf/config.yaml`)
- Added `maps_api_key` configuration option
- Includes fallback to current key for backward compatibility
- Supports environment variable override

### 2. Configuration Loading (`conf/__init__.py`)
- Added environment variable support
- `GOOGLE_MAPS_API_KEY` environment variable takes precedence
- Maintains backward compatibility

### 3. Template Update (`src/development-map.html`)
- Replaced hardcoded API key with `{{ maps_api_key }}` template variable
- Now uses configuration-driven approach

## Usage

### Development
The API key will use the fallback value from `config.yaml`:
```yaml
maps_api_key: "AIzaSyB3YiQ---yL6-QfoW9heq4-VbrAQzerhhA"
```

### Production
Set the environment variable to override the configuration:
```bash
export GOOGLE_MAPS_API_KEY="your-production-key-here"
```

### Docker/Container
```bash
docker run -e GOOGLE_MAPS_API_KEY="your-key" ...
```

## Security Recommendations

### 1. Google Cloud Console Settings
- **HTTP referrers**: Set to `*.sagemath.org/*`
- **API restrictions**: Only enable Maps JavaScript API
- **Usage quotas**: Set reasonable daily limits

### 2. Environment Variables
- Use different keys for development/staging/production
- Never commit production keys to version control
- Rotate keys regularly

### 3. Monitoring
- Monitor API usage in Google Cloud Console
- Set up alerts for quota thresholds
- Review usage patterns regularly

## Migration Steps

1. **Immediate**: The current setup will continue working with the fallback key
2. **Short-term**: Set up proper Google Cloud Console restrictions
3. **Long-term**: Implement environment variable in production deployment

## Files Modified
- `conf/config.yaml` - Added API key configuration
- `conf/__init__.py` - Added environment variable support
- `src/development-map.html` - Updated to use configuration variable 