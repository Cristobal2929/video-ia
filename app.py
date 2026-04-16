import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil, math, random
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V92", layout="centered")

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
    .pro-title { font-size: 40px; font-weight: 900; background: -webkit-linear-gradient(45deg, #00FFD1, #FFD700); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 5px; text-transform: uppercase;}
    .stSelectbox div[data-baseweb="select"] { background-color: #1e293b; color: white; }
    .info-card { padding: 10px; border-radius: 8px; background: #0f172a; border: 1px solid #00FFD1; text-align: center; color: #00FFD1; margin-bottom: 15px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V92 🎥</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center; color:#94A3B8; margin-bottom: 30px;">Transiciones Suaves • Imágenes Únicas (Seed) • Zoom Dinámico</div>', unsafe_allow_html=True)

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
    prompt = f"Escribe un guion para TikTok de {longitud_palabras} palabras sobre {tema}. Solo el texto que dirá el locutor, sin emojis, directo al grano con un gancho fuerte."
    url = f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}"
    try:
        r = requests.get(url, timeout=15)
        return re.sub(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ.,! ]', '', r.text).strip()
    except: return "El éxito depende de tu esfuerzo diario. No te rindas nunca."

def traducir_a_ingles(palabra):
    try:
        url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(palabra)}&langpair=es|en"
        respuesta = requests.get(url, timeout=5).json()
        return respuesta['responseData']['translatedText']
    except: return palabra

def extraer_palabra_clave(texto_chunk):
    palabras = re.sub(r'[^\w\s]', '', texto_chunk).split()
    palabras_utiles = [p for p in palabras if len(p) > 4]
    if palabras_utiles: return max(palabras_utiles, key=len)
    return "cinematic"

def preparar_entorno():
    if os.path.exists("taller"): shutil.rmtree("taller")
    os.makedirs("taller", exist_ok=True)

with st.sidebar:
    st.header("⚙️ Estilo Visual")
    color_sub = st.selectbox("🎨 Color Subtítulos", ["yellow", "white", "#00FFD1", "#FF0055"])
    estilo_visual = st.text_input("🎨 Ambientación (Ej: Cyberpunk, Luxury, Dark Forest):", value="Luxury cinematic")

tema = st.text_input("🧠 Tema del vídeo para la IA:")
duracion_opcion = st.selectbox("⏱️ Duración del Vídeo:", [
    "Corto (~15 segundos)", 
    "Medio (~30 segundos)", 
    "Largo (~60 segundos)"
])

if st.button("🚀 CREAR VÍDEO FLUIDO (V92)"):
    if not tema: st.warning("⚠️ Escribe un tema para la IA.")
    else:
        preparar_entorno()
        
        if "15" in duracion_opcion: palabras_target = 35
        elif "30" in duracion_opcion: palabras_target = 70
        else: palabras_target = 130
            
        with st.status(f"🎬 Generando Obra de Arte IA ({duracion_opcion})...", expanded=True) as status:
            
            status.write("🧠 IA Redactando guion...")
            guion = generar_guion(tema, palabras_target)
            
            status.write("🎙️ Grabando voz de locutor...")
            audio = "taller/audio.mp3"
            exito_voz = False
            for _ in range(2):
                subprocess.run(f'python -m edge_tts --voice es-MX-JorgeNeural --rate=+10% --text "{guion}" --write-media "{audio}"', shell=True)
                if os.path.exists(audio) and os.path.getsize(audio) > 1000:
                    exito_voz = True
                    break
                time.sleep(1)
            
            if not exito_voz:
                try:
                    url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={urllib.parse.quote(guion[:150])}&tl=es&client=tw-ob"
                    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
                    if r.status_code == 200:
                        with open(audio, "wb") as f: f.write(r.content)
                except: pass
            
            if not os.path.exists(audio) or os.path.getsize(audio) < 100:
                subprocess.run(f'ffmpeg -y -f lavfi -i anullsrc=r=44100:cl=mono -t 15 -acodec libmp3lame "{audio}"', shell=True)
            
            dur = 15.0
            try: dur = float(subprocess.check_output(f'ffprobe -i "{audio}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
            except: pass
            
            num_clips = math.ceil(dur / 3.5)
            t_por_escena = dur / num_clips
            dur_frames = int(t_por_escena * 24)
            
            status.write(f"🎨 Dibujando {num_clips} escenas (Forzando variedad)...")
            clips_finales = []
            palabras_guion = guion.split()
            chunk_size = max(len(palabras_guion) // num_clips, 1)
            
            for i in range(num_clips):
                start_idx = i * chunk_size
                end_idx = start_idx + chunk_size if i < num_clips - 1 else len(palabras_guion)
                texto_del_clip = " ".join(palabras_guion[start_idx:end_idx])
                
                palabra_es = extraer_palabra_clave(texto_del_clip)
                palabra_en = traducir_a_ingles(palabra_es)
                
                status.write(f"⏳ Escena {i+1}: '{palabra_en}'...")
                time.sleep(3.5)
                
                img = f"taller/img_{i}.jpg"
                vid = f"taller/vid_{i}.mp4"
                
                # TRUCO 1: Añadimos un seed aleatorio para forzar a la IA a no repetir la imagen
                seed_aleatorio = random.randint(1, 999999)
                prompt_ia = f"{palabra_en} {estilo_visual}, 8k resolution, Unreal Engine 5 render, hyperrealistic photograph, masterpiece, cinematic lighting, extremely detailed, depth of field"
                url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt_ia)}?width=720&height=1280&nologo=true&seed={seed_aleatorio}"
                
                exito = False
                try:
                    r = requests.get(url, timeout=20)
                    if r.status_code == 200:
                        with open(img, 'wb') as f: f.write(r.content)
                        
                        # TRUCO 2: Zoom aleatorio (hacia adelante o hacia atrás)
                        zoom_dir = random.choice(["z='min(zoom+0.0015,1.2)'", "z='max(1.2-0.0015*on,1.0)'"])
                        vf = f"scale=800:1422,zoompan={zoom_dir}:d={dur_frames}:s=720x1280:fps=24,format=yuv420p" 
                        subprocess.run(f'ffmpeg -y -loop 1 -i "{img}" -vf "{vf}" -c:v libx264 -preset ultrafast -crf 26 -threads 1 -t {t_por_escena} "{vid}"', shell=True)
                        
                        if os.path.exists(vid): exito = True
                        if os.path.exists(img): os.remove(img)
                except: pass
                
                if not exito:
                    if i > 0 and os.path.exists(f"taller/vid_{i-1}.mp4"):
                        subprocess.run(f'cp taller/vid_{i-1}.mp4 "{vid}"', shell=True)
                    else:
                        subprocess.run(f'ffmpeg -y -f lavfi -i color=c=#111827:s=720x1280:d={t_por_escena}:r=24 -c:v libx264 -preset ultrafast "{vid}"', shell=True)
                
                clips_finales.append(f"taller/vid_{i}.mp4")

            status.write("🎬 Fusionando escenas con efecto de transición (Fade)...")
            v_mudo = "taller/mudo.mp4"
            
            # TRUCO 3: El Mega Filtro de Transición (xfade)
            if len(clips_finales) > 1:
                filter_complex = ""
                inputs = ""
                for idx, c in enumerate(clips_finales):
                    inputs += f"-i {c} "
                    if idx == 0:
                        filter_complex += f"[0:v]settb=AVTB[v0];"
                    else:
                        filter_complex += f"[{idx}:v]settb=AVTB[v{idx}];"
                
                # Montar la cadena de fundidos cruzados (0.5 segundos)
                offset = t_por_escena - 0.5
                curr_offset = offset
                last_out = "[v0]"
                
                for k in range(1, len(clips_finales)):
                    out_name = f"[fade{k}]" if k < len(clips_finales)-1 else "[outv]"
                    filter_complex += f"{last_out}[v{k}]xfade=transition=fade:duration=0.5:offset={curr_offset}{out_name};"
                    last_out = f"[fade{k}]"
                    curr_offset += offset
                
                cmd_merge = f"ffmpeg -y {inputs} -filter_complex \"{filter_complex[:-1]}\" -map \"[outv]\" -c:v libx264 -preset fast -crf 25 {v_mudo}"
                subprocess.run(cmd_merge, shell=True)
            else:
                subprocess.run(f'cp {clips_finales[0]} {v_mudo}', shell=True)

            status.write("✨ Mapeando Subtítulos Inmortales...")
            texto_seguro = re.sub(r'[^\w\s]', '', guion.replace('\n', ' ').upper()).replace('_', '')
            palabras = texto_seguro.split()
            
            subs_cmd = []
            font_cmd = f"fontfile='{font_abs}':" if os.path.exists(font_abs) else ""
            chunks_raw = [palabras[j:j+2] for j in range(0, len(palabras), 2)]
            tiempo_por_chunk = dur / max(len(chunks_raw), 1)
            
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
            
            with open("taller/subs_filter.txt", "w") as f: f.write(",\n".join(subs_cmd))

            status.write("✨ Renderizando Máster Final HD...")
            final_path = "taller/master.mp4"
            cmd_f = f"""ffmpeg -y -i "{v_mudo}" -i "{audio}" -filter_complex_script taller/subs_filter.txt -c:v libx264 -preset fast -crf 25 -c:a copy -threads 1 -t {dur} "{final_path}" """
            subprocess.run(cmd_f, shell=True)
            
            if os.path.exists(final_path) and os.path.getsize(final_path) > 1000:
                status.update(label="✅ ¡Proceso 100% Completado!", state="complete")
            else:
                st.error("❌ Error crítico en el renderizado.")
                st.stop()
        
        st.markdown('<div class="info-card">🎉 VÍDEO EXPORTADO. Haz clic derecho o pulsa para descargar.</div>', unsafe_allow_html=True)
        with open(final_path, 'rb') as video_file:
            st.video(video_file.read())
