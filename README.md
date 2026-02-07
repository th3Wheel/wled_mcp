# WLED MCP Server

A Model Context Protocol (MCP) server for controlling WLED devices through LLM interactions. This server enables Claude and other LLMs to directly control your WLED smart lighting devices with natural language commands.

**NEW: Now supports multiple WLED devices and Docker deployment!**

## Features

- **Multi-Device Support**: Control multiple WLED devices simultaneously with named device management
- **Docker Support**: Easy deployment with Docker and docker-compose
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

### Option 1: Standard Python Installation

1. Clone this repository:

```bash
git clone https://github.com/mrkprdo/wled_mcp.git
cd wled_mcp
```

2. Install dependencies:

```bash
pip install -e .
```

### Option 2: Docker Installation (Recommended for Multi-Device)

1. Clone this repository:

```bash
git clone https://github.com/mrkprdo/wled_mcp.git
cd wled_mcp
```

2. Configure your devices in `docker-compose.yml` (see Configuration section below)

3. Build and run with docker-compose:

```bash
docker-compose up -d
```

Or build the Docker image manually:

```bash
docker build -t wled-mcp .
docker run -e WLED_DEVICES='{"living_room":"192.168.1.100","bedroom":"192.168.1.101"}' --network host wled-mcp
```

## Quick Start

### 1. Configure Your WLED Device(s)

#### Single Device (Backward Compatible)

Set your WLED device IP address:

```bash
export WLED_HOST=192.168.1.100
```

#### Multiple Devices - Option A: JSON Configuration

```bash
export WLED_DEVICES='{"living_room":"192.168.1.100","bedroom":"192.168.1.101","kitchen":"192.168.1.102"}'
```

#### Multiple Devices - Option B: Individual Environment Variables

```bash
export WLED_DEVICE_LIVING_ROOM=192.168.1.100
export WLED_DEVICE_BEDROOM=192.168.1.101
export WLED_DEVICE_KITCHEN=192.168.1.102
```

### 2. Test the Connection

#### Single Device Test

```bash
python examples/test_server.py
```

#### Multi-Device Test

```bash
export WLED_DEVICE_LIVING_ROOM=192.168.1.100
export WLED_DEVICE_BEDROOM=192.168.1.101
python examples/test_multi_device.py
```

### 3. Use with Claude Desktop

#### Single Device Configuration

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

#### Multi-Device Configuration

Add this configuration to your Claude Desktop MCP settings:

```json
{
  "mcpServers": {
    "wled": {
      "command": "python",
      "args": ["-m", "wled_mcp.server"],
      "env": {
        "WLED_DEVICES": "{\"living_room\":\"192.168.1.100\",\"bedroom\":\"192.168.1.101\",\"kitchen\":\"192.168.1.102\"}"
      }
    }
  }
}
```

Or use the example configuration file:

```bash
cp mcp_client_config.multi-device.json ~/.config/claude/config.json
```

### 4. Start Controlling Your WLED

You can now ask Claude to control your WLED devices with natural language:

#### Single Device Commands:
- "Turn on my WLED and set it to bright blue"
- "Set a rainbow effect with medium speed"
- "Dim the lights to 25% brightness"

#### Multi-Device Commands:
- "Turn on the living room lights and set them to warm white"
- "Set the bedroom to a soft blue color"
- "Turn off all devices" (Claude will iterate through your devices)
- "Set the kitchen lights to rainbow effect"
- "Show me all configured devices"
- "What's the status of the bedroom lights?"

## Available Tools

### Device Management

- `wled_list_devices()` - List all configured WLED devices with their names and IP addresses

### Basic Controls

- `wled_set_power(on: bool, device_name?: str, direct_ip?: str)` - Turn device on/off
- `wled_set_brightness(brightness: int, device_name?: str, direct_ip?: str)` - Set brightness (0-255)
- `wled_set_color(r: int, g: int, b: int, device_name?: str, direct_ip?: str)` - Set RGB color (0-255 each)

### Effects & Animation

- `wled_set_effect(effect_id: int, speed?: int, intensity?: int, device_name?: str, direct_ip?: str)` - Set lighting effect with optional speed/intensity (0-255)
- `wled_get_effects(device_name?: str, direct_ip?: str)` - List all available effects with IDs and names
- `wled_get_palettes(device_name?: str, direct_ip?: str)` - List available color palettes

### Presets

- `wled_get_presets(device_name?: str, direct_ip?: str)` - List all saved presets with IDs and names
- `wled_activate_preset(preset_id: int, device_name?: str, direct_ip?: str)` - Activate a preset by ID (1-250)

### Device Information

- `wled_get_info(device_name?: str, direct_ip?: str)` - Get device information (name, version, LED count, capabilities)
- `wled_get_state(device_name?: str, direct_ip?: str)` - Get current device state (power, brightness, color, effect)

### Advanced

- `wled_set_state(state_json: str, device_name?: str, direct_ip?: str)` - Set device state using raw JSON for complex operations

_Note: All tools support two optional parameters for targeting devices:_
- _`device_name`: Reference a pre-configured device from your registry (e.g., "living_room")_
- _`direct_ip`: Specify an IP address directly for ad-hoc connections (e.g., "192.168.1.105")_
- _If neither is provided, the default device or `WLED_HOST` environment variable will be used._
- _`direct_ip` takes precedence if both parameters are provided._

## Example Usage

### Via Claude Desktop

Once configured, you can use natural language commands:

#### Single Device:
```
"Turn on my WLED lights and set them to a soft purple color"
"Set a rainbow effect with slow speed"
"Show me all available presets"
"Activate preset 5"
"Set brightness to 50%"
```

#### Multi-Device:
```
"List all my WLED devices"
"Turn on the living room lights"
"Set the bedroom lights to blue"
"What's the current state of the kitchen lights?"
"Turn off all the lights in the bedroom"
"Set living room to rainbow effect and bedroom to solid red"
```

### Direct API Usage

```python
# Single device - backward compatible
await wled_set_power(True)
await wled_set_color(128, 0, 128)

# Multi-device - using device names from registry
await wled_set_power(True, device_name="living_room")
await wled_set_color(255, 0, 0, device_name="bedroom")

# Ad-hoc connection - using direct IP (no configuration needed)
await wled_set_color(0, 255, 0, direct_ip="192.168.1.105")

# Set rainbow effect with custom speed
await wled_set_effect(9, speed=150, intensity=200, device_name="kitchen")

# Get device info
info = await wled_get_info(device_name="living_room")

# List all devices
devices = await wled_list_devices()

# Activate a preset
await wled_activate_preset(3, device_name="bedroom")
```

## Docker Deployment

### Using Docker Compose (Recommended)

1. Edit `docker-compose.yml` and configure your devices:

```yaml
environment:
  - WLED_DEVICES={"living_room":"192.168.1.100","bedroom":"192.168.1.101"}
```

2. Start the container:

```bash
docker-compose up -d
```

3. View logs:

```bash
docker-compose logs -f
```

4. Stop the container:

```bash
docker-compose down
```

### Using Docker Run

Single device:
```bash
docker build -t wled-mcp .
docker run -d --name wled-mcp --network host \
  -e WLED_HOST=192.168.1.100 \
  wled-mcp
```

Multiple devices:
```bash
docker run -d --name wled-mcp --network host \
  -e WLED_DEVICES='{"living_room":"192.168.1.100","bedroom":"192.168.1.101"}' \
  wled-mcp
```

### Docker with MCP Client

To use with Claude Desktop when running in Docker, you'll need to expose the MCP server. The recommended approach is:

1. Run the container with host networking (as shown above)
2. Configure Claude Desktop to connect to the containerized server

Note: Docker deployment is primarily useful for running the server as a persistent service. For direct Claude Desktop integration, local installation is typically easier.

## Troubleshooting

### Common Issues

- **Connection Errors**:

  - Ensure your WLED devices are powered on and connected to the same network
  - Verify the IP addresses are correct (check your router or WLED web interface)
  - Test connectivity with `ping <WLED_IP>`
  - If using Docker with host networking, ensure the container can access your local network

- **Environment Variable Issues**:

  - Make sure environment variables are set correctly
  - For single device: `export WLED_HOST=192.168.1.100`
  - For multiple devices JSON: `export WLED_DEVICES='{"name":"ip"}'`
  - For multiple devices individual: `export WLED_DEVICE_NAME=192.168.1.100`
  - On Windows: `set WLED_HOST=192.168.1.100`

- **Multi-Device Issues**:

  - Use `wled_list_devices()` to verify devices are loaded correctly
  - Device names are case-insensitive and derived from environment variable names
  - Ensure JSON format is valid when using `WLED_DEVICES`
  - Check logs for device loading messages

- **Docker Issues**:

  - Use `--network host` to allow container to access local network devices
  - Check container logs: `docker logs wled-mcp` or `docker-compose logs`
  - Verify environment variables are passed correctly to container
  - Ensure WLED devices are on the same network as the Docker host

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

#### Single Device:
```bash
export WLED_HOST=192.168.1.100
python examples/test_server.py
```

#### Multiple Devices:
```bash
export WLED_DEVICE_LIVING_ROOM=192.168.1.100
export WLED_DEVICE_BEDROOM=192.168.1.101
python examples/test_multi_device.py
```

This will test basic connectivity and functionality with your WLED device(s).

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
