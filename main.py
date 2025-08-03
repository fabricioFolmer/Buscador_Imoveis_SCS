import streamlit.components.v1 as components
import streamlit as st
import pandas as pd
import os

# Configuração da página
st.set_page_config(layout="wide", page_title="Imóveis em Santa Cruz do Sul", page_icon="🏠")


@st.cache_data
def load_data(file_path):
    """
    Carrega os dados do arquivo Parquet e faz um pré-processamento básico.
    """
    if not os.path.exists(file_path):
        import Scraper
        Scraper.update_scraped_data()
        if not os.path.exists(file_path):
            st.error(f"Erro: O arquivo '{file_path}' não foi encontrado após a atualização. Verifique se o scraper foi executado corretamente.")
            return pd.DataFrame()
    else:
        data = pd.read_parquet(file_path)
    
    # Garante que as colunas numéricas sejam do tipo float
    for col in ['bedrooms', 'bathrooms', 'parking_spaces', 'private_area_m2', 'price', 'latitude', 'longitude']:
        data[col] = pd.to_numeric(data[col], errors='coerce')
    # Remove linhas onde colunas essenciais são nulas
    data.dropna(subset=['id', 'price', 'city', 'neighborhood'], inplace=True) # TODO Review
    return data


def get_unique_sorted_values(series):
    """
    Retorna uma lista de valores únicos e ordenados de uma série Pandas, tratando nulos.
    """
    return sorted(series.dropna().unique())


def float_to_str(value: float, decimals: int) -> str:
    if pd.notna(value):
        return f"{value:,.{decimals}f}".replace(',', ';').replace('.', ',').replace(';', '.')
    return ''


def main():
    """
    Função principal que executa a aplicação Streamlit.
    """
    # Carregamento dos dados
    df = load_data('data\\all_properties.parquet')
    if df.empty:
        return

    # --- PAINEL DE FILTROS (SIDEBAR) ---
    with st.sidebar:
        st.title("Filtros")

        # Ordenação
        sort_order = st.selectbox("Ordenar por Preço", ["Menor para o Maior", "Maior para o Menor"])
        ascending_order = sort_order == "Menor para o Maior"

        # Filtro de Cidade
        cities = get_unique_sorted_values(df['city'])
        default_city_index = cities.index("Santa Cruz do Sul") if "Santa Cruz do Sul" in cities else 0
        selected_city = st.selectbox(
            "Cidade",
            options=cities,
            index=default_city_index
        )

        # Filtro de Tipo (com valor padrão)
        types = get_unique_sorted_values(df['type'])
        default_type_index = types.index("Apartamento") if "Apartamento" in types else 0
        selected_type = st.selectbox(
            "Tipo",
            options=types,
            index=default_type_index
        )

        # Filtros aplicados à cidade e tipo para gerar opções dinâmicas
        df_filtered_for_options = df[
            df['city'].str.contains(selected_city, case=False, na=False) &
            df['type'].str.contains(selected_type, case=False, na=False)
        ]
        
        # Filtro de Preço
        min_price, max_price = float(df_filtered_for_options['price'].min()), float(df_filtered_for_options['price'].max())
        price_range = st.slider(
            "Preço (R$)",
            min_value=100000.0,
            max_value=500000.0,
            value=(100000.0, 500000.0),
            format="R$ %d",
            step=5000.0
        )

        # Filtro de Área Privativa
        min_area, max_area = float(df_filtered_for_options['private_area_m2'].min()), float(df_filtered_for_options['private_area_m2'].max())
        area_range = st.slider(
            "Área Privativa (m²)",
            min_value=min_area,
            max_value=max_area,
            value=(min_area, max_area),
            format="%d",
            step=1.0
        )

        # Filtro de Quartos
        bedroom_options = sorted(df_filtered_for_options['bedrooms'].dropna().unique().astype(int))
        bedroom_options_str = [str(b) for b in bedroom_options if b < 4]
        if any(b >= 4 for b in bedroom_options):
            bedroom_options_str.append("4+")
        selected_bedrooms = st.multiselect("Quartos", options=bedroom_options_str)

        # Filtro de Banheiros
        bathroom_options = sorted(df_filtered_for_options['bathrooms'].dropna().unique().astype(int))
        bathroom_options_str = [str(b) for b in bathroom_options if b < 4]
        if any(b >= 4 for b in bathroom_options):
            bathroom_options_str.append("4+")
        selected_bathrooms = st.multiselect("Banheiros", options=bathroom_options_str)

        # Filtro de Vagas de Garagem
        parking_options = sorted(df_filtered_for_options['parking_spaces'].dropna().unique().astype(int))
        parking_options_str = [str(p) for p in parking_options if p < 4]
        if any(p >= 4 for p in parking_options):
            parking_options_str.append("4+")
        selected_parking = st.multiselect("Vagas de Garagem", options=parking_options_str)

        # Filtro de Bairro
        neighborhoods = get_unique_sorted_values(df_filtered_for_options['neighborhood'])
        selected_neighborhoods = st.multiselect("Bairros", options=neighborhoods)

    # --- LÓGICA DE FILTRAGEM ---
    if True:
        df_filtered = df.copy()

        # Aplica filtros sequencialmente
        df_filtered = df_filtered[df_filtered['city'].str.contains(selected_city, case=False, na=False)]
        if selected_type:
            df_filtered = df_filtered[df_filtered['type'].str.contains(selected_type, case=False, na=False)]
        df_filtered = df_filtered[df_filtered['price'].between(price_range[0], price_range[1])]
        df_filtered = df_filtered[df_filtered['private_area_m2'].between(area_range[0], area_range[1])]

        if selected_neighborhoods:
            df_filtered = df_filtered[df_filtered['neighborhood'].isin(selected_neighborhoods)]

        if selected_bedrooms:
            bedroom_conditions = pd.Series([False] * len(df_filtered), index=df_filtered.index)
            if "4+" in selected_bedrooms:
                bedroom_conditions |= (df_filtered['bedrooms'] >= 4)
            numeric_bedrooms = [int(b) for b in selected_bedrooms if b.isdigit()]
            if numeric_bedrooms:
                bedroom_conditions |= (df_filtered['bedrooms'].isin(numeric_bedrooms))
            df_filtered = df_filtered[bedroom_conditions]

        if selected_bathrooms:
            bathroom_conditions = pd.Series([False] * len(df_filtered), index=df_filtered.index)
            if "4+" in selected_bathrooms:
                bathroom_conditions |= (df_filtered['bathrooms'] >= 4)
            numeric_bathrooms = [int(b) for b in selected_bathrooms if b.isdigit()]
            if numeric_bathrooms:
                bathroom_conditions |= (df_filtered['bathrooms'].isin(numeric_bathrooms))
            df_filtered = df_filtered[bathroom_conditions]

        if selected_parking:
            parking_conditions = pd.Series([False] * len(df_filtered), index=df_filtered.index)
            if "4+" in selected_parking:
                parking_conditions |= (df_filtered['parking_spaces'] >= 4)
            numeric_parking = [int(p) for p in selected_parking if p.isdigit()]
            if numeric_parking:
                parking_conditions |= (df_filtered['parking_spaces'].isin(numeric_parking))
            df_filtered = df_filtered[parking_conditions]

    # --- VISUALIZAÇÃO PRINCIPAL ---
#    st.markdown(f"### Imóveis em Santa Cruz do Sul")
    tab1, tab2 = st.tabs(["Anúncios", "Mapa"])

    with tab1:
        # --- ABA DE ANÚNCIOS ---        
        df_sorted = df_filtered.sort_values(by="price", ascending=ascending_order)

        # Paginação
        items_per_page = 20
        total_items = len(df_sorted)
        total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)
        
        # Initialize page_number in session state if not exists
        if 'page_number' not in st.session_state:
            st.session_state.page_number = 1
        
        # Ensure page_number is within valid range
        if st.session_state.page_number > total_pages:
            st.session_state.page_number = total_pages
        
        page_number = st.session_state.page_number
        
        # Informações de paginação centralizadas
        st.markdown(f"<div style='text-align: center; margin-bottom: 20px;'>Página {page_number} de {total_pages} | Exibindo {min(items_per_page, total_items - (page_number-1)*items_per_page)} de {total_items} imóveis</div>", unsafe_allow_html=True)
        
        start_index = (page_number - 1) * items_per_page
        end_index = start_index + items_per_page
        df_paginated = df_sorted.iloc[start_index:end_index]

        # Exibição em cards
        if df_paginated.empty:
            st.write("Nenhum imóvel encontrado para os filtros selecionados nesta página.")
        else:
            # Criar uma única estrutura de 3 colunas
            col1, col2, col3 = st.columns(3)
            cols = [col1, col2, col3]
            
            # Distribuir os imóveis nas 3 colunas
            for idx, (_, row) in enumerate(df_paginated.iterrows()):
                col_idx = idx % 3  # Determina qual coluna usar (0, 1, ou 2)
                
                with cols[col_idx]:
                    # Obter a primeira imagem ou placeholder
                    image_urls_str = str(row['image_urls']) if pd.notna(row['image_urls']) else ""
                    image_urls = image_urls_str.split(' | ') if image_urls_str else []
                    image_url = image_urls[0] if image_urls and image_urls[0] and image_urls[0] != 'nan' else None
                    
                    # Exibir imagem
                    if image_url:
                        st.image(image_url, use_container_width=True)
                    else:
                        st.markdown("""
                        <div style="width:100%; height: 200px; background-color: #f0f0f0; display: flex; align-items: center; justify-content: center; border-radius: 8px; margin-bottom: 10px;">
                            <span style="color: #888; font-size: 14px;">Imagem Indisponível</span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Cabeçalho com preço e informações básicas
                    col_price, col_features = st.columns([1, 1])
                    col_price.markdown(f"**R$ {float_to_str(row['price'], 0)}**")
                    # Area, Bedrooms, Bathrooms, Parking Spaces
                    area = f"{float_to_str(row['private_area_m2'], 0)} m²" if pd.notna(row['private_area_m2']) else None
                    bedrooms = f"🛏️ {float_to_str(row['bedrooms'], 0)}" if pd.notna(row['bedrooms']) else None
                    bathrooms = f"🚿 {float_to_str(row['bathrooms'], 0)}" if pd.notna(row['bathrooms']) else None
                    parking_spaces = f"🚗 {float_to_str(row['parking_spaces'], 0)}" if pd.notna(row['parking_spaces']) else None
                    col_features.markdown(f"<div style='text-align: right;'>{' | '.join(filter(None, [area, bedrooms, bathrooms, parking_spaces]))}</div>", unsafe_allow_html=True)
                    st.markdown(f"<a href='{row['property_url']}' target='_blank' style='text-decoration: none; color: inherit;'>📍 {row['neighborhood']}, {row['city']} 🔗</a>", unsafe_allow_html=True)
                    
                    # Mostrar descrição do anúncio sempre visível
                    if pd.notna(row['description']) or pd.notna(row['title']):
                        with st.expander("Descrição do Anúncio", expanded=False):
                            if pd.notna(row['title']):
                                st.markdown(f"**{row['title']}**")
                            if pd.notna(row['description']):
                                st.write(row['description'])
                    
                    
                    st.markdown("---")
            
            # Controles de paginação na parte inferior
            st.markdown("---")
            col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
            
            with col1:
                if st.button("⏮️ Primeira", disabled=(page_number == 1), use_container_width=True):
                    st.session_state.page_number = 1
                    st.rerun()
            
            with col2:
                if st.button("⬅️ Anterior", disabled=(page_number == 1), use_container_width=True):
                    st.session_state.page_number = max(1, page_number - 1)
                    st.rerun()
            
            with col3:
                st.markdown(f"<div style='text-align: center; padding: 8px; background-color: #f0f2f6; border-radius: 5px; margin: 0 10px;'>Página {page_number} de {total_pages}</div>", unsafe_allow_html=True)
            
            with col4:
                if st.button("Próxima ➡️", disabled=(page_number == total_pages), use_container_width=True):
                    st.session_state.page_number = min(total_pages, page_number + 1)
                    st.rerun()
            
            with col5:
                if st.button("Última ⏭️", disabled=(page_number == total_pages), use_container_width=True):
                    st.session_state.page_number = total_pages
                    st.rerun()

    with tab2:
        # --- ABA DE MAPA ---
        df_map = df_filtered.dropna(subset=['latitude', 'longitude'])
        
        if df_map.empty:
            st.write("Nenhum imóvel com coordenadas válidas para exibir no mapa.")
        else:
            # Preparando dados para o popup do mapa com formatação brasileira
            def create_popup(row):
                # Obter a primeira imagem ou usar placeholder
                image_urls_str = str(row['image_urls']) if pd.notna(row['image_urls']) else ""
                image_urls = image_urls_str.split(' | ') if image_urls_str else []
                image_url = image_urls[0] if image_urls and image_urls[0] and image_urls[0] != 'nan' else None
                
                # Formatação do preço em estilo brasileiro
                price_formatted = f"R$ {float_to_str(row['price'], 0)}"
                # Outros dados do imóvel - Area, Bedrooms, Bathrooms, Parking Spaces
                area = f"{float_to_str(row['private_area_m2'], 0)} m²" if pd.notna(row['private_area_m2']) else None
                bedrooms = f"🛏️ {float_to_str(row['bedrooms'], 0)}" if pd.notna(row['bedrooms']) else None
                parking_spaces = f"🚗 {float_to_str(row['parking_spaces'], 0)}" if pd.notna(row['parking_spaces']) else None
                dados = ' | '.join(filter(None, [area, bedrooms, parking_spaces]))

                # Criação do HTML para o popup
                if image_url:
                    return f"""
                        <div style="width: 300px; font-family: Arial, sans-serif;">
                            <img src="{image_url}" style="width: 100%; max-width: 270px; height: auto; border-radius: 5px; margin-bottom: 8px;" alt="Imagem do imóvel">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                                <div style="font-weight: bold; font-size: 16px;">{price_formatted}</div>
                                <div style="font-size: 13px; text-align: right;">{dados if dados else ''}</div>
                            </div>
                        </div>
                    """
                else:
                    return f"""
                        <div style="width: 300px; font-family: Arial, sans-serif;">
                            <div style="width: 100%; height: 150px; background-color: #f0f0f0; display: flex; align-items: center; justify-content: center; border-radius: 5px; margin-bottom: 8px; color: #888; font-size: 14px;">
                                Imagem Indisponível
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                                <div style="font-weight: bold; font-size: 16px;">{price_formatted}</div>
                                <div style="font-size: 13px; text-align: right;">{dados if dados else ''}</div>
                            </div>
                        </div>
                    """
            
            df_map['popup'] = df_map.apply(create_popup, axis=1)
            

            # Função para lidar com cliques no mapa
            def handle_map_selection():
                if st.session_state.get('code'):
                    selection = st.session_state.code.get('selection')
                    if selection and selection.get('objects'):
                        # Obter a URL da propriedade selecionada
                        property_url = selection['objects']['code'][0]['property_url']
                        components.html(f"""
                            <script>
                                window.open('{property_url}', '_blank');
                            </script>
                        """, height=0)

            st.pydeck_chart(pdk.Deck(
                map_style='road',  # Usa um estilo que não requer token do Mapbox
                
                # Initial view é de Santa Cruz do Sul
                initial_view_state=pdk.ViewState(
                    latitude=-29.7175,
                    longitude=-52.4264,
                    zoom=11.7,
                    pitch=0  # Vista superior (sem inclinação) para melhor visualização dos pontos
                ),
                
                layers=[
                    pdk.Layer(
                       'ScatterplotLayer',
                       data=df_map,
                       get_position='[longitude, latitude]',
                       get_color='[200, 30, 0, 160]',  # Cor vermelha para os pontos
                       get_radius=30,  # Raio fixo otimizado para visualização
                       radius_scale=1,
                       radius_min_pixels=6,  # Raio mínimo em pixels
                       radius_max_pixels=30,  # Raio máximo em pixels
                       pickable=True,
                       auto_highlight=True,  # Destaca o ponto ao passar o mouse
                       id='code',  # ID para seleção
                    ),
                ],
                tooltip={"html": "{popup}", "style": {"color": "white", "background": "rgba(0,0,0,0.8)", "border-radius": "5px"}}
            ), height=680, on_select=handle_map_selection, selection_mode='single-object', key='code')
            
# Adiciona PyDeck se necessário para o mapa
try:
    import pydeck as pdk
except ImportError:
    st.error("A biblioteca PyDeck é necessária para a visualização do mapa. Por favor, instale-a com 'pip install pydeck'.")


if __name__ == "__main__":
    main()
