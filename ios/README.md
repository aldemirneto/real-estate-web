# Imóveis — iOS nativo

Primeira versão em SwiftUI para iPhone/iPad com iOS 17 ou superior. Inclui catálogo real coletado em 14/09/2026 UTC (13/09 no Brasil), busca por cidade/bairro/tipo, filtros de preço e quartos, favoritos persistidos no aparelho, compartilhamento e link para o anúncio original. Funciona offline desde a primeira abertura; os preços não são atualizados automaticamente.

## Rodar no seu iPhone

1. Instale e abra o Xcode, aceite a licença e conclua a configuração inicial, incluindo a plataforma iOS.
2. Abra `RealEstate.xcodeproj` e selecione o scheme `RealEstate`.
3. Em **Signing & Capabilities**, selecione sua equipe/Personal Team. O projeto não inclui identidade de assinatura.
4. Conecte seu iPhone, habilite o Modo de Desenvolvedor se solicitado e selecione-o como destino. Clique em Run (⌘R).

É possível testar no próprio aparelho com uma Personal Team, sem publicar na App Store. A assinatura gratuita pode exigir reinstalação periódica. Referências: [contas Apple](https://developer.apple.com/support/compare-memberships/) e [execução em dispositivos](https://developer.apple.com/documentation/Xcode/running-your-app-on-simulated-or-physical-devices).

Para testar sem assinatura, escolha um simulador de iPhone como destino.

## Atualizar o catálogo incluído

No repositório `Real-Estate-Predictor`, com as dependências instaladas:

```sh
uv run python scripts/export_catalog.py --sources LopesLT LopesRTG Premier --output ../real-estate-web/backend/catalog.json
cp ../real-estate-web/backend/catalog.json ../real-estate-web/ios/RealEstate/Resources/catalog.json
```

Recompile o app para atualizar o catálogo incluído. Um aparelho que já atualizou pela API prefere seu cache: use a API para atualizá-lo novamente ou reinstale o app para voltar ao catálogo incluído (isso remove também os favoritos).

## Atualização pela API local, opcional

No repositório `real-estate-web`:

```sh
python -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
.venv/bin/python -m uvicorn main:app --app-dir backend --host 0.0.0.0 --port 8000
```

Deixe `DATABASE_URL` sem definição para usar `backend/catalog.json` sem Postgres. No app, vá em Ajustes e informe `http://IP-DO-MAC:8000` com o iPhone na mesma rede do Mac. No simulador, use `http://localhost:8000`. Autorize o acesso à rede local quando o iOS solicitar. O app baixa todas as páginas de todas as cidades e só troca o cache após sucesso completo. Não há servidor público, login nem publicação nesta versão.

## Limitações desta versão

- Informações ausentes na fonte aparecem como não informadas; não são inferidas.
- O catálogo reúne anúncios de duas fontes de SP (Lopes LT/RTG) e da Premier em Piracicaba. O coletor LT é limitado a duas páginas e o RTG aos links destacados na página inicial. A abrangência não é a cidade inteira.
- Fotos, mapa e estimativa de preços ainda não fazem parte do app iOS. A API mantém a estimativa limitada a Piracicaba; o modelo existente não foi treinado para São Paulo.
- Favoritos e cache ficam somente no aparelho. Não há sincronização entre aparelhos.
