# WLED MCP Server

A Model Context Protocol (MCP) server for controlling WLED devices through LLM interactions. This server enables Claude and other LLMs to directly control your WLED smart lighting devices with natural language commands.

## Features

- **Device Control**: Turn WLED devices on/off, adjust brightness (0-255)
- **Color Management**: Set RGB colors with precise control
- **Effects & Animation**: Access 100+ built-in lighting effects with customizable speed and intensity
- **Presets**: Create, list, and activate saved lighting presets
- **Palettes**: Browse and apply color palettes for effects
- **Device Information**: Get detailed device status, capabilities, and configuration
- **Advanced Control**: Use raw JSON API for complex operations and custom states

## ⚠️ IMPORTANT DISCLAIMER

**USE AT YOUR OWN RISK**: This MCP server directly controls your WLED device and can modify its configuration, effects, colors, and settings. The author is **NOT LIABLE** for any damage, malfunction, or unintended behavior that may occur to your WLED device, LED strips, or related hardware when using this software.

**STRONGLY RECOMMENDED BEFORE USE:**

- **Backup your WLED configuration**: Export your current WLED config via the web interface (Config → Security & Updates → Backup Configuration)
- **Save your presets**: Document or export any custom presets you want to keep
- **Test on non-critical devices first**: Try this software on a test setup before using on important lighting installations
- **Understand the risks**: This software can change brightness, colors, effects, and potentially overwrite your saved presets

By using this software, you acknowledge that you understand these risks and agree that you are solely responsible for any consequences.

## Installation

1. Clone this repository:

```bash
git clone https://github.com/mrkprdo/wled_mcp.git
cd wled_mcp
```

2. Install dependencies:

```bash
pip install -e .
```

## Quick Start

### 1. Configure Your WLED Device

Set your WLED device IP address:

```bash
export WLED_HOST=192.168.1.100
```

### 2. Test the Connection

Run the test script to verify connectivity:

```bash
python examples/test_server.py
```

### 3. Use with Claude Desktop

Add this configuration to your Claude Desktop MCP settings:

```json
{
  "mcpServers": {
    "wled": {
      "command": "python",
      "args": ["-m", "wled_mcp.server"],
      "env": {
        "WLED_HOST": "192.168.1.100"
      }
    }
  }
}
```

### 4. Start Controlling Your WLED

You can now ask Claude to control your WLED device with natural language:

- "Turn on my WLED and set it to bright blue"
- "Set a rainbow effect with medium speed"
- "Dim the lights to 25% brightness"
- "Show me the current device status"
- "Activate my bedtime preset"
- "Set the lights to a warm white color"
- "List all available effects"

## Available Tools

### Basic Controls

- `wled_set_power(on: bool, host?: str)` - Turn device on/off
- `wled_set_brightness(brightness: int, host?: str)` - Set brightness (0-255)
- `wled_set_color(r: int, g: int, b: int, host?: str)` - Set RGB color (0-255 each)

### Effects & Animation

- `wled_set_effect(effect_id: int, speed?: int, intensity?: int, host?: str)` - Set lighting effect with optional speed/intensity (0-255)
- `wled_get_effects(host?: str)` - List all available effects with IDs and names
- `wled_get_palettes(host?: str)` - List available color palettes

### Presets

- `wled_get_presets(host?: str)` - List all saved presets with IDs and names
- `wled_activate_preset(preset_id: int, host?: str)` - Activate a preset by ID (1-250)

### Device Information

- `wled_get_info(host?: str)` - Get device information (name, version, LED count, capabilities)
- `wled_get_state(host?: str)` - Get current device state (power, brightness, color, effect)

### Advanced

- `wled_set_state(state_json: str, host?: str)` - Set device state using raw JSON for complex operations

_Note: All tools support an optional `host` parameter. If not provided, the `WLED_HOST` environment variable will be used._

## Example Usage

### Via Claude Desktop

Once configured, you can use natural language commands:

```
"Turn on my WLED lights and set them to a soft purple color"
"Set a rainbow effect with slow speed"
"Show me all available presets"
"Activate preset 5"
"Set brightness to 50%"
```

### Direct API Usage

```python
# Turn on and set to purple
await wled_set_power(True)
await wled_set_color(128, 0, 128)

# Set rainbow effect with custom speed
await wled_set_effect(9, speed=150, intensity=200)

# Get device info
info = await wled_get_info()

# Activate a preset
await wled_activate_preset(3)
```

## Troubleshooting

### Common Issues

- **Connection Errors**:

  - Ensure your WLED device is powered on and connected to the same network
  - Verify the IP address is correct (check your router or WLED web interface)
  - Test connectivity with `ping <WLED_IP>`

- **Environment Variable Issues**:

  - Make sure `WLED_HOST` is set correctly: `export WLED_HOST=192.168.1.100`
  - On Windows: `set WLED_HOST=192.168.1.100`

- **Tool/Command Errors**:

  - Use `wled_get_effects()` to see available effect IDs (usually 0-100+)
  - Use `wled_get_presets()` to see available preset IDs (1-250)
  - Check device capabilities with `wled_get_info()`

- **Claude Desktop Integration**:
  - Restart Claude Desktop after updating MCP configuration
  - Check that Python is in your system PATH
  - Verify the MCP server starts without errors

### Testing Your Setup

Run the test script to verify everything works:

```bash
python examples/test_server.py
```

This will test basic connectivity and functionality with your WLED device.

## Development

### Project Structure

```
wled_mcp/
├── wled_mcp/
│   ├── __init__.py
│   ├── server.py          # MCP server implementation
│   └── wled_client.py     # WLED HTTP client
├── examples/
│   └── test_server.py     # Test script
├── pyproject.toml         # Project configuration
└── README.md
```

### Contributing

The server uses WLED's JSON API for reliable communication and supports all standard WLED features. Contributions welcome!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### MIT License Summary

- ✅ Commercial use allowed
- ✅ Modification allowed
- ✅ Distribution allowed
- ✅ Private use allowed
- ❌ No liability or warranty provided
