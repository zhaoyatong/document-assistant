from typing import Optional, List

from llama_index.core.workflow import (
    Event,
)

from schemas.agent_schemas import DocumentMetadataFilters


class GenerateFiltersEvent(Event):
    """
    生成元数据过滤器事件
    """
    classification: Optional[List[str]]


class MetadataFiltersHandleEvent(Event):
    """
    处理元数据过滤器事件
    """
    filters: DocumentMetadataFilters


class MetadataQueryEvent(Event):
    """
    元数据查询事件
    """
    filters: DocumentMetadataFilters


class MetadataSummaryEvent(Event):
    """
    元数据摘要事件
    """
    metadata: dict

class SimpleQueryEvent(Event):
    """
    简单查询事件
    """
    filters: Optional[DocumentMetadataFilters]