import os

from langchain_community.utilities import SQLDatabase

url = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@db:5432/realestate"
)

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
