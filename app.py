import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil, math, random
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V99", layout="centered")

components.html("""<script>if('wakeLock' in navigator){navigator.wakeLock.request('screen');}</script>""", height=0)

st.markdown("""
<style>
    .stApp { background: #000000; color: #FFFFFF; }
    .pro-title { font-size: 40px; font-weight: 900; background: -webkit-linear-gradient(45deg, #00FFD1, #FFD700); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; text-transform: uppercase;}
    .msg { color: #00FFD1; font-family: monospace; font-size: 14px; margin-bottom: 5px; border-left: 3px solid #FFD700; padding-left: 10px; }
    .info-card { padding: 15px; border-radius: 10px; background: #0f172a; border: 1px solid #00FFD1; text-align: center; color: #00FFD1; margin-top: 20px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V99 🎥</div>', unsafe_allow_html=True)

@st.cache_resource
def get_f():
    p = "font.ttf"
    if not os.path.exists(p):
        r = requests.get("https://github.com/matomo-org/travis-scripts/raw/master/fonts/Arial.ttf")
        with open(p, "wb") as f: f.write(r.content)
    return os.path.abspath(p)

f_abs = get_f()

def preparar():
    if os.path.exists("taller"): shutil.rmtree("taller")
    os.makedirs("taller", exist_ok=True)

tema = st.text_input("🧠 Tema del vídeo:", placeholder="Ej: La mentalidad del éxito")
color_sub = st.selectbox("🎨 Color Subtítulos", ["yellow", "white", "#00FFD1"])
n_escenas = st.select_slider("📸 Cantidad de escenas:", options=[4, 8, 12], value=8)

if st.button("🚀 CREAR VÍDEO (MOTOR V99)"):
    if not tema: st.error("Escribe un tema")
    else:
        preparar()
        log = st.container()
        
        with log:
            st.markdown('<div class="msg">📝 Redactando guion único...</div>', unsafe_allow_html=True)
            guion = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote('Escribe un guion de TikTok sobre '+tema+'. Solo texto, 65 palabras.')}").text
            guion = re.sub(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ.,! ]', '', guion).strip()
            
            st.markdown('<div class="msg">🎙️ Grabando voz profesional...</div>', unsafe_allow_html=True)
            audio = "taller/audio.mp3"
            subprocess.run(f'edge-tts --voice es-MX-JorgeNeural --text "{guion}" --write-media "{audio}"', shell=True)
            
            dur = 15.0
            try: dur = float(subprocess.check_output(f'ffprobe -i "{audio}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
            except: pass
            
            t_escena = dur / n_escenas
            clips = []
            words = guion.split()

            for i in range(n_escenas):
                st.markdown(f'<div class="msg">🎬 Procesando Escena {i+1}: IA generando imagen única...</div>', unsafe_allow_html=True)
                kw = words[min(i*5, len(words)-1)]
                img = f"taller/i_{i}.jpg"
                vid = f"taller/v_{i}.mp4"
                
                # MOTOR V99: Reintentos y Prompt de Lujo
                exito = False
                for intento in range(3):
                    seed = random.randint(1, 999999)
                    prompt = f"{kw} {tema}, cinematic, hyperrealistic, 8k, luxury style, sharp focus"
                    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=720&height=1280&nologo=true&seed={seed}"
                    try:
                        r = requests.get(url, timeout=30)
                        if r.status_code == 200:
                            with open(img, 'wb') as f: f.write(r.content)
                            exito = True
                            break
                    except: time.sleep(2)

                if exito:
                    z = random.choice(["1.0+0.001*on", "1.2-0.001*on"])
                    vf = f"scale=800:1422,zoompan=z='{z}':d={int(t_escena*24)}:s=720x1280:fps=24,format=yuv420p"
                    subprocess.run(f'ffmpeg -y -loop 1 -i "{img}" -vf "{vf}" -t {t_escena} -c:v libx264 -preset ultrafast -crf 24 "{vid}"', shell=True)
                    if os.path.exists(vid): clips.append(f"v_{i}.mp4")
                
                if os.path.exists(img): os.remove(img)

            st.markdown('<div class="msg">🎞️ Montaje final y subtítulos...</div>', unsafe_allow_html=True)
            with open("taller/lista.txt", "w") as f:
                for c in clips: f.write(f"file '{c}'\n")
            
            mudo = "taller/mudo.mp4"
            subprocess.run(f'ffmpeg -y -f concat -safe 0 -i taller/lista.txt -c copy "{mudo}"', shell=True)
            
            master = "taller/master.mp4"
            # Subtítulos Estilo Hormozi (V58)
            sub_f = f"drawtext=text='{guion[:35].upper()}...':fontcolor={color_sub}:fontsize=60:fontfile='{f_abs}':x=(w-tw)/2:y=(h-th)/2:borderw=4:bordercolor=black"
            subprocess.run(f'ffmpeg -y -i "{mudo}" -i "{audio}" -vf "{sub_f}" -c:v libx264 -preset fast -t {dur} "{master}"', shell=True)
            
            if os.path.exists(master):
                st.markdown('<div class="info-card">✅ VÍDEO V99 COMPLETADO</div>', unsafe_allow_html=True)
                with open(master, 'rb') as f: st.video(f.read())
                st.balloons()
