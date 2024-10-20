from db import db
from src.models.collection import Collection


class CollectionHandler:

    @classmethod
    def get_collections(cls):
        return Collection.query.all()

    @classmethod
    def add_collection(cls, name: str, description: str):
        collection = Collection(name=name, description=description)
        db.session.add(collection)
        db.session.commit()

        return collection
