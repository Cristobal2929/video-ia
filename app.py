import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil, math, random, gc
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V203", layout="centered")
components.html("<script>if('wakeLock' in navigator){navigator.wakeLock.request('screen');}</script>", height=0)

st.markdown("""
<style>
    .stApp { background: #000000; color: #FFFFFF; }
    .pro-title { font-size: 42px; font-weight: 900; background: -webkit-linear-gradient(45deg, #00FFD1, #FF00FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; text-transform: uppercase; margin-bottom: 20px;}
    .msg { color: #00FFD1; font-family: 'Courier New', monospace; font-size: 14px; margin-bottom: 8px; border-left: 3px solid #00FFD1; padding-left: 12px; }
    .info-card { padding: 15px; border-radius: 12px; background: #0f172a; border: 1px solid #00FFD1; text-align: center; color: #00FFD1; margin-top: 25px; font-weight: bold;}
    .stButton>button { width: 100%; background: linear-gradient(45deg, #00FFD1, #0088ff); color: white; border: none; font-weight: 900; height: 65px; border-radius: 12px; font-size: 20px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX GÉNESIS V203 🦅✨</div>', unsafe_allow_html=True)

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

tema = st.text_input("🧬 ¿Qué quieres que el bot CONSTRUYA?", placeholder="Ej: Energía azul, galaxia roja, flujo digital...")
guion_txt = st.text_area("📝 Guion para la locución:", height=80)

if st.button("🏗️ CONSTRUIR PÍXELES (V203 ESTABLE)"):
    preparar()
    with st.container():
        st.markdown('<div class="msg">🎙️ Grabando voz...</div>', unsafe_allow_html=True)
        guion = guion_txt.strip() if guion_txt.strip() else "Construyendo una nueva realidad desde el código fuente."
        
        audio_voz = "taller/voz.mp3"
        subprocess.run(f'edge-tts --voice es-MX-JorgeNeural --text "{guion}" --write-media "{audio_voz}"', shell=True)
        
        try:
            dur = float(subprocess.check_output(f'ffprobe -i "{audio_voz}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
        except: dur = 5.0

        st.markdown('<div class="msg">🏗️ Fabricando metraje visual ligero...</div>', unsafe_allow_html=True)
        video_gen = "taller/gen.mp4"
        
        # MOTOR LIGERO: Genera un fondo de plasma dinámico basado en ruido que no funde el servidor
        # Usamos 'testsrc2' que es mucho más eficiente que mandelbrot
        cmd_v = f'ffmpeg -y -f lavfi -i "testsrc2=s=720x1280:rate=24" -t {dur} -vf "hue=h=t*100,chromashift=cb=2:cr=2,zoompan=z=\'1.1+sin(t)/10\':d=1:s=720x1280" -c:v libx264 -preset ultrafast -pix_fmt yuv420p "{video_gen}" > /dev/null 2>&1'
        subprocess.run(cmd_v, shell=True)

        st.markdown('<div class="msg">🎬 Montando escena final...</div>', unsafe_allow_html=True)
        palabras = guion.upper().split()
        pares = [palabras[j:j+2] for j in range(0, len(palabras), 2)]
        t_par = dur / max(len(pares), 1)
        draws = []
        for k, p in enumerate(pares):
            ts, te = k * t_par, (k+1) * t_par
            txt = " ".join(p)
            draws.append(f"drawtext=text='{txt}':fontfile='{f_abs}':fontcolor=white:fontsize=70:box=1:boxcolor=black@0.6:boxborderw=20:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{ts},{te})'")

        final = "taller/master.mp4"
        subprocess.run(f'ffmpeg -y -i "{video_gen}" -i "{audio_voz}" -vf "{",".join(draws)}" -c:v libx264 -preset ultrafast -t {dur} "{final}" > /dev/null 2>&1', shell=True)

        if os.path.exists(final):
            st.markdown('<div class="info-card">🏆 VÍDEO CONSTRUIDO (SISTEMA ESTABLE)</div>', unsafe_allow_html=True)
            with open(final, "rb") as f: st.video(f.read())
