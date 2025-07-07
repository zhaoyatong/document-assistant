"""
简单查询（不涉及RAG）工作流
"""

from llama_index.core.workflow import (
    StartEvent,
    StopEvent,
    Workflow,
    step,
)

from agent.simple_query_agent import SimpleQueryAgent


class SimpleQueryWorkflow(Workflow):
    """
    文档简单查询（不涉及RAG）工作流
    """

    @step
    async def start(self, ev: StartEvent) -> StopEvent:
        """
        启动
        """
        result = await SimpleQueryAgent.run(ev.query_text)
        return StopEvent(result=result)


simple_query_workflow = SimpleQueryWorkflow(timeout=20, verbose=False)
