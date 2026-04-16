import streamlit as st
import os, time, random, subprocess, textwrap, re, urllib.parse, math
import requests

st.set_page_config(page_title="Fénix Estudio PRO | V57", layout="centered")

st.markdown("""
<style>
    .stApp { background: radial-gradient(circle, #0f172a 0%, #000000 100%); color: #F8FAFC; }
    .pro-title { font-size: 45px; font-weight: 900; background: -webkit-linear-gradient(45deg, #00FFD1, #FFD700); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 5px; text-transform: uppercase;}
    .stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] { background-color: #1e293b !important; color: #ffffff !important; border: 2px solid #00FFD1 !important; border-radius: 10px; font-size: 16px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V57</div>', unsafe_allow_html=True)
st.markdown('<div class="pro-subtitle" style="text-align:center; color:#94A3B8; margin-bottom: 30px;">Inteligencia Semántica • Contexto Visual 100% Perfecto • Sincro 30 FPS</div>', unsafe_allow_html=True)

font_path = "Arial.ttf"
if not os.path.exists(font_path):
    try:
        r = requests.get("https://github.com/matomo-org/travis-scripts/raw/master/fonts/Arial.ttf", timeout=5)
        with open(font_path, "wb") as f: f.write(r.content)
    except: pass
font_abs = os.path.abspath(font_path).replace('\\', '/')

IDIOMAS = {
    "🇪🇸 Español": {"tl": "es", "voces": {"Jorge (Latino)": "es-MX-JorgeNeural", "Elvira (España)": "es-ES-ElviraNeural", "Alvaro (España)": "es-ES-AlvaroNeural"}},
    "🇺🇸 English": {"tl": "en", "voces": {"Guy (Masculino US)": "en-US-GuyNeural", "Aria (Femenina US)": "en-US-AriaNeural", "Christopher (Masculino US)": "en-US-ChristopherNeural"}},
    "🇫🇷 Français": {"tl": "fr", "voces": {"Henri (Masculino)": "fr-FR-HenriNeural", "Denise (Femenina)": "fr-FR-DeniseNeural"}},
    "🇩🇪 Deutsch": {"tl": "de", "voces": {"Killian (Masculino)": "de-DE-KillianNeural", "Amala (Femenina)": "de-DE-AmalaNeural"}},
    "🇮🇹 Italiano": {"tl": "it", "voces": {"Diego (Masculino)": "it-IT-DiegoNeural", "Elsa (Femenina)": "it-IT-ElsaNeural"}},
    "🇧🇷 Português": {"tl": "pt", "voces": {"Antonio (Brasil)": "pt-BR-AntonioNeural", "Francisca (Brasil)": "pt-BR-FranciscaNeural"}}
}

def generar_voz_inmortal(texto, codigo_voz, tl_code):
    texto_limpio = re.sub(r'[^\w\s.,;?!]', '', texto.replace('\n', ' ')).replace('_', '')
    with open("temp_txt.txt", "w", encoding="utf-8") as f: f.write(texto_limpio)
    
    for _ in range(2):
        subprocess.run(["python", "-m", "edge_tts", "--voice", codigo_voz, "--rate=+15%", "-f", "temp_txt.txt", "--write-media", "t.mp3"])
        if os.path.exists("t.mp3") and os.path.getsize("t.mp3") > 1000: return True
        time.sleep(1.5)

    oraciones = textwrap.wrap(texto_limpio, width=150)
    archivos = []
    for idx, oracion in enumerate(oraciones):
        try:
            url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={urllib.parse.quote(oracion)}&tl={tl_code}&client=tw-ob"
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            if r.status_code == 200:
                with open(f"g_{idx}.mp3", "wb") as f: f.write(r.content)
                archivos.append(f"g_{idx}.mp3")
        except: pass
        
    if archivos:
        with open("lista_audio.txt", "w") as f:
            for a in archivos: f.write(f"file '{a}'\n")
        subprocess.run('ffmpeg -y -f concat -safe 0 -i lista_audio.txt -c copy t.mp3', shell=True)
        if os.path.exists("t.mp3") and os.path.getsize("t.mp3") > 1000: return True
    return False

# CEREBRO LECTOR: Extrae la palabra más importante de un trozo de guion
def extraer_palabra_clave(texto_chunk):
    palabras = re.sub(r'[^\w\s]', '', texto_chunk).split()
    # Filtramos palabras cortas (que suelen ser conectores como "el", "de", "con", "and", "the")
    palabras_utiles = [p for p in palabras if len(p) > 4]
    if palabras_utiles:
        # Devuelve la palabra más larga (suele ser el sustantivo principal: "criptomonedas", "millonario", etc.)
        return max(palabras_utiles, key=len)
    return "cinematic"

with st.sidebar:
    st.header("🌍 Mercado Global")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    
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
tema_broll = st.text_input("🎨 ¿Qué filtro o ambiente le damos? (Ej: Dark, Luxury, Cyberpunk, Cinematic...):", placeholder="Luxury")

if st.button("🚀 CREAR VÍDEO (INTELIGENCIA SEMÁNTICA V57)"):
    if len(guion_usuario.strip()) < 20 or len(tema_broll.strip()) < 2:
        st.warning("⚠️ Rellena el guion y el estilo visual.")
    else:
        with st.status(f"🎬 Leyendo guion y buscando contexto perfecto...", expanded=True) as status:
            subprocess.run("rm -f a_*.mp3 g_*.mp3 v_*.mp4 p_*.mp4 clip_*.mp4 text_*.txt temp_txt.txt lista*.txt music.m4a audio_final.m4a video_mudo.mp4 final.mp4 t.mp3 subs_filter.txt", shell=True)
            
            status.write("🎙️ Grabando locución nativa...")
            if not generar_voz_inmortal(guion_usuario, codigo_voz, tl_code):
                st.error("❌ Servidores de voz caídos.")
                st.stop()
            dur_audio = float(subprocess.check_output("ffprobe -i t.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True).decode('utf-8').strip())

            status.write("🎵 Mezclando banda sonora...")
            freq = 60 if "Misterio" in musica_tipo else 75
            subprocess.run(f'ffmpeg -y -i t.mp3 -f lavfi -i "sine=f={freq}:d={dur_audio}" -filter_complex "[1:a]volume=0.03[m];[0:a][m]amix=inputs=2:duration=first" -c:a aac -ar 44100 audio_final.m4a', shell=True)

            status.write("🎞️ Analizando el guion palabra por palabra...")
            
            dur_corte = 3.5
            num_clips = math.ceil(dur_audio / dur_corte)
            clips_finales = []
            
            # Cortamos el guion en el mismo número de trozos que vídeos vamos a necesitar
            palabras_guion = guion_usuario.split()
            chunk_size = max(len(palabras_guion) // num_clips, 1)
            
            for i in range(num_clips):
                # Extraemos el trozo de guion que suena en este clip exacto
                start_idx = i * chunk_size
                end_idx = start_idx + chunk_size if i < num_clips - 1 else len(palabras_guion)
                texto_del_clip = " ".join(palabras_guion[start_idx:end_idx])
                
                # CEREBRO LECTOR: Sacamos la palabra clave de este trozo
                palabra_magica = extraer_palabra_clave(texto_del_clip)
                query_busqueda = urllib.parse.quote(f"{palabra_magica} {tema_broll} 4k")
                status.write(f"🔍 Escena {i+1}: Leyendo '{palabra_magica}' -> Buscando vídeo...")

                # Ajuste de tiempo (1 seg de propina al final para que no se congele)
                t_clip = dur_corte if i < num_clips - 1 else (dur_audio - (i * dur_corte)) + 1.0 
                if t_clip <= 0: t_clip = 1.0
                
                v_url = None
                try:
                    r = requests.get(f"https://api.pexels.com/videos/search?query={query_busqueda}&per_page=5&size=large&orientation=portrait", headers={"Authorization": pexels_key.strip()}, timeout=10).json()
                    if r.get('videos'): v_url = random.choice(r['videos'])['video_files'][0]['link']
                except: pass

                # Si falla la palabra exacta, buscamos solo con el tema visual
                if not v_url:
                    try:
                        r = requests.get(f"https://api.pexels.com/videos/search?query={urllib.parse.quote(tema_broll + ' 4k')}&per_page=5&size=large&orientation=portrait", headers={"Authorization": pexels_key.strip()}, timeout=10).json()
                        if r.get('videos'): v_url = random.choice(r['videos'])['video_files'][0]['link']
                    except: pass
                
                exito_descarga = False
                if v_url:
                    try:
                        vid_data = requests.get(v_url, timeout=20).content
                        with open(f"clip_{i}.mp4", 'wb') as f: f.write(vid_data)
                        exito_descarga = True
                    except: pass
                
                if not exito_descarga:
                    if i > 0 and os.path.exists(f"clip_{i-1}.mp4"):
                        subprocess.run(f"cp clip_{i-1}.mp4 clip_{i}.mp4", shell=True)
                    else:
                        subprocess.run(f'ffmpeg -y -f lavfi -i color=c=#111827:s=720x1280:d={t_clip}:r=30 -c:v libx264 -preset ultrafast -format yuv420p "p_{i}.mp4"', shell=True)
                        clips_finales.append(f"p_{i}.mp4")
                        continue
                
                # RENDERIZAMOS CON -r 30 (Sincronización perfecta de la V56)
                vf = "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,colorchannelmixer=rr=0.7:gg=0.7:bb=0.7,format=yuv420p"
                subprocess.run(f'ffmpeg -y -stream_loop -1 -i "clip_{i}.mp4" -vf "{vf}" -an -c:v libx264 -r 30 -preset ultrafast -t {t_clip} "p_{i}.mp4"', shell=True)
                
                if os.path.exists(f"p_{i}.mp4"):
                    clips_finales.append(f"p_{i}.mp4")

            with open("lista.txt", "w") as f:
                for c in clips_finales: f.write(f"file '{c}'\n")
            subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy video_mudo.mp4', shell=True)

            status.write("🎬 Mapeando Subtítulos (Doble capa anti-errores)...")
            texto_seguro = re.sub(r'[^\w\s]', '', guion_usuario.replace('\n', ' ').upper()).replace('_', '')
            palabras = texto_seguro.split()
            
            subs_cmd = []
            font_cmd = f"fontfile='{font_abs}':" if os.path.exists(font_path) else ""
            
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
            
            with open("subs_filter.txt", "w") as f: f.write(",\n".join(subs_cmd))

            status.write("✨ Renderizando Máster Final...")
            v_final = f"output/v_{int(time.time())}.mp4"
            cmd_f = f"""ffmpeg -y -i video_mudo.mp4 -i audio_final.m4a -filter_complex_script subs_filter.txt -c:v libx264 -preset fast -crf 23 -c:a copy -t {dur_audio} "{v_final}" """
            subprocess.run(cmd_f, shell=True)
            
            if os.path.exists(v_final):
                st.success("🔥 ¡VÍDEO V57 CREADO! Imágenes sincronizadas con el contexto de las palabras.")
                st.video(v_final)
                st.balloons()
            else:
                st.error("❌ Fallo en el renderizado final.")
