from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.deepseek import DeepSeek

from tools.simple_query import SqliteQueryTool


class SimpleQueryAgent:
    """
    简单查询的Agent
    适用于不查询文档具体内容的查询
    """
    _llm = DeepSeek("deepseek-chat", temperature=0)

    _workflow = FunctionAgent(
        tools=[
            SqliteQueryTool.get_all_documents,
            SqliteQueryTool.get_documents_by_classification,
            SqliteQueryTool.get_all_classification,
            SqliteQueryTool.get_documents_by_classification_and_date,
            SqliteQueryTool.get_documents_by_date
        ],
        llm=_llm,
        system_prompt="你是一个文档查询小助手，你可以使用工具进行文档信息的基本检索。"
                      "注意：如果检索不到信息或信息不明确时，直接输出“未检索到任何内容。”。"
                      "注意：遇到和文档信息查询无关的问题时或无法理解、解决问题时直接输出“未检索到任何内容。”。"
    )

    @classmethod
    async def run(cls, query):
        response = await cls._workflow.run(user_msg=query)
        return response
