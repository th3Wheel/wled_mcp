#!/usr/bin/env python3
"""Test script for WLED MCP server functionality."""

import asyncio
import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wled_mcp.wled_client import WLEDClient


async def test_wled_client():
    """Test WLED client functionality."""
    
    # Set your WLED device IP here or via environment variable
    host = os.getenv("WLED_HOST", "192.168.1.100")
    
    print(f"Testing WLED client with host: {host}")
    print("=" * 50)
    
    try:
        client = WLEDClient(host)
        
        # Test getting device info
        print("Getting device info...")
        info = await client.get_info()
        print(f"Device: {info.get('name', 'Unknown')}")
        print(f"Version: {info.get('ver', 'Unknown')}")
        print(f"LED Count: {info.get('leds', {}).get('count', 'Unknown')}")
        print()
        
        # Test getting current state
        print("Getting current state...")
        state = await client.get_state()
        print(f"Power: {'On' if state.get('on') else 'Off'}")
        print(f"Brightness: {state.get('bri', 'Unknown')}")
        print()
        
        # Test setting brightness
        print("Setting brightness to 128...")
        await client.set_brightness(128)
        print("✓ Brightness set")
        
        # Test setting color to red
        print("Setting color to red...")
        await client.set_color(255, 0, 0)
        print("✓ Color set to red")
        
        # Wait a moment
        await asyncio.sleep(2)
        
        # Test setting color to blue
        print("Setting color to blue...")
        await client.set_color(0, 0, 255)
        print("✓ Color set to blue")
        
        # Test setting effect
        print("Setting rainbow effect...")
        await client.set_effect(9, speed=128, intensity=128)  # Rainbow effect
        print("✓ Rainbow effect set")
        
        print("\nAll tests completed successfully!")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        print("Make sure your WLED device is accessible and the IP is correct.")


if __name__ == "__main__":
    asyncio.run(test_wled_client())