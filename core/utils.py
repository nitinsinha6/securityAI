import math
from datetime import datetime, timezone

def haversine_km(lat1, lon1, lat2, lon2):
    if None in (lat1, lon1, lat2, lon2):
        return None
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def parse_ts(ts):
    if isinstance(ts, str):
        return datetime.fromisoformat(ts.replace('Z','+00:00'))
    return ts

def is_off_hours(dt, start_hour=8, end_hour=18):
    h = dt.hour
    if start_hour <= end_hour:
        return not (start_hour <= h < end_hour)
    else:
        return not (h >= start_hour or h < end_hour)
