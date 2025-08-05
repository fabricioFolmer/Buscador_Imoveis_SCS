# Buscador de Imóveis - Santa Cruz do Sul
Este projeto é uma solução completa para coleta, processamento e visualização de dados imobiliários da região de Santa Cruz do Sul/RS. O sistema inclui web scrapers para extração de dados de múltiplas imobiliárias e uma interface web interativa desenvolvida em Streamlit para análise e visualização dos dados coletados.

## Como Usar
```bash
pip install -r requirements.txt
python -m streamlit run main.py
```

## 📋 TO DO List
- ✅ Improve sidebar filters
- Add image side scrolling on the cards when there are multiple images
- Show total and usable area in the cards
- Scrape and show
    - Actual listing description
    - Section "comodidades do imovel"

## Visão Geral
Esse é um projeto desenvolvido para automatizar a coleta de dados imobiliários de sites que compartilham uma estrutura de API comum. O projeto oferece duas abordagens de coleta de dados:

1. **API Scraper** (`Scraper.py`): Extração eficiente via APIs REST
2. **Frontend Scraper** (`Scraper_Frontend.py`): Extração via Selenium para sites com carregamento dinâmico
3. **Interface de Visualização** (`main.py`): Dashboard interativo em Streamlit

## Funcionalidades

### Coleta de Dados
* **Extração de Múltiplos Domínios**: Suporte a 14+ sites imobiliários da região
* **Paginação Automática**: Navegação automática por todas as páginas de resultados
* **Processamento Robusto**: Tratamento de erros e inconsistências nos dados
* **Múltiplos Formatos**: Exportação em CSV e Parquet
* **Geolocalização**: Extração de coordenadas (latitude/longitude)

### Interface Web Interativa
* **Filtros Avançados**: Por cidade, tipo, preço, área, quartos, banheiros, vagas
* **Visualização em Cards**: Layout responsivo com informações detalhadas
* **Mapa Interativo**: Visualização geográfica com PyDeck
* **Paginação**: Navegação eficiente pelos resultados
* **Ordenação Dinâmica**: Por preço (crescente/decrescente)

### Processamento de Dados
* **Limpeza Automática**: Remoção de dados inconsistentes
* **Normalização**: Padronização de formatos numéricos
* **Validação**: Verificação de campos obrigatórios
* **Agregação**: Consolidação de dados de múltiplas fontes

## Arquitetura do Sistema

```
Real_Estate_Scraper/
├── main.py                    # Interface Streamlit
├── Scraper.py                 # API Scraper principal
├── Scraper_Frontend.py        # Selenium Scraper
├── requirements.txt           # Dependências Python
├── data/                      # Dados processados
│   ├── all_properties.csv     # Dados em CSV
│   ├── all_properties.parquet # Dados em Parquet
│   └── all_data_frontend.csv  # Dados do Selenium
└── __pycache__/              # Cache Python
```

## Dados Coletados

Os arquivos CSV gerados contêm os seguintes campos:

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `domain` | String | Site de origem dos dados | `barbianimoveis.com.br` |
| `id` | Integer | ID único do imóvel na plataforma | `1283634` |
| `code` | String | Código de referência da imobiliária | `4740` |
| `title` | String | Título do anúncio | `Terreno Comercial à venda` |
| `description` | Text | Descrição detalhada do imóvel | `Terreno Comercial à venda bairro...` |
| `type` | String | Tipo do imóvel | `Apartamento`, `Casa`, `Terreno` |
| `exclusivity` | Boolean | Exclusividade da imobiliária | `True`/`False` |
| `neighborhood` | String | Bairro de localização | `Santo Inácio`, `Centro` |
| `city` | String | Cidade de localização | `Santa Cruz do Sul` |
| `bedrooms` | Integer | Número de quartos | `3` |
| `bathrooms` | Integer | Número de banheiros | `2` |
| `parking_spaces` | Integer | Vagas de garagem | `1` |
| `private_area_m2` | Float | Área privativa em m² | `120.5` |
| `price` | Float | Preço de venda em R$ | `350000.00` |
| `latitude` | Float | Coordenada de latitude | `-29.6980123` |
| `longitude` | Float | Coordenada de longitude | `-52.4232086` |
| `image_urls` | String | URLs das imagens (separadas por ` \| `) | `https://...1.webp \| https://...2.webp` |
| `property_url` | String | URL completa do anúncio | `https://www.site.com.br/imovel/...` |

## Interface Web

### Funcionalidades da Interface

#### Painel de Filtros (Sidebar)
- **Ordenação**: Por preço (crescente/decrescente)
- **Localização**: Cidade e bairros
- **Tipo**: Apartamento, casa, terreno, etc.
- **Preço**: Faixa de valores com slider
- **Área**: Área privativa em m²
- **Características**: Quartos, banheiros, vagas de garagem

#### Aba "Anúncios"
- **Layout em Cards**: Visualização responsiva em 3 colunas
- **Paginação**: 20 imóveis por página
- **Imagens**: Exibição da primeira foto de cada imóvel
- **Informações**: Preço, área, características principais
- **Navegação**: Controles de primeira/anterior/próxima/última página

#### Aba "Mapa"
- **Visualização Geográfica**: Mapa interativo com PyDeck
- **Marcadores**: Pontos vermelhos para cada imóvel
- **Popup Informativos**: Detalhes ao clicar nos marcadores
- **Zoom Inteligente**: Foco na região de Santa Cruz do Sul

### Tecnologias da Interface

- **Streamlit**: Framework web para Python
- **PyDeck**: Visualização de mapas 3D
- **Pandas**: Manipulação de dados
- **NumPy**: Operações numéricas

### API Jetimob | Endpoints Descobertos

Durante o desenvolvimento, foram identificados endpoints úteis das APIs internas:

```python
# Dados de propriedade específica
GET https://www.imobiliariadcasa.com.br/api/frontend/real-estate-data/property/46031

# Propriedades relacionadas
GET https://www.imobiliariadcasa.com.br/api/frontend/real-estate-data/property/list/46031/related-properties?filter=

# Dados da imobiliária
GET https://www.imoveismdm.com.br/api/frontend/real-estate-data
```
