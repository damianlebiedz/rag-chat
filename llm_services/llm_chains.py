from typing import List

import langchain

from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_neo4j import Neo4jVector

from .llm_utils import format_docs
from .llm_loaders import load_llm, load_embedding_model
from config import URL, USERNAME, PASSWORD
from db_services.db_initializer import get_graph_driver

driver = get_graph_driver()
llm = load_llm()
langchain.debug = True


def configure_llm_only_chain():
    template = """
    You are a helpful assistant that helps a support agent with answering programming questions.
    If you don't know the answer, just say that you don't know, you must not make up an answer.
    """
    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    human_template = "{question}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )
    chain = chat_prompt | llm | StrOutputParser()
    return chain


def configure_qa_rag_chain(chunks: List[str]):
    embeddings, _ = load_embedding_model()

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "human",
                "Based on the provided summary: {summaries} \n Answer the following question:{question}",
            )
        ]
    )

    vectorstore = Neo4jVector.from_texts(
        chunks,
        url=URL,
        username=USERNAME,
        password=PASSWORD,
        embedding=embeddings,
        index_name="pdf_bot",
        node_label="PdfBotChunk",
        pre_delete_collection=True,
    )
    qa = (
            RunnableParallel(
                {
                    "summaries": vectorstore.as_retriever(search_kwargs={"k": 2})
                                 | format_docs,
                    "question": RunnablePassthrough(),
                }
            )
            | qa_prompt
            | llm
            | StrOutputParser()
    )

    return qa
