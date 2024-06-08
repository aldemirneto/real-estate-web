prompt = [
    {
        "question": "Qual o valor total dos imóveis à venda em Piracicaba?",
        "query": "SELECT SUM(preco) AS valor_total_venda FROM real_estate_data WHERE status = 'Venda'"
    },
    {
        "question": "Qual a área total dos imóveis à venda em Piracicaba?",
        "query": "SELECT SUM(area) AS area_total_venda FROM real_estate_data WHERE status = 'Venda'"
    },
    {
        "question": "Qual o número médio de quartos dos imóveis à venda em Piracicaba?",
        "query": "SELECT AVG(quartos) AS media_quartos_venda FROM real_estate_data WHERE status = 'Venda'"
    },
    {
        "question": "Qual o número médio de vagas de garagem dos imóveis à venda em Piracicaba?",
        "query": "SELECT AVG(vagas) AS media_vagas_venda FROM real_estate_data WHERE status = 'Venda'"
    },
    {
        "question": "Qual o número médio de banheiros dos imóveis à venda em Piracicaba?",
        "query": "SELECT AVG(banheiros) AS media_banheiros_venda FROM real_estate_data WHERE status = 'Venda'"
    },
    {
        "question": "Qual o tipo de imóvel mais comum entre os imóveis à venda em Piracicaba?",
        "query": "SELECT tipo, COUNT(*) AS total_tipo_venda FROM real_estate_data WHERE status = 'Venda' GROUP BY tipo ORDER BY total_tipo_venda DESC LIMIT 1"
    },
    {
        "question": "Qual o bairro com o maior número de imóveis à venda em Piracicaba?",
        "query": "SELECT bairro, COUNT(*) AS total_imoveis_venda FROM real_estate_data WHERE status = 'Venda' GROUP BY bairro ORDER BY total_imoveis_venda DESC LIMIT 1"
    },
    {
        "question": "Qual o bairro com o menor número de imóveis à venda em Piracicaba?",
        "query": "SELECT bairro, COUNT(*) AS total_imoveis_venda FROM real_estate_data WHERE status = 'Venda' GROUP BY bairro ORDER BY total_imoveis_venda ASC LIMIT 1"
    },
    {
        "question": "Qual o valor do imóvel mais caro à venda em Piracicaba?",
        "query": "SELECT preco AS preco_maximo_venda FROM real_estate_data WHERE status = 'Venda' ORDER BY preco DESC LIMIT 1"
    },
    {
        "question": "Qual a área do imóvel com a maior área à venda em Piracicaba?",
        "query": "SELECT area AS area_maxima_venda FROM real_estate_data WHERE status = 'Venda' ORDER BY area DESC LIMIT 1"
    },
    {
        "question": "Quantos imóveis à venda em Piracicaba possuem mais de 3 quartos?",
        "query": "SELECT COUNT(*) AS total_imoveis_mais_3_quartos_venda FROM real_estate_data WHERE status = 'Venda' AND quartos > 3"
    },
    {
        "question": "Quantos imóveis à venda em Piracicaba possuem mais de 2 vagas de garagem?",
        "query": "SELECT COUNT(*) AS total_imoveis_mais_2_vagas_venda FROM real_estate_data WHERE status = 'Venda' AND vagas > 2"
    },
    {
        "question": "Quantos imóveis à venda em Piracicaba possuem mais de 2 banheiros?",
        "query": "SELECT COUNT(*) AS total_imoveis_mais_2_banheiros_venda FROM real_estate_data WHERE status = 'Venda' AND banheiros > 2"
    }
]

COLUMNS_DESCRIPTIONS = colunas_descricao = {
  "preco": {
    "nome": "preco",
    "descricao": "Preço do imóvel",
    "tipo": "float"
  },
  "area": {
    "nome": "area",
    "descricao": "Área do imóvel em metros quadrados",
    "tipo": "float"
  },
  "quartos": {
    "nome": "quartos",
    "descricao": "Número de quartos do imóvel. Valores válidos: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 32]",
    "tipo": "inteiro"
  },
  "vagas": {
    "nome": "vagas",
    "descricao": "Número de vagas de garagem do imóvel. Valores válidos: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20, 22, 25, 30, 40, 48, 50, 100, 200]",
    "tipo": "inteiro"
  },
  "banheiros": {
    "nome": "banheiros",
    "descricao": "Número de banheiros do imóvel",
    "tipo": "inteiro"
  },
  "link": {
    "nome": "link",
    "descricao": "URL do anúncio do imóvel",
    "tipo": "string"
  },
  "imobiliaria": {
    "nome": "imobiliaria",
    "descricao": " imobiliária que anunciou o imóvel",
    "tipo": "string"
  },
  "data_scrape": {
    "nome": "data_scrape",
    "descricao": "Data em que os dados do imóvel foram coletados",
    "tipo": "data"
  },
  "bairro": {
    "nome": "bairro",
    "descricao": "Bairro onde o imóvel está localizado. Observação: Utilize o operador 'eq' somente se um bairro específico for mencionado, caso contrário inclua todos os bairros relevantes no filtro.",
    "tipo": "string"
  },
  "status": {
    "nome": "status",
    "descricao": "Tipo de negociação do imóvel (ex.: venda, aluguel)",
    "tipo": "string"
  },
  "tipo": {
    "nome": "tipo",
    "descricao": "Tipo do imóvel (ex.: casa, apartamento). Valores válidos: ['Andar corporativo', 'Apartamento', 'Apartamento duplex', 'Barracão', 'Casa', 'Chácara', 'Cobertura', 'Edícula', 'Fazenda', 'Galpão', 'Kitnet', 'Loja', 'Prédio', 'Sala', 'Salão', 'Sítio', 'Terreno', 'Área']",
    "tipo": "string"
  },
  "last_seen": {
    "nome": "last_seen",
    "descricao": "Data da última vez que o imóvel foi visto online",
    "tipo": "data"
  }
}
