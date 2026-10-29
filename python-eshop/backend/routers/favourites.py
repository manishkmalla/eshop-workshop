from fastapi import APIRouter, Depends, HTTPException, status

from dependencies import get_favourites_service, require_authenticated_user
from models.schemas import FavouriteResponse
from services.favourites_service import FavouritesService

router = APIRouter(prefix="/api/favourites", tags=["favourites"])


@router.get("", response_model=list[FavouriteResponse])
def list_favourites(
    email: str = Depends(require_authenticated_user),
    service: FavouritesService = Depends(get_favourites_service),
):
    return service.list_favourites(email)


@router.post("/{product_id}", status_code=200)
def add_favourite(
    product_id: int,
    email: str = Depends(require_authenticated_user),
    service: FavouritesService = Depends(get_favourites_service),
):
    try:
        service.add(email, product_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
