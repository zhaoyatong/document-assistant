import os
from typing import List, Optional, Dict, Any

import chromadb
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.vector_stores import MetadataFilters, MetadataFilter, FilterOperator
from llama_index.embeddings.dashscope import DashScopeEmbedding, DashScopeTextEmbeddingModels
from llama_index.llms.deepseek import DeepSeek
from llama_index.vector_stores.chroma import ChromaVectorStore

from schemas.agent_schemas import DocumentMetadataFilters


class DocumentQueryEngine:
    """文档查询引擎"""

    _client = None
    _collection = None
    _embedding_fn = None

    @classmethod
    def initialize(
            cls,
            collection_name: str = "documents",
            persist_dir: Optional[str] = None
    ):
        """初始化查询引擎(只需调用一次)"""
        if not persist_dir:
            # 获取当前文件的目录，然后返回上一级目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            persist_dir = os.path.join(parent_dir, "chroma_db")
            cls._client = chromadb.PersistentClient(path=persist_dir)
        else:
            cls._client = chromadb.PersistentClient(path=persist_dir)

        cls._collection = cls._client.get_or_create_collection(name=collection_name)

        cls._vector_store = ChromaVectorStore(chroma_collection=cls._collection)

        cls._storage_context = StorageContext.from_defaults(vector_store=cls._vector_store)

        cls._query_embed_model = DashScopeEmbedding(
            model_name=DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V3,
            text_type="query",
            embed_batch_size=5,
        )

        cls._index = VectorStoreIndex.from_vector_store(
            cls._vector_store,
            embed_model=cls._query_embed_model,
            storage_context=cls._storage_context
        )

    @classmethod
    def _assembly_metadata_filters(
            cls,
            metadata_filters: Optional[DocumentMetadataFilters] = None,
    ):
        """
        组装元数据过滤器

        参数:
            metadata_filters: 元数据过滤

        返回:
            过滤器
        """
        if metadata_filters is None:
            return None

        if (metadata_filters.chapter_title or metadata_filters.creation_date or
                metadata_filters.classification or metadata_filters.file_name or metadata_filters.last_modified_date):
            filter_list = []
            if metadata_filters.chapter_title:
                filter_list.append(
                    MetadataFilter(key="chapter_title", operator=FilterOperator.IN, value=metadata_filters.chapter_title)
                )
            if metadata_filters.creation_date:
                filter_list.append(
                    MetadataFilter(key="creation_date", operator=FilterOperator.IN, value=metadata_filters.creation_date)
                )
            if metadata_filters.classification:
                filter_list.append(
                    MetadataFilter(key="classification", operator=FilterOperator.IN, value=metadata_filters.classification)
                )
            if metadata_filters.file_name:
                filter_list.append(
                    MetadataFilter(key="file_name", operator=FilterOperator.IN, value=metadata_filters.file_name)
                )
            if metadata_filters.last_modified_date:
                filter_list.append(
                    MetadataFilter(key="last_modified_date", operator=FilterOperator.IN, value=metadata_filters.last_modified_date)
                )

            filters = MetadataFilters(filters=filter_list)
        else:
            filters = None

        return  filters


    @classmethod
    def simple_query(
            cls,
            query_text: str,
            metadata_filters: Optional[DocumentMetadataFilters] = None,
            top_k=5
    ) -> str:
        """
        直接通过查询回答问题

        参数:
            query_text: 查询内容
            top_k: 文档向量查询结果数量
            metadata_filters: 元数据过滤

        返回:
            输出结果
        """
        filters = cls._assembly_metadata_filters(metadata_filters)

        _llm = DeepSeek("deepseek-chat", temperature=0.1)

        query_engine = cls._index.as_query_engine(
            llm=_llm,
            similarity_top_k=top_k,
            filters=filters
        )

        llm_response = query_engine.query(query_text)

        return llm_response.response

    @classmethod
    def simple_retriever(
            cls,
            query_text: str,
            metadata_filters: Optional[DocumentMetadataFilters] = None,
            top_k=3
    ) -> str:
        """
        通过查询返回相关片段

        参数:
            query_text: 查询内容
            top_k: 文档向量查询结果数量
            metadata_filters: 元数据过滤

        返回:
            输出结果
        """
        filters = cls._assembly_metadata_filters(metadata_filters)

        retriever = cls._index.as_retriever(similarity_top_k=top_k, filters=filters)

        retrieved_nodes = retriever.retrieve(query_text)
        result = '\n\n'.join([x.text for x in retrieved_nodes])

        return result

    @classmethod
    def query_metadatas(
            cls,
            query_text: str,
            metadata_filters: Optional[DocumentMetadataFilters] = None,
            top_k=3,
    ) -> List[Dict[str, Any]]:
        """
        通过查询返回相关元数据

        参数:
            query_text: 查询内容
            top_k: 文档向量查询结果数量
            metadata_filters: 元数据过滤

        返回:
            输出结果
        """
        filters = cls._assembly_metadata_filters(metadata_filters)

        retriever = cls._index.as_retriever(similarity_top_k=top_k, filters=filters)

        retrieved_nodes = retriever.retrieve(query_text)
        result = [x.metadata for x in retrieved_nodes if x.score > 0.55]

        return result

    @classmethod
    def update_metadata(cls, old: str, new: str):
        wait_update_node = cls._collection.get(
            where={"classification": old}
        )
        if wait_update_node["ids"]:
            for node_id in wait_update_node["ids"]:
                node_data = cls._collection.get(ids=node_id)
                node_data["metadatas"][0]["classification"] = new
                cls._collection.update(
                    ids=node_id,
                    metadatas=node_data["metadatas"],
                )

    @classmethod
    def delete_document(cls, document_name: str):
        cls._collection.delete(where={"file_name": document_name})
