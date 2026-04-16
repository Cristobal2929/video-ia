import streamlit as st
import os, time, subprocess, re, urllib.parse, math
import requests
import tempfile
import concurrent.futures

st.set_page_config(page_title="Fénix Studio V69", layout="centered")

st.markdown("""
<style>
    .stApp { background: #000000; color: #FFFFFF; }
    .pro-title { font-size: 40px; font-weight: 900; color: #00FFD1; text-align: center; margin-bottom: 0; }
    .status-box { padding: 10px; border-radius: 10px; background: #1e293b; border: 1px solid #00FFD1; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V69 🚀</div>', unsafe_allow_html=True)

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
    prompt = f"Guion TikTok 30 palabras sobre {tema}. Solo texto, sin simbolos."
    try:
        r = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}", timeout=15)
        return re.sub(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ ]', '', r.text).strip()
    except: return "Error generando guion"

def generar_voz(texto, tmp):
    mp3 = os.path.join(tmp, "t.mp3")
    # Intentar Edge-TTS
    subprocess.run(f'python -m edge_tts --voice es-MX-JorgeNeural --text "{texto}" --write-media "{mp3}"', shell=True, capture_output=True)
    if os.path.exists(mp3) and os.path.getsize(mp3) > 100: return mp3
    
    # Fallback Silencio (Para evitar error de FFmpeg si falla la voz)
    subprocess.run(f'ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 10 -q:a 9 -acodec libmp3lame "{mp3}"', shell=True)
    return mp3

def procesar_escena(args):
    i, palabra, t, estilo, tmp = args
    img = os.path.join(tmp, f"{i}.jpg")
    vid = os.path.join(tmp, f"{i}.mp4")
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(palabra + ' ' + estilo)}?width=720&height=1280&nologo=true"
    
    try:
        r = requests.get(url, timeout=25)
        with open(img, 'wb') as f: f.write(r.content)
    except:
        # Si falla la imagen, crear un fondo negro para no romper el video
        subprocess.run(f'ffmpeg -f lavfi -i color=c=black:s=720x1280:d=1 -frames:v 1 "{img}"', shell=True)
    
    vf = f"scale=800:1422,zoompan=z='min(zoom+0.001,1.2)':d={int(t*30)}:s=720x1280,format=yuv420p"
    subprocess.run(f'ffmpeg -y -loop 1 -i "{img}" -vf "{vf}" -c:v libx264 -preset ultrafast -t {t} "{vid}"', shell=True)
    return vid

tema = st.text_input("¿De qué trata el vídeo?")
if st.button("🚀 CREAR SIN ERRORES"):
    if not tema: st.warning("Escribe algo")
    else:
        with tempfile.TemporaryDirectory() as tmp:
            with st.status("🏗️ Construyendo vídeo...") as status:
                # PASO 1: GUION Y VOZ
                guion = generar_guion(tema)
                audio = generar_voz(guion, tmp)
                
                # CÁLCULO DE TIEMPO
                dur = float(subprocess.check_output(f'ffprobe -i "{audio}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
                n_escenas = 4
                tiempo_total = int(dur + (n_escenas * 12) + 10)
                
                st.info(f"⏱️ **Tiempo estimado:** {tiempo_total} segundos")
                bar = st.progress(0)
                
                # PASO 2: ESCENAS
                status.write("🎨 Generando imágenes y animación...")
                palabras = guion.split()[:n_escenas]
                tareas = [(i, p, dur/n_escenas, "cinematic", tmp) for i, p in enumerate(palabras)]
                
                clips = []
                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
                    futuros = [ex.submit(procesar_escena, t) for t in tareas]
                    for idx, f in enumerate(concurrent.futures.as_completed(futuros)):
                        clips.append(f.result())
                        bar.progress(int((idx+1)/n_escenas * 70))
                
                # PASO 3: ENSAMBLAJE
                status.write("🎬 Uniendo piezas...")
                txt_lista = os.path.join(tmp, "l.txt")
                with open(txt_lista, "w") as f:
                    for c in sorted(clips): f.write(f"file '{c}'\n")
                
                v_mudo = os.path.join(tmp, "m.mp4")
                subprocess.run(f'ffmpeg -y -f concat -safe 0 -i "{txt_lista}" -c copy "{v_mudo}"', shell=True)
                
                os.makedirs("output", exist_ok=True)
                final = f"output/v_{int(time.time())}.mp4"
                
                # Subtítulos blindados
                sub = f"drawtext=text='{guion[:30]}...':fontcolor=white:fontsize=40:fontfile='{font_abs}':x=(w-tw)/2:y=(h-th)/2:borderw=2:bordercolor=black"
                subprocess.run(f'ffmpeg -y -i "{v_mudo}" -i "{audio}" -vf "{sub}" -c:v libx264 -preset fast -t {dur} "{final}"', shell=True)
                
                bar.progress(100)
                st.video(final)
                st.success("✨ Vídeo completado con éxito")
