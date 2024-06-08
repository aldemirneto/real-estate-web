import os

from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine

engine = create_engine(f'postgresql://postgres.{os.environ["DB_ID"]}:{os.environ["DB_PASSWORD"]}@aws-0-{os.environ["DB_REGION"]}.pooler.supabase.com:{os.environ["DB_PORT"]}/postgres')

db = SQLDatabase(engine=engine, view_support=True)


def get_schema(_):
    schema = db.get_table_info()
    return schema
