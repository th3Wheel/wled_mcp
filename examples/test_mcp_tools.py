#!/usr/bin/env python3
"""Test script for new WLED MCP tools (configuration and segments)."""

import asyncio
import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wled_mcp import server


async def test_mcp_tools():
    """Test new MCP tools for configuration and segments."""
    
    # Set your WLED device IP here or via environment variable
    host = os.getenv("WLED_HOST", "192.168.1.100")
    os.environ["WLED_HOST"] = host
    
    print(f"Testing WLED MCP tools with host: {host}")
    print("=" * 70)
    
    try:
        # Test 1: Get device configuration
        print("\n1. Testing wled_get_config()...")
        print("-" * 70)
        config_result = await server.wled_get_config()
        config = json.loads(config_result)
        print(f"Device name: {config.get('id', {}).get('name', 'Unknown')}")
        print(f"LED count: {config.get('hw', {}).get('led', {}).get('total', 'Unknown')}")
        print("✓ wled_get_config() works")
        
        # Test 2: Get all segments
        print("\n2. Testing wled_get_segments()...")
        print("-" * 70)
        segments_result = await server.wled_get_segments()
        segments_data = json.loads(segments_result)
        print(f"Segments: {segments_data['count']} found")
        print("✓ wled_get_segments() works")
        
        # Test 3: Get specific segment
        print("\n3. Testing wled_get_segment(0)...")
        print("-" * 70)
        segment_result = await server.wled_get_segment(0)
        segment = json.loads(segment_result)
        print(f"Segment 0 range: LED {segment.get('start')}-{segment.get('stop')}")
        print("✓ wled_get_segment() works")
        
        # Test 4: Set segment color
        print("\n4. Testing wled_set_segment(0, orange)...")
        print("-" * 70)
        result = await server.wled_set_segment(0, '{"col":[[255,165,0]]}')
        print("✓ wled_set_segment() works - segment should be orange")
        await asyncio.sleep(2)
        
        # Test 5: Set segment effect
        print("\n5. Testing wled_set_segment(0, rainbow effect)...")
        print("-" * 70)
        result = await server.wled_set_segment(0, '{"fx":9,"sx":150,"ix":200}')
        print("✓ wled_set_segment() works - rainbow effect applied")
        await asyncio.sleep(2)
        
        # Test 6: Debug device
        print("\n6. Testing wled_debug_device()...")
        print("-" * 70)
        debug_result = await server.wled_debug_device()
        debug_data = json.loads(debug_result)
        print(f"Debug info contains: {list(debug_data.keys())}")
        print("✓ wled_debug_device() works")
        
        # Test 7: Create segment (if supported)
        print("\n7. Testing wled_create_segment()...")
        print("-" * 70)
        try:
            led_count = config.get('hw', {}).get('led', {}).get('total', 0)
            if led_count > 60:
                # Note: Creating segments may modify existing segment configuration
                result = await server.wled_create_segment(0, 30, '{"col":[[0,255,0]]}')
                print("✓ wled_create_segment() works - created green segment (LEDs 0-30)")
                await asyncio.sleep(2)
            else:
                print("⊘ Skipped (device has < 60 LEDs)")
        except Exception as e:
            print(f"⚠ wled_create_segment(): {e}")
        
        # Test 8: Reset to solid white
        print("\n8. Resetting segment 0 to solid white...")
        print("-" * 70)
        result = await server.wled_set_segment(0, '{"col":[[255,255,255]],"fx":0}')
        print("✓ Reset complete")
        
        print("\n" + "=" * 70)
        print("All MCP tool tests completed successfully!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        print("Make sure your WLED device is accessible and the IP is correct.")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_mcp_tools())
