import requests
import pandas as pd
from geopy.distance import geodesic

def hastane_listesi_al(lat, lon, radius=10000):  # metre cinsinden
    overpass_url = "http://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    (
      node["amenity"="hospital"](around:{radius},{lat},{lon});
      way["amenity"="hospital"](around:{radius},{lat},{lon});
      relation["amenity"="hospital"](around:{radius},{lat},{lon});
    );
    out center;
    """

    response = requests.post(overpass_url, data=query)
    
    if response.status_code != 200:
        return pd.DataFrame(columns=["name", "lat", "lon", "distance_km"])
    
    data = response.json()
    hospitals = []

    for el in data["elements"]:
        name = el["tags"].get("name")
        if not name:
            continue  # 

        lat_ = el.get("lat") or el.get("center", {}).get("lat")
        lon_ = el.get("lon") or el.get("center", {}).get("lon")
        if lat_ and lon_:
            distance = geodesic((lat, lon), (lat_, lon_)).km
            hospitals.append({
                "name": name,
                "lat": lat_,
                "lon": lon_,
                "distance_km": round(distance, 2)
            })

    df = pd.DataFrame(hospitals)
    df = df.sort_values(by="distance_km").head(4).reset_index(drop=True)
    return df
