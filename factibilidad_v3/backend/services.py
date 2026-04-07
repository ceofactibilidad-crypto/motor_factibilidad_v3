import httpx

async def geocode_address(address: str):
    """Hits Nominatim to get lat/lon. If it fails or is rate-limited, fallback to Mock Data."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": f"{address}, Santiago, Chile", "format": "json", "limit": 1}
    headers = {"User-Agent": "UrbanoAnalyticsMVP/1.0"}
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params, headers=headers, timeout=5.0)
            if resp.status_code == 200 and len(resp.json()) > 0:
                data = resp.json()[0]
                return {
                    "lat": float(data["lat"]),
                    "lon": float(data["lon"]),
                    "address_display": data.get("display_name", address)
                }
    except Exception as e:
        print(f"Geocoding Error: {e}")
            
    # Mock Fallback to Providencia Center if overpass fails
    return {
        "lat": -33.435,
        "lon": -70.615,
        "address_display": address + " (Ubicación Simulada)"
    }
