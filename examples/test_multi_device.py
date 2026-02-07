#!/usr/bin/env python3
"""Test script for multi-device WLED MCP server functionality."""

import asyncio
import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wled_mcp.wled_client import WLEDClient


async def test_multi_device():
    """Test WLED client functionality with multiple devices."""
    
    # Configure multiple devices
    devices = {
        "living_room": os.getenv("WLED_DEVICE_LIVING_ROOM", "192.168.1.100"),
        "bedroom": os.getenv("WLED_DEVICE_BEDROOM", "192.168.1.101"),
    }
    
    print("Testing WLED client with multiple devices")
    print("=" * 50)
    print(f"Configured devices: {list(devices.keys())}")
    print()
    
    for device_name, host in devices.items():
        print(f"\n{'='*50}")
        print(f"Testing device: {device_name} ({host})")
        print(f"{'='*50}")
        
        try:
            client = WLEDClient(host)
            
            # Test getting device info
            print(f"Getting device info...")
            info = await client.get_info()
            print(f"  Device: {info.get('name', 'Unknown')}")
            print(f"  Version: {info.get('ver', 'Unknown')}")
            print(f"  LED Count: {info.get('leds', {}).get('count', 'Unknown')}")
            
            # Test getting current state
            print(f"Getting current state...")
            state = await client.get_state()
            print(f"  Power: {'On' if state.get('on') else 'Off'}")
            print(f"  Brightness: {state.get('bri', 'Unknown')}")
            
            print(f"✓ {device_name} is accessible")
            
        except Exception as e:
            print(f"✗ Error testing {device_name}: {e}")
            print(f"  Make sure device at {host} is accessible")
    
    print("\n" + "=" * 50)
    print("Multi-device test completed!")


if __name__ == "__main__":
    asyncio.run(test_multi_device())
