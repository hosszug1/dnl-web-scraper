from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field

# Represents an ObjectId field in the database.
# It will be represented as a `str` on the model so that it can be serialized to JSON.
PyObjectId = Annotated[str, BeforeValidator(str)]


class Product(BaseModel):
    id: PyObjectId = Field(..., alias="_id")
    make: str = Field(...)
    category: str = Field(...)
    model: str = Field(...)
    part_type: str | None = Field(...)
    part_number: str = Field(...)


class DeleteResponse(BaseModel):
    deleted_count: int = Field(...)
    message: str = Field(...)
