"""WLED MCP Server implementation."""

import json
import os
from typing import Any, Dict, Optional
from pathlib import Path
import logging
import yaml

from mcp.server.fastmcp import FastMCP
from .wled_client import WLEDClient

# Configure logging to stderr
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("WLED Controller")

# Global device registry (cached in memory)
_devices: Dict[str, str] = {}
_config_file_path: Optional[Path] = None

def _get_config_file_path() -> Path:
    """Get the path to the YAML config file."""
    # Check environment variable first
    config_path = os.getenv("WLED_CONFIG_FILE")
    if config_path:
        return Path(config_path)
    
    # Default to ~/.wled_mcp/config.yaml
    home = Path.home()
    config_dir = home / ".wled_mcp"
    return config_dir / "config.yaml"

def _load_from_yaml_file() -> bool:
    """Load devices from YAML config file.
    
    Returns:
        True if devices were loaded from file, False otherwise
    """
    global _devices, _config_file_path
    
    config_path = _get_config_file_path()
    _config_file_path = config_path
    
    if not config_path.exists():
        logger.info(f"Config file not found at {config_path}")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        if not config or 'devices' not in config:
            logger.warning(f"No devices found in config file {config_path}")
            return False
        
        devices = config['devices']
        if not isinstance(devices, dict):
            logger.error(f"Invalid devices format in {config_path}")
            return False
        
        _devices = devices
        logger.info(f"Loaded {len(_devices)} devices from config file {config_path}")
        return True
    except yaml.YAMLError as e:
        logger.error(f"Failed to parse YAML config file {config_path}: {e}")
        return False
    except Exception as e:
        logger.error(f"Error reading config file {config_path}: {e}")
        return False

def _save_to_yaml_file() -> bool:
    """Save current devices to YAML config file.
    
    Returns:
        True if saved successfully, False otherwise
    """
    global _devices, _config_file_path
    
    if _config_file_path is None:
        _config_file_path = _get_config_file_path()
    
    try:
        # Ensure directory exists with secure permissions
        _config_file_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        
        # Create config structure
        config = {
            'devices': _devices
        }
        
        # Write to file with comments
        with open(_config_file_path, 'w') as f:
            f.write("# WLED MCP Device Configuration\n")
            f.write("# Format: device_name: ip_address\n")
            f.write("#\n")
            f.write("# Example:\n")
            f.write("#   living_room: 192.168.1.100\n")
            f.write("#   bedroom: 192.168.1.101\n")
            f.write("#\n")
            yaml.dump(config, f, default_flow_style=False, sort_keys=True)
        
        logger.info(f"Saved {len(_devices)} devices to config file {_config_file_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving config file {_config_file_path}: {e}")
        return False

def _load_devices():
    """Load device configurations from multiple sources with priority order.
    
    Priority:
    1. YAML config file (~/.wled_mcp/config.yaml or WLED_CONFIG_FILE env var)
    2. WLED_DEVICES environment variable (JSON)
    3. WLED_DEVICE_* environment variables
    4. WLED_HOST environment variable (backward compatibility)
    
    Devices are cached in memory after loading.
    """
    global _devices
    
    # Priority 1: Try to load from YAML config file
    if _load_from_yaml_file():
        return
    
    # Priority 2: Try to load from WLED_DEVICES JSON config
    devices_json = os.getenv("WLED_DEVICES")
    if devices_json:
        try:
            _devices = json.loads(devices_json)
            logger.info(f"Loaded {len(_devices)} devices from WLED_DEVICES")
            return
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse WLED_DEVICES JSON: {e}")
    
    # Priority 3: Load from individual WLED_DEVICE_* environment variables
    for key, value in os.environ.items():
        if key.startswith("WLED_DEVICE_") and key != "WLED_DEVICES":
            device_name = key.replace("WLED_DEVICE_", "").lower()
            _devices[device_name] = value
            logger.info(f"Loaded device '{device_name}' from {key}")
    
    # Priority 4: Backward compatibility - if WLED_HOST is set, use it as default device
    if not _devices:
        host = os.getenv("WLED_HOST")
        if host:
            _devices["default"] = host
            logger.info(f"Loaded single device from WLED_HOST as 'default'")

# Load devices on module import (cached in memory)
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
            "message": "No devices configured. Set WLED_DEVICES, WLED_DEVICE_*, WLED_HOST environment variables, or use YAML config file."
        }, indent=2)
    
    config_source = "YAML config file" if _config_file_path and _config_file_path.exists() else "environment variables"
    
    return json.dumps({
        "devices": _devices,
        "count": len(_devices),
        "source": config_source
    }, indent=2)


@mcp.tool()
async def wled_add_device(device_name: str, ip_address: str) -> str:
    """Add a new WLED device to the configuration.
    
    Args:
        device_name: Unique name for the device (e.g., "living_room")
        ip_address: IP address of the WLED device (e.g., "192.168.1.100")
    
    Returns:
        JSON string with operation result
    """
    global _devices
    
    # Validate device name
    if not device_name or not device_name.replace("_", "").replace("-", "").isalnum():
        return json.dumps({
            "success": False,
            "error": "Invalid device name. Use alphanumeric characters, underscores, and hyphens only."
        }, indent=2)
    
    # Check if device already exists
    if device_name in _devices:
        return json.dumps({
            "success": False,
            "error": f"Device '{device_name}' already exists with IP {_devices[device_name]}"
        }, indent=2)
    
    # Add device to registry
    _devices[device_name] = ip_address
    
    # Save to YAML file
    if _save_to_yaml_file():
        logger.info(f"Added device '{device_name}' with IP {ip_address}")
        return json.dumps({
            "success": True,
            "message": f"Device '{device_name}' added successfully",
            "device": {device_name: ip_address}
        }, indent=2)
    else:
        return json.dumps({
            "success": False,
            "error": "Failed to save configuration to file. Device added to memory only."
        }, indent=2)


@mcp.tool()
async def wled_remove_device(device_name: str) -> str:
    """Remove a WLED device from the configuration.
    
    Args:
        device_name: Name of the device to remove
    
    Returns:
        JSON string with operation result
    """
    global _devices
    
    if device_name not in _devices:
        return json.dumps({
            "success": False,
            "error": f"Device '{device_name}' not found in configuration"
        }, indent=2)
    
    # Remove device
    removed_ip = _devices.pop(device_name)
    
    # Save to YAML file
    if _save_to_yaml_file():
        logger.info(f"Removed device '{device_name}' (IP: {removed_ip})")
        return json.dumps({
            "success": True,
            "message": f"Device '{device_name}' removed successfully",
            "removed": {device_name: removed_ip}
        }, indent=2)
    else:
        # Rollback if save failed
        _devices[device_name] = removed_ip
        return json.dumps({
            "success": False,
            "error": "Failed to save configuration to file. No changes made."
        }, indent=2)


@mcp.tool()
async def wled_update_device(device_name: str, ip_address: str) -> str:
    """Update the IP address of an existing WLED device.
    
    Args:
        device_name: Name of the device to update
        ip_address: New IP address for the device
    
    Returns:
        JSON string with operation result
    """
    global _devices
    
    if device_name not in _devices:
        return json.dumps({
            "success": False,
            "error": f"Device '{device_name}' not found in configuration"
        }, indent=2)
    
    old_ip = _devices[device_name]
    _devices[device_name] = ip_address
    
    # Save to YAML file
    if _save_to_yaml_file():
        logger.info(f"Updated device '{device_name}' IP from {old_ip} to {ip_address}")
        return json.dumps({
            "success": True,
            "message": f"Device '{device_name}' updated successfully",
            "old_ip": old_ip,
            "new_ip": ip_address
        }, indent=2)
    else:
        # Rollback if save failed
        _devices[device_name] = old_ip
        return json.dumps({
            "success": False,
            "error": "Failed to save configuration to file. No changes made."
        }, indent=2)


@mcp.tool()
async def wled_get_config_path() -> str:
    """Get the path to the YAML configuration file.
    
    Returns:
        JSON string with config file path and existence status
    """
    config_path = _get_config_file_path()
    parent_exists = config_path.parent.exists()
    
    return json.dumps({
        "config_path": str(config_path),
        "exists": config_path.exists(),
        "can_write": os.access(config_path.parent, os.W_OK) if parent_exists else False,
        "parent_exists": parent_exists
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