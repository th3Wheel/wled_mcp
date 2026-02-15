"""WLED device client for HTTP and JSON API interactions."""

import json
from typing import Any, Dict, Optional
import httpx


class WLEDClient:
    """Client for interacting with WLED devices via HTTP and JSON APIs."""
    
    def __init__(self, host: str, timeout: float = 10.0):
        """Initialize WLED client.
        
        Args:
            host: WLED device IP address or hostname
            timeout: Request timeout in seconds
        """
        self.host = host.rstrip('/')
        self.timeout = timeout
        
    async def get_info(self) -> Dict[str, Any]:
        """Get device information."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://{self.host}/json/info",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
    
    async def get_state(self) -> Dict[str, Any]:
        """Get current device state."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://{self.host}/json/state",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
    
    async def set_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Set device state via JSON API.
        
        Args:
            state: State object to apply
            
        Returns:
            Updated state from device
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://{self.host}/json/state",
                json=state,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
    
    async def set_power(self, on: bool) -> Dict[str, Any]:
        """Turn device on or off."""
        return await self.set_state({"on": on})
    
    async def set_brightness(self, brightness: int) -> Dict[str, Any]:
        """Set brightness (0-255)."""
        if not 0 <= brightness <= 255:
            raise ValueError("Brightness must be between 0 and 255")
        return await self.set_state({"bri": brightness})
    
    async def set_color(self, r: int, g: int, b: int) -> Dict[str, Any]:
        """Set RGB color (0-255 each)."""
        if not all(0 <= c <= 255 for c in [r, g, b]):
            raise ValueError("RGB values must be between 0 and 255")
        return await self.set_state({"seg": [{"col": [[r, g, b]]}]})
    
    async def set_effect(self, effect_id: int, speed: Optional[int] = None, 
                        intensity: Optional[int] = None) -> Dict[str, Any]:
        """Set lighting effect.
        
        Args:
            effect_id: Effect ID (0-101+)
            speed: Effect speed (0-255)
            intensity: Effect intensity (0-255)
        """
        seg_data = {"fx": effect_id}
        if speed is not None:
            if not 0 <= speed <= 255:
                raise ValueError("Speed must be between 0 and 255")
            seg_data["sx"] = speed
        if intensity is not None:
            if not 0 <= intensity <= 255:
                raise ValueError("Intensity must be between 0 and 255")
            seg_data["ix"] = intensity
            
        return await self.set_state({"seg": [seg_data]})
    
    async def get_effects(self) -> Dict[str, Any]:
        """Get available effects metadata."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://{self.host}/json/fxdata",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
    
    async def get_palettes(self) -> Dict[str, Any]:
        """Get available color palettes."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://{self.host}/json/pal", 
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
    
    async def get_presets(self) -> Dict[str, Any]:
        """Get available presets."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://{self.host}/presets.json",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
    
    async def activate_preset(self, preset_id: int) -> Dict[str, Any]:
        """Activate a preset by ID.
        
        Args:
            preset_id: Preset ID to activate (1-250)
            
        Returns:
            Updated state from device
        """
        if not 1 <= preset_id <= 250:
            raise ValueError("Preset ID must be between 1 and 250")
        return await self.set_state({"ps": preset_id})
    
    async def get_config(self) -> Dict[str, Any]:
        """Get device configuration.
        
        Returns:
            Full device configuration including hardware, network, and segment settings
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://{self.host}/json/cfg",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
    
    async def get_segments(self) -> Dict[str, Any]:
        """Get all segments from device state.
        
        Returns:
            Dictionary with segments array and count
        """
        state = await self.get_state()
        segments = state.get("seg", [])
        return {
            "segments": segments,
            "count": len(segments)
        }
    
    async def get_segment(self, segment_id: int) -> Dict[str, Any]:
        """Get specific segment by ID.
        
        Args:
            segment_id: Segment ID to retrieve
            
        Returns:
            Segment data or error if not found
        """
        if segment_id < 0:
            raise ValueError("Segment ID must be non-negative")
        
        state = await self.get_state()
        segments = state.get("seg", [])
        
        for segment in segments:
            if segment.get("id") == segment_id:
                return segment
        
        raise ValueError(f"Segment {segment_id} not found. Available segments: {[s.get('id') for s in segments]}")
    
    async def set_segment(self, segment_id: int, segment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update segment configuration.
        
        Args:
            segment_id: Segment ID to update
            segment_data: Segment properties to update (e.g., col, fx, start, stop, on, etc.)
            
        Returns:
            Updated state from device
        """
        if segment_id < 0:
            raise ValueError("Segment ID must be non-negative")
        
        # Ensure segment_id is included in the data and takes precedence
        segment_update = {**segment_data, "id": segment_id}
        return await self.set_state({"seg": [segment_update]})
    
    async def create_segment(self, start: int, stop: int, segment_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a new segment.
        
        Args:
            start: Start LED index (inclusive)
            stop: Stop LED index (exclusive)
            segment_data: Optional segment properties (colors, effects, etc.)
            
        Returns:
            Updated state from device
        """
        if start < 0:
            raise ValueError("Start index must be non-negative")
        if stop < 0:
            raise ValueError("Stop index must be non-negative")
        if start >= stop:
            raise ValueError("Start index must be less than stop index")
        
        if segment_data:
            # Ensure explicit parameters take precedence over any keys in segment_data
            new_segment = {**segment_data, "start": start, "stop": stop}
        else:
            new_segment = {
                "start": start,
                "stop": stop,
            }
        
        return await self.set_state({"seg": [new_segment]})
    
    async def delete_segment(self, segment_id: int) -> Dict[str, Any]:
        """Delete a segment by ID.
        
        Args:
            segment_id: Segment ID to delete
            
        Returns:
            Updated state from device
        """
        if segment_id < 0:
            raise ValueError("Segment ID must be non-negative")
        
        return await self.set_state({"seg": [{"id": segment_id, "stop": 0}]})