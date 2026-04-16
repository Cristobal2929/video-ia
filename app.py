import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil
import requests
import base64
import gc
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V83", layout="centered")

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
    .stSelectbox div[data-baseweb="select"] { background-color: #1e293b; color: white; }
    .info-card { padding: 10px; border-radius: 8px; background: #0f172a; border: 1px solid #00FFD1; text-align: center; color: #00FFD1; margin-bottom: 15px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V83 🎥</div>', unsafe_allow_html=True)

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

def generar_guion(tema, longitud_palabras):
    prompt = f"Guion TikTok {longitud_palabras} palabras sobre {tema}. Solo texto, sin emojis."
    url = f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}"
    try:
        r = requests.get(url, timeout=15)
        return re.sub(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ.,! ]', '', r.text).strip()
    except: return "El exito depende de tu esfuerzo diario. No te rindas nunca."

def preparar_entorno():
    if os.path.exists("taller"): shutil.rmtree("taller")
    os.makedirs("taller", exist_ok=True)

tema = st.text_input("Tema del vídeo:")
duracion_opcion = st.selectbox("Duración del Vídeo:", [
    "Corto (~15 segundos)", 
    "Medio (~30 segundos)", 
    "Largo (~60 segundos)"
])

if st.button("🚀 CREAR VÍDEO A MEDIDA"):
    if not tema: st.warning("Escribe un tema")
    else:
        preparar_entorno()
        
        # Ajustamos el tamaño del guion según la opción elegida
        if "15" in duracion_opcion:
            palabras_target = 35
            n_escenas = 4
        elif "30" in duracion_opcion:
            palabras_target = 70
            n_escenas = 8
        else:
            palabras_target = 130
            n_escenas = 15
            
        with st.status(f"🎬 Iniciando producción ({duracion_opcion})...", expanded=True) as status:
            
            status.write("🧠 Redactando guion a medida...")
            guion = generar_guion(tema, palabras_target)
            
            status.write("🎙️ Grabando voz...")
            audio = "taller/audio.mp3"
            subprocess.run(f'python -m edge_tts --voice es-MX-JorgeNeural --rate=+10% --text "{guion}" --write-media "{audio}"', shell=True)
            if not os.path.exists(audio) or os.path.getsize(audio) < 100:
                subprocess.run(f'ffmpeg -y -f lavfi -i anullsrc=r=44100:cl=mono -t 10 -acodec libmp3lame "{audio}"', shell=True)
            
            dur = 10.0
            try:
                dur = float(subprocess.check_output(f'ffprobe -i "{audio}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
            except: pass
            
            # Repartimos el tiempo total entre las escenas
            t_por_escena = dur / n_escenas
            dur_frames = int(t_por_escena * 15) # 15 FPS para no saturar
            
            status.write(f"🎨 Creando {n_escenas} escenas secuenciales (Maratón)...")
            clips = []
            
            # Extraemos palabras clave para buscar las imágenes
            palabras_limpias = [p for p in guion.split() if len(p) > 3]
            if len(palabras_limpias) < n_escenas: palabras_limpias = guion.split() * n_escenas
            
            # PROCESAMIENTO SECUENCIAL CON LIMPIEZA DE MEMORIA
            for i in range(n_escenas):
                palabra = palabras_limpias[i]
                status.write(f"⏳ Escena {i+1}/{n_escenas}...")
                
                img = f"taller/img_{i}.jpg"
                vid = f"taller/vid_{i}.mp4"
                url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(palabra + ' cinematic vertical')}?width=480&height=854&nologo=true"
                
                try:
                    r = requests.get(url, timeout=15)
                    with open(img, 'wb') as f: f.write(r.content)
                    
                    # Zoompan a 480p, 15fps. Un solo hilo para no reventar la RAM.
                    vf = f"scale=500:888,zoompan=z='min(zoom+0.001,1.1)':d={dur_frames}:s=480x854:fps=15,format=yuv420p" 
                    subprocess.run(f'ffmpeg -y -loop 1 -i "{img}" -vf "{vf}" -c:v libx264 -preset ultrafast -crf 28 -threads 1 -t {t_por_escena} "{vid}"', shell=True)
                    
                    if os.path.exists(vid): 
                        clips.append(vid)
                    
                    # RESPIRACIÓN DE MEMORIA: Borramos la imagen inmediatamente
                    if os.path.exists(img): os.remove(img)
                except Exception as e:
                    pass
            
            status.write("🎬 Uniendo las piezas del vídeo...")
            lista_txt = "taller/lista.txt"
            with open(lista_txt, "w") as f:
                for c in clips: f.write(f"file '../{c}'\n")
            
            v_mudo = "taller/mudo.mp4"
            subprocess.run(f'ffmpeg -y -f concat -safe 0 -i "{lista_txt}" -c copy "{v_mudo}"', shell=True)
            
            status.write("✨ Añadiendo subtítulos y comprimiendo...")
            final_path = "taller/master.mp4"
            sub_f = f"drawtext=text='{guion[:25]}...':fontcolor=white:fontsize=28:fontfile='{font_abs}':x=(w-tw)/2:y=(h-th)/2:borderw=1.5"
            
            # Compresión final fuerte para que Base64 no bloquee el navegador en vídeos de 1 minuto
            subprocess.run(f'ffmpeg -y -i "{v_mudo}" -i "{audio}" -vf "{sub_f}" -c:v libx264 -preset ultrafast -crf 30 -threads 1 -t {dur} "{final_path}"', shell=True)
            
            if os.path.exists(final_path) and os.path.getsize(final_path) > 1000:
                with open(final_path, "rb") as f:
                    video_bytes = f.read()
                
                b64_video = base64.b64encode(video_bytes).decode()
                video_html = f'''
                    <video width="100%" controls autoplay style="border: 2px solid #00FFD1; border-radius: 10px;">
                        <source src="data:video/mp4;base64,{b64_video}" type="video/mp4">
                    </video>
                '''
                
                status.update(label="✅ ¡Proceso 100% Completado!", state="complete")
                st.markdown('<div class="info-card">🎉 VÍDEO EXPORTADO. Haz clic derecho o mantén pulsado para descargar.</div>', unsafe_allow_html=True)
                st.markdown(video_html, unsafe_allow_html=True)
            else:
                st.error("Error al exportar. El vídeo era demasiado largo para la RAM actual.")
