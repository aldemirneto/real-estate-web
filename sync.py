import duckdb
import os

try:
    os.remove('lineitem.parquet')
except:
    pass

# connect to the database
conn = duckdb.connect()

# install the postgres extension
conn.execute('INSTALL postgres;')
# load the extension
conn.execute('LOAD postgres;')

# attach the connection
conn.execute(f"""
ATTACH 'postgresql://postgres.{os.environ["DB_ID"]}:{os.environ["DB_PASSWORD"]}@aws-0-{os.environ["DB_REGION"]}.pooler.supabase.com:{os.environ["DB_PORT"]}/postgres' AS db (TYPE postgres);
""")

# put the fresh data into the parquet file
conn.execute("""
COPY(SELECT * FROM db.real_estate_data) TO 'lineitem.parquet' (FORMAT PARQUET)
""")

conn.close()