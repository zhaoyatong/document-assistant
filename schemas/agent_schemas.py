from typing import Optional, List

from pydantic import Field

from schemas.agent_response import FiltersGenerateAgentResponse


class DocumentMetadataFilters(FiltersGenerateAgentResponse):
    """
    过滤条件
    """
    classification: Optional[List[str]] = Field(description="文档类型", default=None)
