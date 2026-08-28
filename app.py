import os
import requests
from fastmcp import FastMCP

mcp = FastMCP("MobileWorkspaceServer")

@mcp.tool()
def get_live_weather(location: str = "Bayonet Point, FL") -> dict:
    """Fetches real-time weather using Open-Meteo."""
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={requests.utils.quote(location)}&count=1&language=en&format=json"
        geo_res = requests.get(geo_url, timeout=5).json()

        if not geo_res.get("results"):
            return {"error": f"Could not find coordinates for '{location}'."}

        place = geo_res["results"][0]
        lat = place["latitude"]
        lon = place["longitude"]
        resolved_name = f"{place.get('name')}, {place.get('admin1', '')} ({place.get('country_code', '')})"

        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m"
            f"&temperature_unit=fahrenheit&wind_speed_unit=mph&precipitation_unit=inch"
        )
        weather_res = requests.get(weather_url, timeout=5).json()
        current = weather_res.get("current", {})

        wmo_codes = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Fog", 48: "Depositing rime fog", 51: "Light drizzle", 61: "Slight rain",
            63: "Moderate rain", 65: "Heavy rain", 80: "Rain showers", 95: "Thunderstorm"
        }
        condition = wmo_codes.get(current.get("weather_code", 0), "Variable conditions")

        return {
            "location": resolved_name,
            "temperature_f": current.get("temperature_2m"),
            "feels_like_f": current.get("apparent_temperature"),
            "condition": condition,
            "humidity": f"{current.get('relative_humidity_2m')}%",
            "wind_speed": f"{current.get('wind_speed_10m')} mph",
            "precipitation_in": current.get("precipitation"),
        }
    except Exception as e:
        return {"error": f"Failed to fetch live weather: {str(e)}"}

@mcp.tool()
def get_morning_briefing(user: str = "primary") -> dict:
    """Returns workspace calendar blocks and urgent tasks."""
    return {
        "user": user,
        "schedule": [
            {"time": "09:30 AM", "title": "Team Sync & Standup", "virtual": True},
            {"time": "02:00 PM", "title": "Grid & Deployment Review", "virtual": True}
        ],
        "urgent_tasks": [
            {"id": "tsk-101", "task": "Verify mobile MCP cloud endpoint"},
            {"id": "tsk-102", "task": "Check DeBERTa INT8 verification pipeline"}
        ]
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    mcp.run(transport="sse", host="0.0.0.0", port=port)
