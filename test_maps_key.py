#!/usr/bin/env python
# Test script for Google Maps API key configuration

import os
import sys
from jinja2 import Environment, FileSystemLoader, pass_context

# Add the current directory to the path
sys.path.insert(0, '.')

def test_maps_api_key():
    """Test that the Google Maps API key is properly configured"""
    
    # Test 1: Configuration loading
    try:
        from conf import config
        print("✅ Configuration loaded successfully")
        print(f"   Maps API key configured: {'maps_api_key' in config}")
        if 'maps_api_key' in config:
            print(f"   Key value: {config['maps_api_key'][:20]}...")
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False
    
    # Test 2: Environment variable override
    test_key = "test-env-key-12345"
    os.environ['GOOGLE_MAPS_API_KEY'] = test_key
    
    try:
        # Reload configuration to test environment variable
        import importlib
        import conf
        importlib.reload(conf)
        
        if conf.config['maps_api_key'] == test_key:
            print("✅ Environment variable override works")
        else:
            print(f"❌ Environment variable override failed. Expected: {test_key}, Got: {conf.config['maps_api_key']}")
            return False
    except Exception as e:
        print(f"❌ Environment variable test failed: {e}")
        return False
    
    # Test 3: Template rendering
    try:
        env = Environment(loader=FileSystemLoader(['src', 'templates']))
        
        # Add the prefix filter that the template needs
        @pass_context
        def filter_prefix(ctx, link):
            level = ctx.get("level", 0)
            if level == 0:
                return link
            path = ['..'] * level
            path.append(link)
            return '/'.join(path)
        
        env.filters["prefix"] = filter_prefix
        
        template = env.get_template('development-map.html')
        
        # Create a mock context with required variables
        context = {
            'sage': 'SageMath',
            'maps_api_key': test_key,
            'level': 0,
            'docroot': 'https://doc.sagemath.org'
        }
        
        rendered = template.render(**context)
        
        if test_key in rendered:
            print("✅ Template rendering works correctly")
        else:
            print("❌ Template rendering failed - API key not found in output")
            return False
            
    except Exception as e:
        print(f"❌ Template rendering test failed: {e}")
        return False
    
    print("\n🎉 All tests passed! Google Maps API key is properly configured.")
    return True

if __name__ == '__main__':
    success = test_maps_api_key()
    sys.exit(0 if success else 1) 