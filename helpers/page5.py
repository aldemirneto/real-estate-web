import os
import streamlit as st
import duckdb
def insert_interaction(interaction_id, score):
    # Ensure environment variables are set for DB connection
    if not all(key in os.environ for key in ["DB_ID", "DB_PASSWORD", "DB_REGION", "DB_PORT"]):
        raise EnvironmentError("Database environment variables are not fully set.")

    try:
        # Connect to the database
        conn = duckdb.connect()
        st.write('conectou')

        # Assuming the PostgreSQL extension is pre-installed and just needs to be loaded
        conn.execute('LOAD postgres;')

        # Securely format the connection string
        db_connection_string = f"postgresql://postgres.{os.environ['DB_ID']}:{os.environ['DB_PASSWORD']}@aws-0-{os.environ['DB_REGION']}.pooler.supabase.com:{os.environ['DB_PORT']}/postgres"

        st.write('linkando...')
        # Attach the connection
        conn.execute(f"""
        ATTACH '{db_connection_string}' AS db (TYPE postgres);
        """)
        st.write('nao deu certo pra linkar')

        st.write('inserindo...')
        conn.execute(f"""
        INSERT INTO db.user_interaction (interaction_id, score)
        VALUES ('{interaction_id}', '{score}');
        """)
        st.write('inseriu')
        conn.close()
        return 'Email inserido com sucesso'

    except Exception as e:
        conn.close()
        return (f"An error occurred: {e}")

