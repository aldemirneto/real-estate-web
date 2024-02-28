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


# Function to predict prices using the loaded model
def predict_prices(data):
    input_data = preprocess_input(data)
    predictions = xgb_model.predict(input_data)
    return predictions


st.title('Real Estate Price Prediction')
st.markdown("---")

# Load the dataset to get the unique neighborhood values
df = pd.read_parquet('lineitem.parquet')
neighborhoods = df['bairro'].unique().tolist()

#
selected_neighborhoods = st.selectbox('Select Neighborhood(s)', neighborhoods)
area = st.number_input('Area (in square meters)', min_value=0)
bedrooms = st.number_input('Number of bedrooms', min_value=0)
bathrooms = st.number_input('Number of bathrooms', min_value=0)
parking_spaces = st.number_input('Number of parking spaces', min_value=0)

# Prepare input data
input_data = {
    'bairro': selected_neighborhoods,
    'area': area,
    'quartos': bedrooms,
    'vagas': parking_spaces,
    'banheiros': bathrooms
}

# Make the prediction
if st.button('Predict'):

    prediction = predict_prices(input_data)

    st.subheader('Preço Estimado')
    # write the price in thousands with 2 decimals
    st.success(f"O Preço do seu imóvel é R${prediction[0] / 1000:.3f} mil reais")


# Attribution
st.markdown("---")
st.write("Built with ❤️ by Aldemir")
st.write("Check out my [GitHub](https://github.com/aldemirneto)")
