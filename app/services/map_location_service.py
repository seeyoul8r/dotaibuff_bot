import math

from app.schemas.map_location import MapLocationPoint


UNKNOWN_LOCATION_SLUG = 'unknown'
NEAREST_LOCATION_DISTANCE_LIMIT = 1.35


class MapLocationService:
    def __init__(self):
        """Store calibrated Dota map location points."""
        self.locations = [
            MapLocationPoint('radiant_highground', -6543, -6258, 3547),
            MapLocationPoint('radiant_lotus_pool', 7554, -4371, 1261),
            MapLocationPoint('radiant_tormentor', 7802, -6206, 1076),
            MapLocationPoint('radiant_twin_gate', 6498, -7411, 1055),
            MapLocationPoint('bot_roshan_pit', 3060, -2790, 1049),
            MapLocationPoint('dire_secret_shop', 4723, -1667, 863),
            MapLocationPoint('top_roshan_pit', -3015, 2393, 1007),
            MapLocationPoint('radiant_secret_shop', -5225, 1547, 1054),
            MapLocationPoint('radiant_wisdom_rune', -7929, 1854, 779, 1386, 0),
            MapLocationPoint('radiant_statue', -7936, -1285, 784, 1720, 0),
            MapLocationPoint('dire_lotus_pool', -7614, 4596, 1187),
            MapLocationPoint('dire_tormentor', -7592, 6521, 1000),
            MapLocationPoint('dire_twin_gate', -6416, 7839, 853),
            MapLocationPoint('dire_safelane', -1734, 6169, 4944, 861, 0),
            MapLocationPoint('dire_offlane', 6281, -1891, 861, 4285, 0),
            MapLocationPoint('dire_wisdom_rune', 8071, -1831, 879, 1588, 0),
            MapLocationPoint('dire_triangle', 3547, -4, 1865),
            MapLocationPoint('dire_highground', 6288, 5974, 3793),
            MapLocationPoint('dire_mines', -1202, 7697, 4240, 772, 0),
            MapLocationPoint('radiant_hardlane', -6483, 1292, 809, 4524, 0),
            MapLocationPoint('radiant_midlane', -2273, -2071, 2622, 731, 45),
            MapLocationPoint('dire_midlane', 1682, 1487, 2866, 683, 45),
            MapLocationPoint('dire_graveyard', 8056, 903, 900, 1408, 0),
            MapLocationPoint('radiant_triangle', -4019, -566, 2107, 1383, 55),
            MapLocationPoint('radiant_safelane', 1390, -6453, 4899, 861, 0),
            MapLocationPoint('radiant_well', 1427, -8124, 4644, 951, 0),
            MapLocationPoint('radiant_jungle_big', -423, -3996, 2719, 2270, 0),
            MapLocationPoint('radiant_jungle_small', 3966, -4566, 1715, 1296, 0),
            MapLocationPoint('dire_jungle_big', 41, 3846, 2974, 1858, 0),
            MapLocationPoint('dire_jungle_small', -4573, 4348, 1393)
        ]

    def get_location_slug(self, xpos: int | float | None, ypos: int | float | None):
        """Return calibrated map location slug for coordinates."""
        if not isinstance(xpos, (int, float)) or not isinstance(ypos, (int, float)):
            return UNKNOWN_LOCATION_SLUG

        closest_location = None
        closest_distance = None
        for location in self.locations:
            distance = self.get_location_distance(xpos, ypos, location)
            # Use normalized ellipse distance so circles and ovals are comparable.
            if closest_distance is None or distance < closest_distance:
                closest_location = location
                closest_distance = distance

        if closest_location is None or closest_distance is None or closest_distance > NEAREST_LOCATION_DISTANCE_LIMIT:
            return UNKNOWN_LOCATION_SLUG
        return closest_location.slug

    def get_location_distance(self, xpos: int | float, ypos: int | float, location: MapLocationPoint):
        """Return normalized squared distance from point to location zone."""
        radius_y = location.radius if location.radius_y is None else location.radius_y
        rotation = math.radians(location.rotation)
        delta_x = xpos - location.xpos
        delta_y = ypos - location.ypos
        # Rotate the point into the zone's local axes before ellipse normalization.
        local_x = delta_x * math.cos(rotation) + delta_y * math.sin(rotation)
        local_y = -delta_x * math.sin(rotation) + delta_y * math.cos(rotation)
        return (local_x / location.radius) ** 2 + (local_y / radius_y) ** 2


map_location_service = MapLocationService()
