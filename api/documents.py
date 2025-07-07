import os
import tempfile

from fastapi import APIRouter, UploadFile, File

from schemas.response import ResponseModel, ResponseCode
from utils.db_helper import DBHelper
from utils.document_query import DocumentQueryEngine
from utils.document_embedding import DocumentEmbedding
from utils.logger import logger

router = APIRouter(prefix="/document")


@router.post("/upload")
async def upload_document(classification_id: int, file: UploadFile = File(...)) -> ResponseModel:
    """
    文档上传
    :param file:上传的文档源文件
    :param classification_id:文档分类id
    :return:
    """
    temp_file_path = None
    temp_dir = None
    try:
        # 0. 校验
        if not classification_id:
            return ResponseModel(
                success=False,
                status_code=ResponseCode.BadRequest,
                message="请选择分类",
            )
        document_name = DBHelper.query_one("documents", f"name='{file.filename}'")
        if document_name:
            return ResponseModel(
                success=False,
                status_code=ResponseCode.BadRequest,
                message="文档已存在",
            )

        # 1. 创建临时目录
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, file.filename)

        # 2. 保存到临时目录
        with open(temp_file_path, "wb") as f:
            f.write(await file.read())

        # 3. 存储数据库
        insert_id = DBHelper.insert(
            "documents",
            {
                'classification_id': classification_id,
                'name': file.filename,
            }
        )
        classification_name = DBHelper.query_one("classification", f"id={classification_id}")

        # 4. 向量化存入Chroma
        DocumentEmbedding.vectorize_document(insert_id, classification_name['name'], temp_file_path)

        return ResponseModel(message="上传成功")
    except Exception as e:
        logger.error(f"上传失败: {e}")
        return ResponseModel(
            success=False,
            status_code=ResponseCode.InternalServerError,
            message="服务器内部出错",
        )
    finally:
        # 5. 清理临时文件
        if temp_file_path:
            os.remove(temp_file_path)
        if temp_dir:
            os.rmdir(temp_dir)


@router.get("/list")
async def list_documents() -> ResponseModel:
    sql = """
          SELECT documents.id, documents.name, classification.name AS classification_name
          FROM documents
                   LEFT JOIN classification ON documents.classification_id = classification.id
          """
    result = DBHelper.query_by_sql(sql)
    return ResponseModel(data=result)


@router.delete("/delete")
async def delete_document(document_id: int) -> ResponseModel:
    document_name = DBHelper.query_one("documents", f"id={document_id}")
    DocumentQueryEngine.delete_document(document_name['name'])

    DBHelper.delete("documents", f"id={document_id}")

    return ResponseModel()
