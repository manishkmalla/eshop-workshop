from db.client import DatabaseClient
from models.schemas import FavouriteResponse


class FavouritesService:
    def __init__(self, db: DatabaseClient):
        self.db = db

    def add(self, email: str, product_id: int) -> None:
        if self.db.get_catalog_item_by_id(product_id) is None:
            raise ValueError(f"Product {product_id} not found")
        self.db.add_favourite(email, product_id)

    def list_favourites(self, email: str) -> list[FavouriteResponse]:
        return [
            FavouriteResponse(
                **vars(favourite.item), created_at=favourite.created_at
            )
            for favourite in self.db.list_favourites(email)
        ]
