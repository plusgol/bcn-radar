import streamlit as st
import requests

st.set_page_config(page_title="BCN Club Radar", page_icon="🪩", layout="centered")

st.title("🪩 BCN Club Radar")
st.subheader("Estat real de les entrades actualitzat des de Fourvenues")

# Canals i identificadors oficials que fa servir Fourvenues a Barcelona
CLUBS = {
    "Sutton Barcelona": "sutton-barcelona",
    "Bling Bling": "bling-bling-barcelona",
    "Opium Barcelona": "opium-barcelona",
    "Downtown BCN": "downtown-barcelona"
}

def get_club_data(slug):
    # Accés a l'API directa de contingut de canals de Fourvenues
    url = f"https://api.fourvenues.com/v1/channels/{slug}/events?limit=5"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return r.json().get('data', [])
    except:
        return []
    return []

dia_filtrat = st.selectbox("📅 Quin dia voleu sortir?", ["Dijous", "Divendres", "Dissabte"])

for name, slug in CLUBS.items():
    st.markdown(f"### 📍 {name}")
    events = get_club_data(slug)
    
    if not events:
        st.caption("⚠️ No s'han pogut carregar les dades de Fourvenues o esdeveniment protegit.")
        continue
        
    for ev in events:
        nom_festa = ev.get('name', 'Festa Principal')
        st.markdown(f"**{nom_festa}**")
        
        # Extracció de l'estat exacte de cada Release (Tram de venda)
        tickets = ev.get('tickets', [])
        if tickets:
            for t in tickets[:3]:
                t_name = t.get('name', 'Entrada')
                t_price = t.get('price', 0)
                is_sold_out = t.get('isSoldOut', False)
                left = t.get('availableCount', 0)
                
                if is_sold_out or left == 0:
                    status = "🔴 ESGOTAT"
                elif left < 20:
                    status = f"🟠 ÚLTIMES ({left} tiquets!)"
                else:
                    status = "🟢 Disponible"
                    
                st.markdown(f"- **{t_name}**: {t_price}€ | {status}")
        else:
            st.markdown("- *Reserves només a taquilla o llista de convidats.*")
            
        # Extracció i estat de les Taules VIP
        vips = ev.get('vipTables', [])
        if vips:
            preu_minim = min([v.get('minimumConsumption', 300) for v in vips])
            vips_lliures = sum([1 for v in vips if not v.get('isBooked', False)])
            st.markdown(f"🍾 **VIP:** Des de {preu_minim}€ *(Queden {vips_lliures} taules lliures)*")
        else:
            st.markdown("🍾 **VIP:** Sense dades de taules online.")
        st.divider()