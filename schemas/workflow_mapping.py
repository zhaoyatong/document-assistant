from workflow.document_metadata_retrieval_workflow import document_metadata_retrieval_workflow
from workflow.general_query_workflow import general_query_workflow
from workflow.simple_query_workflow import simple_query_workflow

workflow_mapping = {
    "simple_query": simple_query_workflow.run,
    "metadata_query": document_metadata_retrieval_workflow.run,
    "general_query": general_query_workflow.run,
}
