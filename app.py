import streamlit as st
import os, time, random, subprocess, re, requests

# --- DISEÑO PROFESIONAL ---
st.set_page_config(page_title="Fénix Studio AI", layout="centered", page_icon="🎬")

st.markdown("""
    <style>
    .stApp {background: linear-gradient(135deg, #0f172a, #1e293b); color: white;}
    .stChatMessage {background-color: #334155; border-radius: 15px; padding: 15px; border: 1px solid #475569;}
    .stButton>button {border-radius: 20px; font-weight: bold; background: #6366f1; color: white;}
    .css-1r6slp0 {background-color: #1e293b;}
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DE NEGOCIO ---
TRADUCTOR = {"coche": "cars", "coches": "luxury cars", "auto": "sports car", "negocio": "business", "dinero": "money", "fitness": "gym"}

def buscar_y_descargar_pexels(query, api_key, output_filename):
    busqueda = next((v for k, v in TRADUCTOR.items() if k in query.lower()), query)
    url = f"https://api.pexels.com/videos/search?query={busqueda}&per_page=10&orientation=portrait"
    try:
        res = requests.get(url, headers={"Authorization": api_key.strip()})
        if res.status_code != 200: return False
        data = res.json()
        if not data.get('videos'): return False
        link = random.choice(data['videos'])['video_files'][0]['link']
        with open(output_filename, 'wb') as f:
            f.write(requests.get(link).content)
        return True
    except: return False

with st.sidebar:
    st.title("⚙️ Ajustes")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.color_picker("🎨 Color Sub", "#00FFFF")
    voz = st.selectbox("🗣️ Voz", ["es-ES-AlvaroNeural", "es-MX-JorgeNeural"])

st.title("🎬 Fénix AI Professional Studio")
st.subheader("Tu generador de vídeos virales")

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [{"role": "assistant", "content": "¡Hola! ¿Qué vídeo quieres crear hoy? Ej: 'Hazme un vídeo sobre coches de lujo'."}]

for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "video" in msg:
            with open(msg["video"], "rb") as f:
                st.video(f.read())
                st.download_button("📥 Descargar Vídeo MP4", f, file_name="Fenix_Video.mp4", mime="video/mp4")

if guion := st.chat_input("Escribe tu idea aquí..."):
    st.session_state.mensajes.append({"role": "user", "content": guion})
    with st.chat_message("user"): st.markdown(guion)

    with st.chat_message("assistant"):
        with st.status("🚀 Procesando producción de alto nivel...", expanded=True) as status:
            uid = int(time.time())
            os.makedirs("output", exist_ok=True)
            v_final = f"output/v_{uid}.mp4"
            
            # Generar voz y subs
            subprocess.run(f'edge-tts --voice {voz} --text "{guion}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
            
            if buscar_y_descargar_pexels(guion, pexels_key, "clip.mp4"):
                # Simplificado para mayor velocidad
                cmd = f'ffmpeg -y -stream_loop -1 -i "clip.mp4" -i t.mp3 -vf "scale=480:854:force_original_aspect_ratio=increase,crop=480:854" -c:v libx264 -preset superfast -crf 30 -c:a aac -shortest "{v_final}"'
                subprocess.run(cmd, shell=True)
                
                if os.path.exists(v_final):
                    st.session_state.mensajes.append({"role": "assistant", "content": "✅ ¡Vídeo creado con éxito!", "video": v_final})
                    st.rerun()
                else: status.error("❌ Fallo en el renderizado")
            else: status.error("❌ Error de búsqueda en Pexels")
