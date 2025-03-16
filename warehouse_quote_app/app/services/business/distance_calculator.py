from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
import math

@dataclass
class Location:
    postcode: str
    suburb: str
    state: str
    latitude: float
    longitude: float
    zone: Optional[str] = None

class DistanceCalculator:
    """Calculates distances between Australian postcodes and handles zones."""
    
    def __init__(self):
        self._load_postcode_data()
        self._load_zone_definitions()
        
    def _load_postcode_data(self):
        """Load postcode database with coordinates."""
        # TODO: Load from proper database
        self.postcode_data = {
            "4000": Location("4000", "Brisbane", "QLD", -27.4698, 153.0251, "Brisbane Metro"),
            "4007": Location("4007", "Hamilton", "QLD", -27.4333, 153.0667, "Brisbane Metro"),
            "4172": Location("4172", "Murarrie", "QLD", -27.4539, 153.1041, "Brisbane Metro"),
            "4300": Location("4300", "Springfield", "QLD", -27.6667, 152.9167, "Greater Brisbane"),
            "4500": Location("4500", "Strathpine", "QLD", -27.3000, 152.9833, "Greater Brisbane"),
            # Add more postcodes as needed
        }
        
    def _load_zone_definitions(self):
        """Load zone definitions and pricing."""
        self.zones = {
            "Brisbane Metro": {
                "description": "Brisbane Metropolitan Area",
                "base_rate": "local",
                "postcodes": ["4000", "4007", "4172"]  # Example postcodes
            },
            "Greater Brisbane": {
                "description": "Greater Brisbane Region",
                "base_rate": "local",
                "postcodes": ["4300", "4500"]  # Example postcodes
            },
            "SEQ": {
                "description": "South East Queensland",
                "base_rate": "long_haul",
                "postcodes": []  # Add relevant postcodes
            }
        }
        
        # Define zone relationships for pricing
        self.zone_relationships = {
            ("Brisbane Metro", "Brisbane Metro"): "local",
            ("Brisbane Metro", "Greater Brisbane"): "local",
            ("Greater Brisbane", "Greater Brisbane"): "local",
            ("Brisbane Metro", "SEQ"): "long_haul",
            ("Greater Brisbane", "SEQ"): "long_haul"
        }
    
    def calculate_distance(
        self,
        from_postcode: str,
        to_postcode: str
    ) -> Tuple[float, str]:
        """
        Calculate distance between postcodes and determine transport type.
        Returns (distance_km, transport_type).
        """
        # Get locations
        from_loc = self.postcode_data.get(from_postcode)
        to_loc = self.postcode_data.get(to_postcode)
        
        if not from_loc or not to_loc:
            raise ValueError(
                f"Invalid postcode: {from_postcode if not from_loc else to_postcode}"
            )
        
        # Calculate direct distance
        distance = self._calculate_haversine_distance(
            from_loc.latitude, from_loc.longitude,
            to_loc.latitude, to_loc.longitude
        )
        
        # Determine transport type based on zones
        transport_type = self._determine_transport_type(
            from_loc.zone,
            to_loc.zone
        )
        
        return distance, transport_type
    
    def _calculate_haversine_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees).
        """
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of earth in kilometers
        r = 6371
        
        # Calculate and add 20% for road distance vs direct distance
        return c * r * 1.2
    
    def _determine_transport_type(
        self,
        from_zone: Optional[str],
        to_zone: Optional[str]
    ) -> str:
        """Determine transport type based on zone relationship."""
        if not from_zone or not to_zone:
            return "long_haul"  # Default to long haul if zones unknown
            
        # Check zone relationship
        relationship = self.zone_relationships.get((from_zone, to_zone))
        if not relationship:
            # Check reverse relationship
            relationship = self.zone_relationships.get((to_zone, from_zone))
            
        return relationship or "long_haul"
    
    def get_zone_info(self, postcode: str) -> Optional[Dict]:
        """Get zone information for a postcode."""
        location = self.postcode_data.get(postcode)
        if not location or not location.zone:
            return None
            
        zone = self.zones.get(location.zone)
        if not zone:
            return None
            
        return {
            "zone": location.zone,
            "description": zone["description"],
            "base_rate": zone["base_rate"]
        }
    
    def suggest_alternatives(self, postcode: str) -> List[Location]:
        """Suggest alternative postcodes if exact match not found."""
        # TODO: Implement fuzzy matching or nearby postcode suggestions
        return []
    
    def validate_postcode(self, postcode: str) -> bool:
        """Validate if a postcode exists in our database."""
        return postcode in self.postcode_data
