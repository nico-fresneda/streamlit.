import streamlit as st
import requests

# Configuración inicial de la página de Streamlit
st.set_page_config(
    page_title="Pokedex Web",
    page_icon="🔴",
    layout="centered"
)

# --- BLOQUE 1: CONFIGURACIÓN DE COLORES ---
TYPE_COLORS = {
    'electric': '#FFEA70', 'normal': '#B09398', 'fire': '#FF675C',
    'water': '#0596C7', 'ice': '#AFEAFD', 'rock': '#999799',
    'flying': '#7AE7C7', 'grass': '#4A9681', 'psychic': '#FFC6D9',
    'ghost': '#561D25', 'bug': '#A2FAA3', 'poison': '#795663',
    'ground': '#D2B074', 'dragon': '#DA627D', 'steel': '#1D8A99',
    'fighting': '#2F2F2F', 'default': '#2A1A1F',
}

STAT_HEX_COLORS = {
    'hp': '#FF0000', 'attack': '#F08030', 'defense': '#F8D030',
    'special-attack': '#6890F0', 'special-defense': '#78C850', 'speed': '#F85888'
}

# Inicializar el historial en la variable de sesión de Streamlit
if "historial_busqueda" not in st.session_state:
    st.session_state.historial_busqueda = []

# --- BLOQUE 2: CONEXIÓN CON LA API ---
@st.cache_data(show_spinner=False) # Caché de Streamlit para no hacer requests repetidos al mismo Pokémon
def fetch_pokemon(name):
    url = f'https://pokeapi.co/api/v2/pokemon/{name.lower().strip()}'
    try:
        res = requests.get(url)
        res.raise_for_status()
        return res.json()
    except:
        return None

# --- BLOQUE 3: GENERACIÓN DE LA TARJETA VISUAL ---
def create_card(data):
    name = data['name'].capitalize()
    id_ = data['id']
    sprite = data['sprites']['front_default']
    
    # Si no hay sprite frontal, intenta buscar otro o poner un placeholder
    if not sprite:
        sprite = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png"
        
    types = [t['type']['name'] for t in data['types']]
    color_theme = TYPE_COLORS.get(types[0], TYPE_COLORS['default'])

    stats_html = ""
    for s in data['stats']:
        s_name = s['stat']['name']
        val = s['base_stat']
        s_color = STAT_HEX_COLORS.get(s_name, '#777')
        width = min(100, (val / 150) * 100)
        stats_html += f"""
        <div style='margin-bottom: 5px;'>
            <div style='display:flex; justify-content:space-between; font-size: 11px;'>
                <span>{s_name.upper()}</span>
                <span>{val}</span>
            </div>
            <div style='background: #ddd; border-radius: 5px; height: 8px; width: 100%; overflow: hidden;'>
                <div style='background: {s_color}; width: {width}%; height: 100%;'></div>
            </div>
        </div>
        """

    return f"""
    <div style="background-color: white; border-radius: 20px; padding: 20px; width: 300px; border: 4px solid {color_theme}; font-family: 'Arial', sans-serif; color: #333; box-shadow: 0px 10px 20px rgba(0,0,0,0.2); margin: 0 auto;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h2 style="margin: 0; color: {color_theme};">{name}</h2>
            <span style="background: #eee; padding: 2px 10px; border-radius: 20px; font-weight: bold;">#{id_}</span>
        </div>
        <div style="text-align: center; margin: 15px 0;">
            <img src="{sprite}" style="width: 140px; filter: drop-shadow(2px 4px 6px black);">
        </div>
        <div style="display: flex; justify-content: center; gap: 5px; margin-bottom: 20px;">
            {' '.join([f'<span style="background:{TYPE_COLORS.get(t, "#ccc")}; padding: 4px 12px; border-radius: 15px; font-size: 12px; color: white; text-transform: uppercase; font-weight: bold;">{t}</span>' for t in types])}
        </div>
        <div style="background: #f9f9f9; padding: 10px; border-radius: 10px;">
            {stats_html}
        </div>
    </div>
    """

# --- BLOQUE 4: CLASIFICACIÓN POR PODER ---
def obtener_categoria(total):
    if total > 600:
        return "LEGENDARIO", "#D4AF37"
    elif total > 500:
        return "ELITE", "#999B9B"
    elif total > 300:
        return "ESTÁNDAR", "#CD7F32"
    else:
        return "INICIAL", "#8B4513"

# --- BLOQUE 5: INTERFAZ DE STREAMLIT ---
st.title("🔴 Pokedex Interactivo")
st.markdown("Busca cualquier Pokémon por nombre o número para ver sus estadísticas base.")

# Creando el layout de búsqueda usando un formulario para permitir envío con "Enter"
with st.form(key='search_form'):
    col1, col2 = st.columns([3, 1])
    with col1:
        nombre_busqueda = st.text_input("Consulta tu Pokémon:", placeholder="Ej: Pikachu o 25", label_visibility="collapsed")
    with col2:
        submit_button = st.form_submit_button(label="Buscar 🔍")

# --- BLOQUE 6: LÓGICA DE BÚSQUEDA Y RENDERIZADO ---
if submit_button or nombre_busqueda:
    nombre = nombre_busqueda.strip().lower()
    
    if not nombre:
        st.warning("⚠️ Por favor, ingresa un nombre o número válido.")
    else:
        with st.spinner(f"Buscando a {nombre.capitalize()}..."):
            data = fetch_pokemon(nombre)
            
        if data:
            # Cálculo de categoría
            total_stats = sum(s['base_stat'] for s in data['stats'])
            cat_nombre, cat_color = obtener_categoria(total_stats)

            # Actualización del historial (evitando duplicados seguidos si se desea, o simplemente insertando)
            nombre_capitalizado = data['name'].capitalize()
            if not st.session_state.historial_busqueda or st.session_state.historial_busqueda[0] != nombre_capitalizado:
                st.session_state.historial_busqueda.insert(0, nombre_capitalizado)

            # Contenedor visual para centrar los elementos
            st.write("<br>", unsafe_allow_html=True) # Espacio extra
            
            # HTML para la ficha de categoría superior
            category_card_html = f"""
            <div style="background-color: white; border-radius: 20px; padding: 15px; margin: 0 auto 20px auto; width: 300px; border: 4px solid {cat_color}; font-family: 'Arial', sans-serif; color: #333; box-shadow: 0px 10px 20px rgba(0,0,0,0.1); text-align: center;">
                <h3 style="margin: 0; color: {cat_color}; font-size: 18px;">Categoría: {cat_nombre}</h3>
                <p style="margin: 5px 0 0; font-weight: bold; font-size: 14px;">Total Puntos Base: {total_stats}</p>
            </div>
            """
            
            # Renderizamos el HTML directamente en Streamlit usando st.markdown
            st.markdown(category_card_html, unsafe_allow_html=True)
            st.markdown(create_card(data), unsafe_allow_html=True)
            
            st.write("<br>", unsafe_allow_html=True)
        else:
            st.error(f"❌ El Pokémon '{nombre}' no existe en la base de datos.")

# Mostrar el historial en un expansor en la parte inferior (opcional pero más limpio)
if st.session_state.historial_busqueda:
    with st.expander("🕒 Últimas búsquedas"):
        for i, h in enumerate(st.session_state.historial_busqueda[:5]):
            st.write(f"**{i+1}.** {h}")