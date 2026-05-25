import streamlit as st
import requests

# Configuració inicial de la pàgina
st.set_page_config(
    page_title="BCN Club Radar",
    page_icon="🪩",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estils CSS personalitzats per donar-li aspecte d'App nativa i nocturna
st.markdown("""
    <style>
    /* Fons fosc general i text clar */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }
    
    /* Títols */
    h1, h2, h3 {
        color: #f8fafc !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
    }
    
    h1 {
        background: -webkit-linear-gradient(45deg, #8b5cf6, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding-bottom: 10px;
    }
    
    /* Targetes per cada club */
    .club-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    /* Estilització dels estats */
    .status-badge {
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        display: inline-block;
        margin-left: 10px;
    }
    
    .status-available { background-color: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); }
    .status-fast { background-color: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); }
    .status-soldout { background-color: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); }
    
    /* Amagar elements per defecte de Streamlit per fer-ho més net */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Estil pel desplegable de dies */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #1e293b;
        border: 1px solid #475569;
        border-radius: 10px;
        color: white;
    }
    
    /* Divisors personalitzats */
    hr {
        border-color: #334155 !important;
        margin-top: 15px !important;
        margin-bottom: 15px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🪩 BCN Club Radar")
st.markdown("<p style='color: #94a3b8; font-size: 0.9rem; margin-top: -15px; margin-bottom: 25px;'>📡 Dades en temps real de l'API de Fourvenues</p>", unsafe_allow_html=True)

def get_all_events():
    """Accés a l'API directa de l'enllaç global de Barcelona proporcionat"""
    # Utilitzem el slug exacte del link que has passat per agafar totes les discos de cop
    url = "https://api.fourvenues.com/v1/channels/discotecas-barcelona-1/events?limit=30"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://site.fourvenues.com",
        "Referer": "https://site.fourvenues.com/"
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return r.json().get('data', [])
    except:
        pass
    return []

dia_filtrat = st.selectbox("📅 Filtra per dia:", ["Tots els dies", "Dijous", "Divendres", "Dissabte"])

events = get_all_events()

if not events:
    st.markdown("""
    <div class='club-card' style='text-align: center; padding: 30px 15px;'>
        <p style='color: #64748b; margin: 0;'>Ghost Town 👻</p>
        <p style='color: #475569; font-size: 0.8rem; margin: 0;'>Cap festa detectada (o l'API bloqueja la connexió des del servidor)</p>
    </div>
    """, unsafe_allow_html=True)
else:
    for ev in events:
        # Obtenim la sala directament de l'event (ja que recollim de l'agregador general)
        venue_data = ev.get('venue', {})
        venue_name = venue_data.get('name', 'Discoteca BCN')
        nom_festa = ev.get('name', 'Festa Principal')
        
        # Inici de la targeta (Card)
        st.markdown(f"<div class='club-card'>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='margin-bottom: 5px; color: #a855f7; font-size: 1.1rem;'><i class='fa-solid fa-location-dot'></i> {venue_name}</h3>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='margin-top: 0; color: #e2e8f0; font-size: 0.95rem;'>✨ {nom_festa}</h4>", unsafe_allow_html=True)
        
        # Extracció de l'estat exacte de cada Release (Tram de venda)
        tickets = ev.get('tickets', [])
        if tickets:
            st.markdown("<p style='font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; font-weight: bold; margin-bottom: 8px;'>🎟️ Entrades Generals</p>", unsafe_allow_html=True)
            for t in tickets[:3]:
                t_name = t.get('name', 'Entrada')
                t_price = t.get('price', 0)
                is_sold_out = t.get('isSoldOut', False)
                left = t.get('availableCount', 0)
                
                # Lògica d'estats per a l'HTML
                if is_sold_out or left == 0:
                    badge_class = "status-soldout"
                    badge_text = "Esgotat"
                elif left < 20:
                    badge_class = "status-fast"
                    badge_text = f"Queden {left}!"
                else:
                    badge_class = "status-available"
                    badge_text = "Disponible"
                    
                st.markdown(f"""
                <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; border-bottom: 1px solid #334155; padding-bottom: 5px;'>
                    <span style='font-size: 0.9rem; color: #cbd5e1;'>{t_name} - <b>{t_price}€</b></span>
                    <span class='status-badge {badge_class}'>{badge_text}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<p style='font-size: 0.8rem; color: #94a3b8;'><i>Reserves només a taquilla o llista de convidats.</i></p>", unsafe_allow_html=True)
            
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Extracció i estat de les Taules VIP
        vips = ev.get('vipTables', [])
        if vips:
            preu_minim = min([v.get('minimumConsumption', 300) for v in vips])
            vips_lliures = sum([1 for v in vips if not v.get('isBooked', False)])
            
            vip_badge = f"<span class='status-badge status-soldout'>Esgotat</span>" if vips_lliures == 0 else f"<span class='status-badge status-available'>{vips_lliures} lliures</span>"
            
            st.markdown(f"""
            <div style='display: flex; justify-content: space-between; align-items: center; background: rgba(139, 92, 246, 0.1); padding: 10px; border-radius: 8px; border: 1px solid rgba(139, 92, 246, 0.2);'>
                <div>
                    <p style='margin: 0; font-size: 0.75rem; color: #c4b5fd; text-transform: uppercase; font-weight: bold;'>🍾 Taules VIP</p>
                    <p style='margin: 0; font-size: 0.9rem; font-weight: bold; color: #e2e8f0;'>Des de {preu_minim}€</p>
                </div>
                {vip_badge}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("<p style='font-size: 0.8rem; color: #94a3b8;'>🍾 VIP: Consultar disponibilitat a taquilla.</p>", unsafe_allow_html=True)
            
        # Fi de la targeta (Card)
        st.markdown("</div>", unsafe_allow_html=True)
