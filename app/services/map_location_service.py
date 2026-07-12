from app.schemas.map_location import MapLocationPoint


UNKNOWN_LOCATION_SLUG = 'unknown'


class MapLocationService:
    def __init__(self):
        """Store calibrated Dota map location points."""
        self.locations = [
            MapLocationPoint('radiant_fountain', -6756, -6550, 1300),
            MapLocationPoint('radiant_throne', -5599, -5000, 900),
            MapLocationPoint('radiant_t4', -5544, -4826, 900),
            MapLocationPoint('radiant_mid_t3', -4849, -4381, 1200),
            MapLocationPoint('radiant_mid_t2', -3269, -2768, 1200),
            MapLocationPoint('radiant_mid_t1', -1717, -1399, 1300),
            MapLocationPoint('mid_river', -511, -430, 1300),
            MapLocationPoint('dire_mid_t1', 628, 504, 1300),
            MapLocationPoint('radiant_triangle', -3679, -1683, 1800),
            MapLocationPoint('radiant_triangle', -3213, -419, 1800),
            MapLocationPoint('radiant_triangle', -3956, 822, 1800),
            MapLocationPoint('radiant_triangle', -4773, -57, 1800),
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
            MapLocationPoint('dire_mid_t2', 2381, 1980, 1600)
        ]

    def get_location_slug(self, xpos: int | float | None, ypos: int | float | None):
        """Return calibrated map location slug for coordinates."""
        if not isinstance(xpos, (int, float)) or not isinstance(ypos, (int, float)):
            return UNKNOWN_LOCATION_SLUG

        closest_location = None
        closest_distance = None
        for location in self.locations:
            # Use squared distance because exact distance is not needed for nearest-point selection.
            distance = (xpos - location.xpos) ** 2 + (ypos - location.ypos) ** 2
            if closest_distance is None or distance < closest_distance:
                closest_location = location
                closest_distance = distance

        if closest_location is None or closest_distance is None:
            return UNKNOWN_LOCATION_SLUG
        if closest_distance > closest_location.radius ** 2:
            return UNKNOWN_LOCATION_SLUG
        return closest_location.slug


map_location_service = MapLocationService()
