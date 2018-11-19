# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JingdongItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pro_id = scrapy.Field()

    head_img = scrapy.Field()

    pro_url = scrapy.Field()

    pro_price = scrapy.Field()

    pro_name = scrapy.Field()

    promo_words = scrapy.Field()

    comment = scrapy.Field()

    shop_name = scrapy.Field()

    shop_url = scrapy.Field()

    shop_id = scrapy.Field()

    category_1 = scrapy.Field()

    category_2 = scrapy.Field()

    category_3 = scrapy.Field()

    shop_score = scrapy.Field()

    comments_str = scrapy.Field()

    good_comments_str = scrapy.Field()

    good_comments_rate = scrapy.Field()

    poor_comments_str = scrapy.Field()

    poor_comments_rate = scrapy.Field()

    average_score = scrapy.Field()

    is_ziying = scrapy.Field()

