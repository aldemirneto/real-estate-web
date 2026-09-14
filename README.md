# Real Estate Web + iOS

Busca de imóveis por cidade, bairro, preço e características. A API FastAPI atende o frontend React e o app nativo SwiftUI.

O app iOS funciona offline com um catálogo incluído. Veja `ios/README.md` e abra `ios/RealEstate.xcodeproj` no Xcode.

## API local sem banco

```sh
python -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
.venv/bin/python -m uvicorn main:app --app-dir backend --host 127.0.0.1 --port 8000
```

Sem `DATABASE_URL`, a API usa `backend/catalog.json`. `CATALOG_PATH` permite escolher outro arquivo. Para acessar pelo iPhone na mesma rede, use `--host 0.0.0.0` e configure o IP do Mac nos Ajustes do app.

Endpoints: `/api/health`, `/api/cities`, `/api/neighborhoods?cidade=São Paulo`, `/api/properties?cidade=São Paulo`, `/api/price-range?cidade=São Paulo`. A busca e os bairros usam Piracicaba como cidade padrão para preservar os clientes anteriores. `/api/geo` e `/api/predict` são limitados a Piracicaba.

O modelo é carregado somente ao pedir uma previsão. No macOS, a instalação de XGBoost pode exigir o runtime OpenMP; o catálogo funciona independentemente do modelo.

## Docker local

```sh
docker compose up --build
```

A configuração padrão usa o catálogo JSON e o frontend fica em `http://localhost`. A rede `real-estate-network` precisa existir (é criada pelo compose do predictor); para usar somente este projeto, crie-a com `docker network create real-estate-network`.

Para usar Postgres, aplique primeiro `sql/catalog_cities.sql` e `sql/security.sql` do predictor ao banco existente e configure `DATABASE_URL` com as credenciais do leitor. Não use a senha de exemplo fora do desenvolvimento local. Nenhuma migração ou publicação remota é executada ao iniciar a API.

## Verificação

```sh
.venv/bin/pip install -r backend/requirements-dev.txt
.venv/bin/python -m unittest discover -s backend/tests -v
cd frontend
npm ci
npm run lint
npm run build
```
