ITEM_PIPELINES = {
    "pipelines.MongoPipeline": 1,
}

MONGODB_SERVER = "mongodb://localhost:27017"
MONGODB_PORT = 27017
MONGODB_DB = "scraping_db"
MONGODB_COLLECTION = "scraped_items"
CONCURRENT_REQUESTS = 10
