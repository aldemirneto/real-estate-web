import os

from openai import OpenAI
import numpy as np
import pandas as pd
import streamlit as st
import json
from xgboost import XGBRegressor

st.sidebar.markdown("""
# 🏠 Predição de Preço de Imóvel

Nesta página, você poderá obter uma estimativa do preço de um imóvel com base em suas características.

## Características do Imóvel

Para realizar a predição do preço, serão consideradas as seguintes características do imóvel:

- Área do imóvel
- Número de quartos
- Número de banheiros
- Número de vagas de estacionamento

## Modelo de Machine Learning

Utilizamos um modelo de Machine Learning treinado com dados de imóveis para fazer a predição do preço. O modelo aprendeu padrões nos dados e pode fornecer uma estimativa com base nas características fornecidas.

## Como Usar

1. Preencha as características do imóvel nos campos à direita.
2. Clique no botão "Prever" para obter a estimativa do preço.
3. O resultado será exibido na página principal.

## Limitações

É importante ressaltar que essa estimativa é baseada em dados históricos e em um modelo preditivo. O preço real do imóvel pode variar de acordo com fatores externos e condições do mercado imobiliário.

## Conclusão

Essa página foi criada para ajudar usuários a terem uma ideia aproximada do preço de um imóvel com base em suas características. Lembre-se de considerar outros fatores relevantes ao tomar decisões relacionadas à compra ou venda de um imóvel.

""")

st.markdown(
    """
    <style>

    h1, h2{
        color: #3b5998;
    }
    h2 {
        margin-top: 40px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Function to load the XGBoost model
@st.cache_resource()
def load_model():
    xgb_model = XGBRegressor()
    xgb_model.load_model('Model/xgb_model.json')
    return xgb_model

st.markdown('# Escolha um modelo para começar a predição')
c1, c2 = st.columns(2)

xgboost = c1.button('XGBOOST', use_container_width=True)
gpt = c2.button('ChatGPT', use_container_width=True)

if 'modelo' not in st.session_state:
    st.session_state['modelo'] = 'sem_modelo'
try:
    if xgboost:
        st.session_state['modelo'] = 'xgboost'
    elif gpt:
        st.session_state['modelo'] = 'gpt'
    else:
        modelo = "sem modelo"  # Use the defined variable for clarity
except NameError:
    st.error("Please ensure either 'xgboost' or 'gpt' variable is defined.")
    st.stop()  # Halt execution to prevent unexpected behavior



# Load the XGBoost model
xgb_model = load_model()

# Load the neighborhood encoding mapping
with open('Model/neighborhood_encoding.json', 'r') as f:
    neighborhood_encoding = json.load(f)


# Function to preprocess input data
def preprocess_input(data):
    # Create a DataFrame from the input data
    df = pd.DataFrame([data])

    # Encode the neighborhood using the loaded mapping
    df['bairro_encoded'] = df['bairro'].map(neighborhood_encoding)
    #
    # Reorder the columns to match the training data
    df = df[['area', 'quartos', 'vagas', 'banheiros', 'bairro_encoded']]

    return df

def predict_gpt(input_data):
    client = OpenAI(api_token=os.environ['OPENAI_API_KEY'])

    # Define os anúncios de imóveis
    anuncios = [
        {"preco": 250000.0, "condominio": None, "area": 69.91, "quartos": 3, "vagas": 2, "banheiros": 2,
         "imobiliaria": "Frias_neto", "bairro": "Centro", "status": "Compra",
         "tipo": "Apartamento"},
        {"preco": 140000.0, "condominio": None, "area": 61.46, "quartos": 2, "vagas": 1, "banheiros": 1,
         "imobiliaria": "Frias_neto", "bairro": "Nova_america", "status": "Compra",
         "tipo": "Apartamento"},
        {"preco": 195000.0, "condominio": None, "area": 57.0, "quartos": 2, "vagas": 1, "banheiros": 1,
         "imobiliaria": "Frias_neto", "bairro": "Nova_america", "status": "Compra",
         "tipo": "Apartamento"},
        {"preco": 240000.0, "condominio": None, "area": 100.9, "quartos": 3, "vagas": 1, "banheiros": 1,
         "imobiliaria": "Frias_neto", "bairro": "Alto", "status": "Compra",
         "tipo": "Apartamento"},
        {"preco": 250000.0, "condominio": None, "area": 62.0, "quartos": 2, "vagas": 1, "banheiros": 2,
         "imobiliaria": "Frias_neto", "bairro": "Paulista", "status": "Compra",
         "tipo": "Apartamento", },
        {"preco": 250000.0, "condominio": None, "area": 62.0, "quartos": 2, "vagas": 1, "banheiros": 2,

         "imobiliaria": "Frias_neto", "bairro": "Paulista", "status": "Compra",
         "tipo": "Apartamento"},
        {"preco": 380000.0, "condominio": None, "area": 63.0, "quartos": 2, "vagas": 2, "banheiros": 2,

         "imobiliaria": "Frias_neto", "bairro": "Paulista", "status": "Compra",
         "tipo": "Apartamento"},
        {"preco": 290000.0, "condominio": None, "area": 125.0, "quartos": 2, "vagas": 2, "banheiros": 1,

         "imobiliaria": "Frias_neto", "bairro": "Vila_sonia", "status": "Compra",
         "tipo": "Casa"},
        {"preco": 230000.0, "condominio": None, "area": 55.0, "quartos": 2, "vagas": 1, "banheiros": 1,

         "imobiliaria": "Frias_neto", "bairro": "Jardim_nova_iguacu", "status": "Compra",
         "tipo": "Apartamento"},
        {"preco": 138000.0, "condominio": None, "area": 45.0, "quartos": 2, "vagas": 1, "banheiros": 1,

         "imobiliaria": "Frias_neto", "bairro": "Dois_corregos", "status": "Compra",
         "tipo": "Apartamento"},
        {"preco": 620000.0, "condominio": None, "area": 392.0, "quartos": 3, "vagas": 3, "banheiros": 3,

         "imobiliaria": "Frias_neto", "bairro": "Nova_piracicaba", "status": "Compra",
         "tipo": "Casa"},
    ]

    # Converte os anúncios para JSON
    anuncios_json = json.dumps(anuncios)
    anuncio_predito = json.dumps(input_data)


    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system",
                   "content": f"Você é um corretor de imoveis, acostumado a estimar preços de casas, passado os seguintes imoveis de uma cidade:{anuncios_json}, voce irá estimar exatamente o valor do imovel que eu irei passar para voce na pergunta"},
                  {"role": "user",
                   "content": f"Tenho esse imóvel {anuncio_predito}, qual o valor dele? quero apenas o valor dele formatado, separando as casas decimais, sem nenhum texto a mais, assim: no caso de valor ser 250.690,00 retorne apenas 250.690"}],

    )

    return stream.choices[0].message.content
# Function to predict prices using the loaded model
def predict_prices(data):
    input_data = preprocess_input(data)
    predictions = xgb_model.predict(input_data)
    return predictions

st.markdown("---")

# Load the dataset to get the unique neighborhood values
df = pd.read_parquet('lineitem.parquet')
neighborhoods = df['bairro'].unique().tolist()

#
selected_neighborhoods = st.selectbox('Bairros selecionados', neighborhoods)
area = st.number_input('Area (em metros quadrados)', min_value=0)
quartos = st.number_input('numero de quartos', min_value=0)
banheiros = st.number_input('numero de banheiros', min_value=0)
vagas = st.number_input('numero de vagas', min_value=0)

# Prepare input data
input_data = {
    'bairro': selected_neighborhoods,
    'area': area,
    'quartos': quartos,
    'vagas': vagas,
    'banheiros': banheiros
}

# Make the prediction
if st.button('Predict'):
    prediction = None
    if st.session_state['modelo'] == 'xgboost':
        prediction = predict_prices(input_data)[0] / 1000
        # write the price in thousands with 2 decimals
    elif st.session_state['modelo'] =='gpt':
        prediction = predict_gpt(input_data)
        print('prediction')
    st.subheader('Preço Estimado')
    st.success(f"O Preço do seu imóvel é R${float(prediction) :.3f}")


# Attribution
st.markdown("---")
st.write("Built with ❤️ by Aldemir")
st.write("Check out my [GitHub](https://github.com/aldemirneto)")
