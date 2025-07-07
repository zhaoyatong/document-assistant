from llama_index.llms.deepseek import DeepSeek

from schemas.agent_response import FiltersGenerateAgentResponse

from utils.logger import logger


class FiltersGenerateAgent:
    """
    过滤条件生成Agent
    生成过滤条件
    """
    _llm = DeepSeek("deepseek-chat", temperature=0)
    _structured_llm = _llm.as_structured_llm(FiltersGenerateAgentResponse)

    _prompt = (
        "你是过滤条件生成助手，你精通根据用户提出的有关文档查询的问题进行提取关键元数据信息。"
        "你根据先根据要生成的结果去找寻用户问题中有没有明确的要求，如果有则填充对应结果，若无筛选条件，直接将各个字段留空即可。"
        "强烈注意：筛选条件生成时要十分谨慎，除非你很明确的判断出其一定是一个元数据筛选条件，否则轻易不要生成任何筛选条件！"
        "注意：除非明确指定了针对章节的信息，否则不要生成chapter_title。例如：“哪些章节有许明远在图书馆的情节”是不能够推理出来章节筛选条件的，“哪些文档有主要工作汇总章节”是可以推理出“工作汇总”筛选条件的"
        "注意：除非问题中明确指定了时间相关的信息，否则轻易不要生成creation_date和last_modified_date，例如：上周修改了哪些文档：{last_modified_date:'2025-06-24'}；2024年终总结主要内容：{file_name:'2024年终总结'}。"
        "\n"
        "用户问题："
    )

    @classmethod
    async def run(cls, query):
        filters_generate_result = await cls._structured_llm.acomplete(cls._prompt + query)
        logger.info(f"过滤条件生成Agent: {filters_generate_result.raw}")
        return filters_generate_result.raw
