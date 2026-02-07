"""WLED MCP Server implementation."""

import json
import os
from typing import Any, Dict, Optional
import logging

from mcp.server.fastmcp import FastMCP
from .wled_client import WLEDClient

# Configure logging to stderr
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("WLED Controller")

# Global device registry
_devices: Dict[str, str] = {}

def _load_devices():
    """Load device configurations from environment variables."""
    global _devices
    
    # Try to load from WLED_DEVICES JSON config first
    devices_json = os.getenv("WLED_DEVICES")
    if devices_json:
        try:
            _devices = json.loads(devices_json)
            logger.info(f"Loaded {len(_devices)} devices from WLED_DEVICES")
            return
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse WLED_DEVICES JSON: {e}")
    
    # Load from individual WLED_DEVICE_* environment variables
    for key, value in os.environ.items():
        if key.startswith("WLED_DEVICE_") and key != "WLED_DEVICES":
            device_name = key.replace("WLED_DEVICE_", "").lower()
            _devices[device_name] = value
            logger.info(f"Loaded device '{device_name}' from {key}")
    
    # Backward compatibility: if WLED_HOST is set, use it as default device
    if not _devices:
        host = os.getenv("WLED_HOST")
        if host:
            _devices["default"] = host
            logger.info(f"Loaded single device from WLED_HOST as 'default'")

# Load devices on module import
_load_devices()

def get_wled_client(device_name: Optional[str] = None, direct_ip: Optional[str] = None) -> WLEDClient:
    """Get WLED client instance.
    
    Args:
        device_name: Name of a pre-configured device from the registry (e.g., "living_room")
        direct_ip: Direct IP address for ad-hoc connections (e.g., "192.168.1.105"), 
                   bypasses registry lookup and overrides device_name if both provided
        
    Returns:
        WLEDClient instance
        
    Note:
        Priority order: direct_ip > device_name > "default" device > WLED_HOST env var
    """
    # Direct IP takes precedence - allows ad-hoc connections without configuration
    if direct_ip:
        return WLEDClient(direct_ip)
    
    # Use device name from registry - for pre-configured devices
    if device_name:
        if device_name not in _devices:
            raise ValueError(f"Unknown device: {device_name}. Available devices: {list(_devices.keys())}")
        return WLEDClient(_devices[device_name])
    
    # Backward compatibility: try default device or WLED_HOST
    if "default" in _devices:
        return WLEDClient(_devices["default"])
    
    # Last resort: check WLED_HOST environment variable
    fallback_host = os.getenv("WLED_HOST")
    if fallback_host:
        return WLEDClient(fallback_host)
    
    raise ValueError(
        "No device specified. Either provide device_name (for configured devices), "
        "direct_ip (for ad-hoc connections), or configure devices via WLED_DEVICES or WLED_HOST environment variables"
    )


@mcp.tool()
async def wled_list_devices() -> str:
    """List all configured WLED devices.
    
    Returns:
        JSON string with device names and their host addresses
    """
    if not _devices:
        return json.dumps({
            "devices": {},
            "message": "No devices configured. Set WLED_DEVICES, WLED_DEVICE_*, or WLED_HOST environment variables."
        }, indent=2)
    
    return json.dumps({
        "devices": _devices,
        "count": len(_devices)
    }, indent=2)


@mcp.tool()
async def wled_get_info(device_name: Optional[str] = None, direct_ip: Optional[str] = None) -> str:
    """Get WLED device information including version, LED count, and capabilities.
    
    Args:
        device_name: Name of pre-configured device from registry (e.g., "living_room")
        direct_ip: Direct IP address for ad-hoc connection (e.g., "192.168.1.105")
    
    Returns:
        JSON string with device information
        
    Note:
        - Use device_name for pre-configured devices in your registry
        - Use direct_ip for temporary/ad-hoc connections without configuration
        - If neither provided, uses default device or WLED_HOST environment variable
    """
    try:
        client = get_wled_client(device_name, direct_ip)
        info = await client.get_info()
        return json.dumps(info, indent=2)
    except Exception as e:
        logger.error(f"Error getting WLED info: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
async def wled_get_state(device_name: Optional[str] = None, direct_ip: Optional[str] = None) -> str:
    """Get current WLED device state including power, brightness, colors, and effects.
    
    Args:
        device_name: Name of pre-configured device from registry (e.g., "bedroom")
        direct_ip: Direct IP address for ad-hoc connection (e.g., "192.168.1.105")
    
    Returns:
        JSON string with current device state
    """
    try:
        client = get_wled_client(device_name, direct_ip)
        state = await client.get_state()
        return json.dumps(state, indent=2)
    except Exception as e:
        logger.error(f"Error getting WLED state: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
async def wled_set_power(on: bool, device_name: Optional[str] = None, direct_ip: Optional[str] = None) -> str:
    """Turn WLED device on or off.
    
    Args:
        on: True to turn on, False to turn off
        device_name: Name of pre-configured device from registry
        direct_ip: Direct IP address for ad-hoc connection
    
    Returns:
        JSON string with updated device state
    """
    try:
        client = get_wled_client(device_name, direct_ip)
        result = await client.set_power(on)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error setting WLED power: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
async def wled_set_brightness(brightness: int, device_name: Optional[str] = None, direct_ip: Optional[str] = None) -> str:
    """Set WLED device brightness.
    
    Args:
        brightness: Brightness level (0-255)
        device_name: Name of pre-configured device from registry
        direct_ip: Direct IP address for ad-hoc connection
    
    Returns:
        JSON string with updated device state
    """
    try:
        client = get_wled_client(device_name, direct_ip)
        result = await client.set_brightness(brightness)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error setting WLED brightness: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
async def wled_set_color(r: int, g: int, b: int, device_name: Optional[str] = None, direct_ip: Optional[str] = None) -> str:
    """Set WLED device color using RGB values.
    
    Args:
        r: Red component (0-255)
        g: Green component (0-255)
        b: Blue component (0-255)
        device_name: Name of pre-configured device from registry
        direct_ip: Direct IP address for ad-hoc connection
    
    Returns:
        JSON string with updated device state
    """
    try:
        client = get_wled_client(device_name, direct_ip)
        result = await client.set_color(r, g, b)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error setting WLED color: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
async def wled_set_effect(effect_id: int, speed: Optional[int] = None, 
                         intensity: Optional[int] = None, device_name: Optional[str] = None, direct_ip: Optional[str] = None) -> str:
    """Set WLED lighting effect.
    
    Args:
        effect_id: Effect ID number (0 for solid color, 1+ for various effects)
        speed: Effect speed (0-255, optional)
        intensity: Effect intensity (0-255, optional)
        device_name: Name of pre-configured device from registry
        direct_ip: Direct IP address for ad-hoc connection
    
    Returns:
        JSON string with updated device state
    """
    try:
        client = get_wled_client(device_name, direct_ip)
        result = await client.set_effect(effect_id, speed, intensity)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error setting WLED effect: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
async def wled_get_effects(device_name: Optional[str] = None, direct_ip: Optional[str] = None) -> str:
    """Get list of available WLED effects.
    
    Args:
        device_name: Name of pre-configured device from registry
        direct_ip: Direct IP address for ad-hoc connection
    
    Returns:
        JSON string with available effects and their IDs
    """
    try:
        client = get_wled_client(device_name, direct_ip)
        effects = await client.get_effects()
        return json.dumps(effects, indent=2)
    except Exception as e:
        logger.error(f"Error getting WLED effects: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
async def wled_get_palettes(device_name: Optional[str] = None, direct_ip: Optional[str] = None) -> str:
    """Get list of available WLED color palettes.
    
    Args:
        device_name: Name of pre-configured device from registry
        direct_ip: Direct IP address for ad-hoc connection
    
    Returns:
        JSON string with available color palettes
    """
    try:
        client = get_wled_client(device_name, direct_ip)
        palettes = await client.get_palettes()
        return json.dumps(palettes, indent=2)
    except Exception as e:
        logger.error(f"Error getting WLED palettes: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
async def wled_get_presets(device_name: Optional[str] = None, direct_ip: Optional[str] = None) -> str:
    """Get list of available WLED presets.
    
    Args:
        device_name: Name of pre-configured device from registry
        direct_ip: Direct IP address for ad-hoc connection
    
    Returns:
        JSON string with available presets and their names/IDs
    """
    try:
        client = get_wled_client(device_name, direct_ip)
        presets = await client.get_presets()
        return json.dumps(presets, indent=2)
    except Exception as e:
        logger.error(f"Error getting WLED presets: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
async def wled_activate_preset(preset_id: int, device_name: Optional[str] = None, direct_ip: Optional[str] = None) -> str:
    """Activate a WLED preset by ID.
    
    Args:
        preset_id: Preset ID to activate (1-250)
        device_name: Name of pre-configured device from registry
        direct_ip: Direct IP address for ad-hoc connection
    
    Returns:
        JSON string with updated device state
    """
    try:
        client = get_wled_client(device_name, direct_ip)
        result = await client.activate_preset(preset_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error activating WLED preset: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
async def wled_set_state(state_json: str, device_name: Optional[str] = None, direct_ip: Optional[str] = None) -> str:
    """Set WLED device state using raw JSON state object for advanced control.
    
    Args:
        state_json: JSON string representing the state to set
        device_name: Name of pre-configured device from registry
        direct_ip: Direct IP address for ad-hoc connection
    
    Returns:
        JSON string with updated device state
    """
    try:
        client = get_wled_client(device_name, direct_ip)
        state = json.loads(state_json)
        result = await client.set_state(state)
        return json.dumps(result, indent=2)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in state_json: {e}")
        return f"Error: Invalid JSON - {str(e)}"
    except Exception as e:
        logger.error(f"Error setting WLED state: {e}")
        return f"Error: {str(e)}"


def main():
    """Run the WLED MCP server."""
    mcp.run(transport="stdio")