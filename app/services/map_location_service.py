import math

from app.schemas.map_location import MapLocationPoint


UNKNOWN_LOCATION_SLUG = 'unknown'
NEAREST_LOCATION_DISTANCE_LIMIT = 1.35


class MapLocationService:
    def __init__(self):
        """Store calibrated Dota map location points."""
        self.locations = [
            MapLocationPoint('radiant_fountain', -6756, -6550, 1300),
            MapLocationPoint('radiant_throne', -5770, -5300, 1100),
            MapLocationPoint('radiant_safelane_t3', -3381, -5757, 1500),
            MapLocationPoint('radiant_safelane_t2', 227, -5876, 1700),
            MapLocationPoint('radiant_safelane_t1', 3562, -6200, 1600),
            MapLocationPoint('radiant_safelane_jungle', 4035, -8128, 1600),
            MapLocationPoint('radiant_safelane_jungle', 2712, -7482, 1600),
            MapLocationPoint('radiant_safelane_jungle', -266, -7516, 1700),
            MapLocationPoint('radiant_safelane_jungle', -2098, -7649, 1700),
            MapLocationPoint('radiant_safelane_forest', 2783, -5218, 1700),
            MapLocationPoint('radiant_safelane_forest', 2439, -3991, 1700),
            MapLocationPoint('radiant_safelane_forest', 618, -2390, 1700),
            MapLocationPoint('radiant_safelane_forest', 735, -4705, 1700),
            MapLocationPoint('radiant_safelane_forest', -1048, -3992, 1700),
            MapLocationPoint('radiant_safelane_forest', -1022, -2697, 1700),
            MapLocationPoint('radiant_lotus_pool', 7407, -4196, 1400),
            MapLocationPoint('radiant_tormentor', 7669, -6307, 1400),
            MapLocationPoint('radiant_twin_gate', 6498, -7411, 1400),
            MapLocationPoint('radiant_mid_t3', -4849, -4381, 1200),
            MapLocationPoint('radiant_mid_t2', -3269, -2768, 1200),
            MapLocationPoint('radiant_mid_t1', -1717, -1399, 1300),
            MapLocationPoint('bot_river', 3354, -2509, 1600),
            MapLocationPoint('bot_roshan_pit', 7200, -3150, 1600),
            MapLocationPoint('dire_secret_shop', 4768, -1312, 1000),
            MapLocationPoint('mid_river', -511, -430, 1300),
            MapLocationPoint('dire_mid_t1', 628, 504, 1300),
            MapLocationPoint('top_river', -3354, 2509, 1600),
            MapLocationPoint('top_roshan_pit', -7200, 3150, 1600),
            MapLocationPoint('radiant_secret_shop', -4768, 1312, 1000),
            MapLocationPoint('radiant_triangle', -3900, -350, 2600),
            MapLocationPoint('radiant_offlane_t2', -6328, -851, 1400),
            MapLocationPoint('radiant_offlane_t1', -6162, 1843, 1400),
            MapLocationPoint('radiant_wisdom_rune', -7904, 844, 1300),
            MapLocationPoint('radiant_offlane_jungle', -7864, -1023, 1500),
            MapLocationPoint('radiant_offlane_jungle', -7889, -1664, 1500),
            MapLocationPoint('radiant_offlane_jungle', -8207, -531, 1500),
            MapLocationPoint('radiant_offlane_bridge', -8347, 2699, 1500),
            MapLocationPoint('dire_lotus_pool', -7407, 4196, 1400),
            MapLocationPoint('dire_tormentor', -7669, 6307, 1400),
            MapLocationPoint('dire_twin_gate', -6498, 7411, 1400),
            MapLocationPoint('dire_safelane_jungle', -4035, 8128, 1600),
            MapLocationPoint('dire_safelane_jungle', -2712, 7482, 1600),
            MapLocationPoint('dire_safelane_jungle', 266, 7516, 1700),
            MapLocationPoint('dire_safelane_jungle', 2098, 7649, 1700),
            MapLocationPoint('dire_safelane_t3', 3381, 5757, 1500),
            MapLocationPoint('dire_safelane_t2', -227, 5876, 1700),
            MapLocationPoint('dire_safelane_forest', -2783, 5218, 1700),
            MapLocationPoint('dire_safelane_forest', -2439, 3991, 1700),
            MapLocationPoint('dire_safelane_forest', -618, 2390, 1700),
            MapLocationPoint('dire_safelane_forest', -735, 4705, 1700),
            MapLocationPoint('dire_safelane_forest', 1048, 3992, 1700),
            MapLocationPoint('dire_safelane_forest', 1022, 2697, 1700),
            MapLocationPoint('dire_offlane_t1', 6162, -1843, 1400),
            MapLocationPoint('dire_offlane_t2', 6328, 851, 1400),
            MapLocationPoint('dire_wisdom_rune', 7904, -844, 1300),
            MapLocationPoint('dire_offlane_jungle', 7864, 1023, 1500),
            MapLocationPoint('dire_offlane_jungle', 7889, 1664, 1500),
            MapLocationPoint('dire_offlane_jungle', 8207, 531, 1500),
            MapLocationPoint('dire_offlane_bridge', 8347, -2699, 1500),
            MapLocationPoint('dire_triangle', 3900, 350, 2600),
            MapLocationPoint('dire_mid_t2', 2381, 1980, 1600),
            MapLocationPoint('dire_mid_t3', 4849, 4381, 1200),
            MapLocationPoint('dire_throne', 5770, 5300, 1100),
            MapLocationPoint('dire_fountain', 6756, 6550, 1300)
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
