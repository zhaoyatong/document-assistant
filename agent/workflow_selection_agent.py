from llama_index.llms.deepseek import DeepSeek

from schemas.workflow_mapping import workflow_mapping
from utils.logger import logger


class WorkflowSelectionAgent:
    """
    流程选择的Agent
    """
    _llm = DeepSeek("deepseek-chat", temperature=0)

    _prompt = (
        "你是一个文档信息查询的工作流选择专家，精通于根据用户的问题来选择对应的文档信息查询工作流。"
        "接下来你将收到一个关于文档信息查询相关的请求。"
        "你可选的流程如下："
        "simple_query：简单查询，只需要查现有的文档和分类等信息，不涉及RAG，例如：“网络小说分类下有那些文档？”。"
        "metadata_query：元数据查询，只需要查现有的文档的元数据信息，包括文件名，所属类别等，需要RAG，例如：“哪些文档中提到了“网络安全”？”。"
        "general_query：通用查询，如果你不觉得其他流程都不合适，就选择这一个。"
        "请检查你的输出，只输出流程名并确保其在上述流程之内。"
        "注意：除非用户明确指定要查询的内容是文档元数据而不包括文档内容本身，否则一律返回general_query。"
        "\n"
        "用户的问题："
    )

    @classmethod
    async def run(cls, query):
        response = await cls._llm.acomplete(cls._prompt + query)

        result = workflow_mapping["general_query"]

        if response.text in workflow_mapping.keys():
            result = workflow_mapping[response.text]

            logger.info(f"用户问题：{query}，选择的工作流：{response.text}。")

        return result
