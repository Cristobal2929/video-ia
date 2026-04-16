import streamlit as st
import os, time, subprocess, re, urllib.parse, math
import requests
import tempfile
import concurrent.futures

st.set_page_config(page_title="Fénix Studio V70", layout="centered")

st.markdown("""
<style>
    .stApp { background: #000000; color: #FFFFFF; }
    .pro-title { font-size: 40px; font-weight: 900; color: #00FFD1; text-align: center; margin-bottom: 10px; }
    .time-card { padding: 20px; border-radius: 15px; background: #111827; border: 2px solid #00FFD1; text-align: center; margin: 15px 0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V70 🚀</div>', unsafe_allow_html=True)

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
    prompt = f"Guion TikTok 30 palabras sobre {tema}. Solo texto plano."
    try:
        r = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}", timeout=15)
        return re.sub(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ ]', '', r.text).strip()
    except: return "Error en la conexion"

def generar_voz(texto, tmp):
    mp3 = os.path.join(tmp, "t.mp3")
    subprocess.run(f'python -m edge_tts --voice es-MX-JorgeNeural --text "{texto}" --write-media "{mp3}"', shell=True, capture_output=True)
    return mp3 if os.path.exists(mp3) else None

def procesar_escena(args):
    i, palabra, t, estilo, tmp = args
    img = os.path.join(tmp, f"{i}.jpg")
    vid = os.path.join(tmp, f"{i}.mp4")
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(palabra + ' ' + estilo)}?width=720&height=1280&nologo=true"
    try:
        r = requests.get(url, timeout=25)
        with open(img, 'wb') as f: f.write(r.content)
        vf = f"scale=800:1422,zoompan=z='min(zoom+0.001,1.2)':d={int(t*30)}:s=720x1280,format=yuv420p"
        subprocess.run(f'ffmpeg -y -loop 1 -i "{img}" -vf "{vf}" -c:v libx264 -preset ultrafast -t {t} "{vid}"', shell=True)
        return vid
    except: return None

tema = st.text_input("¿Qué vídeo quieres hoy?")
if st.button("🚀 CREAR VÍDEO (V70)"):
    if not tema: st.warning("Escribe un tema primero")
    else:
        # PANTALLA DE CARGA INICIAL
        tiempo_container = st.empty()
        with tiempo_container.container():
            st.markdown('<div class="time-card">⏳ <b>Calculando presupuesto de tiempo...</b></div>', unsafe_allow_html=True)
        
        with tempfile.TemporaryDirectory() as tmp:
            with st.status("🛠️ Construyendo...", expanded=True) as status:
                
                # ESTIMACIÓN VISIBLE
                guion = generar_guion(tema)
                audio = generar_voz(guion, tmp)
                
                dur = 10.0
                if audio:
                    try:
                        dur = float(subprocess.check_output(f'ffprobe -i "{audio}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
                    except: pass
                
                n_escenas = 4
                t_aprox = int(dur + (n_escenas * 10) + 15)
                
                # AQUÍ SE MUESTRA EL TIEMPO CLARAMENTE
                tiempo_container.markdown(f'<div class="time-card">⏳ <b>TIEMPO RESTANTE:</b> ~{t_aprox} segundos<br><small>No cierres la ventana, la IA está trabajando para ti.</small></div>', unsafe_allow_html=True)
                
                bar = st.progress(10)
                
                # PROCESO DE ESCENAS
                status.write("🎨 Pintando imágenes únicas...")
                palabras = guion.split()[:n_escenas]
                tareas = [(i, p, dur/n_escenas, "cinematic", tmp) for i, p in enumerate(palabras)]
                
                clips = []
                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
                    futuros = [ex.submit(procesar_escena, t) for t in tareas]
                    for idx, f in enumerate(concurrent.futures.as_completed(futuros)):
                        res = f.result()
                        if res: clips.append(res)
                        bar.progress(20 + int((idx+1)/n_escenas * 60))
                
                # ENSAMBLAJE
                status.write("🎬 Masterizando vídeo final...")
                txt_lista = os.path.join(tmp, "l.txt")
                with open(txt_lista, "w") as f:
                    for c in sorted(clips): f.write(f"file '{c}'\n")
                
                v_mudo = os.path.join(tmp, "m.mp4")
                subprocess.run(f'ffmpeg -y -f concat -safe 0 -i "{txt_lista}" -c copy "{v_mudo}"', shell=True)
                
                os.makedirs("output", exist_ok=True)
                final = f"output/v_{int(time.time())}.mp4"
                
                sub = f"drawtext=text='{guion[:35]}...':fontcolor=white:fontsize=45:fontfile='{font_abs}':x=(w-tw)/2:y=(h-th)/2:borderw=3:bordercolor=black"
                subprocess.run(f'ffmpeg -y -i "{v_mudo}" -i "{audio}" -vf "{sub}" -c:v libx264 -preset fast -t {dur} "{final}"', shell=True)
                
                tiempo_container.empty() # Borramos el contador al terminar
                st.video(final)
                st.success("🔥 ¡VÍDEO COMPLETADO!")
                st.balloons()
