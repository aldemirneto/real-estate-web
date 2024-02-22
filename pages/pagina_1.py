import json
from streamlit.components.v1 import html
import streamlit as st
import folium
import pandas as pd
import geopandas as gpd
import time
from streamlit_folium import st_folium
import numpy as np
from streamlit_modal import Modal
import helpers.page1 as helper




st.sidebar.markdown("""
# 📊 

Nesta página, você encontrará dados detalhados sobre os imóveis em cada bairro de Piracicaba, incluindo informações como:

- Número de quartos
- Número de banheiros
- Número de vagas de garagem
- Preço do imóvel

## Análise de Dados

Com esses dados, é possível fazer análises mais aprofundadas sobre cada bairro e suas propriedades, como a média de preços, a distribuição dos tipos de imóveis em cada bairro, entre outras informações relevantes para compradores, vendedores e investidores no mercado imobiliário.

## Utilização

Essas informações podem ser usadas para entender melhor o mercado imobiliário em Piracicaba, ajudando os usuários a tomar decisões informadas na compra, venda ou investimento em imóveis na cidade.

## Conclusão

Esta página fornece informações detalhadas sobre os imóveis em cada bairro de Piracicaba. Com essas informações, esperamos ajudar os usuários a entenderem melhor o mercado imobiliário e tomarem decisões mais informadas. 


""")

if 'fonte' not in st.session_state:
    st.session_state['fonte'] = 'Compra'

c1, c2 = st.columns(2)

container_compra = c1.empty()
if st.session_state.fonte == 'Compra':
    Compra = container_compra.button('Compra', type="primary", use_container_width=True)
else:
    Compra = container_compra.button('Compra', use_container_width=True)
if Compra:
    if st.session_state.fonte == 'Aluguel':
        st.session_state.fonte = 'Compra'
        if 'preco' in st.session_state:
            del st.session_state['preco']
        if 'page' not in st.session_state:
            st.session_state['page'] = 1

        st.rerun()

container_2 = c2.empty()
if st.session_state.fonte == 'Aluguel':
    Aluguel = container_2.button('Aluguel', type="primary", use_container_width=True)
else:
    Aluguel = container_2.button('Aluguel', use_container_width=True)
if Aluguel:
    if st.session_state.fonte == 'Compra':
        st.session_state.fonte = 'Aluguel'
        if 'preco' in st.session_state:
            del st.session_state['preco']
        if 'page' not in st.session_state:
            st.session_state['page'] = 1
        st.rerun()


df = pd.read_parquet('lineitem.parquet')

bairro_options = sorted(df['bairro'].unique())
# appending the value todos to the bairro_options
bairro_options = np.append(bairro_options, '_Todos')
if 'bairro' not in st.session_state:
    index = int(np.where(bairro_options == '_Todos')[0][0])
    bairro = st.selectbox("Selecione o bairro", [x.replace('_', ' ') for x in bairro_options], index=index,
                          placeholder='Selecione o bairro')
else:
    try:
        index = int(np.where(bairro_options == st.session_state.bairro)[0][0])
    except:
        index = None
    bairro = st.selectbox("Selecione o bairro", [x.replace('_', ' ') for x in bairro_options], index=index,
                          placeholder='Selecione o bairro')
    st.session_state['bairro'] = bairro.replace(' ', '_')
    if st.session_state.bairro != bairro.replace(' ', '_'):
        st.rerun()

# Inicialização do modal
modal_geo = Modal("Busca georreferenciada de bairros!!", key="modal_geo_key")

# Botão para abrir o modal
btn_geo_busca = st.button("Quer buscar a localização no mapa?", key="btn_geo_busca_key")
if btn_geo_busca:
    modal_geo.open()

st.markdown(
    f"""
    <style>
    div[data-modal-container='true'][key='{modal_geo.key}'] {{
        width: calc(100vw - 300px) !important;  <!-- Ajusta a largura -->
        left: 300px !important; <!-- Posiciona o modal após a barra lateral -->
    }}

    div[data-modal-container='true'][key='{modal_geo.key}'] > div:first-child > div:first-child {{
        background-color: black !important;  <!-- Cor de fundo do modal em preto -->
        color: #eee !important;  <!-- Cor do texto do modal em modo escuro -->
    }}

    div[data-modal-container='true'][key='{modal_geo.key}']::before {{
        background-color: rgba(0, 0, 0, 0.5) !important;  <!-- Cor do fundo semi-transparente em preto -->
    }}
    </style>
    """,
    unsafe_allow_html=True
)
# Conteúdo do modal
if modal_geo.is_open():
    with modal_geo.container():
        df_m = gpd.read_file('piracicaba.json')

        # Specify the target projected CRS
        target_crs = 'urn:ogc:def:crs:OGC:1.3:CRS84'

        # Reproject the geometry column
        df_m['geometry'] = df_m['geometry'].to_crs(target_crs)

        # Calculate centroids
        df_m['centroid'] = df_m['geometry'].centroid

        df_m['Name'] = df_m['Name'].str.replace(' ', '_')
        df_m['Name'] = df_m['Name'].str.capitalize()
        df_m['Name'] = df_m['Name'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')

        # replace 'Bairro Alto' with 'Alto' in the df dataframe
        df_m['Name'] = df_m['Name'].str.replace('Bairro_alto', 'Alto')

        # Create a feature group
        feature_group = folium.FeatureGroup(name='My Polygons')

        # Add your polygons to the feature group
        for _, row in df_m.iterrows():
            folium.GeoJson(
                row['geometry'],
                name=row['Name'],
                style_function=lambda x: {'color': 'black', 'weight': 0, 'fillOpacity': 0.05},
                highlight_function=lambda x: {'weight': 4, 'color': 'red'}
            ).add_to(feature_group)

        # create the folium map
        m = folium.Map(location=[df_m.loc[df_m['Name'] == 'Centro', 'centroid'].values[0].y,
                                 df_m.loc[df_m['Name'] == 'Centro', 'centroid'].values[0].x], zoom_start=12.5)

        feature_group.add_to(m)
        # plot the choropleth map
        choropleth = folium.GeoJson(
            data=df_m[['Name', 'geometry']].to_json()
        ).add_to(m)

        # render the map in streamlit smaller
        map = st_folium(m, height=300, width=600, feature_group_to_add=feature_group)

        data = None
        if map.get("last_clicked"):
            data = helper.get_pos(map["last_clicked"]["lat"], map["last_clicked"]["lng"], df_m)

        if data:
            if st.button(f"esse é o bairro {data.replace('_', ' ')}, quer continuar?"):
                if 'bairro' not in st.session_state:
                    st.session_state['bairro'] = data
                else:
                    st.session_state['bairro'] = data
                modal_geo.close()
                st.rerun()

# Create 4 columns to pla   ce the widgets
col1, col2, col3, col4 = st.columns(4)

# Dropdowns for rooms in Column 1
# Number input for rooms in Column 1
if 'quartos' not in st.session_state:
    quartos = col1.number_input("Quartos", min_value=0, max_value=10, value=0, step=1)
    st.session_state['quartos'] = quartos
else:
    quartos = col1.number_input("Quartos", min_value=0, max_value=10, value=st.session_state.quartos, step=1)

# Number input for bathrooms in Column 2
if 'banheiros' not in st.session_state:
    banheiros = col2.number_input("Banheiros", min_value=0, max_value=9, value=0, step=1)
    st.session_state['banheiros'] = banheiros
else:
    banheiros = col2.number_input("Banheiros", min_value=0, max_value=9, value=st.session_state['banheiros'], step=1)

# Number input for parking spots in Column 3
if 'vagas' not in st.session_state:
    vagas = col3.number_input("Vagas", min_value=0, max_value=9, value=0, step=1)
    st.session_state['vagas'] = vagas

else:
    vagas = col3.number_input("Vagas", min_value=0, max_value=9, value=st.session_state.vagas, step=1)

# Number input for price in Column 4
if 'area' not in st.session_state:
    area = col4.number_input('Área mínima em m2', min_value=0, max_value=1000, value=0, step=10)
    st.session_state['area'] = area
else:
    area = col4.number_input('Área mínima em m2', min_value=0, max_value=1000, value=st.session_state.area, step=10)


preco = st.slider("Preço máximo", min_value=0, max_value=int(df['preco'].max()), value=1000, step=100)
st.session_state['preco'] = preco


pesquisa = st.button('Pesquisar', use_container_width=True)
if pesquisa:
    st.session_state['bairro'] = bairro.replace(' ', '_')
    st.session_state['quartos'] = quartos
    st.session_state['preco'] = preco
    st.session_state['area'] = area
    st.session_state['vagas'] = vagas
    st.session_state['banheiros'] = banheiros
    # Inicialização do modal
    st.session_state['page'] = 1


    if 'bairro' in st.session_state and 'preco' in st.session_state:

        bg = helper.cor_sinc(df)
        st.markdown(f"""<div style= 'background-color: rgba({int(bg[1:3], 16)}, {int(bg[3:5], 16)}, {int(bg[5:7], 16)}, 0.3);
                                    backdrop-filter: blur(10px);
                                    box-shadow: 0 8px 32px 0 rgba({int(bg[1:3], 16)}, {int(bg[3:5], 16)}, {int(bg[5:7], 16)}, 0);
                                    border-radius: 10px;
                                    text-align: center;border-radius: 7px;
                                    padding-left: 12px;
                                    padding-top: 18px;
                                    padding-bottom: 18px;'>"""
                    f"Ultima Atualização: {df['data_scrape'].max()}"
                    "</div>", unsafe_allow_html=True)

        bairro_condition = (df['bairro'] == st.session_state.bairro.replace(' ', '_')) | (
                    st.session_state.bairro == '_Todos')

        # Now apply the rest of the conditions
        other_conditions = (
                (df['quartos'] >= st.session_state.quartos) &
                (df['banheiros'] >= st.session_state.banheiros) &
                (df['vagas'] >= st.session_state.vagas) &
                (df['area'] >= st.session_state.area) &
                (df['preco'] <= st.session_state.preco)
        )

        # Combine the conditions
        resultados = df[bairro_condition & other_conditions]

        if len(resultados) == 0:
            st.markdown(f"""<div style=' 
                            background-color: #red;
                            backdrop-filter: blur(5px); 
                            box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.1); 
                            border-radius: 10px; 
                            text-align: center; 
                            padding: 20px; 
                            font-size: 1.5em; 
                            font-family: Arial, sans-serif;'>"""
                        f"Nenhum resultado encontrado"
                        "</div>", unsafe_allow_html=True)

        else:
            # drop duplicates with the link but keeping the one with the last date on the column 'last-seen'

            resultados = resultados.drop_duplicates(subset=['link'], keep='last')

            # if bairro = 'Todos' then show the bairro column
            if bairro == ' Todos':
                resultados_sem_data_scrape = resultados.drop(['data_scrape', 'last_seen', 'imobiliaria'],
                                                             axis=1).reset_index(drop=True)
                # replace the _ for space in the column 'bairro'
                resultados_sem_data_scrape['bairro'] = resultados_sem_data_scrape['bairro'].str.replace('_', ' ')
                resultados_sem_data_scrape = resultados_sem_data_scrape[
                    ['bairro', 'preco', 'area', 'quartos', 'banheiros', 'vagas', 'link']]

            else:
                resultados_sem_data_scrape = resultados.drop(['data_scrape', 'bairro', 'last_seen'], axis=1).reset_index(
                    drop=True)
                resultados_sem_data_scrape = resultados_sem_data_scrape[
                    ['imobiliaria', 'preco', 'area', 'quartos', 'banheiros', 'vagas', 'link']]

            resultados_sem_data_scrape['preco'] = resultados_sem_data_scrape['preco'].apply(lambda x: helper.format_brl(x))

            table_style = """
            <style>
    
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    border: none;
    
                }}
                th {{
    
                    Font-Weight: Bold;
                    Border-Bottom: 4px Solid #FAFAFA;  /* Optional: For a Subtle Border Under Headers */
                    Padding: 10px;  /* Optional: For a Touch of Space Around Text */
                    text-align: center;
                }}
                td {{
    
                    Border-Bottom: 4px Solid #ddd; /* Optional: For Subtle Borders Between Table Cells */
                    Padding: 10px; /* Optional: For a Touch of Space Around Text */
                    text-align: center;
                }}
    
                tr:hover {{
                    background-color: #a1a1a1; /* Optional: Hover row color */
                    cursor: pointer;
                }}
                a {{
                    color: #000000;
                    text-decoration: none;
                }}
    
            @media (max-width: 500px) {{
                 td, th, tr {{
                border:none; !important;
                border-bottom: none !important; /* Removing the border and ensuring this rule has high specificity */
                border-top: none !important; /* Removing the top border as well */
    
            }}
                td:first-child, th:first-child {{
                #background-color: #1C8394;
                    background-color: #1C8394; /* Choose your color */
                    color: white; /* Text color, choose what suits your background color */
                    border-radius: 5px; /* Optional: for rounded corners */
                    padding: 10px; /* Space inside the cell */
                    text-align: left;
                }}
                td {{
                border-bottom: 0; /* Removing the border */
                display: block;
                position: relative;
                padding-left: 0;
                padding-right: 30px;
                text-align: right;
                font-weight: bold;
                font-style: roboto;
                }}
    
            td:before {{
                content: attr(data-title);
                position: absolute;
                left: 0;
                width: 45%;
                padding-right: 10px;
                white-space: nowrap;
                text-align: right;
                font-weight: normal;
            }}
    
            th {{
                border-bottom: 0; /* Removing the border */
                display: block;
                position: relative;
                text-align: right;
                padding-left: 0;
                font-style: italic;
    ;
            }}
    
            th:before {{
                content: attr(data-title);
                position: absolute;
                left: 0;
                width: 45%;
                padding-right: 10px;
                white-space: nowrap;
                text-align: left;
            }}
    
            .dataframe thead {{
                display: none; /* Hide headers */
            }}
    
            .dataframe tbody td:not(:first-child) {{
                display: block;
                position: relative;
                padding-left: 0; /* Resetting padding to 0 */
                font-weight: normal;
                font-style: roboto;
                border: none;
            }}
    
            .dataframe tbody td:not(:first-child):before {{
                 content: attr(data-title);
                position: absolute;
                left: 0;
                width: 45%;
                padding-right: 10px;
                white-space: nowrap;
                text-align: left;
                font-weight: normal;
    
            }}
        }}
    
            </style>
            """

            st.markdown(table_style.format(), unsafe_allow_html=True)
            # Define the number of rows per page
            rows_per_page = 30

            # Calculate the number of pages
            num_pages = len(resultados_sem_data_scrape) // rows_per_page
            if len(resultados_sem_data_scrape) % rows_per_page > 0:
                num_pages += 1

            start_idx = (st.session_state['page'] - 1) * rows_per_page
            end_idx = st.session_state['page'] * rows_per_page

            resultados_sem_data_scrape = resultados_sem_data_scrape.iloc[start_idx:end_idx]
            # capitalize the first letter of the columns
            resultados_sem_data_scrape.columns = [col.capitalize() for col in resultados_sem_data_scrape.columns]
            # rename the columns area to include an (m²)
            resultados_sem_data_scrape = resultados_sem_data_scrape.rename(
                columns={'Area': 'Area (m²)', 'Preco': 'Preço (R$)'})
            # make the link clickable, the text of the link is the name between the www. and .com
            resultados_sem_data_scrape['Link'] = resultados_sem_data_scrape['Link'].apply(lambda x: f"<a href='{x}' target='_blank'>{x[12:x.find('.com')].capitalize().replace('Imobiliariajunqueira', 'Junqueira')}</a>")

            st.markdown(table_style.format(), unsafe_allow_html=True)
            st.write(resultados_sem_data_scrape.to_html(escape=False, index=False), unsafe_allow_html=True)
            html("""
            <script>
            /*if the size of the window is over 600px*/
            if (parent.window.innerWidth > 600) {{
            var links = parent.window.document.querySelectorAll('tbody tr td a');
                        for (var i = 0; i < links.length; i++) {{
    
                            links[i].innerHTML = '🏠';
                        }}
                        }}
            </script>
            """, height=0, width=0)
            # get the position of the link column
            link_column = resultados_sem_data_scrape.columns.get_loc('Link')

            b1, b2 = st.columns(2)
            Previous = b1.button('Página Anterior', use_container_width=True)

            Next = b2.button('Próxima Pagina', use_container_width=True)

            # Create Next and Previous buttons
            if Previous and st.session_state['page'] > 1:
                st.session_state['page'] -= 1

            if Next and st.session_state['page'] < num_pages:
                st.session_state['page'] += 1


            html(f"""
                    <script>
                    function replaceText(document) {{
                        if (parent.window.innerWidth > 600) {{
                        var links = document.querySelectorAll('tbody tr td a');
                        for (var i = 0; i < links.length; i++) {{
    
                            links[i].innerHTML = '🏠';
                        }}
                        }}
                    }}
    
    
                    function addDataTitles(document) {{
    
                        const table = document.querySelector('.dataframe');
                        const headers = Array.from(table.querySelectorAll('thead th'))
                            .map(th => th.textContent);
    
    
                        const rows = table.querySelectorAll('tbody tr');            
                        rows.forEach(row => {{
                            const cells = row.querySelectorAll('td');
                            cells.forEach((cell, index) => {{
                            if (index === 0) {{
                                 cell.setAttribute('row-scope', '1');
                            }}
                            else{{
                                cell.setAttribute('data-title', headers[index]);
                                }}
                            }});
                        }});
                    }}
                    const elements = parent.window.document.querySelectorAll('.stButton > button');
                    elements[3].addEventListener('click', function() {{
                        console.log('executing');
                        /*wait 1 second and exec the functions*/
                        setTimeout(function() {{
                            console.log('executed');
                            replaceText(parent.window.document);
                            addDataTitles(parent.window.document);
                        }}, 1000);
    
                    }});
                    elements[4].addEventListener('click', function() {{
                        addDataTitles(parent.window.document);
                        replaceText(parent.window.document);
    
                    }});
                    elements[5].addEventListener('click', function() {{
                        addDataTitles(parent.window.document);
                        replaceText(parent.window.document);
    
                    }});
                    addDataTitles(parent.window.document);
    
    
                    </script>
    
                    """, width=0, height=0)

modal_alerta = Modal("Criar Alerta", key="modal_alerta_key")

# Botão para abrir o modal
btn_criar_alerta = st.button(
    "Deseja ser notificado quando novos imóveis correspondentes aos critérios acima estiverem disponíveis?")
if btn_criar_alerta:
    modal_alerta.open()

st.markdown(
    f"""
                    <style>
                    div[data-modal-container='true'][key='{modal_alerta.key}'] {{
                        width: calc(100vw - 300px) !important;  <!-- Ajusta a largura -->
                        left: 300px !important; <!-- Posiciona o modal após a barra lateral -->
                    }}

                    div[data-modal-container='true'][key='{modal_alerta.key}'] > div:first-child > div:first-child {{
                        background-color: black !important;  <!-- Cor de fundo do modal em preto -->
                        color: #eee !important;  <!-- Cor do texto do modal em modo escuro -->
                    }}

                    div[data-modal-container='true'][key='{modal_alerta.key}']::before {{
                        background-color: rgba(0, 0, 0, 0.5) !important;  <!-- Cor do fundo semi-transparente em preto -->
                    }}
                    </style>
                    """,
    unsafe_allow_html=True
)
# Conteúdo do modal
if modal_alerta.is_open():

    with modal_alerta.container():
        st.write(
            "Informe seu e-mail para receber notificações sobre novos imóveis que correspondam aos seus critérios de busca.")

        # Campo para inserção do e-mail
        email = st.text_input("Endereço de E-mail")
        # Botão de confirmação
        if st.button("Confirmar"):
            st.toast('Enviando alerta ')
            # Envia o e-mail
            dados = st.session_state.to_dict()
            # nao pegar chaves que tenham 'key' e 'page' no nome
            dados = {k: v for k, v in dados.items() if 'key' not in k and 'page' not in k}
            st.write(dados)
            # st.toast(helper.insert_email(email, dados), icon='🎉')
            # transform the dict into a json
            dados = json.dumps(dados)
            st.write(helper.insert_email(email, dados))
            time.sleep(.8)
            modal_alerta.close()
