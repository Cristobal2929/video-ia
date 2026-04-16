import streamlit as st
import os, time, subprocess, re, urllib.parse, math
import requests
import tempfile
import concurrent.futures

st.set_page_config(page_title="Fénix Studio V71", layout="centered")

st.markdown("""
<style>
    .stApp { background: #000000; color: #FFFFFF; }
    .pro-title { font-size: 40px; font-weight: 900; color: #00FFD1; text-align: center; margin-bottom: 20px; }
    .time-card { padding: 15px; border-radius: 10px; background: #111827; border: 1px solid #00FFD1; text-align: center; margin-bottom: 20px; color: #00FFD1; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V71 🚀</div>', unsafe_allow_html=True)

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

tema = st.text_input("¿Qué quieres crear hoy?")
if st.button("🚀 INICIAR PROCESO SEGURO"):
    if not tema: st.warning("Escribe un tema")
    else:
        # Usamos un solo contenedor para evitar errores de Node
        info_area = st.empty()
        
        with tempfile.TemporaryDirectory() as tmp:
            with st.status("🛠️ Ejecutando motores de IA...", expanded=True) as status:
                
                guion = generar_guion(tema)
                audio = generar_voz(guion, tmp)
                
                dur = 10.0
                if audio:
                    try:
                        dur = float(subprocess.check_output(f'ffprobe -i "{audio}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
                    except: pass
                
                n_escenas = 4
                t_aprox = int(dur + (n_escenas * 12) + 10)
                
                # Actualizamos el área de info sin borrar nodos antiguos
                info_area.markdown(f'<div class="time-card">⏳ TIEMPO ESTIMADO: {t_aprox} SEG</div>', unsafe_allow_html=True)
                
                bar = st.progress(5)
                
                palabras = guion.split()[:n_escenas]
                tareas = [(i, p, dur/n_escenas, "cinematic", tmp) for i, p in enumerate(palabras)]
                
                clips = []
                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
                    futuros = [ex.submit(procesar_escena, t) for t in tareas]
                    for idx, f in enumerate(concurrent.futures.as_completed(futuros)):
                        res = f.result()
                        if res: clips.append(res)
                        bar.progress(20 + int((idx+1)/n_escenas * 60))
                
                status.write("🎬 Masterizando vídeo...")
                txt_lista = os.path.join(tmp, "l.txt")
                with open(txt_lista, "w") as f:
                    for c in sorted(clips): f.write(f"file '{c}'\n")
                
                v_mudo = os.path.join(tmp, "m.mp4")
                subprocess.run(f'ffmpeg -y -f concat -safe 0 -i "{txt_lista}" -c copy "{v_mudo}"', shell=True)
                
                os.makedirs("output", exist_ok=True)
                final = f"output/v_{int(time.time())}.mp4"
                
                sub = f"drawtext=text='{guion[:30]}...':fontcolor=white:fontsize=45:fontfile='{font_abs}':x=(w-tw)/2:y=(h-th)/2:borderw=3"
                subprocess.run(f'ffmpeg -y -i "{v_mudo}" -i "{audio}" -vf "{sub}" -c:v libx264 -preset fast -t {dur} "{final}"', shell=True)
                
                bar.progress(100)
                info_area.markdown('<div class="time-card">✅ PROCESO COMPLETADO</div>', unsafe_allow_html=True)
                
                st.video(final)
                st.balloons()
