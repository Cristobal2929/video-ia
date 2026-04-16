import streamlit as st
import os, time, subprocess, re, urllib.parse
import requests
import tempfile
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V74", layout="centered")

# Evita que la pantalla del móvil se apague
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
    .warning-card { padding: 15px; border-radius: 10px; background: #111827; border: 2px solid #FFD700; text-align: center; color: #FFD700; font-weight: bold; font-size: 14px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V74 🦅</div>', unsafe_allow_html=True)

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

def procesar_escena_segura(i, palabra, t, tmp, status):
    status.write(f"🖼️ Generando imagen {i+1} y animando... (Esto lleva su tiempo)")
    img = os.path.join(tmp, f"{i}.jpg")
    vid = os.path.join(tmp, f"{i}.mp4")
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(palabra + ' cinematic 4k')}?width=720&height=1280&nologo=true"
    try:
        r = requests.get(url, timeout=15)
        with open(img, 'wb') as f: f.write(r.content)
        vf = "scale=720:1280,format=yuv420p" 
        # Hilos limitados a 1 para no saturar el servidor gratuito
        subprocess.run(f'ffmpeg -y -loop 1 -i "{img}" -vf "{vf}" -c:v libx264 -preset ultrafast -threads 1 -t {t} "{vid}"', shell=True)
        return vid
    except: return None

tema = st.text_input("Tema del vídeo:")
if st.button("🚀 CREAR (MODO ESTABLE)"):
    if not tema: st.warning("Escribe un tema")
    else:
        st.markdown('<div class="warning-card">⚠️ AVISO HONESTO: Estás usando un servidor gratuito. Renderizar vídeo exige mucha potencia. Tardará entre 2 y 4 minutos. Por favor, ten paciencia y NO cierres Chrome.</div>', unsafe_allow_html=True)
        
        with tempfile.TemporaryDirectory() as tmp:
            with st.status("⚙️ Iniciando proceso paso a paso...", expanded=True) as status:
                
                status.write("🧠 1/4: Pensando el guion...")
                guion = generar_guion(tema)
                
                status.write("🎙️ 2/4: Grabando al locutor...")
                audio = generar_voz(guion, tmp)
                
                dur = 8.0
                if audio:
                    try:
                        dur = float(subprocess.check_output(f'ffprobe -i "{audio}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
                    except: pass
                
                n = 3
                palabras = guion.split()[:n]
                
                status.write(f"🎨 3/4: Creando {n} escenas (El paso más lento)...")
                clips = []
                
                # Procesamiento SECUENCIAL para que no se cuelgue la RAM
                for i, p in enumerate(palabras):
                    vid = procesar_escena_segura(i, p, dur/n, tmp, status)
                    if vid: clips.append(vid)
                
                status.write("🎬 4/4: Exportando máster final...")
                lista = os.path.join(tmp, "l.txt")
                with open(lista, "w") as f:
                    for c in clips: f.write(f"file '{c}'\n")
                
                v_mudo = os.path.join(tmp, "m.mp4")
                subprocess.run(f'ffmpeg -y -f concat -safe 0 -i "{lista}" -c copy "{v_mudo}"', shell=True)
                
                os.makedirs("output", exist_ok=True)
                final = f"output/v_{int(time.time())}.mp4"
                
                sub = f"drawtext=text='{guion[:30]}...':fontcolor=white:fontsize=45:fontfile='{font_abs}':x=(w-tw)/2:y=(h-th)/2:borderw=2"
                subprocess.run(f'ffmpeg -y -i "{v_mudo}" -i "{audio}" -vf "{sub}" -c:v libx264 -preset ultrafast -threads 1 -t {dur} "{final}"', shell=True)
                
                st.video(final)
                st.success("✅ ¡Vídeo terminado! Gracias por la paciencia.")
