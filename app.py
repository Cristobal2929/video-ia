import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil
import requests
import base64
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V78", layout="centered")

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
    .ok-card { padding: 15px; border-radius: 10px; background: #064e3b; border: 2px solid #00FFD1; text-align: center; color: #00FFD1; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V78 ☢️</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center; color:#94A3B8; margin-bottom:20px;">Motor Base64 (Anti-Cuelgues) Activado</div>', unsafe_allow_html=True)

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
    except: return "Aprende a ser el mejor en lo que haces desde hoy mismo"

def preparar_entorno():
    if os.path.exists("taller"): shutil.rmtree("taller")
    os.makedirs("taller", exist_ok=True)

tema = st.text_input("Tema del vídeo:")
if st.button("🚀 INICIAR GENERACIÓN INFALIBLE"):
    if not tema: st.warning("Escribe un tema")
    else:
        preparar_entorno()
        
        with st.status("🛠️ Ejecutando bypass de seguridad...", expanded=True) as status:
            
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
            clips = []
            palabras = guion.split()[:n_escenas]
            
            status.write(f"🎨 3/4: Creando {n_escenas} escenas (Resolución 540p Optimizada)...")
            
            for i, p in enumerate(palabras):
                status.write(f"⏳ Procesando imagen {i+1}...")
                img = f"taller/img_{i}.jpg"
                vid = f"taller/vid_{i}.mp4"
                url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(p + ' cinematic vertical')}?width=540&height=960&nologo=true"
                
                try:
                    r = requests.get(url, timeout=20)
                    with open(img, 'wb') as f: f.write(r.content)
                    
                    dur_frames = int((dur/n_escenas) * 20)
                    # Zoompan en resolución segura (540x960) a 20 FPS
                    vf = f"scale=600:1066,zoompan=z='min(zoom+0.001,1.1)':d={dur_frames}:s=540x960:fps=20,format=yuv420p" 
                    subprocess.run(f'ffmpeg -y -loop 1 -i "{img}" -vf "{vf}" -c:v libx264 -preset ultrafast -threads 1 -t {dur/n_escenas} "{vid}"', shell=True)
                    if os.path.exists(vid): clips.append(vid)
                except: pass
            
            if not clips: st.error("Error al descargar imágenes."); st.stop()
            
            status.write("🎬 4/4: Exportación por Base64...")
            lista_txt = "taller/lista.txt"
            with open(lista_txt, "w") as f:
                for c in clips: f.write(f"file '../{c}'\n")
            
            v_mudo = "taller/mudo.mp4"
            subprocess.run(f'ffmpeg -y -f concat -safe 0 -i "{lista_txt}" -c copy -threads 1 "{v_mudo}"', shell=True)
            
            final_path = "taller/master.mp4"
            sub_f = f"drawtext=text='{guion[:30]}...':fontcolor=white:fontsize=35:fontfile='{font_abs}':x=(w-tw)/2:y=(h-th)/2:borderw=2"
            subprocess.run(f'ffmpeg -y -i "{v_mudo}" -i "{audio}" -vf "{sub_f}" -c:v libx264 -preset ultrafast -threads 1 -t {dur} "{final_path}"', shell=True)
            
            if os.path.exists(final_path) and os.path.getsize(final_path) > 1000:
                with open(final_path, "rb") as f:
                    video_bytes = f.read()
                
                # BYPASS DE STREAMLIT: Convertimos a Base64 y usamos HTML puro
                b64_video = base64.b64encode(video_bytes).decode()
                video_html = f'''
                    <video width="100%" controls autoplay loop style="border: 2px solid #00FFD1; border-radius: 10px;">
                        <source src="data:video/mp4;base64,{b64_video}" type="video/mp4">
                        Tu navegador no soporta vídeos HTML5.
                    </video>
                '''
                
                status.update(label="✅ Proceso completado al 100%", state="complete")
                st.markdown('<div class="ok-card">🎉 ¡AQUÍ TIENES TU VÍDEO!</div><br>', unsafe_allow_html=True)
                st.markdown(video_html, unsafe_allow_html=True)
            else:
                st.error("Error crítico de memoria en FFmpeg. Intenta con un tema distinto.")
