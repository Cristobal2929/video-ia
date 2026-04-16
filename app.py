import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil, math, random, gc
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V102", layout="centered")

st.markdown("""
<style>
    .stApp { background: #000000; color: #FFFFFF; }
    .pro-title { font-size: 40px; font-weight: 900; background: -webkit-linear-gradient(45deg, #00FFD1, #FFD700); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; text-transform: uppercase;}
    .msg { color: #00FFD1; font-family: monospace; font-size: 14px; margin-bottom: 5px; border-left: 3px solid #FFD700; padding-left: 10px; }
    .info-card { padding: 15px; border-radius: 12px; background: #0f172a; border: 1px solid #00FFD1; text-align: center; color: #00FFD1; margin-top: 20px;}
    .stButton>button { width: 100%; background: linear-gradient(45deg, #00FFD1, #0088ff); color: white; border: none; font-weight: 900; height: 50px; border-radius: 10px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V102 ⚡</div>', unsafe_allow_html=True)

@st.cache_resource
def get_font():
    p = "Arial_Pro.ttf"
    if not os.path.exists(p):
        r = requests.get("https://github.com/matomo-org/travis-scripts/raw/master/fonts/Arial.ttf")
        with open(p, "wb") as f: f.write(r.content)
    return os.path.abspath(p)

f_abs = get_font()

def preparar():
    if os.path.exists("taller"): shutil.rmtree("taller")
    os.makedirs("taller", exist_ok=True)
    subprocess.run("pkill ffmpeg", shell=True)

tema = st.text_input("🧠 Tema del vídeo:", placeholder="Ej: Superación personal")
n_escenas = st.selectbox("📸 Escenas:", [4, 6, 8], index=1)

if st.button("🚀 LANZAR FUEGO RÁPIDO (V102)"):
    if not tema: st.error("Escribe un tema")
    else:
        preparar()
        log = st.container()
        
        with log:
            st.write("📝 Redactando guion...")
            guion = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote('TikTok script '+tema+'. Solo texto, 60 palabras.')}").text
            guion = re.sub(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ.,! ]', '', guion).strip()
            
            st.write("🎙️ Grabando voz...")
            audio = "taller/a.mp3"
            subprocess.run(f'edge-tts --voice es-MX-JorgeNeural --text "{guion}" --write-media "{audio}"', shell=True)
            
            dur = 15.0
            try: dur = float(subprocess.check_output(f'ffprobe -i "{audio}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
            except: pass
            
            t_clip = dur / n_escenas
            clips = []
            words = guion.split()

            for i in range(n_escenas):
                kw = words[min(i*6, len(words)-1)]
                st.markdown(f'<div class="msg">📸 Escena {i+1}: IA creando "{kw.upper()}"...</div>', unsafe_allow_html=True)
                
                img = f"taller/i_{i}.jpg"
                vid = f"taller/v_{i}.mp4"
                
                # MOTOR V102: Rapidez absoluta
                url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(kw+' luxury cinematic')}?width=720&height=1280&nologo=true&seed={random.randint(1,999)}"
                
                try:
                    time.sleep(2) # Pausa reducida para no cansar al servidor
                    r = requests.get(url, timeout=15)
                    with open(img, 'wb') as f: f.write(r.content)
                    
                    # Zoom lateral ultra-rápido (V58 style)
                    vf = f"scale=1280:2275,zoompan=z='1.0+0.001*on':x='iw/4-(iw/4/d)*on':s=720x1280:fps=24,format=yuv420p"
                    subprocess.run(f'ffmpeg -y -loop 1 -i "{img}" -vf "{vf}" -t {t_clip} -c:v libx264 -preset ultrafast "{vid}"', shell=True)
                    if os.path.exists(vid): clips.append(f"v_{i}.mp4")
                except: pass
                
                if os.path.exists(img): os.remove(img)
                gc.collect()

            st.write("🎬 Montaje y Subtítulos V58...")
            with open("taller/l.txt", "w") as f:
                for c in clips: f.write(f"file '{c}'\n")
            
            mudo = "taller/m.mp4"
            subprocess.run(f'ffmpeg -y -f concat -safe 0 -i taller/l.txt -c copy "{mudo}"', shell=True)
            
            # Subtítulos Doble Línea V58 (Blindados)
            palabras_sub = guion.upper().split()
            chunks = [palabras_sub[j:j+2] for j in range(0, len(palabras_sub), 2)]
            t_ch = dur / max(len(chunks), 1)
            subs = []
            for j, p in enumerate(chunks):
                ts, te = j*t_ch, j*t_ch + t_ch
                if len(p) == 2:
                    subs.append(f"drawtext=text='{p[0]}':fontcolor=yellow:fontsize=65:fontfile='{f_abs}':borderw=4:x=(w-tw)/2:y=(h-th)/2-40:enable='between(t,{ts},{te})'")
                    subs.append(f"drawtext=text='{p[1]}':fontcolor=yellow:fontsize=65:fontfile='{f_abs}':borderw=4:x=(w-tw)/2:y=(h-th)/2+40:enable='between(t,{ts},{te})'")
                else:
                    subs.append(f"drawtext=text='{p[0]}':fontcolor=yellow:fontsize=65:fontfile='{f_abs}':borderw=4:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{ts},{te})'")
            
            with open("taller/s.txt", "w") as f: f.write(",\n".join(subs))
            
            final = "taller/master.mp4"
            subprocess.run(f'ffmpeg -y -i "{mudo}" -i "{audio}" -filter_complex_script taller/s.txt -c:v libx264 -preset ultrafast -t {dur} "{final}"', shell=True)
            
            if os.path.exists(final):
                st.markdown('<div class="info-card">🏆 VÍDEO V102 COMPLETADO</div>', unsafe_allow_html=True)
                with open(final, "rb") as f: st.video(f.read())
