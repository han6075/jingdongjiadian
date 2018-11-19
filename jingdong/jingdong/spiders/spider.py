# -*- coding: utf-8 -*-
import scrapy
import re
import json
from jingdong.items import JingdongItem
import json


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    allowed_domains = ['jd.com']
    start_urls = ['https://jiadian.jd.com/']

    def parse(self, response):
        navThirds = re.findall("navThird\d+:(.*?\}\]),", response.text, re.S)
        for navThird in navThirds:
            js_navThird = json.loads(navThird)
            for navThird in js_navThird:
                category_2_name = navThird.get("NAME")
                for i, children in enumerate(navThird.get("children")):
                    category_3_name = children.get("NAME")
                    category_3_url = children.get("URL")
                    if i < 2:
                        yield scrapy.Request(url=category_3_url, method="GET", dont_filter=True,
                                     meta={"category_2_name": category_2_name,
                                           "category_3_name": category_3_name}, callback=self.parse_product_list)

    def parse_product_list(self, response):
        page = "1"
        pros = response.xpath("//li[@class='gl-item']/div[contains(@class, 'j-sku-item')]")
        for pro in pros:
            pro_id = pro.xpath("./@data-sku").extract_first()


            if pro.xpath("./div[@class='p-img']/a/img[last()]/@src"):
                head_img = "https:" + pro.xpath("./div[@class='p-img']/a/img[last()]/@src").extract_first()
            elif pro.xpath("./div[@class='p-img']/a/img[last()]/@data-lazy-img"):
                head_img = "https:" + pro.xpath("./div[@class='p-img']/a/img[last()]/@data-lazy-img").extract_first()
            else:
                head_img = ""

            pro_url = "https://item.jd.com/" + pro_id + ".html"

            pro_name = pro.xpath("./div[@class='p-name']/a/em").xpath("string(.)").extract_first()

            shop_id = pro.xpath("./@jdzy_shop_id").extract_first()

            shop_url = "https://mall.jd.com/index-{0}.html".format(shop_id)

            category_1 = u"家用电器"
            category_2 = response.meta.get("category_2_name")
            category_3 = response.meta.get("category_3_name")


            # 价格接口
            # https://p.3.cn/prices/mgets?skuIds=J_7641991
            price_inf_url = "https://p.3.cn/prices/mgets?skuIds=J_" + pro_id
            yield scrapy.Request(url=price_inf_url, method="GET", dont_filter=True, callback=self.parse_price,
                                 meta={"pro_id":pro_id,
                                       "head_img": head_img,
                                       "pro_url": pro_url,
                                       "pro_name": pro_name,
                                       "shop_id": shop_id,
                                       "shop_url": shop_url,
                                       "category_1": category_1,
                                       "category_2": category_2,
                                       "category_3": category_3,
                                    })

            # 翻译操作

            if page == "1":
                page = "2"
                max_page_num_str = response.xpath("//div[@id='J_topPage']//i/text()").extract_first()
                max_page_num = int(max_page_num_str)
                for page_num in range(2, max_page_num + 1):
                    next_url = re.sub("page=\d+", "page=" + str(page), response.url)
                    yield scrapy.Request(url=next_url, method="GET", dont_filter=True,
                                         meta={"category_2_name": response.meta.get("category_2_name"),
                                               "category_3_name": response.meta.get("category_3_name")},
                                         callback=self.parse_product_list)





    def parse_price(self, response):
        # 价格源码
        # price = parseFloat(pInfo.p.substring(0, 6)) | | 0
        prices = json.loads(response.text)
        price1 = prices[0].get("p")
        price2 = price1[0: 6]
        price3 = float(price2)
        price = "%.2f" % price3

        p = response.meta
        p['price'] = price

        # 京东店铺接口：
        # https: // rms.shop.jd.com / json / pop / shopInfo.action?ids = 65779
        shop_id = p.get("shop_id")
        shop_inf_url = "https://rms.shop.jd.com/json/pop/shopInfo.action?ids=" + shop_id
        yield scrapy.Request(url=shop_inf_url, method="GET", meta=p, dont_filter=False, callback=self.parse_shop)


    def parse_shop(self, response):
        shop_msg = json.loads(response.text)
        shop_name = shop_msg[0].get("name")
        shop_score = shop_msg[0].get("score")
        p = response.meta
        p['shop_name'] = shop_name
        p['shop_score'] = shop_score


        # 评论和数量接口：
        # https: // club.jd.com / comment / productCommentSummaries.action?referenceIds = 7641991
        comment_inf_url = "https://club.jd.com/comment/productCommentSummaries.action?referenceIds=" + p.get("pro_id")
        yield scrapy.Request(url=comment_inf_url, meta=p, method="GET", dont_filter=True, callback=self.parse_comment)

    def parse_comment(self, response):
        comments = json.loads(response.text)
        commentsCount = comments.get("CommentsCount")[0]
        comments_str = commentsCount.get("CommentCountStr")
        good_comments_str = commentsCount.get("GoodCountStr")
        good_comments_rate = commentsCount.get("GoodRate")
        poor_comments_str = commentsCount.get("PoorCountStr")
        poor_comments_rate = commentsCount.get("PoorRate")
        average_score = commentsCount.get("AverageScore")

        item = JingdongItem()
        p = response.meta
        item['pro_id'] = p.get("pro_id")
        item['head_img'] = p.get("head_img")
        item['pro_url'] = p.get("pro_url")
        item['pro_name'] = p.get("pro_name")
        item['shop_id'] = p.get("shop_id")
        if len(item['shop_id']) > 7:
            item['is_ziying'] = u"自营"
        else:
            item['is_ziying'] = u"非自营"


        item['shop_url'] = p.get("shop_url")
        item['category_1'] = p.get("category_1")
        item['category_2'] = p.get("category_2")
        item['category_3'] = p.get("category_3")
        item['pro_price'] = p.get("price")
        item['shop_name'] = p.get("shop_name")
        item['shop_score'] = p.get("shop_score")
        item['comments_str'] = comments_str
        item['good_comments_str'] = good_comments_str
        item['good_comments_rate'] = good_comments_rate
        item['poor_comments_str'] = poor_comments_str
        item['poor_comments_rate'] = poor_comments_rate
        item['average_score'] = average_score

        yield item

