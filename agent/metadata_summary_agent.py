from llama_index.llms.deepseek import DeepSeek


class MetadataSummaryAgent:
    """
    元数据总结Agent，针对已经检索的元数据，结合用户问题进行总结。
    """
    _llm = DeepSeek("deepseek-chat", temperature=0)

    _prompt = (
        "你是元数据总结助手，你精通根据用户提出的有关文档查询的问题来分析用户的意图，从提供的元数据中精准提取所需信息并组织成自然语言回答。"
        "其中元数据是已经根据用户问题查询匹配好的结果，你无需关心问题本身以及问题和元数据的匹配性。"
        "元数据信息用JSON来表达，字段说明如下："
        "file_name：文档文件名。"
        "chapter_title：文档里面的章节名。"
        "creation_date：文档创建时间。"
        "last_modified_date：文档最后修改时间。"
        "classification：文档所属分类。"
        "\n"
        "你的思路是这样的："
        "1. 意图识别 - 首先根据用户的问题，提取出用户意图，例如：“哪些文档里提到了财务报告？”，用户意图是查询文档文件名。"
        "2. 信息提取 - 直接从用户提供的元数据信息中提取内容，无需验证内容是否匹配。"
        "3. 回答 - 用自然语言组织提取的内容，通顺的表述即可。"
        "\n"
        "用户提供的元数据信息：{metadata}"
        "\n"
        "用户的问题：{query_text}"
    )

    @classmethod
    async def run(cls, metadata, query):
        summary_result = await cls._llm.acomplete(cls._prompt.format(metadata=metadata, query_text=query))
        return summary_result.text
