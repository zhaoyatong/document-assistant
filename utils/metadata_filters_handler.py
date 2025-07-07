from schemas.agent_schemas import DocumentMetadataFilters
from utils.db_helper import DBHelper


class MetadataFiltersHandler:
    """
    元数据过滤条件处理
    """
    @staticmethod
    def handle(metadata_filters: DocumentMetadataFilters) -> DocumentMetadataFilters:
        if not metadata_filters:
            return DocumentMetadataFilters(
                chapter_title=None,
                classification=None,
                creation_date=None,
                file_name=None,
                last_modified_date=None
            )

        if metadata_filters.file_name:
            condition = ""
            filename = metadata_filters.file_name.pop()
            condition += f"name like '%{filename}%' "
            while metadata_filters.file_name:
                filename = metadata_filters.file_name.pop()
                condition += f"or name like '%{filename}%'"
            filename_query_result = DBHelper.query_many("documents", condition)
            metadata_filters.file_name = [x["name"] for x in filename_query_result]
        if metadata_filters.chapter_title:
            condition = ""
            chapter_title = metadata_filters.chapter_title.pop()
            condition += f"title like '%{chapter_title}%' "
            while metadata_filters.chapter_title:
                chapter_title = metadata_filters.chapter_title.pop()
                condition += f"or title like '%{chapter_title}%'"
            chapter_title_query_result = DBHelper.query_many("document_titles", f"title like '%{metadata_filters.chapter_title}%'")
            metadata_filters.chapter_title = [x["title"] for x in chapter_title_query_result]

        return metadata_filters