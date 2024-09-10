import scipy.stats as stats
import numpy as np
import streamlit as st
import pandas as pd
import sqlite3 as s3
import plotly.graph_objects as go

# Read the dataset
data = pd.read_parquet('lineitem.parquet')

st.write(s3.version)
def treated_chart(data):
    # Calculate the IQR
    Q1 = np.percentile(data['preco'], 1)
    Q3 = np.percentile(data['preco'], 75)
    IQR = Q3 - Q1

    # Define the lower and upper bounds
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Filter out the outliers
    filtered_data = data[(data['preco'] >= lower_bound) & (data['preco'] <= upper_bound)]

    # Create the treated version of the chart
    fig = go.Figure(data=[go.Histogram(x=filtered_data['preco'], marker_color='#EB89B5', opacity=0.75)])
    fig.update_layout(title_text='Histograma de Preços', xaxis_title_text='Preço', yaxis_title_text='Contagem')

    return fig


# Function to create the raw version of the chart
def raw_chart(data):
    # Create the raw version of the chart
    fig = go.Figure(data=[go.Histogram(x=data['preco'], marker_color='#EB89B5', opacity=0.75)])
    fig.update_layout(title_text='Histograma de Preços ', xaxis_title_text='Preço', yaxis_title_text='Contagem')

    return fig


# # Chart 2: Scatter Plot: Price vs. Area with an no transparency, edgecolor black, instead of 1e^7, show as 10,000,000 and an correlation line


def treated_scatter(data):
    # Calculate the IQR for 'preco' column
    Q1 = data['preco'].quantile(0.1)
    Q3 = data['preco'].quantile(0.75)
    IQR = Q3 - Q1

    # Define the lower and upper bounds
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Filter out the outliers
    filtered_data = data[(data['preco'] >= lower_bound) & (data['preco'] <= upper_bound)]

    # Create the treated scatter plot
    fig = go.Figure(data=go.Scatter(x=filtered_data['area'], y=filtered_data['preco'], mode='markers'))
    fig.update_xaxes(showline=True, linewidth=1, linecolor='black', mirror=True)
    fig.update_yaxes(showline=True, linewidth=1, linecolor='black', mirror=True)
    fig.update_layout(title='Preço vs. Área', xaxis_title='Área', yaxis_title='Preço')

    return fig


# Function to create the raw version of the scatter plot
def raw_scatter(data):
    # Create the raw scatter plot
    fig = go.Figure(data=go.Scatter(x=data['area'], y=data['preco'], mode='markers'))
    fig.update_xaxes(showline=True, linewidth=1, linecolor='black', mirror=True)
    fig.update_yaxes(showline=True, linewidth=1, linecolor='black', mirror=True)
    fig.update_layout(title='Preço vs. Área', xaxis_title='Área', yaxis_title='Preço')

    return fig


# Chart 3: Bar Chart: Number of Properties by Number of Rooms, with a button to take the outliars out of the dataset

def treated_bar_bedrooms(data):
    # Filter out any outliers or unwanted data manipulation
    # (since it's a bar chart, outliers may not be applicable, but you can customize this function as needed)
    filtered_data = data[data['quartos'] < data['quartos'].quantile(0.99)]

    # Create the treated bar chart
    fig = go.Figure(
        data=[go.Bar(x=sorted(filtered_data['quartos'].unique().tolist()), y=filtered_data['quartos'].value_counts())])
    fig.update_layout(title='Número de Propriedades por Número de Quartos',
                      xaxis_title='Número de Quartos',
                      yaxis_title='Número de Propriedades')

    return fig


# Function to create the raw version of the bar chart
def raw_bar_bedrooms(data):
    # Create the raw bar chart
    fig = go.Figure(data=[go.Bar(x=sorted(data['quartos'].unique().tolist()), y=data['quartos'].value_counts())])
    fig.update_layout(title='Número de Propriedades por Número de Quartos',
                      xaxis_title='Número de Quartos',
                      yaxis_title='Número de Propriedades')

    return fig


# # Chart 4: Bar Chart: Number of Properties by Number of Bathrooms
# Function to create the treated version of the bar chart for number of bathrooms
def treated_bar_bathrooms(data):
    # Filter out outliers by removing the outliers number of bathrooms

    filtered_data = data[data['banheiros'] < data['banheiros'].quantile(0.99)]

    # Create the treated bar chart
    fig = go.Figure(data=[
        go.Bar(x=sorted(filtered_data['banheiros'].unique().tolist()), y=filtered_data['banheiros'].value_counts())])
    fig.update_layout(title='Número de Propriedades por Número de Banheiros ',
                      xaxis_title='Número de Banheiros',
                      yaxis_title='Número de Propriedades')

    return fig


# Function to create the raw version of the bar chart for number of bathrooms
def raw_bar_bathrooms(data):
    # Create the raw bar chart
    fig = go.Figure(data=[go.Bar(x=sorted(data['banheiros'].unique().tolist()), y=data['banheiros'].value_counts())])
    fig.update_layout(title='Número de Propriedades por Número de Banheiros ',
                      xaxis_title='Número de Banheiros',
                      yaxis_title='Número de Propriedades')

    return fig


# Chart 5: Bar Chart: Number of Properties by Number of Parking Spaces adding title and labels and description and making it interactive

def treated_bar_parking_spots(data):
    # Filter out outliers by removing the outliers number of bathrooms

    filtered_data = data[data['vagas'] < data['vagas'].quantile(0.99)]

    # Create the treated bar chart
    fig = go.Figure(
        data=[go.Bar(x=sorted(filtered_data['vagas'].unique().tolist()), y=filtered_data['vagas'].value_counts())])
    fig.update_layout(title='Número de Propriedades por Número de Vagas ',
                      xaxis_title='Número de Banheiros',
                      yaxis_title='Número de Propriedades')

    return fig


# Function to create the raw version of the bar chart for number of bathrooms
def raw_bar_parking_spots(data):
    # Create the raw bar chart
    fig = go.Figure(data=[go.Bar(x=sorted(data['vagas'].unique().tolist()), y=data['vagas'].value_counts())])
    fig.update_layout(title='Número de Propriedades por Número de Vagas ',
                      xaxis_title='Número de vagas',
                      yaxis_title='Número de Propriedades')

    return fig


st.markdown('## **Análise Exploratória de Dados**')
st.sidebar.markdown("""
#  🔍 Análise de Dados Imobiliários
## Outliers na Análise de Dados

Outliers são pontos de dados que se desviam significativamente do restante dos dados. Eles podem ter um impacto significativo na análise e visualização de dados, potencialmente distorcendo os resultados ou conduzindo a interpretações equivocadas. É importante considerar os outliers e lidar com eles de maneira adequada para garantir a integridade da análise.

Nesta página, você pode explorar o impacto dos outliers na visualização de dados, Como? alterne entre as versões tratada e bruta para ver.

Ao passo que na versao tratada estamos pegando dados ate o 75 percentil, na versao bruta estamos pegando todos os dados, o impacto é instantâneo!

""")

# Botão para alternar entre as versões tratada e bruta do gráfico de barras
version = st.sidebar.radio("Versão do Gráfico", ('Tratada', 'Bruta'))
if version == 'Bruta':
    st.plotly_chart(raw_chart(data), use_container_width=True)
    st.plotly_chart(raw_scatter(data), use_container_width=True)
    st.plotly_chart(raw_bar_bedrooms(data), use_container_width=True)
    st.plotly_chart(raw_bar_bathrooms(data), use_container_width=True)
    st.plotly_chart(raw_bar_parking_spots(data), use_container_width=True)
else:
    st.plotly_chart(treated_chart(data), use_container_width=True)
    st.plotly_chart(treated_scatter(data), use_container_width=True)
    st.plotly_chart(treated_bar_bedrooms(data), use_container_width=True)
    st.plotly_chart(treated_bar_bathrooms(data), use_container_width=True)
    st.plotly_chart(treated_bar_parking_spots(data), use_container_width=True)

# Calculate mean and median
mean_price = np.mean(data['preco'])
median_price = np.median(data['preco'])
std_price = np.std(data['preco'])
# Chart 6: Normal Distribution of Prices displaying the quartiles
# Calculate mean, median, and quantiles

quantiles = np.percentile(data['preco'], [1, 25, 50, 75, 99])

# Chart 6: Normal Distribution of Prices
# the linspace should be between the 1% quantile and the 99% quantile

x = np.linspace(quantiles[0], quantiles[-1], 100)
y = stats.norm.pdf(x, mean_price, std_price)
# Create the figure using Plotly graph objects
fig = go.Figure()

## Add the normal distribution curve
fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='Curva Normal', line=dict(color='blue')))

# Add vertical lines for mean and quantiles using go.Line stopping on the normal distribution curve

fig.add_trace(go.Scatter(x=[mean_price, mean_price], y=[0, stats.norm.pdf(mean_price, mean_price, std_price)],
                         mode='lines', name='Média', line=dict(color='red', dash='dash')))

fig.add_trace(go.Scatter(x=[quantiles[0], quantiles[0]], y=[0, stats.norm.pdf(quantiles[0], mean_price, std_price)],
                         mode='lines', name='1º Percentil', line=dict(color='green', dash='dash')))
fig.add_trace(go.Scatter(x=[quantiles[1], quantiles[1]], y=[0, stats.norm.pdf(quantiles[1], mean_price, std_price)],
                         mode='lines', name='25º Percentil', line=dict(color='blue', dash='dash')))
fig.add_trace(go.Scatter(x=[quantiles[2], quantiles[2]], y=[0, stats.norm.pdf(quantiles[2], mean_price, std_price)],
                         mode='lines', name='50º Percentil', line=dict(color='orange', dash='dash')))
fig.add_trace(go.Scatter(x=[quantiles[3], quantiles[3]], y=[0, stats.norm.pdf(quantiles[3], mean_price, std_price)],
                         mode='lines', name='75º Percentil', line=dict(color='pink', dash='dash')))
fig.add_trace(go.Scatter(x=[quantiles[4], quantiles[4]], y=[0, stats.norm.pdf(quantiles[4], mean_price, std_price)],
                         mode='lines', name='99º Percentil', line=dict(color='purple', dash='dash')))

# Update layout and axis labels
fig.update_layout(title='Distribuição de Preços',
                  xaxis_title='Preço',
                  yaxis_title='Densidade')

# Display the plot
st.plotly_chart(fig)

st.markdown('''
# Distribuição Assimétrica e Tratamento Logarítmico

Uma distribuição assimétrica ocorre quando os valores de um conjunto de dados estão deslocados em relação à média ou mediana, resultando em uma forma assimétrica. Existem dois tipos principais de distribuição assimétrica:

- **Distribuição Assimétrica Positiva:** Também conhecida como distribuição assimétrica para a direita, é caracterizada por uma cauda longa à direita e uma concentração de valores à esquerda da média. Nesse caso, a mediana é menor que a média.

Exemplo: O gráfico acima, que mostra a distribuição de preços dos imóveis, é um exemplo de distribuição assimétrica positiva.

- **Distribuição Assimétrica Negativa:** Também chamada de distribuição assimétrica para a esquerda, é caracterizada por uma cauda longa à esquerda e uma concentração de valores à direita da média. Nesse caso, a mediana é maior que a média.

Exemplo: Considere um conjunto de dados que represente o tempo de reação de um grupo de pessoas a um estímulo. Se algumas pessoas tiverem tempos de reação muito curtos, isso pode resultar em uma distribuição assimétrica negativa.

## Tratamento Logarítmico

Em alguns casos, é necessário realizar um tratamento logarítmico em uma distribuição assimétrica para garantir a integridade do modelo estatístico. Esse tratamento é especialmente útil quando a assimetria está relacionada a valores extremamente altos ou baixos.

O uso do tratamento logarítmico ajuda a reduzir a magnitude dos valores extremos e aproxima a distribuição de uma forma mais simétrica, facilitando a interpretação dos resultados e a aplicação de técnicas estatísticas.

Por exemplo, ao aplicar o tratamento logarítmico a uma distribuição assimétrica positiva, os valores extremamente altos são reduzidos, aproximando-se mais da média e reduzindo a influência desses valores extremos na análise.

É importante ressaltar que o tratamento logarítmico deve ser aplicado com cautela e apenas quando faz sentido em relação ao contexto do problema. Além disso, é fundamental que sejam feitas análises adicionais para validar a adequação do tratamento logarítmico aos dados.

Em resumo, ao se deparar com uma distribuição assimétrica, o tratamento logarítmico pode ser uma técnica útil para transformar a distribuição e melhorar a interpretação e análise dos dados, especialmente quando há presença de valores extremos.

''')
# Filter data for prices greater than 0 and between the 25 and 75 percentiles
filtered_data = data[(data['preco'] > 0) & (data['preco'] >= data['preco'].quantile(0.1)) & (
            data['preco'] <= data['preco'].quantile(0.75))]

# Calculate the log-transformed prices
log_prices = filtered_data['preco']

# Generate data for the normal distribution curve

# Calculate the mean, median, and quantiles of log-transformed prices
mean_log_price = np.mean(log_prices)

std_log_price = np.std(log_prices)
quantiles_log_price = np.percentile(log_prices, [1, 25, 50, 75, 99])

x = np.linspace(quantiles_log_price[0], quantiles_log_price[-1], 100)
# Calculate the normal distribution curve with the mean and standard deviation of the log-transformed prices, and the y being the count of the prices
y = stats.norm.pdf(x, mean_log_price, std_log_price)
# Create the figure using Plotly graph objects
fig = go.Figure()

## Add the normal distribution curve
fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='Curva Normal', line=dict(color='blue')))

# Add vertical lines for mean and quantiles using go.Line
fig.add_trace(
    go.Scatter(x=[mean_log_price, mean_log_price], y=[0, stats.norm.pdf(mean_log_price, mean_log_price, std_log_price)],
               mode='lines', name='Média', line=dict(color='red', dash='dash')))

fig.add_trace(go.Scatter(x=[quantiles_log_price[0], quantiles_log_price[0]],
                         y=[0, stats.norm.pdf(quantiles_log_price[0], mean_log_price, std_log_price)],
                         mode='lines', name='1º Percentil', line=dict(color='green', dash='dash')))
fig.add_trace(go.Scatter(x=[quantiles_log_price[1], quantiles_log_price[1]],
                         y=[0, stats.norm.pdf(quantiles_log_price[1], mean_log_price, std_log_price)],
                         mode='lines', name='25º Percentil', line=dict(color='blue', dash='dash')))
fig.add_trace(go.Scatter(x=[quantiles_log_price[2], quantiles_log_price[2]],
                         y=[0, stats.norm.pdf(quantiles_log_price[2], mean_log_price, std_log_price)],
                         mode='lines', name='50º Percentil', line=dict(color='orange', dash='dash')))
fig.add_trace(go.Scatter(x=[quantiles_log_price[3], quantiles_log_price[3]],
                         y=[0, stats.norm.pdf(quantiles_log_price[3], mean_log_price, std_log_price)],
                         mode='lines', name='75º Percentil', line=dict(color='pink', dash='dash')))
fig.add_trace(go.Scatter(x=[quantiles_log_price[4], quantiles_log_price[4]],
                         y=[0, stats.norm.pdf(quantiles_log_price[4], mean_log_price, std_log_price)],
                         mode='lines', name='99º Percentil', line=dict(color='purple', dash='dash')))

# Update layout and axis labels
fig.update_layout(title='Distribuição de Preços transformados em Log',
                  xaxis_title='Preço (Transformação Logarítmica)',
                  yaxis_title='Densidade')

# Display the plot
st.plotly_chart(fig)
