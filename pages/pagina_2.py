import streamlit as st
import folium
import pandas as pd
import geopandas as gpd
from streamlit_folium import st_folium



st.sidebar.markdown("""
# 🗺️ 

Nesta página, você encontrará dados sobre cada bairro de Piracicaba, representados no mapa com o preço médio de venda de imóvel em cada um deles.

## Visualização no Mapa

Utilizando dados geoespaciais, é possível visualizar no mapa os bairros de Piracicaba e o preço médio de venda de imóvel em cada um deles. Essa visualização é útil para entender como o mercado imobiliário está distribuído na cidade.

## Análise de Dados

Com base nos dados coletados, é possível fazer análises mais aprofundadas sobre cada bairro, como a média de preços, tipos de imóveis mais comuns, etc. Essas informações são valiosas para compradores, vendedores e investidores no mercado imobiliário.

## Conclusão

Esta página fornece uma visão geral dos dados de cada bairro de Piracicaba no mapa. Com essas informações, esperamos ajudar os usuários a entenderem melhor o mercado imobiliário e tomarem decisões mais informadas.

    
""")

df = gpd.read_file('piracicaba.json')

# Specify the target projected CRS
target_crs = 'urn:ogc:def:crs:OGC:1.3:CRS84'

# Reproject the geometry column
df['geometry'] = df['geometry'].to_crs(target_crs)

# Calculate centroids
df['centroid'] = df['geometry'].centroid

# create a column with the average price per neighborhood(if the neighborhood has more than 10 estates), read from the csv file
df_bairros = pd.read_parquet('lineitem.parquet')
# Remove non-numeric values from 'preco' column
df_bairros['preco'] = pd.to_numeric(df_bairros['preco'], errors='coerce')

# Filter out groups with less than 10 rows
df_bairros = df_bairros.groupby('bairro').filter(lambda x: len(x) > 10)

# Calculate the mean of 'preco' after grouping
df_bairros = df_bairros.groupby('bairro')['preco'].mean().reset_index()
#comparing the two dataframes, we can see that the neighborhood names are not the same
#so we need to change the names in one of the dataframes

df['Name'] = df['Name'].str.replace(' ', '_')
df['Name'] = df['Name'].str.capitalize()
df['Name'] = df['Name'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')


#replace 'Bairro Alto' with 'Alto' in the df dataframe
df['Name'] = df['Name'].str.replace('Bairro_alto', 'Alto')


#now i want the column preco of the df_bairros dataframe to be in the df dataframe
df = df.merge(df_bairros, left_on='Name', right_on='bairro', how='left')

#drop the column bairro and switch NA values to 0
df = df.drop(columns=['bairro'])
df['preco'] = df['preco'].fillna(0)
df['preco'] = df['preco']/1000000

#create the folium map
#the starting point is the centroid of the 'centro' neighborhood
m = folium.Map(location=[df.loc[df['Name'] == 'Centro', 'centroid'].values[0].y, df.loc[df['Name'] == 'Centro', 'centroid'].values[0].x], zoom_start=12.5)

#marker for each neighborhood with the color based on the average price of the neighborhood
for i in range(len(df)):
    folium.Marker(
        location=[df.loc[i, 'centroid'].y, df.loc[i, 'centroid'].x],
        tooltip=f"Preço médio venda bairro {df.loc[i,'Name'].replace('_', ' ')}<br>" \
              f"<div style='text-align: center;'>{float(round(df.loc[i, 'preco'],2)) if df.loc[i, 'preco'] > 0.0 else 'N/A'} milhões de reais</div>",
        icon=folium.Icon(color='green' if df.loc[i, 'preco'] < 1 else 'orange' if df.loc[i, 'preco'] < 2 else 'red')
    ).add_to(m)
# m.show_in_browser()
#plot the choropleth map
choropleth = folium.Choropleth(
    geo_data=df[['Name', 'geometry']],
    data=df,
    columns=['Name', 'preco'],
    key_on='feature.properties.Name',
    fill_color='YlOrRd',
    fill_opacity=0.7,
    line_opacity=0.2,
    line_weight=3,
    legend_name='Preço médio dos imóveis (milhões de reais)'
).add_to(m)



# # Renderiza o mapa no Streamlit
st_folium(m)
