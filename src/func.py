import geopy.distance
from . import parameter as param
prm = param.Para()
def decayfunc(time_inf,time_ref):
    """Return the decayed score for infection."""

    return 1

def proximityfunc(lat1, long1, lat2,long2):
    """ 
    Check two node's cordinates for possibility of infection.  
  
    Parameters: 
    lat1 (decimal): Latitude coordinate 1
    long1 (decimal): Longitude coordinate 1
    lat2 (decimal): Latitude coordinate 2
    long2 (decimal): Longitude coordinate 2

    Returns: 
    bool: return 1 and 0 for infection possibility
  
    """

    threshold= prm.infectdist
    distance=geopy.distance.geodesic((lat1, long1), (lat2,long2)).m
    if (distance <= threshold):
        return 1
    else:
        return 0