import streamlit as st
import os, time, subprocess, re, urllib.parse
import requests
import tempfile
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V77", layout="centered")

# Mantiene la pantalla activa
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
    .ram-shield { padding: 15px; border-radius: 10px; background: #064e3b; border: 2px solid #00FFD1; text-align: center; color: #00FFD1; font-weight: bold; font-size: 14px; margin-bottom: 20px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V77 🛡️</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center; color:#94A3B8; margin-bottom:20px;">Modo Blindaje de RAM Activado</div>', unsafe_allow_html=True)

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
    except: return "Cinco consejos de negocios para empezar hoy mismo"

def generar_voz_paso_a_paso(texto, tmp):
    mp3 = os.path.join(tmp, "t.mp3")
    # Limpiamos memoria antes de llamar al subproceso
    subprocess.run(f'python -m edge_tts --voice es-MX-JorgeNeural --text "{texto}" --write-media "{mp3}"', shell=True, capture_output=True)
    if os.path.exists(mp3) and os.path.getsize(mp3) > 100:
        return mp3
    # Fallback silencioso
    subprocess.run(f'ffmpeg -y -f lavfi -i anullsrc=r=44100:cl=mono -t 10 -acodec libmp3lame "{mp3}"', shell=True)
    return mp3

def animar_escena_individual(i, palabra, t, estilo, tmp, status):
    status.write(f"⏳ **Paso 3.{i+1}:** Procesando escena única...")
    img = os.path.join(tmp, f"{i}.jpg")
    vid = os.path.join(tmp, f"{i}.mp4")
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(palabra + ' ' + estilo + ' vertical')}?width=720&height=1280&nologo=true"
    
    try:
        # Descarga
        r = requests.get(url, timeout=20)
        with open(img, 'wb') as f: f.write(r.content)
        
        # FFmpeg con hilos limitados a 1 para proteger la RAM
        dur_frames = int(t * 25)
        vf = f"scale=800:1422,zoompan=z='min(zoom+0.001,1.1)':d={dur_frames}:s=720x1280:fps=25,format=yuv420p" 
        subprocess.run(f'ffmpeg -y -loop 1 -i "{img}" -vf "{vf}" -c:v libx264 -preset ultrafast -threads 1 -t {t} "{vid}"', shell=True)
        
        # Borramos la imagen inmediatamente para liberar espacio
        if os.path.exists(img): os.remove(img)
        return vid if os.path.exists(vid) else None
    except: return None

tema = st.text_input("¿Qué quieres crear sin errores?")
if st.button("🚀 INICIAR PRODUCCIÓN ESCUDO"):
    if not tema: st.warning("Escribe un tema")
    else:
        st.markdown('<div class="ram-shield">🛡️ PROTECCIÓN DE RAM ACTIVA: Procesando tareas una por una. No salgas de la pestaña.</div>', unsafe_allow_html=True)
        
        with tempfile.TemporaryDirectory() as tmp:
            with st.status("🛠️ Ejecutando plan paso a paso...", expanded=True) as status:
                
                status.write("🧠 **Paso 1:** Redactando guion básico...")
                guion = generar_guion(tema)
                
                status.write("🎙️ **Paso 2:** Generando archivo de audio...")
                audio = generar_voz_paso_a_paso(guion, tmp)
                
                dur = 9.0
                try:
                    dur = float(subprocess.check_output(f'ffprobe -i "{audio}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
                except: pass
                
                n_escenas = 3
                clips = []
                status.write(f"🎨 **Paso 3:** Creando {n_escenas} escenas secuenciales...")
                
                # Bucle estrictamente secuencial
                palabras = guion.split()[:n_escenas]
                for i, p in enumerate(palabras):
                    v_clip = animar_escena_individual(i, p, dur/n_escenas, "cinematic detailed", tmp, status)
                    if v_clip: clips.append(v_clip)
                
                if not clips: st.error("No se pudo crear ninguna escena."); st.stop()
                
                status.write("🎬 **Paso 4:** Montaje del máster final...")
                lista_txt = os.path.join(tmp, "l.txt")
                with open(lista_txt, "w") as f:
                    for c in clips: f.write(f"file '{c}'\n")
                
                v_mudo = os.path.join(tmp, "m.mp4")
                subprocess.run(f'ffmpeg -y -f concat -safe 0 -i "{lista_txt}" -c copy -threads 1 "{v_mudo}"', shell=True)
                
                final_path = os.path.join(tmp, "v_final.mp4")
                sub_f = f"drawtext=text='{guion[:30]}...':fontcolor=white:fontsize=40:fontfile='{font_abs}':x=(w-tw)/2:y=(h-th)/2:borderw=2"
                
                # Unión final con limitación de hilos
                subprocess.run(f'ffmpeg -y -i "{v_mudo}" -i "{audio}" -vf "{sub_f}" -c:v libx264 -preset ultrafast -threads 1 -t {dur} "{final_path}"', shell=True)
                
                if os.path.exists(final_path):
                    with open(final_path, "rb") as f:
                        v_bytes = f.read()
                    status.update(label="✅ Vídeo completado con éxito", state="complete")
                    st.success("🎉 ¡Aquí tienes tu vídeo blindado!")
                    st.video(v_bytes)
                else:
                    st.error("Error al exportar el archivo final.")
