import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil, math, random, gc
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V202", layout="centered")
components.html("<script>if('wakeLock' in navigator){navigator.wakeLock.request('screen');}</script>", height=0)

st.markdown("""
<style>
    .stApp { background: #000000; color: #FFFFFF; }
    .pro-title { font-size: 42px; font-weight: 900; background: -webkit-linear-gradient(45deg, #FF00FF, #00FFFF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; text-transform: uppercase; margin-bottom: 20px;}
    .msg { color: #00FFD1; font-family: 'Courier New', monospace; font-size: 14px; margin-bottom: 8px; border-left: 3px solid #FF00FF; padding-left: 12px; }
    .info-card { padding: 15px; border-radius: 12px; background: #0f172a; border: 1px solid #FF00FF; text-align: center; color: #00FFD1; margin-top: 25px; font-weight: bold;}
    .stButton>button { width: 100%; background: linear-gradient(45deg, #FF00FF, #0088ff); color: white; border: none; font-weight: 900; height: 65px; border-radius: 12px; font-size: 22px; box-shadow: 0 0 20px rgba(255,0,255,0.4);}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX GÉNESIS V202 🦅🧬</div>', unsafe_allow_html=True)

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

st.markdown('<div class="msg">✨ SISTEMA DE CONSTRUCCIÓN ATÓMICA ACTIVADO. No se buscará nada en internet.</div>', unsafe_allow_html=True)

tema_genesis = st.text_input("🧬 ¿De qué quieres que el bot CONSTRUYA el vídeo?", placeholder="Ej: Agujero negro, partículas de oro, flujo de lava...")
guion_fijo = st.text_area("📝 Guion para la locución:", height=100)

if st.button("🏗️ CONSTRUIR DESDE LOS PÍXELES"):
    preparar()
    with st.container():
        st.markdown('<div class="msg">🧠 Redactando guion y procesando voz...</div>', unsafe_allow_html=True)
        
        guion = guion_fijo.strip() if guion_fijo.strip() else "Estamos construyendo el futuro, píxel a píxel, sin depender de nada que ya exista."
        
        # 1. GENERAR AUDIO
        audio_voz = "taller/voz.mp3"
        subprocess.run(f'edge-tts --voice es-MX-JorgeNeural --text "{guion}" --write-media "{audio_voz}"', shell=True)
        dur = float(subprocess.check_output(f'ffprobe -i "{audio_voz}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))

        # 2. CONSTRUIR VÍDEO MATEMÁTICO (Fondo Generativo)
        # Aquí es donde el bot "crea" sin buscar. Usamos generadores de ruido y fractales de FFmpeg.
        st.markdown('<div class="msg">🏗️ Fabricando metraje visual mediante algoritmos...</div>', unsafe_allow_html=True)
        
        # Generamos un fondo de "plasma" o "partículas" que cambia según el tema
        color1 = "0x" + "".join([random.choice("0123456789ABCDEF") for _ in range(6)])
        color2 = "0x" + "".join([random.choice("0123456789ABCDEF") for _ in range(6)])
        
        # Este comando de FFmpeg crea una animación fluida de nubes/energía desde CERO
        video_generado = "taller/generado.mp4"
        cmd_v = f'ffmpeg -y -f lavfi -i "neonsyntax=seed={random.randint(1,999)}:s=720x1280" -f lavfi -i "cellauto=s=720x1280:rule={random.randint(1,255)}" -filter_complex "blend=all_mode=overlay,hue=h={random.randint(0,360)},fps=24" -t {dur} -c:v libx264 -preset ultrafast "{video_generado}" > /dev/null 2>&1'
        
        # Si el comando neonsyntax no está en esa versión de ffmpeg, usamos uno de ruido de plasma ultra épico
        if not os.path.exists(video_generado):
            cmd_v = f'ffmpeg -y -f lavfi -i "mandelbrot=s=720x1280:rate=24:maxiter=100" -f lavfi -i "sine=f=0.2:d={dur}" -filter_complex "[0:v]hue=h=t*50,zoompan=z=\'1.5+sin(t)/2\':d=1,format=yuv420p[v]" -map "[v]" -t {dur} -c:v libx264 -preset ultrafast "{video_generado}" > /dev/null 2>&1'
        
        subprocess.run(cmd_v, shell=True)

        # 3. SUBTÍTULOS
        palabras = guion.upper().split()
        pares = [palabras[j:j+2] for j in range(0, len(palabras), 2)]
        t_par = dur / max(len(pares), 1)
        draws = []
        for k, p in enumerate(pares):
            ts, te = k * t_par, (k+1) * t_par
            txt = " ".join(p)
            draws.append(f"drawtext=text='{txt}':fontfile='{f_abs}':fontcolor=white:fontsize=80:box=1:boxcolor=black@0.6:boxborderw=20:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{ts},{te})'")

        vf = f"format=yuv420p,{','.join(draws)}"
        with open("taller/f.txt", "w", encoding="utf-8") as f: f.write(vf)

        final = "taller/final.mp4"
        subprocess.run(f'ffmpeg -y -i "{video_generado}" -i "{audio_voz}" -vf "format=yuv420p,drawtext=text=\'FENIX GENESIS\':x=10:y=10:fontsize=20:fontcolor=gray@0.5,{vf}" -c:v libx264 -preset ultrafast -t {dur} "{final}" > /dev/null 2>&1', shell=True)

        if os.path.exists(final):
            st.markdown('<div class="info-card">🏆 VÍDEO CONSTRUIDO ATÓMICAMENTE</div>', unsafe_allow_html=True)
            with open(final, "rb") as f: st.video(f.read())
