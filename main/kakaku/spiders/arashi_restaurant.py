import scrapy
import re
from kakaku.items import Restaurant

RED_START = "\033[31m"
RED_END = "\033[0m"


def _print_red(message):
    print(RED_START + message + RED_END)


class ArashiRestaurantSpider(scrapy.Spider):
    name = "arashi_restaurant"
    allowed_domains = ["kakaku.com"]
    max_page_num = 139
    current_page_num = max_page_num
    start_urls = [
        "https://kakaku.com/tv/channel=4/programID=23065/category=restaurant/page={}/".format(
            max_page_num
        )
    ]

    def parse(self, response):
        # 現在のページ番号取得
        current_page_num_str = (
            response.css(".navibox ul.count li.now::text").extract_first().strip()
        )

        for post in response.css(".box-bk .pdBtm20"):
            # 店名
            name = post.css(".tvnamebk p::text").extract_first().strip()

            # リンク
            link = ""
            link_element = post.css("a.tvnamebk::attr(href)").extract_first()
            if link_element is not None:
                link = link_element.strip()
            else:
                _print_red("not found link: (page: {} name: {})".format(current_page_num_str, name))

            # 住所
            address = ""
            area_infos = post.css("ul.itemAddress li::text").extract()
            # 文字列要素が複数見つかる場合があるので該当の箇所を見つける
            for area_info in area_infos:
                area_info = area_info.strip()
                if not ("住所" in area_info):
                    continue
                address = area_info[area_info.rfind("住所：") + 3 :]

                p = re.compile("[0-9]+")
                if not (p.search(address)):
                    _print_red(
                        "invalid address: (page: {} name: {} address: {})".format(
                            current_page_num_str, name, address
                        )
                    )
                    # 数値が含まれない場合は、住所検索に店名を使う
                    address = name
                break

            # コメント
            info = ""
            info_element = post.css("div.iteminfo p::text").extract_first()
            if info_element is not None:
                info = info_element.strip()
            else:
                _print_red("not found info: (page: {} name: {})".format(current_page_num_str, name))

            yield Restaurant(
                name=name,
                info=info,
                address=address,
                link=link,
            )

        # 一番古いページまでクローリングしたら終了
        if current_page_num_str == "1":
            return

        # 古いページにさかのぼってクローリング
        self.current_page_num = self.current_page_num - 1
        older_page_num = self.current_page_num
        older_page_link = ArashiRestaurantSpider.start_urls[0].replace(
            "page={}".format(self.max_page_num), "page={}".format(older_page_num)
        )
        _print_red(older_page_link)
        yield scrapy.Request(older_page_link, callback=self.parse)
