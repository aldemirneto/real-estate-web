
from langchain.retrievers import SelfQueryRetriever

from langchain_community.vectorstores.chroma import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
import json
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
import streamlit as st
from langchain_community.document_loaders import DuckDBLoader
from langchain.chains.query_constructor.base import AttributeInfo

from agent.multi_agent import create_agent
from tools.tools import build_rag_tools


@st.cache_resource(show_spinner=False)
def initialize_chain():
    llm = ChatOpenAI(temperature=0, max_tokens=1000, model_name="gpt-3.5-turbo", streaming=True)
    doc_contents = "Listing informations aggrouped of piracicaba"

    retriever_tools = build_rag_tools(llm)
    retriever_agent = create_agent(
        llm,
        retriever_tools,
        "You are a real estate assistant who can retrieve information from the embedding documents related to real estate information"
        "DO NOT MAKE UP INFORMATION, if you dont know the answer, just say you dont know and the other member will pick up where you left",

    )

    return retriever_agent
