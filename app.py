import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil, math, random, gc
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V96", layout="centered")

# Mantener pantalla activa
components.html("<script>if('wakeLock' in navigator){navigator.wakeLock.request('screen');}</script>", height=0)

st.markdown("""
<style>
    .stApp { background: #000000; color: #FFFFFF; }
    .pro-title { font-size: 38px; font-weight: 900; background: -webkit-linear-gradient(45deg, #FFD700, #00FFD1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; text-transform: uppercase; margin-bottom: 10px;}
    .msg { color: #94A3B8; font-family: monospace; font-size: 13px; margin-bottom: 5px; border-left: 2px solid #00FFD1; padding-left: 8px; }
    .info-card { padding: 15px; border-radius: 10px; background: #111827; border: 1px solid #00FFD1; text-align: center; color: #00FFD1; margin-top: 15px;}
    .stButton>button { width: 100%; background: linear-gradient(45deg, #00FFD1, #0088ff); color: white; border: none; font-weight: bold; border-radius: 8px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V96 🎥</div>', unsafe_allow_html=True)

@st.cache_resource
def get_font():
    f_path = "font.ttf"
    if not os.path.exists(f_path):
        try:
            r = requests.get("https://github.com/matomo-org/travis-scripts/raw/master/fonts/Arial.ttf", timeout=10)
            with open(f_path, "wb") as f: f.write(r.content)
        except: pass
    return os.path.abspath(f_path).replace('\\', '/')

f_abs = get_font()

def preparar():
    if os.path.exists("taller"): shutil.rmtree("taller")
    os.makedirs("taller", exist_ok=True)
    # Limpiar procesos zombies de ffmpeg para liberar RAM
    subprocess.run("pkill ffmpeg", shell=True)

tema = st.text_input("🧠 Tema del vídeo:", placeholder="Ej: Motivación millonaria")
n_escenas = st.select_slider("⏱️ Número de escenas:", options=[4, 6, 8, 10], value=6)

if st.button("🚀 GENERAR VÍDEO (MODO ESTABLE)"):
    if not tema:
        st.error("Escribe un tema")
    else:
        preparar()
        log = st.container()
        
        with log:
            st.markdown('<div class="msg">📝 Creando guion...</div>', unsafe_allow_html=True)
            guion = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote('Guion TikTok '+tema+'. Solo texto, 50 palabras.')}").text
            guion = re.sub(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ.,! ]', '', guion).strip()
            
            st.markdown('<div class="msg">🎙️ Generando voz...</div>', unsafe_allow_html=True)
            audio = "taller/a.mp3"
            subprocess.run(f'edge-tts --voice es-MX-JorgeNeural --text "{guion}" --write-media "{audio}"', shell=True)
            
            dur = 15.0
            try: dur = float(subprocess.check_output(f'ffprobe -i "{audio}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
            except: pass
            
            t_escena = dur / n_escenas
            clips = []
            words = guion.split()

            for i in range(n_escenas):
                st.markdown(f'<div class="msg">🎬 Procesando escena {i+1}...</div>', unsafe_allow_html=True)
                keyword = words[min(i*4, len(words)-1)]
                img = f"taller/i_{i}.jpg"
                vid = f"taller/v_{i}.mp4"
                
                # Imagen optimizada (menos peso para evitar crash)
                seed = random.randint(1, 9999)
                url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(keyword + ' cinematic 4k style')}?width=540&height=960&nologo=true&seed={seed}"
                
                try:
                    r = requests.get(url, timeout=15)
                    if r.status_code == 200:
                        with open(img, 'wb') as f: f.write(r.content)
                        # Zoom suave y ultra rápido
                        vf = f"scale=600:1066,zoompan=z='1.0+0.001*on':d={int(t_escena*24)}:s=540x960:fps=24,format=yuv420p"
                        subprocess.run(f'ffmpeg -y -loop 1 -i "{img}" -vf "{vf}" -t {t_escena} -c:v libx264 -preset ultrafast -crf 28 "{vid}"', shell=True)
                        if os.path.exists(vid): clips.append(f"v_{i}.mp4")
                except: pass
                
                if os.path.exists(img): os.remove(img)
                gc.collect() # Liberar RAM después de cada escena

            st.markdown('<div class="msg">🎞️ Montaje final...</div>', unsafe_allow_html=True)
            with open("taller/l.txt", "w") as f:
                for c in clips: f.write(f"file '{c}'\n")
            
            mudo = "taller/m.mp4"
            subprocess.run(f'ffmpeg -y -f concat -safe 0 -i taller/l.txt -c copy "{mudo}"', shell=True)
            
            final = "taller/final.mp4"
            # Subtítulos centrados y simples para máxima estabilidad
            txt_f = f"drawtext=text='{guion[:40]}...':fontcolor=white:fontsize=45:fontfile='{f_abs}':x=(w-tw)/2:y=(h-th)/2:borderw=2:bordercolor=black"
            subprocess.run(f'ffmpeg -y -i "{mudo}" -i "{audio}" -vf "{txt_f}" -c:v libx264 -preset fast -t {dur} "{final}"', shell=True)
            
            if os.path.exists(final):
                st.markdown('<div class="info-card">✅ VÍDEO LISTO</div>', unsafe_allow_html=True)
                st.video(final)
