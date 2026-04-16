import streamlit as st
import os, time, random, subprocess, textwrap, re, urllib.parse
import requests

st.set_page_config(page_title="Fénix Estudio PRO | V44", layout="centered")

st.markdown("""
<style>
    .stApp { background: radial-gradient(circle, #0f172a 0%, #000000 100%); color: #F8FAFC; }
    .pro-title { font-size: 45px; font-weight: 900; background: -webkit-linear-gradient(45deg, #00FFD1, #FFD700); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 5px; text-transform: uppercase;}
    .stTextArea textarea { background-color: #1e293b !important; color: #ffffff !important; border: 2px solid #00FFD1 !important; border-radius: 10px; font-size: 16px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V44</div>', unsafe_allow_html=True)
st.markdown('<div class="pro-subtitle" style="text-align:center; color:#94A3B8; margin-bottom: 30px;">Imágenes Inteligentes • Sincronización de Contexto • HD Limpio</div>', unsafe_allow_html=True)

# 1. DESCARGA DE FUENTE SEGURA
font_path = "Arial.ttf"
if not os.path.exists(font_path):
    try:
        r = requests.get("https://github.com/matomo-org/travis-scripts/raw/master/fonts/Arial.ttf", timeout=5)
        with open(font_path, "wb") as f: f.write(r.content)
    except: pass
font_abs = os.path.abspath(font_path).replace('\\', '/')

# --- MOTOR DE VOZ INMORTAL DUAL ---
def generar_voz_inmortal(texto):
    with open("temp_txt.txt", "w", encoding="utf-8") as f: f.write(texto)
    subprocess.run(["python", "-m", "edge_tts", "--voice", "es-ES-AlvaroNeural", "--rate=+5%", "-f", "temp_txt.txt", "--write-media", "t.mp3"])
    
    if os.path.exists("t.mp3") and os.path.getsize("t.mp3") > 1000: return True
        
    oraciones = re.split(r'[.,;?!]', texto)
    oraciones = [o.strip() for o in oraciones if len(o.strip()) > 2]
    archivos = []
    
    for idx, oracion in enumerate(oraciones):
        try:
            url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={urllib.parse.quote(oracion)}&tl=es&client=tw-ob"
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            if r.status_code == 200:
                with open(f"g_{idx}.mp3", "wb") as f: f.write(r.content)
                archivos.append(f"g_{idx}.mp3")
        except: pass
        
    if archivos:
        with open("lista_audio.txt", "w") as f:
            for a in archivos: f.write(f"file '{a}'\n")
        subprocess.run('ffmpeg -y -f concat -safe 0 -i lista_audio.txt -c copy t.mp3', shell=True)
        return True
    return False

# --- EL ANALISTA DE GUION (BUSCADOR INTELIGENTE) ---
def extraer_palabra_clave(texto_chunk, atmosfera):
    basura = ["COMO", "PERO", "PARA", "ESTE", "ESTA", "TODO", "TODA", "NUNCA", "SIEMPRE", "PORQUE", "CUANDO", "DONDE", "QUIEN", "AUNQUE", "INCLUSO", "ADEMAS", "ENTONCES", "REALMENTE", "SOLAMENTE", "TIENES", "PUEDES", "QUIERES", "HACER", "DECIR", "ESTAR", "TENER", "SABER", "PODER", "MUCHO", "POCO", "NADA", "ALGO", "AHORA", "DESPUES", "ANTES", "DESDE", "HASTA", "SOBRE", "ENTRE", "MISMO", "TAMBIEN", "EXACTAMENTE", "HACIA", "CUALQUIER", "MIENTRAS", "SOLO"]
    palabras = re.sub(r'[^A-Z\s]', '', texto_chunk.upper()).split()
    palabras_utiles = [p for p in palabras if len(p) > 4 and p not in basura]

    # Cogemos la palabra más larga y descriptiva del fragmento
    keyword = max(palabras_utiles, key=len) if palabras_utiles else ""

    # Le añadimos el modificador de atmósfera para que el vídeo cuadre visualmente
    if "Terror" in atmosfera: mod = "dark creepy"
    elif "Negocios" in atmosfera: mod = "business finance"
    elif "Espacio" in atmosfera: mod = "space abstract"
    elif "Naturaleza" in atmosfera: mod = "nature landscape"
    else: mod = "epic cinematic"

    return f"{keyword} {mod}".strip()

ATMOSFERAS = ["💀 Terror / Misterio", "💰 Negocios / Lujo", "🌌 Espacio / Ciencia", "🌿 Naturaleza / Paz", "🔥 Motivación / Gym"]

with st.sidebar:
    st.header("⚙️ Controles Visuales")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.selectbox("🎨 Color Subtítulos", ["yellow", "white", "#00FFD1", "#FF0055"])
    atmosfera_elegida = st.selectbox("🎬 Atmósfera Visual", ATMOSFERAS)
    
guion_usuario = st.text_area("📝 Pega tu Guion aquí:", height=200, placeholder="Pega un guion largo (ej. 100 palabras) para que las imágenes tengan sentido...")

if st.button("🚀 CREAR VÍDEO INTELIGENTE HD"):
    if len(guion_usuario.strip()) < 20:
        st.warning("⚠️ El guion es muy corto.")
    else:
        with st.status("🎬 Analizando guion y buscando imágenes que cuadren...", expanded=True) as status:
            subprocess.run("rm -f a_*.mp3 g_*.mp3 v_*.mp4 p_*.mp4 text_*.txt temp_txt.txt lista*.txt music.m4a audio_final.m4a video_mudo.mp4 final.mp4 base.mp4 t.mp3 subs_filter.txt", shell=True)
            
            # 1. VOZ DUAL
            status.write("🎙️ Sintetizando voz...")
            if not generar_voz_inmortal(guion_usuario):
                st.error("❌ Servidores de voz caídos.")
                st.stop()
                
            dur_audio = float(subprocess.check_output("ffprobe -i t.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True).decode('utf-8').strip())

            # 2. MEZCLA DE AUDIO
            status.write("🎵 Añadiendo banda sonora...")
            freq = 60 if "Terror" in atmosfera_elegida else 75
            subprocess.run(f'ffmpeg -y -i t.mp3 -f lavfi -i "sine=f={freq}:d={dur_audio}" -filter_complex "[1:a]volume=0.03[m];[0:a][m]amix=inputs=2:duration=first" -c:a aac -ar 44100 audio_final.m4a', shell=True)

            # 3. ANÁLISIS DE GUION Y BÚSQUEDA INTELIGENTE
            status.write("🎞️ Buscando vídeos que coincidan con tus palabras...")
            clips_finales = []
            dur_escena = dur_audio / 5
            
            # Partimos el texto del usuario en 5 partes iguales
            palabras_guion = guion_usuario.split()
            chunk_size = max(len(palabras_guion) // 5, 1)
            partes_texto = [" ".join(palabras_guion[i*chunk_size : (i+1)*chunk_size]) for i in range(5)]
            if len(partes_texto) > 5: partes_texto[4] += " " + " ".join(palabras_guion[5*chunk_size:])
            
            for i in range(5):
                # Extraemos la palabra clave de ese trozo específico del guion
                busqueda_inteligente = extraer_palabra_clave(partes_texto[i], atmosfera_elegida)
                
                v_url = None
                try:
                    # locale=es-ES permite que Pexels entienda la palabra en español
                    r = requests.get(f"https://api.pexels.com/videos/search?query={urllib.parse.quote(busqueda_inteligente)}&per_page=5&orientation=portrait&locale=es-ES", headers={"Authorization": pexels_key.strip()}, timeout=5).json()
                    if r.get('videos'): v_url = random.choice(r['videos'])['video_files'][0]['link']
                except: pass
                
                # Fallback por si la palabra no se encuentra
                if not v_url:
                    fallback_query = "dark cinematic" if "Terror" in atmosfera_elegida else "business money"
                    try:
                        r = requests.get(f"https://api.pexels.com/videos/search?query={fallback_query}&per_page=3&orientation=portrait", headers={"Authorization": pexels_key.strip()}).json()
                        v_url = r['videos'][0]['video_files'][0]['link']
                    except: pass

                try:
                    if not v_url: raise Exception()
                    with open(f"clip_{i}.mp4", 'wb') as f: f.write(requests.get(v_url, timeout=10).content)
                    zoom_dir = random.choice(["zoom+0.0015", "zoom-0.001"])
                    vf_magic = f"scale=800:1422,zoompan=z='min({zoom_dir},1.5)':d=300:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280,colorchannelmixer=rr=0.7:gg=0.7:bb=0.7,format=yuv420p"
                    subprocess.run(f'ffmpeg -y -stream_loop -1 -i "clip_{i}.mp4" -vf "{vf_magic}" -an -c:v libx264 -preset ultrafast -t {dur_escena} "p_{i}.mp4"', shell=True)
                except:
                    subprocess.run(f'ffmpeg -y -f lavfi -i color=c=black:s=720x1280:d={dur_escena}:r=30 -c:v libx264 -preset ultrafast -format yuv420p "p_{i}.mp4"', shell=True)
                    
                if os.path.exists(f"p_{i}.mp4"): clips_finales.append(f"p_{i}.mp4")

            # Montar Base
            with open("lista.txt", "w") as f:
                for c in clips_finales: f.write(f"file '{c}'\n")
            subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy video_mudo.mp4', shell=True)

            # 4. SUBTÍTULOS CAPCUT HD (Tamaño equilibrado 65)
            status.write("🎬 Mapeando Subtítulos...")
            txt_m = guion_usuario.upper().replace('Á','A').replace('É','E').replace('Í','I').replace('Ó','O').replace('Ú','U').replace('Ñ','N')
            txt_m = re.sub(r'[^A-Z0-9\s]', '', txt_m)
            palabras = txt_m.split()
            
            chunks = [" ".join(palabras[j:j+2]) for j in range(0, len(palabras), 2)]
            if len(chunks) == 0: chunks = ["ERROR"]
            tiempo_por_chunk = dur_audio / len(chunks)
            
            subs_cmd = []
            font_cmd = f"fontfile='{font_abs}':" if os.path.exists(font_path) else ""
            
            for j, chunk in enumerate(chunks):
                t_start = j * tiempo_por_chunk
                t_end = t_start + tiempo_por_chunk
                subs_cmd.append(f"drawtext=text='{chunk}':fontcolor={color_sub}:fontsize=65:{font_cmd}borderw=5:bordercolor=black:shadowcolor=black@0.8:shadowx=4:shadowy=4:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{t_start},{t_end})'")
                
            with open("subs_filter.txt", "w") as f: f.write(",\n".join(subs_cmd))

            # 5. RENDER FINAL
            status.write("✨ Renderizando Master Final...")
            v_final = f"output/v_{int(time.time())}.mp4"
            
            cmd_f = f"""ffmpeg -y -i video_mudo.mp4 -i audio_final.m4a -filter_complex_script subs_filter.txt -c:v libx264 -preset fast -crf 23 -c:a copy -t {dur_audio} "{v_final}" """
            subprocess.run(cmd_f, shell=True)
            
            if os.path.exists(v_final) and os.path.getsize(v_final) > 1000:
                st.success("🔥 ¡VÍDEO INTELIGENTE COMPLETADO! Imágenes acordes al guion.")
                st.video(v_final)
                st.balloons()
            else:
                st.error("❌ Fallo en el renderizado final de FFmpeg.")
