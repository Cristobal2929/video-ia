import streamlit as st
import os, time, subprocess, re, urllib.parse, math
import requests
import tempfile
import concurrent.futures

st.set_page_config(page_title="Fénix Studio V72", layout="centered")

st.markdown("""
<style>
    .stApp { background: #000000; color: #FFFFFF; }
    .pro-title { font-size: 40px; font-weight: 900; color: #00FFD1; text-align: center; }
    .time-card { padding: 15px; border-radius: 10px; background: #111827; border: 2px solid #FF0055; text-align: center; color: #FF0055; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V72 ⚡</div>', unsafe_allow_html=True)

@st.cache_resource
def descargar_fuente():
    font_path = "Arial_Pro.ttf"
    if not os.path.exists(font_path):
        try:
            r = requests.get("https://github.com/matomo-org/travis-scripts/raw/master/fonts/Arial.ttf", timeout=10)
            with open(font_path, "wb") as f: f.write(r.content)
        except: pass
    return os.path.abspath(font_path).replace('\\', '/')

font_abs = descargar_fuente()

def generar_guion(tema):
    prompt = f"Guion TikTok 25 palabras sobre {tema}. Solo texto plano."
    url = f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}"
    try:
        r = requests.get(url, timeout=10)
        return re.sub(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ ]', '', r.text).strip()
    except: return "Error conexion"

def generar_voz(texto, tmp):
    mp3 = os.path.join(tmp, "t.mp3")
    subprocess.run(f'python -m edge_tts --voice es-MX-JorgeNeural --text "{texto}" --write-media "{mp3}"', shell=True, capture_output=True)
    return mp3 if os.path.exists(mp3) else None

def procesar_escena_turbo(args):
    i, palabra, t, tmp = args
    img = os.path.join(tmp, f"{i}.jpg")
    vid = os.path.join(tmp, f"{i}.mp4")
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(palabra + ' cinematic 4k')}?width=720&height=1280&nologo=true"
    try:
        r = requests.get(url, timeout=15)
        with open(img, 'wb') as f: f.write(r.content)
        # ACELERACIÓN FFmpeg: preset ultrafast y threads auto
        vf = f"scale=720:1280,format=yuv420p" 
        subprocess.run(f'ffmpeg -y -loop 1 -i "{img}" -vf "{vf}" -c:v libx264 -preset ultrafast -threads 0 -t {t} "{vid}"', shell=True)
        return vid
    except: return None

tema = st.text_input("Tema del vídeo:")
if st.button("🚀 GENERACIÓN TURBO"):
    if not tema: st.warning("Escribe un tema")
    else:
        timer_area = st.empty()
        with tempfile.TemporaryDirectory() as tmp:
            with st.status("⚡ Motor Turbo activado...", expanded=True) as status:
                
                guion = generar_guion(tema)
                audio = generar_voz(guion, tmp)
                
                dur = 8.0
                if audio:
                    try:
                        dur = float(subprocess.check_output(f'ffprobe -i "{audio}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
                    except: pass
                
                # ESTIMACIÓN HONESTA (V72)
                t_aprox = int(dur + 35) 
                timer_area.markdown(f'<div class="time-card">⌛ TIEMPO REAL ESTIMADO: {t_aprox} SEG</div>', unsafe_allow_html=True)
                
                n = 3 # Reducimos a 3 escenas para máxima velocidad sin perder calidad
                palabras = guion.split()[:n]
                tareas = [(i, p, dur/n, tmp) for i, p in enumerate(palabras)]
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
                    clips = [c for c in list(ex.map(procesar_escena_turbo, tareas)) if c]
                
                status.write("🎬 Ensamblaje rápido...")
                lista = os.path.join(tmp, "l.txt")
                with open(lista, "w") as f:
                    for c in clips: f.write(f"file '{c}'\n")
                
                v_mudo = os.path.join(tmp, "m.mp4")
                subprocess.run(f'ffmpeg -y -f concat -safe 0 -i "{lista}" -c copy "{v_mudo}"', shell=True)
                
                os.makedirs("output", exist_ok=True)
                final = f"output/v_{int(time.time())}.mp4"
                
                # Subtítulos rápidos
                sub = f"drawtext=text='{guion[:30]}...':fontcolor=white:fontsize=45:fontfile='{font_abs}':x=(w-tw)/2:y=(h-th)/2:borderw=2"
                subprocess.run(f'ffmpeg -y -i "{v_mudo}" -i "{audio}" -vf "{sub}" -c:v libx264 -preset ultrafast -t {dur} "{final}"', shell=True)
                
                timer_area.empty()
                st.video(final)
                st.success("⚡ ¡Vídeo generado en tiempo récord!")
