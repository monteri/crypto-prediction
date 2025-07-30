from fastapi import APIRouter
from typing import List

router = APIRouter(prefix="/items", tags=["Items"])

_items = []


@router.post("/", response_model=dict)
def create_item(item: dict):
    item_id = len(_items) + 1
    item_data = {"id": item_id, **item}
    _items.append(item_data)
    return item_data


@router.get("/", response_model=List[dict])
def list_items():
    return _items
