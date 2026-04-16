import streamlit as st
import os, time, subprocess, textwrap, re, urllib.parse, math
import requests
import tempfile
import concurrent.futures

st.set_page_config(page_title="Fénix Estudio PRO | V67", layout="centered")

st.markdown("""
<style>
    .stApp { background: radial-gradient(circle, #0f172a 0%, #000000 100%); color: #F8FAFC; }
    .pro-title { font-size: 45px; font-weight: 900; background: -webkit-linear-gradient(45deg, #00FFD1, #FFD700); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 5px; text-transform: uppercase;}
    .stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] { background-color: #1e293b !important; color: #ffffff !important; border: 2px solid #00FFD1 !important; border-radius: 10px; font-size: 16px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V67</div>', unsafe_allow_html=True)
st.markdown('<div class="pro-subtitle" style="text-align:center; color:#94A3B8; margin-bottom: 30px;">IA Generativa • Sistema Anti-Bloqueo • Calidad Máxima</div>', unsafe_allow_html=True)

@st.cache_resource
def descargar_fuente():
    font_path = "Arial_Pro.ttf"
    if not os.path.exists(font_path):
        try:
            r = requests.get("https://github.com/matomo-org/travis-scripts/raw/master/fonts/Arial.ttf", timeout=5)
            with open(font_path, "wb") as f: f.write(r.content)
        except: pass
    return os.path.abspath(font_path).replace('\\', '/')

font_abs = descargar_fuente()

IDIOMAS = {
    "🇪🇸 Español": {"tl": "es", "voces": {"Jorge": "es-MX-JorgeNeural", "Elvira": "es-ES-ElviraNeural"}},
    "🇺🇸 English": {"tl": "en", "voces": {"Guy": "en-US-GuyNeural", "Aria": "en-US-AriaNeural"}}
}

def generar_guion_ia(tema, idioma):
    # Prompt optimizado para evitar caracteres de control
    prompt = f"Escribe un guion para TikTok de 35 palabras sobre: {tema}. Idioma: {idioma}. Solo texto plano, sin emojis ni comillas."
    url = f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}"
    try:
        r = requests.get(url, timeout=15)
        clean = re.sub(r'[^\w\s.,!?]', '', r.text)
        return clean.strip()
    except: return ""

def generar_voz_inmortal(texto, codigo_voz, tl_code, dir_trabajo):
    mp3_path = os.path.join(dir_trabajo, "t.mp3")
    vtt_path = os.path.join(dir_trabajo, "subs.vtt")
    
    # INTENTO 1: EDGE TTS (Alta Calidad)
    try:
        cmd = f'python -m edge_tts --voice {codigo_voz} --rate=+15% --text "{texto}" --write-media "{mp3_path}" --write-subtitles "{vtt_path}"'
        subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
        if os.path.exists(mp3_path) and os.path.getsize(mp3_path) > 1000:
            return True, "premium"
    except: pass
    
    # INTENTO 2: GOOGLE TTS (Fallback infalible)
    try:
        url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={urllib.parse.quote(texto[:200])}&tl={tl_code}&client=tw-ob"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if r.status_code == 200:
            with open(mp3_path, "wb") as f: f.write(r.content)
            return True, "fallback"
    except: pass
    
    return False, None

def leer_vtt(vtt_path):
    subs = []
    if not os.path.exists(vtt_path): return subs
    with open(vtt_path, 'r', encoding='utf-8') as f: content = f.read()
    blocks = re.findall(r'(\d{2}:\d{2}:\d{2}\.\d{3})\s-->\s(\d{2}:\d{2}:\d{2}\.\d{3})\n(.*?)(?=\n\n|\Z)', content, re.DOTALL)
    for start, end, text in blocks:
        def to_sec(t):
            h, m, s = t.split(':')
            return float(h)*3600 + float(m)*60 + float(s)
        subs.append((to_sec(start), to_sec(end), text.strip().upper()))
    return subs

def procesar_escena_ia(args):
    i, palabra, t_clip, tema_broll, dir_trabajo = args
    img_path = os.path.join(dir_trabajo, f"img_{i}.jpg")
    p_path = os.path.join(dir_trabajo, f"p_{i}.mp4")
    prompt_ia = f"{palabra}, {tema_broll}, vertical, 4k"
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt_ia)}?width=720&height=1280&nologo=true"
    try:
        r = requests.get(url, timeout=30)
        with open(img_path, 'wb') as f: f.write(r.content)
        vf = f"scale=800:1422,zoompan=z='min(zoom+0.001,1.2)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={int(t_clip*30)}:s=720x1280,format=yuv420p"
        subprocess.run(f'ffmpeg -y -loop 1 -i "{img_path}" -vf "{vf}" -c:v libx264 -preset ultrafast -t {t_clip} "{p_path}"', shell=True)
        return p_path
    except: return None

with st.sidebar:
    idioma = st.selectbox("Idioma", list(IDIOMAS.keys()))
    voz = st.selectbox("Voz", list(IDIOMAS[idioma]["voces"].keys()))
    codigo_voz = IDIOMAS[idioma]["voces"][voz]
    tl_code = IDIOMAS[idioma]["tl"]
    color_sub = st.selectbox("Color Subs", ["yellow", "white", "cyan"])

st.markdown("### 🤖 Generador Automático")
tema = st.text_input("Tema del vídeo:")
estilo = st.text_input("Estilo visual:", value="Cinematic, detailed")

if st.button("🚀 CREAR VÍDEO V67"):
    if not tema: st.warning("Escribe un tema.")
    else:
        with tempfile.TemporaryDirectory() as dir_trabajo:
            with st.status("🎬 Creando contenido...", expanded=True) as status:
                status.write("🧠 Redactando guion...")
                guion = generar_guion_ia(tema, idioma)
                if not guion: st.error("Error IA"); st.stop()
                
                status.write("🎙️ Grabando voz...")
                exito, motor = generar_voz_inmortal(guion, codigo_voz, tl_code, dir_trabajo)
                if not exito: st.error("Error Voz"); st.stop()
                
                mp3_path = os.path.join(dir_trabajo, "t.mp3")
                dur = float(subprocess.check_output(f'ffprobe -i "{mp3_path}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
                
                num_escenas = 5
                status.write(f"🎨 Pintando {num_escenas} escenas IA...")
                palabras = guion.split()[:num_escenas]
                tareas = [(i, p, dur/num_escenas, estilo, dir_trabajo) for i, p in enumerate(palabras)]
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
                    clips = [c for c in list(ex.map(procesar_escena_ia, tareas)) if c]
                
                status.write("✨ Montaje final...")
                lista = os.path.join(dir_trabajo, "l.txt")
                with open(lista, "w") as f:
                    for c in clips: f.write(f"file '{c}'\n")
                
                v_mudo = os.path.join(dir_trabajo, "m.mp4")
                subprocess.run(f'ffmpeg -y -f concat -safe 0 -i "{lista}" -c copy "{v_mudo}"', shell=True)
                
                vtt_path = os.path.join(dir_trabajo, "subs.vtt")
                vtt_data = leer_vtt(vtt_path)
                draw = []
                if motor == "premium" and vtt_data:
                    for v in vtt_data:
                        draw.append(f"drawtext=text='{v[2]}':fontcolor={color_sub}:fontsize=60:fontfile='{font_abs}':x=(w-tw)/2:y=(h-th)/2:borderw=4:enable='between(t,{v[0]},{v[1]})'")
                else:
                    # Fallback simple de subtítulos si falla el VTT
                    draw.append(f"drawtext=text='{guion[:40]}...':fontcolor={color_sub}:fontsize=50:fontfile='{font_abs}':x=(w-tw)/2:y=(h-th)/2:borderw=4")

                f_txt = os.path.join(dir_trabajo, "f.txt")
                with open(f_txt, "w", encoding="utf-8") as f: f.write(",".join(draw) if draw else "null")
                
                os.makedirs("output", exist_ok=True)
                v_final = f"output/v_{int(time.time())}.mp4"
                subprocess.run(f'ffmpeg -y -i "{v_mudo}" -i "{mp3_path}" -filter_complex_script "{f_txt}" -c:v libx264 -preset fast -t {dur} "{v_final}"', shell=True)
                
                st.success(f"✅ ¡Vídeo V67 Listo! (Motor: {motor})")
                st.video(v_final)
