import os

from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine


url = f'postgresql://postgres.{os.environ["DB_ID"]}:{os.environ["DB_PASSWORD"]}@aws-0-{os.environ["DB_REGION"]}.pooler.supabase.com:{os.environ["DB_PORT"]}/postgres'

db = SQLDatabase.from_uri(
    url,
    schema="public",
    include_tables=['real_estate_data'],
    sample_rows_in_table_info=1,
    view_support=True
)


def get_schema(_):
    schema = db.get_table_info()
    return schema
