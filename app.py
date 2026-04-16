import streamlit as st
import os, time, random, subprocess, textwrap, re, urllib.parse, math
import requests

st.set_page_config(page_title="Fénix Estudio PRO | V46", layout="centered")

st.markdown("""
<style>
    .stApp { background: radial-gradient(circle, #0f172a 0%, #000000 100%); color: #F8FAFC; }
    .pro-title { font-size: 45px; font-weight: 900; background: -webkit-linear-gradient(45deg, #00FFD1, #FFD700); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 5px; text-transform: uppercase;}
    .stTextArea textarea, .stTextInput input { background-color: #1e293b !important; color: #ffffff !important; border: 2px solid #00FFD1 !important; border-radius: 10px; font-size: 16px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V46</div>', unsafe_allow_html=True)
st.markdown('<div class="pro-subtitle" style="text-align:center; color:#94A3B8; margin-bottom: 30px;">Edición B-Roll • Cortes Rápidos de 3 Segundos • Metraje 4K Exacto</div>', unsafe_allow_html=True)

font_path = "Arial.ttf"
if not os.path.exists(font_path):
    try:
        r = requests.get("https://github.com/matomo-org/travis-scripts/raw/master/fonts/Arial.ttf", timeout=5)
        with open(font_path, "wb") as f: f.write(r.content)
    except: pass
font_abs = os.path.abspath(font_path).replace('\\', '/')

def generar_voz_inmortal(texto, codigo_voz):
    with open("temp_txt.txt", "w", encoding="utf-8") as f: f.write(texto)
    subprocess.run(["python", "-m", "edge_tts", "--voice", codigo_voz, "--rate=+5%", "-f", "temp_txt.txt", "--write-media", "t.mp3"])
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

with st.sidebar:
    st.header("⚙️ Controles de Producción")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    
    voz_elegida = st.selectbox("🗣️ Voz del Locutor", ["🎙️ Jorge (Latino - Muy Natural)", "🎙️ Elvira (Española - Femenina)", "🎙️ Alvaro (Español - Clásico)"])
    if "Jorge" in voz_elegida: codigo_voz = "es-MX-JorgeNeural"
    elif "Elvira" in voz_elegida: codigo_voz = "es-ES-ElviraNeural"
    else: codigo_voz = "es-ES-AlvaroNeural"

    color_sub = st.selectbox("🎨 Color Subtítulos", ["yellow", "white", "#00FFD1", "#FF0055"])
    musica_tipo = st.selectbox("🎵 Tipo de Música", ["Misterio / Tensión (60Hz)", "Acción / Negocios (75Hz)"])

st.markdown("### 1. El Guion")
guion_usuario = st.text_area("📝 Pega tu Guion aquí:", height=150, placeholder="Ejemplo: El 99% de las personas no sabe esto...")

st.markdown("### 2. Lo que se verá de fondo")
tema_broll = st.text_input("🔍 ¿De qué va el vídeo exactamente? (Para buscar los vídeos 4K):", placeholder="Ej: Coches de lujo, Bosque oscuro, Hackers, Wall Street...")

if st.button("🚀 CREAR VÍDEO B-ROLL (CORTES RÁPIDOS)"):
    if len(guion_usuario.strip()) < 20 or len(tema_broll.strip()) < 3:
        st.warning("⚠️ Rellena tanto el guion como el tema de fondo para continuar.")
    else:
        with st.status("🎬 Descargando 4K y cortando cachos dinámicos...", expanded=True) as status:
            subprocess.run("rm -f a_*.mp3 g_*.mp3 v_*.mp4 p_*.mp4 text_*.txt temp_txt.txt lista*.txt music.m4a audio_final.m4a video_mudo.mp4 final.mp4 base.mp4 t.mp3 subs_filter.txt", shell=True)
            
            # 1. VOZ
            status.write("🎙️ Grabando locución premium...")
            if not generar_voz_inmortal(guion_usuario, codigo_voz):
                st.error("❌ Servidores de voz caídos.")
                st.stop()
                
            dur_audio = float(subprocess.check_output("ffprobe -i t.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True).decode('utf-8').strip())

            # 2. AUDIO Y MÚSICA
            status.write("🎵 Ecualizando sonido...")
            freq = 60 if "Misterio" in musica_tipo else 75
            subprocess.run(f'ffmpeg -y -i t.mp3 -f lavfi -i "sine=f={freq}:d={dur_audio}" -filter_complex "[1:a]volume=0.03[m];[0:a][m]amix=inputs=2:duration=first" -c:a aac -ar 44100 audio_final.m4a', shell=True)

            # 3. EDICIÓN B-ROLL (CORTAR CACHOS)
            status.write("🎞️ Descargando piscina de vídeos 4K exactos al tema...")
            
            # Calculamos cuántos cortes de ~3.5 segundos necesitamos
            dur_corte = 3.5
            num_clips = math.ceil(dur_audio / dur_corte)
            
            pool_urls = []
            try:
                # Buscamos masivamente con el tema que puso el usuario + la palabra "4k"
                query_limpia = urllib.parse.quote(f"{tema_broll} 4k motion")
                r = requests.get(f"https://api.pexels.com/videos/search?query={query_limpia}&per_page=15&size=large&orientation=portrait&locale=es-ES", headers={"Authorization": pexels_key.strip()}, timeout=10).json()
                if r.get('videos'):
                    pool_urls = [v['video_files'][0]['link'] for v in r['videos']]
            except: pass
            
            # Si no encuentra nada, metemos un comodín
            if not pool_urls:
                st.warning("No se encontraron suficientes vídeos con ese término exacto, usando vídeos cinematográficos por defecto.")
                r = requests.get(f"https://api.pexels.com/videos/search?query=cinematic%204k&per_page=10&size=large&orientation=portrait", headers={"Authorization": pexels_key.strip()}).json()
                pool_urls = [v['video_files'][0]['link'] for v in r.get('videos', [])]

            clips_finales = []
            status.write(f"✂️ Haciendo {num_clips} cortes dinámicos rápidos...")
            
            for i in range(num_clips):
                v_url = pool_urls[i % len(pool_urls)] if pool_urls else None
                
                # Tiempo de este cacho (el último cacho se ajusta al sobrante exacto del audio)
                tiempo_este_clip = dur_corte if i < num_clips - 1 else dur_audio - (i * dur_corte)
                if tiempo_este_clip <= 0: continue

                try:
                    with open(f"clip_{i}.mp4", 'wb') as f: f.write(requests.get(v_url, timeout=10).content)
                    
                    # MAGIA DEL CORTE: Empezamos a cortar desde el segundo 1 o 2 del vídeo original para saltar intros negras (-ss)
                    start_cut = random.randint(1, 3)
                    zoom_dir = random.choice(["zoom+0.002", "zoom-0.001"])
                    
                    vf_magic = f"scale=800:1422,zoompan=z='min({zoom_dir},1.5)':d=300:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280,colorchannelmixer=rr=0.7:gg=0.7:bb=0.7,format=yuv420p"
                    
                    subprocess.run(f'ffmpeg -y -ss {start_cut} -i "clip_{i}.mp4" -vf "{vf_magic}" -an -c:v libx264 -preset ultrafast -t {tiempo_este_clip} "p_{i}.mp4"', shell=True)
                except:
                    subprocess.run(f'ffmpeg -y -f lavfi -i color=c=black:s=720x1280:d={tiempo_este_clip}:r=30 -c:v libx264 -preset ultrafast -format yuv420p "p_{i}.mp4"', shell=True)
                    
                if os.path.exists(f"p_{i}.mp4"): clips_finales.append(f"p_{i}.mp4")

            # Pegar los cachos
            with open("lista.txt", "w") as f:
                for c in clips_finales: f.write(f"file '{c}'\n")
            subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy video_mudo.mp4', shell=True)

            # 4. SUBTÍTULOS CAPCUT HD
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
            status.write("✨ Exportando con Edición B-Roll HD...")
            v_final = f"output/v_{int(time.time())}.mp4"
            
            cmd_f = f"""ffmpeg -y -i video_mudo.mp4 -i audio_final.m4a -filter_complex_script subs_filter.txt -c:v libx264 -preset fast -crf 23 -c:a copy -t {dur_audio} "{v_final}" """
            subprocess.run(cmd_f, shell=True)
            
            if os.path.exists(v_final) and os.path.getsize(v_final) > 1000:
                st.success("🔥 ¡VÍDEO COMPLETADO! Cortes dinámicos y fondo 100% fiel al tema.")
                st.video(v_final)
                st.balloons()
            else:
                st.error("❌ Fallo en el renderizado final de FFmpeg.")
