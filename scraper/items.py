import scrapy


class ProductItem(scrapy.item.Item):
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "description": "A shiny item",
                    "make": "Volvo",
                    "category": "some category",
                    "part_type": "repair kit",
                    "part_number": "12345ABC",
                }
            ]
        }
    }

    make = scrapy.item.Field()
    category = scrapy.item.Field()
    model = scrapy.item.Field()
    part_type = scrapy.item.Field()
    part_number = scrapy.item.Field()
