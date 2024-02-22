from shapely import Point
from datetime import datetime, timedelta
import duckdb
import os


def cor_sinc(df):
    ultima_data_scrape = df['data_scrape'].max()
    today = datetime.today().date()
    diff = today - ultima_data_scrape
    if diff <= timedelta(days=1):
        return '#a8d8b9'  # green
    elif diff <= timedelta(days=3):
        return '#f3d38c'  # yellow
    else:
        return '#f9b4ab'  # red


def format_brl(amount):
    formatted_amount = f'{amount:,.2f}'.replace(',', 'x').replace('.', ',').replace('x', '.')
    return formatted_amount


def get_pos(lat, lng, df_m):
    for i in range(len(df_m)):
        if Point(lng, lat).within(df_m.loc[i, 'geometry']):
            return df_m.loc[i, 'Name']

    return None


def insert_email(email, criterios):
    # Ensure environment variables are set for DB connection
    if not all(key in os.environ for key in ["DB_ID", "DB_PASSWORD", "DB_REGION", "DB_PORT"]):
        raise EnvironmentError("Database environment variables are not fully set.")

    try:
        # Connect to the database
        conn = duckdb.connect()

        # Assuming the PostgreSQL extension is pre-installed and just needs to be loaded
        conn.execute('LOAD postgres;')

        # Securely format the connection string
        db_connection_string = f"postgresql://postgres.{os.environ['DB_ID']}:{os.environ['DB_PASSWORD']}@aws-0-{os.environ['DB_REGION']}.pooler.supabase.com:{os.environ['DB_PORT']}/postgres"

        # Attach the connection
        conn.execute(f"""
        ATTACH '{db_connection_string}' AS db (TYPE postgres);
        """)

        #check if the email is not an sql injection
        if "'" in email or ";" in email:
            conn.close()
            return "Email inválido"

        conn.execute(f"""
        INSERT INTO db.alerta (criterios, usuario)
        VALUES ('{criterios}', '{email}');
        """)
        conn.close()
        return 'Email inserido com sucesso'

    except Exception as e:
        conn.close()
        return (f"An error occurred: {e}")


