"""
文档元数据检索工作流
"""

from llama_index.core.workflow import (
    StartEvent,
    StopEvent,
    Workflow,
    step,
    Context,
)

from agent.filters_generate_agent import FiltersGenerateAgent
from agent.metadata_summary_agent import MetadataSummaryAgent
from schemas.agent_schemas import DocumentMetadataFilters
from utils.document_query import DocumentQueryEngine
from utils.metadata_filters_handler import MetadataFiltersHandler
from utils.logger import logger
from workflow.events import GenerateFiltersEvent, MetadataFiltersHandleEvent, MetadataQueryEvent, MetadataSummaryEvent


class DocumentMetaRetrievalWorkflow(Workflow):
    """
    文档元数据检索工作流
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
    async def metadata_filters_handle(self, ctx: Context, ev: MetadataFiltersHandleEvent) -> MetadataQueryEvent:
        """
        元数据过滤器处理
        """
        filters = MetadataFiltersHandler.handle(ev.filters)
        logger.info(f"元数据过滤器处理结果：{filters}")
        return MetadataQueryEvent(filters=filters)

    @step
    async def query_metadata(self, ctx: Context, ev: MetadataQueryEvent) -> MetadataSummaryEvent | StopEvent:
        """
        根据用户查询和元数据过滤再次查询符合条件的元数据
        """
        query_text = await ctx.get("query_text")

        metadata_query_result = DocumentQueryEngine.query_metadatas(
            query_text=query_text,
            metadata_filters=ev.filters,
            top_k=100
        )

        if not metadata_query_result:
            return StopEvent(result="未检索到任何内容。")

        filename_set = set()
        classification_set = set()
        creation_date_set = set()
        last_modified_date_set = set()
        chapter_title_set = set()

        for metadata in metadata_query_result:
            filename_set.add(metadata["file_name"])
            classification_set.add(metadata["classification"])
            creation_date_set.add(metadata["creation_date"])
            last_modified_date_set.add(metadata["last_modified_date"])
            chapter_title_set.add(metadata["chapter_title"])

        metadata_result = {
            "file_name": filename_set,
            "classification": classification_set,
            "creation_date": creation_date_set,
            "last_modified_date": last_modified_date_set,
            "chapter_title": chapter_title_set
        }

        return MetadataSummaryEvent(metadata=metadata_result)

    @step
    async def summary_metadata(self, ctx: Context, ev: MetadataSummaryEvent) -> StopEvent:
        """
        生成元数据的总结
        """
        query_text = await ctx.get("query_text")
        result = await MetadataSummaryAgent.run(ev.metadata, query_text)
        return StopEvent(result=result)


document_metadata_retrieval_workflow = DocumentMetaRetrievalWorkflow(timeout=60, verbose=False)
