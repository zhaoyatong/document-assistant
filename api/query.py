from typing import List, Optional

from fastapi import APIRouter

from agent.workflow_selection_agent import WorkflowSelectionAgent
from schemas.response import ResponseModel, ResponseCode
from utils.db_helper import DBHelper
from utils.logger import logger

router = APIRouter(prefix="/query")


@router.post("/")
async def user_query(query_text: str, classification_ids: Optional[List[int]] = None) -> ResponseModel:
    """
    用户自然语言查询
    :param query_text:查询文本
    :param classification_ids:分类ID
    :return:
    """
    try:
        classification_names = []
        if classification_ids:
            classification_data = DBHelper.query_one(
                "classification",
                f"id in ({','.join([str(x) for x in classification_ids])})"
            )
            if classification_data:
                classification_names.append(classification_data["name"])

        execute_workflow = await WorkflowSelectionAgent.run(query_text)

        if classification_names:
            query_result = await execute_workflow(query_text=query_text, classification_filters=classification_names)
        else:
            query_result = await execute_workflow(query_text=query_text)

        return ResponseModel(message=str(query_result))
    except Exception as e:
        logger.error(f"查询失败: {e}")
        return ResponseModel(
            success=False,
            status_code=ResponseCode.InternalServerError,
            message="服务器内部出错",
        )
