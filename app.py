import streamlit as st
import os, time, subprocess, re, urllib.parse, math
import requests
import tempfile
import concurrent.futures

st.set_page_config(page_title="Fénix Studio V68", layout="centered")

# Estilo visual PRO
st.markdown("""
<style>
    .stApp { background: #000000; color: #FFFFFF; }
    .pro-title { font-size: 40px; font-weight: 900; color: #00FFD1; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V68 🚀</div>', unsafe_allow_html=True)

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

def limpiar_texto_extremo(t):
    # Solo deja letras, números y puntuación básica
    return re.sub(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ.,! ]', '', t).strip()

def generar_guion_ia(tema):
    prompt = f"Guion TikTok 30 palabras sobre {tema}. Solo texto, sin emojis."
    url = f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}"
    try:
        r = requests.get(url, timeout=20)
        return limpiar_texto_extremo(r.text)
    except: return ""

def generar_voz_blindada(texto, codigo_voz, dir_trabajo):
    mp3_path = os.path.join(dir_trabajo, "t.mp3")
    vtt_path = os.path.join(dir_trabajo, "subs.vtt")
    
    # Intento con Edge TTS
    cmd = f'python -m edge_tts --voice {codigo_voz} --text "{texto}" --write-media "{mp3_path}" --write-subtitles "{vtt_path}"'
    subprocess.run(cmd, shell=True, capture_output=True)
    
    if os.path.exists(mp3_path) and os.path.getsize(mp3_path) > 500:
        return True, "edge"
    
    # Fallback Google
    try:
        url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={urllib.parse.quote(texto[:200])}&tl=es&client=tw-ob"
        r = requests.get(url, timeout=15)
        with open(mp3_path, "wb") as f: f.write(r.content)
        return True, "google"
    except: return False, None

def procesar_escena(args):
    i, palabra, t_clip, estilo, dir_trabajo = args
    img_path = os.path.join(dir_trabajo, f"img_{i}.jpg")
    p_path = os.path.join(dir_trabajo, f"p_{i}.mp4")
    prompt = f"{palabra}, {estilo}, vertical, high quality"
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=720&height=1280&nologo=true"
    
    # Sistema de reintentos para la imagen
    for _ in range(3):
        try:
            r = requests.get(url, timeout=30)
            if r.status_code == 200:
                with open(img_path, 'wb') as f: f.write(r.content)
                break
        except: time.sleep(2)
    
    if os.path.exists(img_path):
        vf = f"scale=800:1422,zoompan=z='min(zoom+0.001,1.2)':d={int(t_clip*30)}:s=720x1280,format=yuv420p"
        subprocess.run(f'ffmpeg -y -loop 1 -i "{img_path}" -vf "{vf}" -c:v libx264 -preset ultrafast -t {t_clip} "{p_path}"', shell=True)
        return p_path
    return None

tema = st.text_input("Tema:")
if st.button("GENERAR V68"):
    with tempfile.TemporaryDirectory() as tmp:
        with st.status("🚀 Trabajando...") as status:
            guion = generar_guion_ia(tema)
            if not guion: st.error("Fallo IA Texto"); st.stop()
            
            exito, motor = generar_voz_blindada(guion, "es-MX-JorgeNeural", tmp)
            if not exito: st.error("Fallo Voz"); st.stop()
            
            mp3 = os.path.join(tmp, "t.mp3")
            dur = float(subprocess.check_output(f'ffprobe -i "{mp3}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
            
            num = 4 # Menos escenas = Más rapidez y menos errores
            palabras = guion.split()[:num]
            tareas = [(i, p, dur/num, "Cinematic", tmp) for i, p in enumerate(palabras)]
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
                clips = [c for c in list(ex.map(procesar_escena, tareas)) if c]
            
            lista_path = os.path.join(tmp, "l.txt")
            with open(lista_path, "w") as f:
                for c in clips: f.write(f"file '{c}'\n")
            
            v_mudo = os.path.join(tmp, "m.mp4")
            subprocess.run(f'ffmpeg -y -f concat -safe 0 -i "{lista_path}" -c copy "{v_mudo}"', shell=True)
            
            os.makedirs("output", exist_ok=True)
            v_final = f"output/v_{int(time.time())}.mp4"
            
            # Subtítulos simplificados para evitar errores de filtro
            sub_filt = f"drawtext=text='{guion[:35]}...':fontcolor=yellow:fontsize=45:fontfile='{font_abs}':x=(w-tw)/2:y=(h-th)/2:borderw=3"
            subprocess.run(f'ffmpeg -y -i "{v_mudo}" -i "{mp3}" -vf "{sub_filt}" -c:v libx264 -preset fast -t {dur} "{v_final}"', shell=True)
            
            st.video(v_final)
            st.success(f"Vídeo creado con {motor}")
