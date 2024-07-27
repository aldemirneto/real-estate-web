
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
    llm = ChatOpenAI(temperature=0, max_tokens=1000, model_name="gpt-4o-mini", streaming=True)
    doc_contents = "Listing informations aggrouped of piracicaba"

    retriever_tools = build_rag_tools(llm)
    retriever_agent = create_agent(
        llm,
        retriever_tools,
        "You are an expert real estate researcher and assistant, specializing in retrieving and analyzing information from embedding documents related to real estate. Your role is to:"
        "1. Thoroughly search and analyze the available embedded documents for relevant real estate information."
        "2. Provide accurate and detailed responses based solely on the information found in these documents."
        "3. When statistical analysis or database queries are required, defer to the SQL agent for precise data retrieval."
        "4. Maintain a professional and helpful demeanor, similar to a highly competent real estate agent."
        "Guidelines:"
        "- Always prioritize accuracy over completeness. If you cannot find specific information in the documents, clearly state I don't have that information in my current database rather than speculating."
        "- For statistical queries or detailed data analysis, respond with I'll need to consult our database for this information. I'm passing this query to our SQL specialist."

    )

    return retriever_agent
