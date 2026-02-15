#!/usr/bin/env python3
"""Test script for WLED configuration and segments functionality."""

import asyncio
import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wled_mcp.wled_client import WLEDClient


async def test_config_and_segments():
    """Test WLED configuration and segments functionality."""
    
    # Set your WLED device IP here or via environment variable
    host = os.getenv("WLED_HOST", "192.168.1.100")
    
    print(f"Testing WLED configuration and segments with host: {host}")
    print("=" * 70)
    
    try:
        client = WLEDClient(host)
        
        # Test 1: Get device configuration
        print("\n1. Getting device configuration...")
        print("-" * 70)
        config = await client.get_config()
        print(f"Device name: {config.get('id', {}).get('name', 'Unknown')}")
        print(f"LED count: {config.get('hw', {}).get('led', {}).get('total', 'Unknown')}")
        print(f"Max segments: {config.get('hw', {}).get('led', {}).get('maxseg', 'Unknown')}")
        print("✓ Configuration fetched successfully")
        
        # Test 2: Get all segments
        print("\n2. Getting all segments...")
        print("-" * 70)
        segments_info = await client.get_segments()
        print(f"Total segments: {segments_info['count']}")
        for i, seg in enumerate(segments_info['segments']):
            print(f"  Segment {seg.get('id', i)}: LEDs {seg.get('start', '?')}-{seg.get('stop', '?')}, "
                  f"On: {seg.get('on', False)}, Effect: {seg.get('fx', '?')}")
        print("✓ Segments fetched successfully")
        
        # Test 3: Get specific segment
        print("\n3. Getting segment 0 details...")
        print("-" * 70)
        segment = await client.get_segment(0)
        print(f"Segment 0 full details:")
        print(json.dumps(segment, indent=2))
        print("✓ Segment 0 fetched successfully")
        
        # Test 4: Update segment color
        print("\n4. Updating segment 0 to purple...")
        print("-" * 70)
        result = await client.set_segment(0, {"col": [[128, 0, 128]]})
        print("✓ Segment 0 updated to purple")
        await asyncio.sleep(2)
        
        # Test 5: Update segment with effect
        print("\n5. Setting segment 0 to rainbow effect...")
        print("-" * 70)
        result = await client.set_segment(0, {
            "fx": 9,  # Rainbow effect
            "sx": 128,  # Speed
            "ix": 128   # Intensity
        })
        print("✓ Segment 0 set to rainbow effect")
        await asyncio.sleep(2)
        
        # Test 6: Create a new segment (if multiple segments are supported)
        print("\n6. Testing segment creation (if device has enough LEDs)...")
        print("-" * 70)
        try:
            # Get LED count from config
            led_count = config.get('hw', {}).get('led', {}).get('total', 0)
            if led_count > 30:
                # Create segment from LED 0-15 with red color
                result = await client.create_segment(0, 15, {"col": [[255, 0, 0]]})
                print("✓ Created segment (LEDs 0-15) with red color")
                await asyncio.sleep(2)
                
                # Create segment from LED 15-30 with blue color
                result = await client.create_segment(15, 30, {"col": [[0, 0, 255]]})
                print("✓ Created segment (LEDs 15-30) with blue color")
                await asyncio.sleep(2)
            else:
                print("⊘ Skipping segment creation test (device has < 30 LEDs)")
        except Exception as e:
            print(f"⚠ Segment creation test: {e}")
        
        # Test 7: Set segment back to solid color
        print("\n7. Resetting segment 0 to solid white...")
        print("-" * 70)
        result = await client.set_segment(0, {
            "col": [[255, 255, 255]],
            "fx": 0  # Solid color
        })
        print("✓ Segment 0 reset to solid white")
        
        print("\n" + "=" * 70)
        print("All configuration and segment tests completed successfully!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        print("Make sure your WLED device is accessible and the IP is correct.")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_config_and_segments())
