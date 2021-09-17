from main.kakaku.items import Restaurant


class TestRestaurant:
    def test(self):
        item = Restaurant()
        assert item.fields == {"name": {}, "info": {}, "address": {}, "link": {}}
