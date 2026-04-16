import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil
import requests
import base64
import concurrent.futures
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V79", layout="centered")

components.html("""
<script>
if ('wakeLock' in navigator) {
  let wakeLock = null;
  const requestWakeLock = async () => {
    try { wakeLock = await navigator.wakeLock.request('screen'); } catch (err) {}
  };
  requestWakeLock();
}
</script>
""", height=0)

st.markdown("""
<style>
    .stApp { background: #000000; color: #FFFFFF; }
    .pro-title { font-size: 40px; font-weight: 900; color: #00FFD1; text-align: center; }
    .speed-card { padding: 15px; border-radius: 10px; background: #1e3a8a; border: 2px solid #3b82f6; text-align: center; color: #60a5fa; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V79 🚀</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center; color:#94A3B8; margin-bottom:20px;">Twin-Turbo Base64 Activado</div>', unsafe_allow_html=True)

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
        r = requests.get(url, timeout=12)
        return re.sub(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ ]', '', r.text).strip()
    except: return "El secreto del exito esta en no rendirse nunca jamas"

def preparar_entorno():
    if os.path.exists("taller"): shutil.rmtree("taller")
    os.makedirs("taller", exist_ok=True)

# Nueva función para descargar rápido en paralelo
def descargar_imagen(args):
    i, palabra = args
    img = f"taller/img_{i}.jpg"
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(palabra + ' cinematic vertical dark')}?width=540&height=960&nologo=true"
    try:
        r = requests.get(url, timeout=20)
        with open(img, 'wb') as f: f.write(r.content)
        return img
    except: return None

tema = st.text_input("Tema del vídeo:")
if st.button("⚡ CREAR RÁPIDO Y SEGURO"):
    if not tema: st.warning("Escribe un tema")
    else:
        preparar_entorno()
        
        with st.status("🚀 Procesando a máxima velocidad...", expanded=True) as status:
            
            status.write("🧠 1/4: Guion...")
            guion = generar_guion(tema)
            
            status.write("🎙️ 2/4: Audio...")
            audio = "taller/audio.mp3"
            subprocess.run(f'python -m edge_tts --voice es-MX-JorgeNeural --text "{guion}" --write-media "{audio}"', shell=True)
            if not os.path.exists(audio) or os.path.getsize(audio) < 100:
                subprocess.run(f'ffmpeg -y -f lavfi -i anullsrc=r=44100:cl=mono -t 10 -acodec libmp3lame "{audio}"', shell=True)
            
            dur = 8.0
            try:
                dur = float(subprocess.check_output(f'ffprobe -i "{audio}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
            except: pass
            
            n_escenas = 3
            palabras = guion.split()[:n_escenas]
            
            # ACELERADOR 1: Descarga en paralelo
            status.write("📥 3/4: Descargando imágenes simultáneamente...")
            tareas_img = [(i, p) for i, p in enumerate(palabras)]
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
                imgs_descargadas = list(ex.map(descargar_imagen, tareas_img))
            
            # ACELERADOR 2: Animación secuencial con 2 núcleos
            status.write(f"🎨 Animando con efecto cinemático (Doble Núcleo)...")
            clips = []
            dur_frames = int((dur/n_escenas) * 20)
            
            for i, img in enumerate(imgs_descargadas):
                if not img or not os.path.exists(img): continue
                vid = f"taller/vid_{i}.mp4"
                vf = f"scale=600:1066,zoompan=z='min(zoom+0.001,1.1)':d={dur_frames}:s=540x960:fps=20,format=yuv420p" 
                subprocess.run(f'ffmpeg -y -loop 1 -i "{img}" -vf "{vf}" -c:v libx264 -preset ultrafast -threads 2 -t {dur/n_escenas} "{vid}"', shell=True)
                if os.path.exists(vid): clips.append(vid)
            
            if not clips: st.error("Error al descargar imágenes."); st.stop()
            
            status.write("🎬 4/4: Exportación Final Rápida...")
            lista_txt = "taller/lista.txt"
            with open(lista_txt, "w") as f:
                for c in clips: f.write(f"file '../{c}'\n")
            
            v_mudo = "taller/mudo.mp4"
            subprocess.run(f'ffmpeg -y -f concat -safe 0 -i "{lista_txt}" -c copy -threads 2 "{v_mudo}"', shell=True)
            
            final_path = "taller/master.mp4"
            sub_f = f"drawtext=text='{guion[:30]}...':fontcolor=white:fontsize=35:fontfile='{font_abs}':x=(w-tw)/2:y=(h-th)/2:borderw=2"
            # Renderizado final con 2 hilos para mayor velocidad
            subprocess.run(f'ffmpeg -y -i "{v_mudo}" -i "{audio}" -vf "{sub_f}" -c:v libx264 -preset ultrafast -threads 2 -t {dur} "{final_path}"', shell=True)
            
            if os.path.exists(final_path) and os.path.getsize(final_path) > 1000:
                with open(final_path, "rb") as f:
                    video_bytes = f.read()
                
                b64_video = base64.b64encode(video_bytes).decode()
                video_html = f'''
                    <video width="100%" controls autoplay loop style="border: 2px solid #00FFD1; border-radius: 10px;">
                        <source src="data:video/mp4;base64,{b64_video}" type="video/mp4">
                        Tu navegador no soporta vídeos HTML5.
                    </video>
                '''
                
                status.update(label="✅ Proceso completado en tiempo récord", state="complete")
                st.markdown('<div class="speed-card">⚡ ¡AQUÍ TIENES TU VÍDEO!</div><br>', unsafe_allow_html=True)
                st.markdown(video_html, unsafe_allow_html=True)
            else:
                st.error("Error al exportar. Intenta de nuevo.")
