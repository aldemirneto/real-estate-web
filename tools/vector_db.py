import pysqlite3
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import json
from langchain.chains.query_constructor.schema import AttributeInfo
from langchain_community.document_loaders import PyPDFLoader, DuckDBLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings


VECTOR_STORE_PERSIST_PATH = "vector_data"


def load_chunk_persist_pdf() -> Chroma:
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

    return vectorstore
