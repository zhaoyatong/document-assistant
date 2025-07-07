from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class FiltersGenerateAgentResponse(BaseModel):
    """
    过滤条件
    """
    file_name: Optional[List[str]] = Field(description="文件名称", default=None)
    chapter_title: Optional[List[str]] = Field(description="章节标题", default=None)
    creation_date: Optional[List[datetime]] = Field(description="创建时间", default=None)
    last_modified_date: Optional[List[datetime]] = Field(description="最后修改时间", default=None)
