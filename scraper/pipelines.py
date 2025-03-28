import items
import pymongo
import scrapy.crawler
from itemadapter import ItemAdapter
from scrapy.statscollectors import StatsCollector


class MongoPipeline:
    def __init__(self, uri: str, db: str, collection: str, stats: StatsCollector):
        """Pipeline step for saving spider results into MongoDB.

        Simply dump any new crawl data into a predefined Mongo collection. Also save
        the end of run stats to a separate collection.

        Args:
            uri: the address of the database server (in URI format).
            db: the name of the database.
            collection: the name of the collection.
            stats: use this Scrapy object to fetch the end of run stats.
        """
        self.mongo_uri = uri
        self.mongo_db = db
        self.collection_name = collection
        self.stats_collection_name = "stats"
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            uri=crawler.settings.get("MONGODB_SERVER"),
            db=crawler.settings.get("MONGODB_DB"),
            collection=crawler.settings.get("MONGODB_COLLECTION"),
            stats=crawler.stats,
        )

    def open_spider(self, _):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, _):
        # Save the stats of the crawl at the end of the run
        self.db[self.stats_collection_name].insert_one(self.stats.get_stats())
        self.client.close()

    def process_item(
        self, item: items.ProductItem, _: scrapy.crawler.Crawler
    ) -> items.ProductItem:
        """This is the entry point into this pipeline step, after the spider
        discovers a new data point. We intercept it in this method and send it to the
        database.

        Args:
            item: the crawled data item.
            _: unused.

        Returns:
            Bounces back the crawled data dictionary.
        """
        self.db[self.collection_name].insert_one(ItemAdapter(item).asdict())
        return item
