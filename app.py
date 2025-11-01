import streamlit as st
from PyPDF2 import PdfReader
from langchain.callbacks.base import BaseCallbackHandler
from langchain.text_splitter import RecursiveCharacterTextSplitter
from streamlit.logger import get_logger

from llm_services.llm_chains import configure_qa_rag_chain

logger = get_logger(__name__)


class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)


def app():
    st.header("📄Chat with your pdf file")

    pdf = st.file_uploader("Upload your PDF", type="pdf")

    if pdf is not None:
        pdf_reader = PdfReader(pdf)

        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200, length_function=len
        )

        chunks = text_splitter.split_text(text=text)

        output_function = configure_qa_rag_chain(chunks)

        query = st.text_input("Ask questions about your PDF file")

        if query:
            stream_handler = StreamHandler(st.empty())
            output_function.invoke(query, {"callbacks": [stream_handler]})


if __name__ == "__main__":
    app()
