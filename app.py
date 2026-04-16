import streamlit as st
import os, time, subprocess, textwrap, re, urllib.parse, math
import requests
import tempfile
import concurrent.futures

st.set_page_config(page_title="Fénix Estudio PRO | V65", layout="centered")

st.markdown("""
<style>
    .stApp { background: radial-gradient(circle, #0f172a 0%, #000000 100%); color: #F8FAFC; }
    .pro-title { font-size: 45px; font-weight: 900; background: -webkit-linear-gradient(45deg, #00FFD1, #FFD700); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 5px; text-transform: uppercase;}
    .stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] { background-color: #1e293b !important; color: #ffffff !important; border: 2px solid #00FFD1 !important; border-radius: 10px; font-size: 16px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V65</div>', unsafe_allow_html=True)
st.markdown('<div class="pro-subtitle" style="text-align:center; color:#94A3B8; margin-bottom: 30px;">IA Total • Estimador de Tiempo Real • Multi-Thread</div>', unsafe_allow_html=True)

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
    "🇪🇸 Español": {"tl": "es", "voces": {"Jorge (Latino)": "es-MX-JorgeNeural", "Elvira (España)": "es-ES-ElviraNeural", "Alvaro (España)": "es-ES-AlvaroNeural"}},
    "🇺🇸 English": {"tl": "en", "voces": {"Guy (Masculino US)": "en-US-GuyNeural", "Aria (Femenina US)": "en-US-AriaNeural", "Christopher (Masculino US)": "en-US-ChristopherNeural"}},
    "🇫🇷 Français": {"tl": "fr", "voces": {"Henri (Masculino)": "fr-FR-HenriNeural", "Denise (Femenina)": "fr-FR-DeniseNeural"}}
}

def generar_guion_ia(tema, idioma):
    prompt = f"Escribe un guion corto y viral de 40 palabras para TikTok sobre: {tema}. Idioma: {idioma}. Ve directo al grano, sin saludos ni introducciones, usa un tono persuasivo."
    url = f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}"
    try:
        r = requests.get(url, timeout=15)
        return re.sub(r'[\*\[\]]', '', r.text).strip()
    except:
        return ""

def extraer_palabra_clave(texto_chunk):
    palabras = re.sub(r'[^\w\s]', '', texto_chunk).split()
    palabras_utiles = [p for p in palabras if len(p) > 4 and not p.lower().endswith("mente")]
    if palabras_utiles: return max(palabras_utiles, key=len)
    return "cinematic"

def traducir_a_ingles(palabra, tl_code):
    if tl_code == "en": return palabra
    try:
        url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(palabra)}&langpair={tl_code}|en"
        respuesta = requests.get(url, timeout=5).json()
        return respuesta['responseData']['translatedText']
    except:
        return palabra

def generar_voz_inmortal(texto, codigo_voz, tl_code, dir_trabajo):
    texto_limpio = re.sub(r'[^\w\s.,;?!]', '', texto.replace('\n', ' ')).replace('_', '')
    txt_path = os.path.join(dir_trabajo, "temp_txt.txt")
    mp3_path = os.path.join(dir_trabajo, "t.mp3")
    vtt_path = os.path.join(dir_trabajo, "subs.vtt")
    with open(txt_path, "w", encoding="utf-8") as f: f.write(texto_limpio)
    subprocess.run(["python", "-m", "edge_tts", "--voice", codigo_voz, "--rate=+15%", "-f", txt_path, "--write-media", mp3_path, "--write-subtitles", vtt_path])
    return os.path.exists(mp3_path)

def leer_vtt(vtt_path):
    subs = []
    try:
        with open(vtt_path, 'r', encoding='utf-8') as f: content = f.read()
        blocks = re.findall(r'(\d{2}:\d{2}:\d{2}\.\d{3})\s-->\s(\d{2}:\d{2}:\d{2}\.\d{3})\n(.*?)(?=\n\n|\Z)', content, re.DOTALL)
        for start, end, text in blocks:
            def to_sec(t):
                h, m, s = t.split(':')
                return float(h)*3600 + float(m)*60 + float(s)
            txt_clean = re.sub(r'[^\w\s]', '', text.strip()).upper()
            if txt_clean: subs.append((to_sec(start), to_sec(end), txt_clean))
    except: pass
    return subs

def procesar_escena_ia(args):
    i, texto_del_clip, t_clip, tema_broll, tl_code, dir_trabajo = args
    palabra_es = extraer_palabra_clave(texto_del_clip)
    palabra_en = traducir_a_ingles(palabra_es, tl_code)
    prompt_ia = f"{palabra_en}, {tema_broll}, masterpiece, 4k, vertical"
    img_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt_ia)}?width=720&height=1280&nologo=true"
    img_path = os.path.join(dir_trabajo, f"img_{i}.jpg")
    p_path = os.path.join(dir_trabajo, f"p_{i}.mp4")
    try:
        img_data = requests.get(img_url, timeout=20).content
        with open(img_path, 'wb') as f: f.write(img_data)
        frames = int(t_clip * 30)
        vf = f"scale=800:1422,zoompan=z='min(zoom+0.0015,1.2)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=720x1280:fps=30,colorchannelmixer=rr=0.7:gg=0.7:bb=0.7,vignette=PI/3,format=yuv420p"
        subprocess.run(f'ffmpeg -y -loop 1 -i "{img_path}" -vf "{vf}" -c:v libx264 -preset ultrafast -t {t_clip} "{p_path}"', shell=True)
        return (i, p_path)
    except:
        return (i, None)

with st.sidebar:
    st.header("🌍 Mercado Global")
    idioma_elegido = st.selectbox("🌐 Idioma del Vídeo", list(IDIOMAS.keys()))
    voces_disponibles = IDIOMAS[idioma_elegido]["voces"]
    nombre_voz = st.selectbox("🗣️ Voz del Locutor", list(voces_disponibles.keys()))
    codigo_voz = voces_disponibles[nombre_voz]
    tl_code = IDIOMAS[idioma_elegido]["tl"]
    color_sub = st.selectbox("🎨 Color Subtítulos", ["yellow", "white", "#00FFD1"])
    musica_tipo = st.selectbox("🎵 Música", ["Misterio (60Hz)", "Negocios (75Hz)"])

st.markdown("### 1. El Cerebro")
tema_usuario = st.text_input("💡 ¿De qué quieres que trate el vídeo?", placeholder="Ej: Curiosidades del espacio")
st.markdown("### 2. Estilo Visual")
tema_broll = st.text_input("🎨 Estilo IA:", value="Dark cinematic, hyperrealistic")

if st.button("🚀 GENERAR MAGIA (V65)"):
    if len(tema_usuario.strip()) < 3:
        st.warning("⚠️ Escribe un tema.")
    else:
        with tempfile.TemporaryDirectory() as dir_trabajo:
            # INICIO DE ESTIMACIÓN
            with st.status("🎬 Calculando tiempos...", expanded=True) as status:
                
                status.write("🧠 IA redactando guion...")
                guion = generar_guion_ia(tema_usuario, idioma_elegido)
                if not guion: st.stop()
                
                status.write("🎙️ Grabando voz...")
                generar_voz_inmortal(guion, codigo_voz, tl_code, dir_trabajo)
                
                mp3_path = os.path.join(dir_trabajo, "t.mp3")
                vtt_path = os.path.join(dir_trabajo, "subs.vtt")
                dur_audio = float(subprocess.check_output(f'ffprobe -i "{mp3_path}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True).decode('utf-8').strip())
                
                num_clips = math.ceil(dur_audio / 3.5)
                
                # CÁLCULO DE TIEMPO APROXIMADO
                tiempo_estimado = (num_clips * 8) + 20 
                st.info(f"⏳ **Tiempo estimado total:** {tiempo_estimado} segundos.")
                progreso = st.progress(0)
                
                status.write(f"🎨 Pintando {num_clips} escenas IA (Este es el paso más largo)...")
                
                # PROCESAMIENTO
                tareas = []
                for i in range(num_clips):
                    t_clip = 3.5 if i < num_clips - 1 else (dur_audio - (i * 3.5)) + 1.0
                    txt_part = " ".join(guion.split()[i*5:(i+1)*5])
                    tareas.append((i, txt_part, t_clip, tema_broll, tl_code, dir_trabajo))

                clips_finales = []
                with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                    futuros = [executor.submit(procesar_escena_ia, arg) for arg in tareas]
                    for idx, future in enumerate(concurrent.futures.as_completed(futuros)):
                        clips_finales.append(future.result())
                        # Actualizar barra de progreso
                        porcentaje = int(((idx + 1) / num_clips) * 80)
                        progreso.progress(porcentaje)
                
                clips_finales.sort(key=lambda x: x[0])
                
                status.write("✨ Renderizando máster final...")
                video_mudo = os.path.join(dir_trabajo, "video_mudo.mp4")
                lista_video_path = os.path.join(dir_trabajo, "lista.txt")
                with open(lista_video_path, "w") as f:
                    for c in clips_finales: 
                        if c[1]: f.write(f"file '{c[1]}'\n")
                
                subprocess.run(f'ffmpeg -y -f concat -safe 0 -i "{lista_video_path}" -c copy "{video_mudo}"', shell=True)
                
                # AUDIO Y SUBS
                audio_final = os.path.join(dir_trabajo, "audio_final.m4a")
                freq = 60 if "Misterio" in musica_tipo else 75
                subprocess.run(f'ffmpeg -y -i "{mp3_path}" -f lavfi -i "sine=f={freq}:d={dur_audio}" -filter_complex "[0:a]bass=g=5,treble=g=3,acompressor[v]; [1:a]volume=0.03[m]; [v][m]amix=inputs=2:duration=first" -c:a aac "{audio_final}"', shell=True)
                
                vtt_data = leer_vtt(vtt_path)
                subs_cmd = []
                for v in vtt_data:
                    subs_cmd.append(f"drawtext=text='{v[2]}':fontcolor={color_sub}:fontsize=65:fontfile='{font_abs}':borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{v[0]},{v[1]})'")
                
                filt_path = os.path.join(dir_trabajo, "f.txt")
                with open(filt_path, "w", encoding="utf-8") as f: f.write(",\n".join(subs_cmd))
                
                v_final = f"output/v_{int(time.time())}.mp4"
                os.makedirs("output", exist_ok=True)
                subprocess.run(f'ffmpeg -y -i "{video_mudo}" -i "{audio_final}" -filter_complex_script "{filt_path}" -c:v libx264 -preset fast -t {dur_audio} "{v_final}"', shell=True)
                
                progreso.progress(100)
                st.success("🔥 ¡VÍDEO LISTO!")
                st.video(v_final)
                st.balloons()
