from langchain.tools import Tool
from datetime import datetime
from langchain.chains.llm_math.base import LLMMathChain
from langchain_community.utilities.google_serper import GoogleSerperAPIWrapper
from langchain_community.tools.google_serper import GoogleSerperRun
from tools.vector_db import load_chunk_persist_pdf
from langchain.chains import RetrievalQA
from utils.constants import COLUMNS_DESCRIPTIONS
from database.db import db
from dotenv import load_dotenv

load_dotenv()
import json, ast


def build_utility_tools(llm):
    calculator = Tool(
        name="calculator",
        func=LLMMathChain.from_llm(llm=llm, verbose=True).run,
        description="A tool for performing complex mathematics.",
    )

    dt = Tool(
        name="Datetime",
        func=lambda x: datetime.now().isoformat(),
        description="A tool for getting the current date and time.",
    )
    return [calculator, dt]


def build_search_tools():
    column_description_tool = Tool.from_function(
        name="column_description_search",
        func=get_columns_descriptions,
        description="A tool for fetching column description of the table. USE THIS to get deeper understanding about table descriptions or IF when you get an error or when you get 0 results, USE to double check query."
    )


    return [column_description_tool]


def build_rag_tools(llm):
    vector_db = load_chunk_persist_pdf()
    documents_search = Tool(
        name="documents_search",
        func=RetrievalQA.from_chain_type(llm, chain_type="stuff", retriever=vector_db.as_retriever()).run,
        description="A tool for retrieving information from the internal documents. Use query as input. response in English"
    )

    return [documents_search]


def get_bairros_proximos():
    pass

def get_location_google():
    pass

def get_columns_descriptions(query: str) -> str:
    """
    Useful to get the description of the columns in the table.
    """
    return json.dumps(COLUMNS_DESCRIPTIONS)


def run_query_save_results(db, query):
    """
    Runs a query on the specified database and returns the results.

    Args:
        db: The database object to run the query on.
        query: The query to be executed.

    Returns:
        A list containing the results of the query.
    """
    res = db.run(query)
    res = [el for sub in ast.literal_eval(res) for el in sub]
    return res



















