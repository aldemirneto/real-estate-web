from langchain.chains import create_sql_query_chain, MultiRetrievalQAChain
from operator import itemgetter
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_community.utilities.sql_database import SQLDatabase
from sqlalchemy import create_engine
from database.db import get_schema, db
import streamlit as st


@st.cache_resource(show_spinner=False)
def initialize_analytical_chain():
    answer_prompt = PromptTemplate.from_template(
        """Given the following user question, corresponding SQL query, and SQL result, answer the user question.

    Question: {question}
    SQL Query: {query}
    SQL Result: {result}
    Answer: """
    )

    sql_database = db

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    write_query = create_sql_query_chain(llm, sql_database)
    execute_query = QuerySQLDataBaseTool(db=sql_database)
    answer = answer_prompt | llm | StrOutputParser()

    sql_chain = (
            RunnablePassthrough
            .assign(schema=get_schema)
            .assign(query=write_query)
            .assign(result=itemgetter("query") | execute_query)
            | answer
    )

    def save(input_output):
        output = {"output": input_output.pop("output")}
        return output["output"]

    qa = RunnablePassthrough.assign(output=sql_chain) | save

    return qa


