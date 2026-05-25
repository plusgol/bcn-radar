import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

st.set_page_config(page_title="BCN Club Radar (Web Scraper)", page_icon="🪩", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; font-family: 'Inter', sans-serif; }
    h1, h2, h3 { color: #f8fafc !important; }
    .club-card { background-color: #1e293b; border: 1px solid #334155; border-radius: 16px; padding: 20px; margin-bottom: 20px; }
    .status-badge { padding: 4px 10px; border-radius: 9999px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; display: inline-block; }
    .status-available { background-color: rgba(16, 185, 129, 0.2); color: #34d399; }
    .status-soldout { background-color: rgba(239, 68, 68, 0.2); color: #f87171; }
    </style>
""", unsafe_allow_html=True)

st.title("🪩 BCN Club Radar")
st.markdown("<p style='color: #94a3b8;'>📡 Obtenint dades per Scraping Web Directe</p>", unsafe_allow_html=True)

# Llista de webs a analitzar (URLs d'exemple, cal ajustar-les a les pàgines de calendari reals)
CLUBS_URLS = {
    "Sutton": "https://suttonbarcelona.com/es/eventos/",
    "Bling Bling": "https://blingblingbcn.com/es/eventos/",
    "Sala Apolo": "https://www.sala-apolo.com/ca/programacio/"
}

@st.cache_data(ttl=300)
def scrape_club(name, url):
    """Extrau dades bàsiques fent scraping de l'HTML de la web oficial."""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/116.0.0.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return {"error": f"La web de {name} ha bloquejat l'accés (Codi {response.status_code})."}
            
        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = soup.get_text().lower()
        
        # Lògica molt bàsica de detecció per paraules clau
        resultats = {
            "nom": f"Pròxima festa a {name}",
            "preu_estimat": "No detectat",
            "esgotat": False,
            "vip_disponible": True
        }
        
        # Intentem buscar preus (ex: 20€, 25€) fent servir expressions regulars
        preus = re.findall(r'(\d{2,3})\s*€', soup.get_text())
        if preus:
            # Agafem el preu més baix que sembli una entrada (menor de 100€)
            entrades = [int(p) for p in preus if int(p) < 100]
            if entrades:
                resultats["preu_estimat"] = f"Aprox. {min(entrades)}€"
                
        # Detecció de sold out
        if "sold out" in text_content or "agotado" in text_content or "esgotat" in text_content:
            resultats["esgotat"] = True
            
        # Detecció de VIP amagat o esgotat
        if "vip sold out" in text_content or "mesas agotadas" in text_content:
             resultats["vip_disponible"] = False

        return resultats
        
    except Exception as e:
        return {"error": str(e)}

# Renderització de resultats
for name, url in CLUBS_URLS.items():
    st.markdown(f"<div class='club-card'>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color: #a855f7;'>📍 {name}</h3>", unsafe_allow_html=True)
    
    with st.spinner(f"Analitzant la web de {name}..."):
        dades = scrape_club(name, url)
        
    if "error" in dades:
        st.error(dades["error"])
    else:
        st.markdown(f"**{dades['nom']}**")
        
        # Estat General
        badge = "status-soldout" if dades['esgotat'] else "status-available"
        text_badge = "ESGOTAT" if dades['esgotat'] else "Disponibles a la web"
        st.markdown(f"""
        <div style='display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 5px;'>
            <span style='color: #cbd5e1;'>🎟️ Preu detectat: <b>{dades['preu_estimat']}</b></span>
            <span class='status-badge {badge}'>{text_badge}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Estat VIP
        vip_badge = "status-available" if dades['vip_disponible'] else "status-soldout"
        vip_text = "Disponibles a la web" if dades['vip_disponible'] else "ESGOTAT"
        st.markdown(f"""
        <div style='display: flex; justify-content: space-between; align-items: center; margin-top: 10px; background: rgba(139, 92, 246, 0.1); padding: 10px; border-radius: 8px;'>
            <span style='color: #c4b5fd; font-weight: bold;'>🍾 Estat VIP Estimatiu</span>
            <span class='status-badge {vip_badge}'>{vip_text}</span>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)
