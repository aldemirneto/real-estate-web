
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import streamlit as st


st.sidebar.markdown("""
# 🏠 Recomendação de Imóveis

Nesta página, você receberá recomendações personalizadas de imóveis com base na sua navegação.

## Descubra Seu Imóvel Ideal

Insira suas preferências para obter recomendações de imóveis que combinam com seu estilo de vida e necessidades.

## Características Consideradas

Para as recomendações, levaremos em conta características como:

- Área do imóvel
- Número de quartos
- Número de banheiros
- Localização
- Faixa de preço

## Tecnologia de Recomendação

Utilizamos algoritmos de aprendizado de máquina para analisar seu comportamento de navegação e oferecer imóveis que se alinham ao seu perfil.

## Como Usar

1. Navegue pelos imóveis listados e interaja com as opções.
2. O sistema aprenderá com suas interações e ajustará as recomendações.
3. Explore as recomendações atualizadas e encontre o imóvel dos seus sonhos.

## Limitações

As recomendações são baseadas em padrões de navegação e podem não refletir todas as suas preferências pessoais. Considere visitar os imóveis recomendados antes de tomar qualquer decisão.

## Conclusão

Este sistema está aqui para facilitar sua busca pelo imóvel ideal. Suas preferências são valiosas para afinar as recomendações e ajudar você a encontrar o que procura.

""")

st.markdown(
    """
    <style>
    h1, h2 {
        color: #3b5998;
    }
    h2 {
        margin-top: 40px;
    }
    .sidebar .sidebar-content {
        background-color: #f1f1f1;
    }
    </style>
    """,
    unsafe_allow_html=True
)

with st.status("Gerando Recomendação"):
    # Standardize the data
    scaler = StandardScaler()
    kmeans = KMeans(n_clusters=7, random_state=42)
    df = pd.read_parquet('lineitem.parquet')
    # One-hot encode the 'bairro' column
    st.write("Normalizando dataset...")
    one_hot = pd.get_dummies(df['bairro'])
    df_encoded = df.join(one_hot)
    # List of features to use for clustering, including the one-hot encoded 'bairro'
    features = ['preco', 'area', 'quartos', 'banheiros'] + list(one_hot.columns)
    scaled_features = scaler.fit_transform(df_encoded[features])
    # Apply k-means clustering
    st.write("Clusterizando data...")
    df_encoded['cluster'] = kmeans.fit_predict(scaled_features)

    def recommend_properties(user_preferences, df_encoded):
        # Convert 'bairro' preference to one-hot encoded format
        bairro_preference = [1 if bairro in user_preferences['bairro'] else 0 for bairro in one_hot.columns]

        # Combine numerical preferences with 'bairro' preference
        combined_preferences = user_preferences['numerical'] + bairro_preference

        # Scale the combined preferences
        scaled_preferences = scaler.transform([combined_preferences])

        # Predict the cluster for the user's preferences
        user_cluster = kmeans.predict(scaled_preferences)

        # Filter the properties that belong to the selected cluster
        cluster_properties = df_encoded[df_encoded['cluster'] == user_cluster[0]]
        # Rank properties based on some criteria
        cluster_properties['distance_to_center'] = cluster_properties.apply(
            lambda x: sum((x[features] - combined_preferences) ** 2), axis=1)

        # Sort properties by their distance to the user's preferences
        recommended_properties = cluster_properties.sort_values('distance_to_center')

        return recommended_properties.head(10)  # return top 10 recommendations


    #i'll get the user preferences from the state

    dados = st.session_state.to_dict()

    # nao pegar chaves que tenham 'key' e 'page' no nome
    dados = {k: v for k, v in dados.items() if 'key' not in k and 'page' not in k}
    st.write("tratando dados do usuario...")
    if dados != {}:
        try:
            data = dict()
            data['numerical'] = [dados['preco'], dados['area'], dados['quartos'], dados['banheiros']]
            data['bairro'] = dados['bairro']
            st.write("Gerando Recomendação")
            recommendations = recommend_properties(data, df_encoded)
            recommendations.reset_index(drop=True, inplace=True)

            st.data_editor(recommendations[['area', 'preco', 'quartos','banheiros','bairro','link']])
        except Exception as e:
            st.write(f"houve um erro durante a geração da sua recomendação")
    else:
        st.markdown("## nao tem recomendação")
