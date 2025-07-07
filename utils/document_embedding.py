import copy
import os
import re
import uuid
from pathlib import Path
from typing import List, Dict, Union, Optional

import chromadb
from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import Document as LlamaindexDocument
from llama_index.embeddings.dashscope import DashScopeEmbedding, DashScopeTextEmbeddingModels
from llama_index.vector_stores.chroma import ChromaVectorStore

from utils.db_helper import DBHelper
from utils.logger import logger


class DocumentEmbedding:
    """多格式文档向量化存储工具类"""

    @classmethod
    def initialize(
            cls,
            collection_name: str = "documents",
            persist_dir: Optional[str] = None,
            chunk_size: int = 512,
            chunk_overlap: int = 50
    ):
        """初始化向量存储配置(只需调用一次)"""

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

        cls._node_parser = SentenceSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            include_metadata=True
        )

        cls._embed_model = DashScopeEmbedding(
            model_name=DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V3,
            embed_batch_size=5,
        )

        # 默认支持的文档格式映射
        cls._default_ext = ['.csv', '.docx', '.pptx', '.epub', '.txt', '.md', '.pdf', '.mobx', '.ipynb']
        # 拓展的文档格式映射
        cls._custom_support_ext = ['.json', '.html', '.xlsx']

    @classmethod
    def vectorize_document(cls, document_id: int, classification_name: str, file_path: Union[str, Path]) -> None:
        """
        向量化单个文档并存储

        参数:
            document_id: 文档id
            file_path: 文档路径
            classification_name: 文档分类

        返回:
            插入的文本块数量
        """
        if not hasattr(cls, '_collection'):
            cls.initialize()

        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        file_ext = file_path.suffix.lower()
        if file_ext in cls._default_ext:
            cls._process_generic(document_id, classification_name, file_path)
        elif file_ext in cls._custom_support_ext:
            pass
        else:
            raise ValueError(f"不支持的文件格式: {file_ext}")

    @classmethod
    def get_supported_formats(cls) -> List[str]:
        """获取支持的文档格式列表"""
        return cls._default_ext + cls._custom_support_ext

    @classmethod
    def _process_generic(cls, document_id: int, classification_name: str, file_path: Path) -> None:
        """处理默认的通用文档格式"""
        reader = SimpleDirectoryReader(input_files=[str(file_path)])
        documents = reader.load_data()
        nodes = cls._node_parser.get_nodes_from_documents(documents)

        chapter_title = None
        all_chapter_title = set()

        # 声明一个待添加的node，当某个node有多个章节时，复制一个node修改其元数据的章节信息，并添加到need_append_nodes中
        need_append_nodes = []

        for node in nodes:
            chapter_titles = cls._extract_chapters(node.text)

            if chapter_titles:
                if chapter_title:
                    temp_node = copy.deepcopy(node)
                    node.node_id = str(uuid.uuid4())
                    temp_node.metadata["chapter_title"] = chapter_title
                    temp_node.metadata["classification"] = classification_name
                    need_append_nodes.append(temp_node)

                chapter_title = chapter_titles.pop()
                all_chapter_title.add(chapter_title)

            node.metadata["chapter_title"] = chapter_title
            node.metadata["classification"] = classification_name

            while chapter_titles:
                temp_chapter_title = chapter_titles.pop()
                all_chapter_title.add(temp_chapter_title)

                temp_node = copy.deepcopy(node)
                node.node_id = str(uuid.uuid4())
                temp_node.metadata["chapter_title"] = temp_chapter_title
                temp_node.metadata["classification"] = classification_name
                need_append_nodes.append(temp_node)

                chapter_title = temp_chapter_title

        nodes += need_append_nodes

        VectorStoreIndex(
            nodes,
            embed_model=cls._embed_model,
            storage_context=cls._storage_context,
            store_nodes_override=True
        )

        for title in all_chapter_title:
            try:
                DBHelper.insert("document_titles", {"document_id": document_id, "title": title})
            except Exception as e:
                logger.error(f"插入文档标题失败: {e}")

    @classmethod
    def _process_html(cls, file_path: Path, metadata: Dict) -> List[LlamaindexDocument]:
        """处理HTML文件"""
        from bs4 import BeautifulSoup

        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')

        # 清理HTML标签
        for element in soup(['script', 'style', 'header', 'footer', 'nav']):
            element.decompose()

        text = soup.get_text(strip=True)

        nodes = cls._node_parser.split_text(text)
        for node in nodes:
            node.metadata.update({
                **metadata,
                "file_path": str(file_path),
                "file_type": file_path.suffix,
                "document_title": soup.title.string if soup.title else "Untitled"
            })

        return nodes

    @classmethod
    def _process_json(cls, file_path: Path, metadata: Dict) -> List[LlamaindexDocument]:
        """处理JSON文件"""
        pass

    @staticmethod
    def _extract_chapters(text: str) -> List[str]:
        """从文本中提取章节结构"""
        # 支持多级标题检测
        patterns = [
            re.compile(r'^(#+)\s+(.+)$', re.MULTILINE),  # Markdown
            re.compile(r'^(\d+(?:\.\d+)*)\s+(.+)$', re.MULTILINE),
            # 数字标题
            re.compile(r'^([A-Z][A-Z0-9 ]+)$', re.MULTILINE),  # 全大写标题
            re.compile(r'^第[一二三四五六七八九十]+章\s+.+$', re.MULTILINE)  # 中文章节
        ]

        chapters = []
        lines = text.split('\n')

        for line in lines:
            for pattern in patterns:
                match = pattern.match(line)
                if match:
                    chapters.append(line)

        return chapters
