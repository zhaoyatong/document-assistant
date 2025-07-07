from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from api.classification import router as classification_router
from api.documents import router as documents_router
from api.query import router as query_router
from schemas.response import ResponseCode, ResponseModel
from utils.document_query import DocumentQueryEngine
from utils.document_embedding import DocumentEmbedding
from utils.logger import logger


# 应用生命周期管理
@asynccontextmanager
async def lifespan(fast_api_app: FastAPI):
    # 启动时执行
    DocumentEmbedding.initialize()
    logger.info("文档向量工具初始化完成。")
    DocumentQueryEngine.initialize()
    logger.info("文档查询引擎初始化完成。")

    logger.info("应用已启动...")

    yield  # 应用运行期间

    # 关闭时执行
    logger.info("应用退出...")

    # 在这里可以清理资源
    logger.info("")


# 创建FastAPI应用
app = FastAPI(
    title="文档查询小助手",
    description="通过自然语言与个人文档库进行查询交互",
    version="0.1.0",
    lifespan=lifespan
)


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"发生异常: {exc}")
    response = ResponseModel(
        success=False,
        status_code=ResponseCode.InternalServerError,
        message="服务器内部出错",
    )
    return JSONResponse(response.__dict__)


# 基础健康检查端点
@app.get("/health")
async def health_check():
    logger.info("Health check requested")
    return ResponseModel(
        message="OK",
    )


app.include_router(classification_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(query_router, prefix="")

if __name__ == "__main__":
    # 启动uvicorn服务器
    logger.info("开启Uvicorn服务...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_config=None,  # 禁用uvicorn的日志配置，使用loguru
        access_log=False  # 禁用uvicorn的访问日志
    )
