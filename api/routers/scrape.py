from clients.mongo import MongoDB
from constants import MONGO_SCRAPED_COLLECTION
from dependencies import get_db
from fastapi import APIRouter, Depends, Query
from fastapi_pagination import Page
from fastapi_pagination.ext.motor import paginate as motor_paginate
from models import Product

router = APIRouter(
    prefix="/scrape",
    tags=["Scraper"],
    responses={404: {"description": "Not found"}},
)


@router.get("/products", response_model=Page[Product])
async def get_products(
    model: str = Query(
        None, title="Model", description="Filter by model", min_length=1
    ),
    category: str = Query(
        None, title="Category", description="Filter by category", min_length=1
    ),
    make: str = Query(None, title="Make", description="Filter by make", min_length=1),
    part_number: str = Query(
        None, title="Part Number", description="Filter by part number", min_length=1
    ),
    part_type: str = Query(
        None, title="Part Type", description="Filter by part type", min_length=0
    ),
    db: MongoDB = Depends(get_db),
) -> Page[Product]:
    """
    Retrieve a list of products from the database, based on different query parameters.
    """
    # Constructing the filter based on provided query parameters
    filter_query = {}
    if model:
        filter_query["model"] = model
    if category:
        filter_query["category"] = category
    if make:
        filter_query["make"] = make
    if part_number:
        filter_query["part_number"] = part_number
    if part_type:
        filter_query["part_type"] = part_type

    scraped_col = db.get_collection(MONGO_SCRAPED_COLLECTION)

    result = await motor_paginate(scraped_col, query_filter=filter_query)

    return result
