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
    # LLM only response
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


def configure_qa_rag_chain():
    embeddings, _ = load_embedding_model()

    # RAG response
    #   System: Always talk in pirate speech.
    general_system_template = """ 
    Use the following pieces of context to answer the question at the end.
    The context contains question-answer pairs and their links from Stackoverflow.
    You should prefer information from accepted or more upvoted answers.
    Make sure to rely on information from the answers and not on questions to provide accurate responses.
    When you find particular answer in the context useful, make sure to cite it in the answer using the link.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    ----
    {summaries}
    ----
    Each answer you generate should contain a section at the end of links to 
    Stackoverflow questions and answers you found useful, which are described under Source value.
    You can only use links to StackOverflow questions that are present in the context and always
    add links to the end of the answer in the style of citations.
    Generate concise answers with references sources section of links to 
    relevant StackOverflow questions only at the end of the answer.
    """
    general_user_template = "Question:```{question}```"
    messages = [
        SystemMessagePromptTemplate.from_template(general_system_template),
        HumanMessagePromptTemplate.from_template(general_user_template),
    ]
    qa_prompt = ChatPromptTemplate.from_messages(messages)

    # Vector + Knowledge Graph response
    kg = Neo4jVector.from_existing_index(
        embedding=embeddings,
        url=URL,
        username=USERNAME,
        password=PASSWORD,
        database="neo4j",  # neo4j by default
        index_name="stackoverflow",  # vector by default
        text_node_property="body",  # text by default
        retrieval_query="""
                        WITH node AS question, score AS similarity
                            CALL {
                        with question
                            MATCH (question)<-[:ANSWERS]-(answer)
                        WITH answer
                        ORDER BY answer.is_accepted DESC, answer.score DESC
                        WITH collect(answer)[..2] as answers
                            RETURN reduce(str='', answer IN answers | str +
                            '\n### Answer (Accepted: '+ answer.is_accepted +
                            ' Score: ' + answer.score+ '): '+ answer.body + '\n') as answerTexts
                            }
                            RETURN '##Question: ' + question.title + '\n' + question.body + '\n'
                            + answerTexts AS text, similarity as score, {source : question.link} AS metadata
                        ORDER BY similarity ASC // so that best answers are the last
                        """,
    )
    kg_qa = (
            RunnableParallel(
                {
                    "summaries": kg.as_retriever(search_kwargs={"k": 2}) | format_docs,
                    "question": RunnablePassthrough(),
                }
            )
            | qa_prompt
            | llm
            | StrOutputParser()
    )
    return kg_qa
