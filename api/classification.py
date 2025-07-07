from utils.db_helper import DBHelper
from schemas.response import ResponseModel
from fastapi import APIRouter

from utils.document_query import DocumentQueryEngine

router = APIRouter(prefix="/classification")


@router.get("/list")
async def list_classification() -> ResponseModel:
    result = DBHelper.query_all("classification")
    return ResponseModel(data=result)


@router.post("")
async def add_classification(name: str) -> ResponseModel:
    DBHelper.insert("classification", {'name': name})
    return ResponseModel()


@router.put("")
async def update_classification(classification_id: int, name: str) -> ResponseModel:
    old_name = DBHelper.query_one("classification", f"id={classification_id}")
    DocumentQueryEngine.update_metadata(old_name['name'], name)

    DBHelper.update("classification", {'name': name}, f"id={classification_id}")

    return ResponseModel()
