from unittest.mock import AsyncMock, MagicMock

import pytest
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)

from api.clients.mongo import MongoDB
from api.constants import MONGO_SCRAPED_COLLECTION


@pytest.fixture
def mock_motor_client(mocker):
    """Create a mock for the AsyncIOMotorClient."""
    mock_client = MagicMock(spec=AsyncIOMotorClient)
    mock_db = MagicMock(spec=AsyncIOMotorDatabase)
    mock_collection = MagicMock(spec=AsyncIOMotorCollection)

    # Setup the chain of mocks
    mocker.patch("motor.motor_asyncio.AsyncIOMotorClient", return_value=mock_client)
    mock_client.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = mock_collection

    return mock_client, mock_db, mock_collection


@pytest.fixture
def mongo_db(mock_motor_client):
    """Create a MongoDB instance with mocked client."""
    mock_client, _, _ = mock_motor_client
    mongo = MongoDB(mongo_uri="mongodb://localhost:27017", db_name="test_db")
    mongo.client = mock_client
    return mongo


class TestMongoDB:
    """Tests for the MongoDB client class."""

    def test_init(self):
        """Test MongoDB initialization."""
        mongo = MongoDB(
            mongo_uri="mongodb://localhost:27017", db_name="test_db"
        )
        assert mongo.mongo_uri == "mongodb://localhost:27017"
        assert mongo.db_name == "test_db"
        assert mongo.client is None

    @pytest.mark.asyncio
    async def test_connect(self, mocker):
        """Test connecting to MongoDB."""
        mock_client = MagicMock(spec=AsyncIOMotorClient)
        mocker.patch("motor.motor_asyncio.AsyncIOMotorClient", return_value=mock_client)

        mongo = MongoDB(
            mongo_uri="mongodb://localhost:27017", db_name="test_db"
        )
        await mongo.connect()

        assert mongo.client is not None

    @pytest.mark.asyncio
    async def test_connect_failure(self, mocker):
        """Test handling connection failure."""
        mocker.patch(
            "motor.motor_asyncio.AsyncIOMotorClient",
            side_effect=Exception("Connection failed"),
        )

        mongo = MongoDB(
            mongo_uri="mongodb://localhost:27017", db_name="test_db"
        )

        with pytest.raises(Exception, match="Connection failed"):
            await mongo.connect()

    @pytest.mark.asyncio
    async def test_disconnect(self, mongo_db):
        """Test disconnecting from MongoDB."""
        mongo_db.client = MagicMock()
        mongo_db.client.close = AsyncMock()

        await mongo_db.disconnect()

        mongo_db.client.close.assert_called_once()
        assert mongo_db.client is None

    def test_get_collection(self, mongo_db, mock_motor_client):
        """Test getting a collection."""
        mock_client, mock_db, mock_collection = mock_motor_client

        collection = mongo_db.get_collection(MONGO_SCRAPED_COLLECTION)

        mock_client.__getitem__.assert_called_with("test_db")
        mock_db.__getitem__.assert_called_with(MONGO_SCRAPED_COLLECTION)
        assert collection == mock_collection

    @pytest.mark.asyncio
    async def test_find_one(self, mongo_db, mock_motor_client):
        """Test finding a single document."""
        _, _, mock_collection = mock_motor_client
        mock_collection.find_one = AsyncMock(
            return_value={"_id": "123", "name": "test"}
        )

        result = await mongo_db.find_one(MONGO_SCRAPED_COLLECTION, {"name": "test"})

        mock_collection.find_one.assert_called_once_with({"name": "test"})
        assert result == {"_id": "123", "name": "test"}

    @pytest.mark.asyncio
    async def test_find_many(self, mongo_db, mock_motor_client):
        """Test finding multiple documents."""
        _, _, mock_collection = mock_motor_client
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(
            return_value=[
                {"_id": "123", "name": "test1"},
                {"_id": "456", "name": "test2"},
            ]
        )
        mock_collection.find = MagicMock(return_value=mock_cursor)

        result = await mongo_db.find_many(
            MONGO_SCRAPED_COLLECTION, {"category": "parts"}
        )

        mock_collection.find.assert_called_once_with({"category": "parts"})
        mock_cursor.to_list.assert_called_once_with(length=None)
        assert len(result) == 2
        assert result[0]["name"] == "test1"
        assert result[1]["name"] == "test2"

    @pytest.mark.asyncio
    async def test_insert_one(self, mongo_db, mock_motor_client):
        """Test inserting a single document."""
        _, _, mock_collection = mock_motor_client
        mock_collection.insert_one = AsyncMock(
            return_value=MagicMock(inserted_id="123")
        )

        document = {"name": "test", "category": "parts"}
        result = await mongo_db.insert_one(MONGO_SCRAPED_COLLECTION, document)

        mock_collection.insert_one.assert_called_once_with(document)
        assert result == "123"

    @pytest.mark.asyncio
    async def test_insert_many(self, mongo_db, mock_motor_client):
        """Test inserting multiple documents."""
        _, _, mock_collection = mock_motor_client
        mock_collection.insert_many = AsyncMock(
            return_value=MagicMock(inserted_ids=["123", "456"])
        )

        documents = [{"name": "test1"}, {"name": "test2"}]
        result = await mongo_db.insert_many(MONGO_SCRAPED_COLLECTION, documents)

        mock_collection.insert_many.assert_called_once_with(documents)
        assert result == ["123", "456"]

    @pytest.mark.asyncio
    async def test_update_one(self, mongo_db, mock_motor_client):
        """Test updating a single document."""
        _, _, mock_collection = mock_motor_client
        mock_collection.update_one = AsyncMock(return_value=MagicMock(modified_count=1))

        filter_query = {"name": "test"}
        update = {"$set": {"category": "new_category"}}
        result = await mongo_db.update_one(
            MONGO_SCRAPED_COLLECTION, filter_query, update
        )

        mock_collection.update_one.assert_called_once_with(filter_query, update)
        assert result == 1

    @pytest.mark.asyncio
    async def test_delete_one(self, mongo_db, mock_motor_client):
        """Test deleting a single document."""
        _, _, mock_collection = mock_motor_client
        mock_collection.delete_one = AsyncMock(return_value=MagicMock(deleted_count=1))

        filter_query = {"name": "test"}
        result = await mongo_db.delete_one(MONGO_SCRAPED_COLLECTION, filter_query)

        mock_collection.delete_one.assert_called_once_with(filter_query)
        assert result == 1

    @pytest.mark.asyncio
    async def test_delete_many(self, mongo_db, mock_motor_client):
        """Test deleting multiple documents."""
        _, _, mock_collection = mock_motor_client
        mock_collection.delete_many = AsyncMock(return_value=MagicMock(deleted_count=2))

        filter_query = {"category": "parts"}
        result = await mongo_db.delete_many(MONGO_SCRAPED_COLLECTION, filter_query)

        mock_collection.delete_many.assert_called_once_with(filter_query)
        assert result == 2

    @pytest.mark.asyncio
    async def test_count_documents(self, mongo_db, mock_motor_client):
        """Test counting documents."""
        _, _, mock_collection = mock_motor_client
        mock_collection.count_documents = AsyncMock(return_value=5)

        filter_query = {"category": "parts"}
        result = await mongo_db.count_documents(MONGO_SCRAPED_COLLECTION, filter_query)

        mock_collection.count_documents.assert_called_once_with(filter_query)
        assert result == 5
