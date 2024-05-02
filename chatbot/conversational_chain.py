
from langchain.retrievers import SelfQueryRetriever

from langchain_community.vectorstores.chroma import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
import json
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
import streamlit as st
from langchain_community.document_loaders import DuckDBLoader
from langchain.chains.query_constructor.base import AttributeInfo
from langchain_core.prompts import PromptTemplate


@st.cache_resource(show_spinner=False)
def initialize_chain(system_prompt, _memory):
    llm = ChatOpenAI(temperature=0, max_tokens=1000, model_name="gpt-3.5-turbo", streaming=True)
    doc_contents = "Listing informations aggrouped of piracicaba"

    with open('Metadata/metadata_dataset.json', 'r', encoding='utf-8') as f:
        # Read the file contents
        file_content = f.read()
        # Now parse the JSON data using json.loads
        dict_attr = json.loads(file_content)

    attribute_info = dict_attr['data']
    metadata = [AttributeInfo(name=a["name"], description=a["description"], type=a["type"]) for a in attribute_info]

    loader = DuckDBLoader(
        "SELECT *,CAST(data_scrape as varchar(30)) as data_scrape_varchar,CAST(last_seen AS VARCHAR(30)) as last_varchar FROM read_parquet('lineitem.parquet')",
        page_content_columns=["link", "area", "preco", "quartos", "banheiros", "vagas", "data_scrape_varchar",
                              "bairro"],
        metadata_columns=["area", "preco", "quartos", "banheiros", "vagas", "data_scrape_varchar", "bairro",
                          "last_varchar", "tipo", "status", "imobiliaria"],
        )

    data = loader.load()
    embeddings = OpenAIEmbeddings(model='text-embedding-3-small')
    vectorstore = Chroma.from_documents(data, embeddings)

    retriever = SelfQueryRetriever.from_llm(
        llm=llm,
        document_contents=doc_contents,
        metadata_field_info=metadata,
        vectorstore=vectorstore, verbose=True
    )

    qa = ConversationalRetrievalChain.from_llm(llm, retriever,
                                               memory=_memory)

    return qa
