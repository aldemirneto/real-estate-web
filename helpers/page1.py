from shapely import Point
from datetime import datetime, timedelta


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