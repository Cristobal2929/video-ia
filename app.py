import streamlit as st
import os, time, random, subprocess, textwrap, re, urllib.parse, math
import requests
import tempfile
import concurrent.futures

st.set_page_config(page_title="Fénix Estudio PRO | V59", layout="centered")

st.markdown("""
<style>
    .stApp { background: radial-gradient(circle, #0f172a 0%, #000000 100%); color: #F8FAFC; }
    .pro-title { font-size: 45px; font-weight: 900; background: -webkit-linear-gradient(45deg, #00FFD1, #FFD700); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 5px; text-transform: uppercase;}
    .stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] { background-color: #1e293b !important; color: #ffffff !important; border: 2px solid #00FFD1 !important; border-radius: 10px; font-size: 16px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V59</div>', unsafe_allow_html=True)
st.markdown('<div class="pro-subtitle" style="text-align:center; color:#94A3B8; margin-bottom: 30px;">Multi-Thread • Cerebro Bilingüe Avanzado • Entorno Aislado</div>', unsafe_allow_html=True)

# Descarga de fuente con caché para no descargarla en cada ejecución
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

def extraer_palabra_clave(texto_chunk):
    palabras = re.sub(r'[^\w\s]', '', texto_chunk).split()
    # MEJORA 1: Filtramos palabras cortas Y adverbios terminados en "mente"
    palabras_utiles = [p for p in palabras if len(p) > 4 and not p.lower().endswith("mente")]
    if palabras_utiles: return max(palabras_utiles, key=len)
    return "cinematic"

def traducir_a_ingles(palabra, tl_code):
    if tl_code == "en": return palabra
    try:
        # MEJORA 4: El langpair ahora es dinámico (ej. fr|en, es|en)
        url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(palabra)}&langpair={tl_code}|en"
        respuesta = requests.get(url, timeout=5).json()
        return respuesta['responseData']['translatedText']
    except:
        return palabra

def generar_voz_inmortal(texto, codigo_voz, tl_code, dir_trabajo):
    texto_limpio = re.sub(r'[^\w\s.,;?!]', '', texto.replace('\n', ' ')).replace('_', '')
    txt_path = os.path.join(dir_trabajo, "temp_txt.txt")
    mp3_path = os.path.join(dir_trabajo, "t.mp3")
    
    with open(txt_path, "w", encoding="utf-8") as f: f.write(texto_limpio)

    for _ in range(2):
        subprocess.run(["python", "-m", "edge_tts", "--voice", codigo_voz, "--rate=+15%", "-f", txt_path, "--write-media", mp3_path])
        if os.path.exists(mp3_path) and os.path.getsize(mp3_path) > 1000: return True
        time.sleep(1.5)

    oraciones = textwrap.wrap(texto_limpio, width=150)
    archivos = []
    for idx, oracion in enumerate(oraciones):
        try:
            url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={urllib.parse.quote(oracion)}&tl={tl_code}&client=tw-ob"
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            if r.status_code == 200:
                chunk_path = os.path.join(dir_trabajo, f"g_{idx}.mp3")
                with open(chunk_path, "wb") as f: f.write(r.content)
                archivos.append(chunk_path)
        except: pass

    if archivos:
        lista_path = os.path.join(dir_trabajo, "lista_audio.txt")
        with open(lista_path, "w") as f:
            for a in archivos: f.write(f"file '{a}'\n")
        subprocess.run(f'ffmpeg -y -f concat -safe 0 -i "{lista_path}" -c copy "{mp3_path}"', shell=True)
        if os.path.exists(mp3_path) and os.path.getsize(mp3_path) > 1000: return True
    return False

# MEJORA 2: Función aislada para ser ejecutada en paralelo
def procesar_escena(args):
    i, texto_del_clip, t_clip, tema_broll, pexels_key, tl_code, dir_trabajo = args
    palabra_es = extraer_palabra_clave(texto_del_clip)
    palabra_en = traducir_a_ingles(palabra_es, tl_code)
    
    query_busqueda = urllib.parse.quote(f"{palabra_en} {tema_broll} 4k")
    clip_path = os.path.join(dir_trabajo, f"clip_{i}.mp4")
    p_path = os.path.join(dir_trabajo, f"p_{i}.mp4")

    v_url = None
    try:
        r = requests.get(f"https://api.pexels.com/videos/search?query={query_busqueda}&per_page=5&size=large&orientation=portrait", headers={"Authorization": pexels_key.strip()}, timeout=10).json()
        if r.get('videos'): v_url = random.choice(r['videos'])['video_files'][0]['link']
    except: pass

    if not v_url:
        try:
            r = requests.get(f"https://api.pexels.com/videos/search?query={urllib.parse.quote(tema_broll + ' 4k')}&per_page=5&size=large&orientation=portrait", headers={"Authorization": pexels_key.strip()}, timeout=10).json()
            if r.get('videos'): v_url = random.choice(r['videos'])['video_files'][0]['link']
        except: pass

    exito_descarga = False
    if v_url:
        try:
            vid_data = requests.get(v_url, timeout=20).content
            with open(clip_path, 'wb') as f: f.write(vid_data)
            exito_descarga = True
        except: pass

    if not exito_descarga:
        subprocess.run(f'ffmpeg -y -f lavfi -i color=c=#111827:s=720x1280:d={t_clip}:r=30 -c:v libx264 -preset ultrafast -format yuv420p "{p_path}"', shell=True)
        return (i, p_path, palabra_es, palabra_en)

    vf = "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,colorchannelmixer=rr=0.7:gg=0.7:bb=0.7,vignette=PI/3,format=yuv420p"
    subprocess.run(f'ffmpeg -y -stream_loop -1 -i "{clip_path}" -vf "{vf}" -an -c:v libx264 -r 30 -preset ultrafast -t {t_clip} "{p_path}"', shell=True)
    
    return (i, p_path, palabra_es, palabra_en)

with st.sidebar:
    st.header("🌍 Mercado Global")
    # MEJORA 3: Limpiamos la key por defecto para seguridad (usar st.secrets en el futuro)
    pexels_key = st.text_input("🔑 API Pexels:", value="", type="password", help="Pega tu token de Pexels. ¡No lo dejes en el código fuente!")
    
    idioma_elegido = st.selectbox("🌐 Idioma del Vídeo", list(IDIOMAS.keys()))
    voces_disponibles = IDIOMAS[idioma_elegido]["voces"]
    nombre_voz = st.selectbox("🗣️ Voz del Locutor", list(voces_disponibles.keys()))
    codigo_voz = voces_disponibles[nombre_voz]
    tl_code = IDIOMAS[idioma_elegido]["tl"]
    
    color_sub = st.selectbox("🎨 Color Subtítulos", ["yellow", "white", "#00FFD1", "#FF0055"])
    musica_tipo = st.selectbox("🎵 Música", ["Misterio / Tensión (60Hz)", "Acción / Negocios (75Hz)"])

st.markdown("### 1. El Guion")
guion_usuario = st.text_area("📝 Pega tu Guion aquí:", height=150)
st.markdown("### 2. Estilo Visual")
tema_broll = st.text_input("🎨 Estilo General (Ej: Dark, Luxury, Cinematic...):", placeholder="Luxury")

if st.button("🚀 CREAR VÍDEO (CEREBRO BILINGÜE V59)"):
    if len(guion_usuario.strip()) < 20 or len(tema_broll.strip()) < 2:
        st.warning("⚠️ Rellena el guion y el estilo visual.")
    elif not pexels_key:
        st.error("⚠️ Falta la API Key de Pexels en la barra lateral.")
    else:
        # MEJORA 3: Directorio temporal único. Aísla a cada usuario y se borra al terminar.
        with tempfile.TemporaryDirectory() as dir_trabajo:
            with st.status(f"🎬 Iniciando Motor V59 en entorno aislado...", expanded=True) as status:
                
                status.write("🎙️ Grabando locución...")
                if not generar_voz_inmortal(guion_usuario, codigo_voz, tl_code, dir_trabajo):
                    st.error("❌ Servidores de voz caídos.")
                    st.stop()
                
                mp3_path = os.path.join(dir_trabajo, "t.mp3")
                dur_audio = float(subprocess.check_output(f'ffprobe -i "{mp3_path}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True).decode('utf-8').strip())
                
                status.write("🎵 Mezclando audio y ondas...")
                freq = 60 if "Misterio" in musica_tipo else 75
                audio_final = os.path.join(dir_trabajo, "audio_final.m4a")
                subprocess.run(f'ffmpeg -y -i "{mp3_path}" -f lavfi -i "sine=f={freq}:d={dur_audio}" -filter_complex "[1:a]volume=0.03[m];[0:a][m]amix=inputs=2:duration=first" -c:a aac -ar 44100 "{audio_final}"', shell=True)
                
                dur_corte = 3.5
                num_clips = math.ceil(dur_audio / dur_corte)
                palabras_guion = guion_usuario.split()
                chunk_size = max(len(palabras_guion) // num_clips, 1)
                
                tareas = []
                status.write(f"⚡ Descargando y procesando {num_clips} escenas en paralelo...")
                
                # PREPARAMOS TAREAS PARALELAS
                for i in range(num_clips):
                    start_idx = i * chunk_size
                    end_idx = start_idx + chunk_size if i < num_clips - 1 else len(palabras_guion)
                    texto_del_clip = " ".join(palabras_guion[start_idx:end_idx])
                    
                    t_clip = dur_corte if i < num_clips - 1 else (dur_audio - (i * dur_corte)) + 1.0
                    if t_clip <= 0: t_clip = 1.0
                    
                    tareas.append((i, texto_del_clip, t_clip, tema_broll, pexels_key, tl_code, dir_trabajo))

                # EJECUCIÓN MULTI-THREAD (3 workers para no saturar CPU)
                resultados = []
                with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                    futuros = [executor.submit(procesar_escena, arg) for arg in tareas]
                    for future in concurrent.futures.as_completed(futuros):
                        res = future.result()
                        resultados.append(res)
                        status.write(f"✔️ Escena {res[0]+1} lista ('{res[2]}' -> '{res[3]}')")

                # ORDENAMOS LOS RESULTADOS (ya que el as_completed los devuelve desordenados)
                resultados.sort(key=lambda x: x[0])
                clips_finales = [res[1] for res in resultados]
                
                lista_video_path = os.path.join(dir_trabajo, "lista_video.txt")
                video_mudo = os.path.join(dir_trabajo, "video_mudo.mp4")
                with open(lista_video_path, "w") as f:
                    for c in clips_finales: f.write(f"file '{c}'\n")
                subprocess.run(f'ffmpeg -y -f concat -safe 0 -i "{lista_video_path}" -c copy "{video_mudo}"', shell=True)

                status.write("🎬 Generando motor de subtítulos dinámicos...")
                texto_seguro = re.sub(r'[^\w\s]', '', guion_usuario.replace('\n', ' ').upper()).replace('_', '')
                palabras = texto_seguro.split()
                
                subs_cmd = []
                font_cmd = f"fontfile='{font_abs}':" if os.path.exists(font_abs) else ""
                chunks_raw = [palabras[j:j+2] for j in range(0, len(palabras), 2)]
                tiempo_por_chunk = dur_audio / max(len(chunks_raw), 1)
                
                for j, p_list in enumerate(chunks_raw):
                    t_start = j * tiempo_por_chunk
                    t_end = t_start + tiempo_por_chunk
                    if len(p_list) == 2 and (len(p_list[0]) + len(p_list[1]) > 12):
                        w1, w2 = p_list[0], p_list[1]
                        subs_cmd.append(f"drawtext=text='{w1}':fontcolor={color_sub}:fontsize=65:{font_cmd}borderw=5:bordercolor=black:shadowcolor=black@0.8:shadowx=4:shadowy=4:x=(w-tw)/2:y=(h-th)/2-40:enable='between(t,{t_start},{t_end})'")
                        subs_cmd.append(f"drawtext=text='{w2}':fontcolor={color_sub}:fontsize=65:{font_cmd}borderw=5:bordercolor=black:shadowcolor=black@0.8:shadowx=4:shadowy=4:x=(w-tw)/2:y=(h-th)/2+40:enable='between(t,{t_start},{t_end})'")
                    else:
                        frase = " ".join(p_list)
                        subs_cmd.append(f"drawtext=text='{frase}':fontcolor={color_sub}:fontsize=65:{font_cmd}borderw=5:bordercolor=black:shadowcolor=black@0.8:shadowx=4:shadowy=4:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{t_start},{t_end})'")
                
                subs_filter_path = os.path.join(dir_trabajo, "subs_filter.txt")
                with open(subs_filter_path, "w", encoding="utf-8") as f: f.write(",\n".join(subs_cmd))

                status.write("✨ Renderizando Máster Final...")
                os.makedirs("output", exist_ok=True)
                v_final = f"output/v_{int(time.time())}.mp4"
                
                cmd_f = f"""ffmpeg -y -i "{video_mudo}" -i "{audio_final}" -filter_complex_script "{subs_filter_path}" -c:v libx264 -preset fast -crf 23 -c:a copy -t {dur_audio} "{v_final}" """
                subprocess.run(cmd_f, shell=True)

            if os.path.exists(v_final):
                st.success("🔥 ¡VÍDEO V59 LISTO! Procesamiento Paralelo y Seguro completado.")
                st.video(v_final)
                st.balloons()
            else:
                st.error("❌ Fallo en renderizado final. Revisa los logs.")
