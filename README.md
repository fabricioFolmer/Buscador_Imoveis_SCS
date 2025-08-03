# Scraper de Dados Imobiliários

Este projeto contém um script em Python para extrair (scrape) dados de imóveis de múltiplos sites de imobiliárias que utilizam a mesma estrutura de API. Ele consolida os dados de todos os provedores em um único arquivo CSV.

## Funcionalidades

* **Extração de Múltiplos Domínios**: O script é configurado para extrair dados de uma lista pré-definida de sites imobiliários.
* **Paginação Automática**: Navega automaticamente por todas as páginas de resultados da API de cada site.
* **Processamento de Dados**: Extrai, limpa e formata campos de dados relevantes de cada anúncio de imóvel.
* **Saída Unificada**: Salva todos os dados coletados em um único arquivo CSV (`all_properties.csv`) para fácil análise.
* **Tratamento de Erros**: Projetado para lidar com falhas de rede e inconsistências nos dados (campos ausentes) de forma robusta.

---

## Estrutura do Arquivo de Saída (`all_properties.csv`)

O arquivo CSV gerado contém os seguintes campos para cada imóvel extraído:

| Coluna | Descrição | Exemplo |
| :--- | :--- | :--- |
| `domain` | O nome de domínio do site de onde o dado foi extraído. | `barbianimoveis.com.br` |
| `id` | O identificador único do imóvel na plataforma. | `1283634` |
| `code` | O código de referência do imóvel usado pela imobiliária. | `4740` |
| `title` | O título do anúncio do imóvel. | `Terreno Comercial à venda` |
| `description` | Uma breve descrição do imóvel. | `Terreno Comercial à venda bairro...` |
| `type` | O tipo do imóvel. | `Terreno Comercial` |
| `exclusivity` | Um valor booleano (`True`/`False`) que indica se o imóvel é exclusivo da imobiliária. | `False` |
| `neighborhood` | O bairro onde o imóvel está localizado. | `Santo Inácio` |
| `city` | A cidade onde o imóvel está localizado. | `Santa Cruz do Sul` |
| `bedrooms` | O número de quartos. | `3` |
| `bathrooms` | O número de banheiros. | `2` |
| `parking_spaces` | O número de vagas de garagem. | `1` |
| `private_area_m2` | A área privativa do imóvel em metros quadrados (m²). | `120.5` |
| `price` | O preço de venda do imóvel. | `350000.00` |
| `latitude` | A coordenada de latitude do imóvel. | `-29.6980123` |
| `longitude` | A coordenada de longitude do imóvel. | `-52.4232086` |
| `image_urls` | Uma string contendo todas as URLs das imagens do imóvel, separadas por ` | `. | `https://...1.webp | https://...2.webp` |
| `property_url` | A URL completa para a página do anúncio do imóvel. | `https://www.barbianimoveis.com.br/imovel/...` |
