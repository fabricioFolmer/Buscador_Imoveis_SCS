import requests
import pandas as pd
import logging
from typing import List, Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class RealEstateAPIScraper:
    """
    Uma classe para extrair dados imobiliários de sites que compartilham uma estrutura de API comum.

    Este scraper busca dados de imóveis de um domínio especificado, extrai detalhes relevantes
    e retorna os dados como uma lista de dicionários.
    """

    def __init__(self, domain_name: str):
        """
        Inicializa o scraper com o domínio de destino.

        Args:
            domain_name (str): O nome de domínio do site imobiliário
                               (ex: "barbianimoveis.com.br").
        """
        if not domain_name:
            raise ValueError("O nome de domínio não pode estar vazio.")
        self.domain_name = domain_name
        self.base_api_url = f"https://www.{self.domain_name}/api/frontend/real-estate-data/property/list"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })

    def _fetch_page_data(self, offset: int) -> Optional[List[Dict[str, Any]]]:
        """
        Busca uma única página de dados de imóveis da API.

        Args:
            offset (int): O deslocamento inicial para a paginação.

        Returns:
            Optional[List[Dict[str, Any]]]: Uma lista de itens de imóveis da resposta da API,
                                            ou None se a solicitação falhar.
        """
        params = {'offset': offset}
        try:
            response = self.session.get(self.base_api_url, params=params, timeout=15)
            response.raise_for_status()  # Lança um HTTPError para respostas ruins (4xx ou 5xx)
            data = response.json()
            return data.get("items")
        except requests.exceptions.RequestException as e:
            logging.error(f"A requisição para {self.domain_name} com offset {offset} falhou: {e}")
        except ValueError: # Captura erros de decodificação JSON
            logging.error(f"Falha ao decodificar JSON para {self.domain_name} com offset {offset}.")
        return None

    def _parse_property_data(self, prop: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analisa com segurança um único objeto JSON de imóvel para extrair os campos necessários.

        Args:
            prop (Dict[str, Any]): O dicionário que representa um único imóvel.

        Returns:
            Um dicionário com os dados extraídos.
        """
        # Extração segura usando .get() para evitar KeyError
        address = prop.get("address", {})
        coordinate = address.get("coordinate", {})
        private_area = prop.get("privateArea", {})
        contracts = prop.get("contracts", [])
        images = prop.get("images", [])

        # Extrai o preço com segurança, convertendo de centavos para um valor decimal
        price_value = None
        if contracts and isinstance(contracts, list) and contracts[0] and 'price' in contracts[0]:
            price_data = contracts[0].get('price', {})
            if price_data and 'value' in price_data:
                try:
                    price_value = float(price_data['value']) / 100
                except (ValueError, TypeError):
                    price_value = None # Lida com valores de preço não numéricos

        # Constrói a URL completa do imóvel
        property_url_path = prop.get("url")
        full_property_url = f"https://www.{self.domain_name}{property_url_path}" if property_url_path else None
        
        # Extrai todas as URLs de imagem e as une com um separador
        image_urls = [img.get("src") for img in images if img and img.get("src")]
        all_image_urls = " | ".join(image_urls) if image_urls else None

        return {
            "domain": self.domain_name,
            "id": prop.get("id"),
            "code": prop.get("code"),
            "title": prop.get("title"),
            "description": prop.get("description"),
            "type": prop.get("type"),
            "exclusivity": prop.get("exclusivity"),
            "neighborhood": address.get("neighborhood"),
            "city": address.get("city"),
            "bedrooms": prop.get("bedrooms"),
            "bathrooms": prop.get("bathrooms"),
            "parking_spaces": prop.get("garage"),
            "private_area_m2": private_area.get("value"),
            "price": price_value,
            "latitude": coordinate.get("latitude"),
            "longitude": coordinate.get("longitude"),
            "image_urls": all_image_urls,
            "property_url": full_property_url,
        }

    def fetch_properties(self) -> List[Dict[str, Any]]:
        """
        Orquestra o processo de scraping para o domínio, buscando todas as páginas e
        processando os dados.

        Returns:
            List[Dict[str, Any]]: Uma lista de todos os imóveis analisados para o domínio.
        """
        logging.info(f"Iniciando o scraper para {self.domain_name}...")
        all_properties = []
        offset = 0
        page_count = 1

        while True:
            logging.info(f"Buscando página {page_count} para {self.domain_name} com offset {offset}...")
            items = self._fetch_page_data(offset)

            if items is None: # Ocorreu um erro
                logging.error(f"Interrompendo a extração para {self.domain_name} devido a um erro na busca.")
                break
            
            if not items: # Fim dos dados
                logging.info(f"Não foram encontrados mais itens para {self.domain_name}. Extração completa.")
                break

            for prop in items:
                parsed_data = self._parse_property_data(prop)
                if parsed_data:
                    all_properties.append(parsed_data)

            offset += 8
            page_count += 1
        
        return all_properties


def update_scraped_data():
    """
    Função principal para executar o scraper em uma lista de domínios e salvar os resultados em um CSV.
    """
    logging.info("Iniciando o processo de scraping para múltiplos domínios...")

    # Lista de domínios a serem processados
    domains_to_scrape = [
        'imoveisinvest.com', 
        'imobiliariadcasa.com.br', 
        'barbianimoveis.com.br', 
        'oktoberimoveis.com.br', 
        'borbaimoveis.com.br', 
        'predilarimoveis.com.br', 
        'karnoppimoveis.com.br', 
        'imoveismdm.com.br', 
        'verenaimoveis.com.br', 
        'imoveisdasantinha.com.br', 
        'muranoimobiliaria.com.br', 
        'imobjardim.com.br', 
        'imobiliariaimigrante.com.br', 
        'garbonegociosimobiliarios.com.br'
    ]

    all_scraped_data = []

    for domain in domains_to_scrape:
        try:
            scraper = RealEstateAPIScraper(domain_name=domain)
            properties = scraper.fetch_properties()
            if properties:
                all_scraped_data.extend(properties)
            logging.info(f"--- Processamento de {domain} finalizado ---\n")
        except ValueError as e:
            logging.error(f"Não foi possível criar o scraper para o domínio '{domain}': {e}")
        except Exception as e:
            logging.error(f"Ocorreu um erro inesperado ao processar {domain}: {e}")

    if all_scraped_data:
        logging.info(f"Total de imóveis extraídos de todos os domínios: {len(all_scraped_data)}")
        
        # Cria o DataFrame e salva em um único CSV
        df = pd.DataFrame(all_scraped_data)
        output_filename = "data\\all_properties.csv"

        try:
            df.to_csv(output_filename, index=False, encoding='utf-8')
            df.to_parquet(output_filename.replace('.csv', '.parquet'), index=False)
            logging.info(f"Todos os imóveis foram salvos com sucesso em {output_filename}")
        except IOError as e:
            logging.error(f"Falha ao escrever no arquivo CSV {output_filename}: {e}")
    else:
        logging.warning("Nenhum imóvel foi extraído de nenhum domínio. O arquivo CSV não será criado.")


if __name__ == "__main__":
   update_scraped_data()