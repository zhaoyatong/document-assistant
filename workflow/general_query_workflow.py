"""
通用查询工作流
"""

from llama_index.core.workflow import (
    StartEvent,
    StopEvent,
    Workflow,
    step,
    Context
)

from agent.filters_generate_agent import FiltersGenerateAgent
from schemas.agent_schemas import DocumentMetadataFilters
from utils.document_query import DocumentQueryEngine
from utils.metadata_filters_handler import MetadataFiltersHandler
from utils.logger import logger
from workflow.events import GenerateFiltersEvent, MetadataFiltersHandleEvent, SimpleQueryEvent


class GeneralQueryWorkflow(Workflow):
    """
    文档通用查询工作流
    """

    @step
    async def start(self, ctx: Context, ev: StartEvent) -> GenerateFiltersEvent:
        """
        启动
        """
        await ctx.set("query_text", ev.query_text)

        return GenerateFiltersEvent(classification=ev.get("classification_filters", None))

    @step
    async def generate_filters(self, ctx: Context, ev: GenerateFiltersEvent) -> MetadataFiltersHandleEvent:
        """
        生成元数据过滤器
        """
        query_text = await ctx.get("query_text")
        metadata_filters = await FiltersGenerateAgent.run(query_text)

        filters = DocumentMetadataFilters(
            chapter_title=metadata_filters.chapter_title,
            classification=ev.classification,
            creation_date=metadata_filters.creation_date,
            file_name=metadata_filters.file_name,
            last_modified_date=metadata_filters.last_modified_date
        )

        return MetadataFiltersHandleEvent(filters=filters)

    @step
    async def metadata_filters_handle(self, ctx: Context, ev: MetadataFiltersHandleEvent) -> SimpleQueryEvent:
        """
        元数据过滤器处理
        """
        filters = MetadataFiltersHandler.handle(ev.filters)
        logger.info(f"元数据过滤器处理结果：{filters}")
        return SimpleQueryEvent(filters=filters)

    @step
    async def simple_query(self, ctx: Context, ev: SimpleQueryEvent) -> StopEvent:
        """
        进行通用查询
        """
        query_text = await ctx.get("query_text")
        result = DocumentQueryEngine.simple_query(query_text, ev.filters)
        return StopEvent(result=result)


general_query_workflow = GeneralQueryWorkflow(timeout=30, verbose=False)
