from selenium import webdriver
from typing import Optional
import pandas as pd
import numpy as np
import time
import os


class FrontEnd_Scraper:
    
    def __init__(self, params: Optional[dict] = None):
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        
        # Fixed parameters
        self.sites = ['imoveisinvest.com', 'imobiliariadcasa.com.br', 'barbianimoveis.com.br', 'oktoberimoveis.com.br', 'borbaimoveis.com.br', 'predilarimoveis.com.br', 'karnoppimoveis.com.br', 'imoveismdm.com.br', 'verenaimoveis.com.br', 'imoveisdasantinha.com.br', 'muranoimobiliaria.com.br', 'imobjardim.com.br', 'imobiliariaimigrante.com.br', 'garbonegociosimobiliarios.com.br']

        # Query parameters
        link_params = ['ordenacao="menor-valor"', 'pagina=1']
        if params is not None:
            # Iterate through the provided parameters and build the query string
            for key, value in params.items():
                if isinstance(value, list):
                    value = '%2C'.join(value)
                if isinstance(value, str):
                    value = '"' + value + '"'
                else:
                    value = str(value)
                link_params.append(f'{key}={value}')
        self.link_params = '&'.join(link_params)
        print(self.link_params)

        # Initialize the browser
        options = Options()
        options.add_argument("--log-level=3")  # Suppresses INFO, WARNING, and DEBUG messages
        options.add_experimental_option("excludeSwitches", ["enable-logging"])  # Suppresses "DevTools listening" message
        service = Service(log_path=os.devnull)  # Hides chromedriver's own logging
        self.driver = webdriver.Chrome(service=service, options=options)


    def __del__(self):
        """
        Ensure the driver is closed when the scraper is deleted from memory.
        """
        if self.driver:
            self.driver.quit()


    def __force_page_load(self, driver: webdriver.Chrome) -> webdriver.Chrome:
        """
        Force the page to load completely by scrolling to the bottom.
        """
        
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for new content to load
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)  # Wait for the scroll to complete

        return driver


    def scrape_all(self) -> list:
        """
        Scrape all sites defined in the class.
        """
        all_data = []
        for site in self.sites:
            print(f'Scraping {site}...')
            data = self.get_listings(site)
            all_data.extend(data)
            print(f'Finished scraping {site}. Found {len(data)} listings.')
        
        df = pd.DataFrame(all_data)
        df.to_csv('data\\all_data_frontend.csv', index=False, encoding='utf-8')
        print('Data saved successfully.')

        return all_data
    

    def get_listings(self, site) -> list:
        from selenium.webdriver.common.by import By
        from selenium.common.exceptions import NoSuchElementException

        data = []
        reached_end = False
        
        # Open the URL
        url = f'https://www.{site}/venda?{self.link_params}'
        self.driver.get(url)
        time.sleep(3)
        
        while not reached_end:

            # Force the page to load completely
            self.driver = self.__force_page_load(self.driver)

            # Iterate through each listing card
            listings = self.driver.find_elements(By.CSS_SELECTOR, f'[itemtype="https://schema.org/Apartment"]')
            for element in listings:

                # Suspended | Extrai imagens do card
                images = []
                #try:
                #    img_bullets_container = element.find_element(By.CSS_SELECTOR, '[class^="image-gallery-bullets-container"]')

                #    # Faz o scroll para o container de imagens
                #    location = img_bullets_container.location # Dict {'x': int, 'y': int}
                #    self.driver.execute_script(f'window.scrollTo({location["x"]}, {location["y"]-100});')  # Scroll to the bullet
                #    time.sleep(1)  # Wait for the scroll to complete
                #    
                #    # Clica em cada botão de imagem do Card, para carregar as imagens
                #    img_bullets = img_bullets_container.find_elements(By.CSS_SELECTOR, '[type="button"]')
                #    for bullet in img_bullets:
                #        bullet.click()
                #        time.sleep(.1)  # Wait for the image to load

                #    # Extrai as imagens do card        
                #    for img in element.find_elements(By.CSS_SELECTOR, '[aria-label="Ver imagem"]'):
                #        try:
                #            img_src = img.find_element(By.TAG_NAME, 'img')
                #            images.append(img_src.get_attribute('src'))
                #        except NoSuchElementException:
                #            print("Image not found in card, skipping...")
                #            continue
                #except NoSuchElementException:
                #    continue

                # Extrai informações do card
                neighborhood = element.find_element(By.CSS_SELECTOR, '[class^="vertical-property-card_neighborhood__"]').text
                address = element.find_element(By.CSS_SELECTOR, '[class^="vertical-property-card_fullAddress__"]').text
                typeOfAgreement = element.find_element(By.CSS_SELECTOR, '[class^="contracts_typeOfAgreement__"]').text
                price = float(element.find_element(By.CSS_SELECTOR, '[class^="contracts_priceNumber__"]').text.replace('R$', '').replace('.', '').replace(',', '.').strip())
                try:
                    exclusivity_elem = element.find_element(By.CSS_SELECTOR, '[class^="carousel-card_exclusivity__"]')
                    isExclusive = 'Sim'
                except NoSuchElementException:
                    isExclusive = 'Não'
                listing_id = element.find_element(By.CSS_SELECTOR, '[class^="card-buttons_code__"]').text.replace('Cód.', '').strip()
                listing_link = f'https://www.{site}/imovel/{listing_id}'

                # Extrai informações da linha de características do card
                characteristics = element.find_element(By.CSS_SELECTOR, '[class^="vertical-property-card_characteristics__"]')
                characteristics_list = []
                for span in characteristics.find_elements(By.TAG_NAME, 'span'):
                    characteristics_list.append(span.text)

                # Extrai cada característica individualmente
                size = bedrooms = restrooms = parkingSpaces = None
                for characteristic in characteristics_list:
                    if 'm²' in characteristic:
                        size = characteristic.split(' ')[0].replace('m²', '').replace('.', '').replace(',', '.').strip()
                        size = float(size) if size.isdigit() else np.nan
                    elif 'quarto' in characteristic.lower():
                        bedrooms = characteristic.split(' ')[0]
                        bedrooms = int(bedrooms) if bedrooms.isdigit() else np.nan
                    elif 'banheiro' in characteristic.lower():
                        restrooms = characteristic.split(' ')[0]
                        restrooms = int(restrooms) if restrooms.isdigit() else np.nan
                    elif 'vaga' in characteristic.lower():
                        parkingSpaces = characteristic.split(' ')[0]
                        parkingSpaces = int(parkingSpaces) if parkingSpaces.isdigit() else np.nan
                    else:
                        print(f'Unknown characteristic: {characteristic}. Website: {site}')

                data.append({
                    'site': site,
                    'bairro': neighborhood,
                    'endereço': address,
                    'tipo_negocio': typeOfAgreement,
                    'preco': price,
                    'area': size,
                    'quartos': bedrooms,
                    'banheiros': restrooms,
                    'vagas_de_garagem': parkingSpaces,
                    'id_anuncio': listing_id,
                    'link_anuncio': listing_link,
                    'flag_exclusivo': isExclusive,
                    'imagens': '|'.join(images)
                })

            # Go to next page if available
            try:
                for btn in self.driver.find_elements(By.CSS_SELECTOR, '[class^="building-card-pages_labelText__"]'):
                    if btn.text == 'Próximo':
                        if btn.is_enabled():
                            location = btn.location # Dict {'x': int, 'y': int}
                            self.driver.execute_script(f'window.scrollTo({location["x"]}, {location["y"]-100});')  # Scroll to the bullet
                            time.sleep(1)  # Wait for the scroll to complete
                            old_url = self.driver.current_url
                            btn.click()
                            time.sleep(3)
                            if self.driver.current_url == old_url:
                                reached_end = True
                        break
            except NoSuchElementException:
                reached_end = True

        return data


def update_scraped_data():
    scraper = FrontEnd_Scraper(params={'tipos': ['apartamento', 'casa'], 'precoMinimo': 25000000, 'precoMaximo': 32000000})
    scraper.scrape_all()

if __name__ == "__main__":
    update_scraped_data()
