from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine

connect_args = {
        'read_only': True
    }

engine = create_engine("duckdb:///database/my_database.duckdb", connect_args=connect_args)

db = SQLDatabase(engine=engine, view_support=True)

def get_schema(_):
    schema = db.get_table_info()
    return schema