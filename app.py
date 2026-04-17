import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil, math, random, gc
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Quantum V204", layout="centered")

st.markdown("""
<style>
    .stApp { background: #000000; color: #FFFFFF; }
    .pro-title { font-size: 42px; font-weight: 900; background: -webkit-linear-gradient(45deg, #00FFD1, #FF00FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; text-transform: uppercase; margin-bottom: 20px;}
    .msg { color: #00FFD1; font-family: 'Courier New', monospace; font-size: 14px; margin-bottom: 8px; border-left: 3px solid #00FFD1; padding-left: 12px; }
    .stButton>button { width: 100%; background: linear-gradient(45deg, #00FFD1, #0088ff); color: white; border: none; font-weight: 900; height: 65px; border-radius: 12px; font-size: 20px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX QUANTUM V204 🦅🌌</div>', unsafe_allow_html=True)

@st.cache_resource
def get_font():
    p = "font.ttf"
    if not os.path.exists(p):
        r = requests.get("https://github.com/matomo-org/travis-scripts/raw/master/fonts/Arial.ttf")
        with open(p, "wb") as f: f.write(r.content)
    return "font.ttf"

def preparar():
    if os.path.exists("taller"): shutil.rmtree("taller")
    os.makedirs("taller", exist_ok=True)
    subprocess.run("pkill ffmpeg", shell=True)

f_abs = get_font()

# INTERFAZ
tema_ia = st.text_input("🧬 ¿Qué quieres que la IA CONSTRUYA desde 0?", placeholder="Ej: Un ferrari futurista en Marte, una ciudad de cristal...")
guion_ia = st.text_area("📝 Guion (Si lo dejas vacío, la IA lo inventará):", height=80)

if st.button("🛸 GENERAR PÍXELES CON IA GRATIS"):
    if not tema_ia:
        st.error("Dime qué quieres construir, Dayron.")
        st.stop()
        
    preparar()
    with st.container():
        # 1. GENERAR IMAGEN ÚNICA (Pollinations IA - Gratis e Ilimitado)
        st.markdown('<div class="msg">🎨 La IA está dibujando tu imagen desde cero...</div>', unsafe_allow_html=True)
        img_path = "taller/base.jpg"
        prompt_img = f"{tema_ia}, cinematic lighting, hyperrealistic, 8k, vertical orientation, high detail"
        img_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt_img)}?width=720&height=1280&nologo=true&seed={random.randint(1,99999)}"
        
        try:
            r = requests.get(img_url, timeout=30)
            with open(img_path, "wb") as f: f.write(r.content)
        except:
            st.error("La IA de dibujo está saturada. Inténtalo en 10 segundos.")
            st.stop()

        # 2. GENERAR GUION Y VOZ
        st.markdown('<div class="msg">🎙️ Redactando y grabando voz...</div>', unsafe_allow_html=True)
        if not guion_ia.strip():
            prompt_txt = f"Escribe un guion épico de 10 segundos sobre {tema_ia}. Solo español."
            guion_final = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote(prompt_txt)}").text
        else:
            guion_final = guion_ia.strip()
            
        audio_path = "taller/voz.mp3"
        subprocess.run(f'edge-tts --voice es-MX-JorgeNeural --text "{guion_final}" --write-media "{audio_path}"', shell=True)
        
        try: dur = float(subprocess.check_output(f'ffprobe -i "{audio_path}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
        except: dur = 10.0

        # 3. CONVERTIR IMAGEN EN VÍDEO CON ZOOM DINÁMICO (Efecto Ken Burns Pro)
        st.markdown('<div class="msg">🎥 Transformando imagen en vídeo de 10s...</div>', unsafe_allow_html=True)
        video_output = "taller/final.mp4"
        
        # Este comando hace que la imagen generada se mueva y tenga vida
        palabras = guion_final.upper().split()
        pares = [palabras[j:j+2] for j in range(0, len(palabras), 2)]
        t_par = dur / max(len(pares), 1)
        draws = []
        for k, p in enumerate(pares):
            ts, te = k * t_par, (k+1) * t_par
            txt = " ".join(p)
            draws.append(f"drawtext=text='{txt}':fontfile='{f_abs}':fontcolor=yellow:fontsize=75:box=1:boxcolor=black@0.6:boxborderw=20:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{ts},{te})'")

        # El filtro de ZoomPan crea el efecto de que la cámara se mete dentro de la imagen IA
        vf = f"scale=1280:2275,zoompan=z='min(zoom+0.001,1.5)':d={int(dur*24)}:s=720x1280,format=yuv420p,{','.join(draws)}"
        
        subprocess.run(f'ffmpeg -y -loop 1 -i "{img_path}" -i "{audio_path}" -vf "{vf}" -c:v libx264 -preset ultrafast -tune stillimage -c:a copy -t {dur} -pix_fmt yuv420p "{video_output}" > /dev/null 2>&1', shell=True)

        if os.path.exists(video_output):
            st.markdown('<div class="info-card">🏆 VÍDEO CONSTRUIDO POR IA DESDE 0</div>', unsafe_allow_html=True)
            with open(video_output, "rb") as f: st.video(f.read())
            st.balloons()
