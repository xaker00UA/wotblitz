from pymongo import MongoClient
from logging import getLogger
import logging
from config import DATABASE

logger = getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(f"log\\{__name__}.log", encoding="utf-8")
handler.setFormatter(
    logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]-%(message)s",
        datefmt="%d-%m-%Y %H:%M:%S",
    )
)
logger.addHandler(handler)
logger.propagate = True


class Base:
    CLUSTER = MongoClient(DATABASE)
    DATABASE = CLUSTER["test"]

    def __init__(self, name, key="id", key_name="name"):
        self._collection = Base.DATABASE[name]
        self._key = key
        self._name = key_name

    def add(self, data: dict) -> None:
        self._collection.replace_one(
            filter={self._key: data.get(self._key)}, replacement=data, upsert=True
        )

    def get(self, user_id: int) -> dict | None:
        return self._collection.find_one(filter={self._key: user_id})

    def get_all_id(self) -> list[dict]:
        return list(
            self._collection.find(
                projection={self._key: True, "_id": False, self._name: True}
            )
        )

    def add_many(self, items: list):
        self._collection.insert_many(items)


class Session(Base):
    def __init__(self):
        super().__init__("Session", key_name="nickname")


class User(Base):
    def __init__(self):
        super().__init__("User")

    def get_all(self):
        return list(
            self._collection.find(projection={"id": True, "_id": False, "name": True})
        )


class General(Base):
    def __init__(self):
        super().__init__("General")


class All_General(Base):
    def __init__(self):
        super().__init__("all_session")

    def get(self, name):
        return list(
            self._collection.find(
                filter={"nickname": {"$regex": name, "$options": "i"}}
            )
        )

    def add(self, data: dict):
        self._collection.insert_one(data)


class Clan(Base):
    def __init__(self):
        super().__init__("Clan", key="clan_id")


class Tank(Base):
    def __init__(self):
        super().__init__("Tank", key="tank_id")

    def add(self, data: dict) -> None:
        self._collection.replace_one(
            filter={self._key: data.get(self._key)}, replacement=data, upsert=True
        )

    def get(self, tank_id) -> dict | None:

        data = self._collection.find_one(
            filter={self._key: tank_id}, projection={"_id": False}
        )
        if not data:
            logger.warning("Не найден танк с айди %d", tank_id)
            return {"name": "undefined", "tier": "undefined"}
        return data
