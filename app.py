import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil, math, random
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V98", layout="centered")

# Mantener pantalla activa
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

st.markdown('<div class="pro-title">FÉNIX STUDIO V98 🎥</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center; color:#94A3B8; margin-bottom: 30px;">Guion IA + Vídeos Reales + Subs CapCut + Fix Final</div>', unsafe_allow_html=True)

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
    st.header("⚙️ Configuración")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.selectbox("🎨 Color Subtítulos", ["yellow", "white", "#00FFD1", "#FF0055"])
    estilo_visual = st.text_input("🎨 Filtro Visual (Ej: Dark, Luxury, Cinematic):", value="Cinematic")

tema = st.text_input("🧠 Tema del vídeo para la IA:")
duracion_opcion = st.selectbox("⏱️ Duración del Vídeo:", [
    "Corto (~15 segundos)", 
    "Medio (~30 segundos)", 
    "Largo (~60 segundos)"
])

if st.button("🚀 CREAR VÍDEO (FIX FINAL V98)"):
    if not tema: st.warning("⚠️ Escribe un tema para la IA.")
    else:
        preparar_entorno()
        
        if "15" in duracion_opcion: palabras_target = 35; dur_corte = 3.5
        elif "30" in duracion_opcion: palabras_target = 70; dur_corte = 3.5
        else: palabras_target = 130; dur_corte = 3.5
            
        with st.status(f"🎬 Fabricando contenido ({duracion_opcion})...", expanded=True) as status:
            
            status.write("🧠 IA Redactando guion único...")
            guion = generar_guion(tema, palabras_target)
            
            status.write("🎙️ Grabando voz de locutor...")
            audio = "taller/audio.mp3"
            subprocess.run(f'python -m edge_tts --voice es-MX-JorgeNeural --rate=+10% --text "{guion}" --write-media "{audio}"', shell=True)
            
            dur = 15.0
            try: dur = float(subprocess.check_output(f'ffprobe -i "{audio}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
            except: pass
            
            num_clips = math.ceil(dur / dur_corte)
            status.write(f"🎞️ Buscando {num_clips} chachitos de vídeo reales...")
            clips_finales = []
            palabras_guion = guion.split()
            chunk_size = max(len(palabras_guion) // num_clips, 1)
            
            for i in range(num_clips):
                start_idx = i * chunk_size
                end_idx = start_idx + chunk_size if i < num_clips - 1 else len(palabras_guion)
                texto_del_clip = " ".join(palabras_guion[start_idx:end_idx])
                
                palabra_es = extraer_palabra_clave(texto_del_clip)
                palabra_en = traducir_a_ingles(palabra_es)
                query_busqueda = urllib.parse.quote(f"{palabra_en} {estilo_visual} 4k")
                status.write(f"🔍 Escena {i+1}: IA busca '{palabra_en}'...")

                t_clip = dur_corte if i < num_clips - 1 else (dur - (i * dur_corte)) + 1.0 
                if t_clip <= 0: t_clip = 1.0
                
                v_url = None
                try:
                    r = requests.get(f"https://api.pexels.com/videos/search?query={query_busqueda}&per_page=5&size=large&orientation=portrait", headers={"Authorization": pexels_key.strip()}, timeout=10).json()
                    if r.get('videos'): v_url = random.choice(r['videos'])['video_files'][0]['link']
                except: pass
                
                exito_descarga = False
                vid = f"taller/vid_{i}.mp4"
                if v_url:
                    try:
                        vid_data = requests.get(v_url, timeout=15).content
                        with open(f"taller/raw_{i}.mp4", 'wb') as f: f.write(vid_data)
                        vf = "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,colorchannelmixer=rr=0.7:gg=0.7:bb=0.7,vignette=PI/3,format=yuv420p"
                        subprocess.run(f'ffmpeg -y -stream_loop -1 -i "taller/raw_{i}.mp4" -vf "{vf}" -an -c:v libx264 -r 30 -preset ultrafast -t {t_clip} "{vid}"', shell=True)
                        if os.path.exists(vid): exito_descarga = True
                    except: pass
                
                if not exito_descarga:
                    if i > 0 and os.path.exists(f"taller/vid_{i-1}.mp4"):
                        subprocess.run(f'cp taller/vid_{i-1}.mp4 "{vid}"', shell=True)
                    else:
                        subprocess.run(f'ffmpeg -y -f lavfi -i color=c=#111827:s=720x1280:d={t_clip}:r=30 -c:v libx264 -preset ultrafast "{vid}"', shell=True)
                
                clips_finales.append(f"vid_{i}.mp4")

            status.write("🎬 Uniendo secuencias...")
            with open("taller/lista.txt", "w") as f:
                for c in clips_finales: f.write(f"file '{c}'\n")
            
            v_mudo = "taller/mudo.mp4"
            subprocess.run(f'ffmpeg -y -f concat -safe 0 -i taller/lista.txt -c copy "{v_mudo}"', shell=True)

            status.write("✨ Añadiendo Subtítulos CapCut...")
            texto_seguro = re.sub(r'[^\w\s]', '', guion.replace('\n', ' ').upper()).replace('_', '')
            palabras = texto_seguro.split()
            
            subs_cmd = []
            font_cmd = f"fontfile='{font_abs}':" if os.path.exists(font_path) else ""
            chunks_raw = [palabras[j:j+2] for j in range(0, len(palabras), 2)]
            tiempo_por_chunk = dur / max(len(chunks_raw), 1)
            
            for j, p_list in enumerate(chunks_raw):
                t_start = j * tiempo_por_chunk
                t_end = t_start + tiempo_por_chunk
                anim_size = f"if(lt(t,{t_start}+0.2),30+(65-30)*(t-{t_start})/0.2,65)"
                
                if len(p_list) == 2 and (len(p_list[0]) + len(p_list[1]) > 12):
                    w1, w2 = p_list[0], p_list[1]
                    subs_cmd.append(f"drawtext=text='{w1}':fontcolor={color_sub}:fontsize='{anim_size}':{font_cmd}borderw=5:bordercolor=black:shadowcolor=black@0.8:shadowx=4:shadowy=4:x=(w-tw)/2:y=(h-th)/2-40:enable='between(t,{t_start},{t_end})'")
                    subs_cmd.append(f"drawtext=text='{w2}':fontcolor={color_sub}:fontsize='{anim_size}':{font_cmd}borderw=5:bordercolor=black:shadowcolor=black@0.8:shadowx=4:shadowy=4:x=(w-tw)/2:y=(h-th)/2+40:enable='between(t,{t_start},{t_end})'")
                else:
                    frase = " ".join(p_list)
                    subs_cmd.append(f"drawtext=text='{frase}':fontcolor={color_sub}:fontsize='{anim_size}':{font_cmd}borderw=5:bordercolor=black:shadowcolor=black@0.8:shadowx=4:shadowy=4:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{t_start},{t_end})'")
            
            # EL FIX: Guardamos el archivo con el nombre EXACTO en minúsculas
            with open("taller/subs_filter.txt", "w") as f: f.write(",\n".join(subs_cmd))

            status.write("✨ Compilando Máster Final...")
            final_path = "taller/master.mp4"
            # EL FIX: FFmpeg busca el archivo EXACTO en minúsculas
            cmd_f = f"""ffmpeg -y -i "{v_mudo}" -i "{audio}" -filter_complex_script taller/subs_filter.txt -c:v libx264 -preset fast -crf 25 -c:a copy -threads 1 -t {dur} "{final_path}" """
            subprocess.run(cmd_f, shell=True)
            
            if os.path.exists(final_path) and os.path.getsize(final_path) > 1000:
                status.update(label="✅ ¡Proceso 100% Completado!", state="complete")
            else:
                st.error("❌ Error crítico en el renderizado final. Revisa los logs.")
                st.stop()
        
        st.markdown('<div class="info-card">🎉 VÍDEO EXPORTADO. Haz clic derecho o mantén pulsado para descargar.</div>', unsafe_allow_html=True)
        with open(final_path, 'rb') as video_file:
            st.video(video_file.read())
