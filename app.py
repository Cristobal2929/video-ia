import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil, math
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V86", layout="centered")

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
    .stSelectbox div[data-baseweb="select"] { background-color: #1e293b; color: white; }
    .info-card { padding: 10px; border-radius: 8px; background: #0f172a; border: 1px solid #00FFD1; text-align: center; color: #00FFD1; margin-bottom: 15px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V86 🎥</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center; color:#94A3B8; margin-bottom: 30px;">IA Hiperrealista • Subtítulos Dinámicos • Zoom Cinemático</div>', unsafe_allow_html=True)

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
    prompt = f"Escribe un guion para TikTok de {longitud_palabras} palabras sobre {tema}. Solo el texto que dirá el locutor, sin emojis, sin poner 'Escena 1', directo al grano."
    url = f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}"
    try:
        r = requests.get(url, timeout=15)
        return re.sub(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ.,! ]', '', r.text).strip()
    except: return "El éxito depende de tu esfuerzo diario. No te rindas nunca y persigue tus sueños."

def extraer_palabra_clave(texto_chunk):
    palabras = re.sub(r'[^\w\s]', '', texto_chunk).split()
    palabras_utiles = [p for p in palabras if len(p) > 4]
    if palabras_utiles: return max(palabras_utiles, key=len)
    return "cinematic"

def preparar_entorno():
    if os.path.exists("taller"): shutil.rmtree("taller")
    os.makedirs("taller", exist_ok=True)

tema = st.text_input("Tema del vídeo:")
color_sub = st.selectbox("🎨 Color Subtítulos", ["yellow", "white", "#00FFD1", "#FF0055"])
duracion_opcion = st.selectbox("Duración del Vídeo:", [
    "Corto (~15 segundos)", 
    "Medio (~30 segundos)", 
    "Largo (~60 segundos)"
])

if st.button("🚀 CREAR VÍDEO CINE IA"):
    if not tema: st.warning("Escribe un tema")
    else:
        preparar_entorno()
        
        if "15" in duracion_opcion:
            palabras_target = 35
            n_escenas = 4
        elif "30" in duracion_opcion:
            palabras_target = 70
            n_escenas = 8
        else:
            palabras_target = 130
            n_escenas = 15
            
        with st.status(f"🎬 Producción de Alta Calidad IA ({duracion_opcion})...", expanded=True) as status:
            
            status.write("🧠 Redactando guion...")
            guion = generar_guion(tema, palabras_target)
            
            status.write("🎙️ Grabando voz HD...")
            audio = "taller/audio.mp3"
            subprocess.run(f'python -m edge_tts --voice es-MX-JorgeNeural --rate=+10% --text "{guion}" --write-media "{audio}"', shell=True)
            if not os.path.exists(audio) or os.path.getsize(audio) < 100:
                subprocess.run(f'ffmpeg -y -f lavfi -i anullsrc=r=44100:cl=mono -t 10 -acodec libmp3lame "{audio}"', shell=True)
            
            dur = 10.0
            try:
                dur = float(subprocess.check_output(f'ffprobe -i "{audio}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
            except: pass
            
            t_por_escena = dur / n_escenas
            dur_frames = int(t_por_escena * 24) # 24 FPS CINEMÁTICOS
            
            status.write(f"🎨 Generando {n_escenas} escenas IA Hiperrealistas...")
            clips = []
            
            palabras_guion = guion.split()
            chunk_size = max(len(palabras_guion) // n_escenas, 1)
            
            for i in range(n_escenas):
                start_idx = i * chunk_size
                end_idx = start_idx + chunk_size if i < n_escenas - 1 else len(palabras_guion)
                texto_del_clip = " ".join(palabras_guion[start_idx:end_idx])
                
                palabra_es = extraer_palabra_clave(texto_del_clip)
                status.write(f"⏳ Escena {i+1}: IA Imaginando '{palabra_es}'...")
                
                # Truco Anti-Bloqueo
                time.sleep(3.0)
                
                img = f"taller/img_{i}.jpg"
                vid = f"taller/vid_{i}.mp4"
                
                # PROMPT MÁGICO: Obligamos a la IA a hacer calidad premium
                prompt_ia = f"{palabra_es} {tema}, hyperrealistic photography, cinematic lighting, 8k resolution, highly detailed, no text"
                url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt_ia)}?width=720&height=1280&nologo=true"
                
                exito = False
                try:
                    r = requests.get(url, timeout=20)
                    if r.status_code == 200:
                        with open(img, 'wb') as f: f.write(r.content)
                        
                        # ZOOM CINEMÁTICO SUAVE A 720p 24FPS
                        vf = f"scale=800:1422,zoompan=z='min(zoom+0.0015,1.2)':d={dur_frames}:s=720x1280:fps=24,format=yuv420p" 
                        subprocess.run(f'ffmpeg -y -loop 1 -i "{img}" -vf "{vf}" -c:v libx264 -preset ultrafast -crf 26 -threads 1 -t {t_por_escena} "{vid}"', shell=True)
                        
                        if os.path.exists(vid): exito = True
                        if os.path.exists(img): os.remove(img)
                except Exception as e: pass
                
                if not exito:
                    if i > 0 and os.path.exists(f"taller/vid_{i-1}.mp4"):
                        subprocess.run(f'cp taller/vid_{i-1}.mp4 "{vid}"', shell=True)
                    else:
                        subprocess.run(f'ffmpeg -y -f lavfi -i color=c=#111827:s=720x1280:d={t_por_escena}:r=24 -c:v libx264 -preset ultrafast "{vid}"', shell=True)
                
                clips.append(f"vid_{i}.mp4")
            
            status.write("🎬 Uniendo secuencias...")
            lista_txt = "taller/lista.txt"
            with open(lista_txt, "w") as f:
                for c in clips: f.write(f"file '{c}'\n")
            
            v_mudo = "taller/mudo.mp4"
            subprocess.run(f'ffmpeg -y -f concat -safe 0 -i "{lista_txt}" -c copy "{v_mudo}"', shell=True)
            
            # EL RETORNO DE LOS SUBTÍTULOS VIRALES DE LA V58
            status.write("✨ Mapeando Subtítulos Dinámicos...")
            texto_seguro = re.sub(r'[^\w\s]', '', guion.replace('\n', ' ').upper()).replace('_', '')
            palabras = texto_seguro.split()
            
            subs_cmd = []
            font_cmd = f"fontfile='{font_abs}':" if os.path.exists(font_path) else ""
            chunks_raw = [palabras[j:j+2] for j in range(0, len(palabras), 2)]
            tiempo_por_chunk = dur / max(len(chunks_raw), 1)
            
            for j, p_list in enumerate(chunks_raw):
                t_start = j * tiempo_por_chunk
                t_end = t_start + tiempo_por_chunk
                
                # Animación de rebote CapCut
                anim_size = f"if(lt(t,{t_start}+0.2),30+(65-30)*(t-{t_start})/0.2,65)"
                
                if len(p_list) == 2 and (len(p_list[0]) + len(p_list[1]) > 12):
                    w1, w2 = p_list[0], p_list[1]
                    subs_cmd.append(f"drawtext=text='{w1}':fontcolor={color_sub}:fontsize='{anim_size}':{font_cmd}borderw=4:bordercolor=black:shadowcolor=black@0.8:shadowx=3:shadowy=3:x=(w-tw)/2:y=(h-th)/2-40:enable='between(t,{t_start},{t_end})'")
                    subs_cmd.append(f"drawtext=text='{w2}':fontcolor={color_sub}:fontsize='{anim_size}':{font_cmd}borderw=4:bordercolor=black:shadowcolor=black@0.8:shadowx=3:shadowy=3:x=(w-tw)/2:y=(h-th)/2+40:enable='between(t,{t_start},{t_end})'")
                else:
                    frase = " ".join(p_list)
                    subs_cmd.append(f"drawtext=text='{frase}':fontcolor={color_sub}:fontsize='{anim_size}':{font_cmd}borderw=4:bordercolor=black:shadowcolor=black@0.8:shadowx=3:shadowy=3:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{t_start},{t_end})'")
            
            with open("taller/subs_filter.txt", "w") as f: f.write(",\n".join(subs_cmd))

            status.write("✨ Renderizando Máster Final HD...")
            final_path = "taller/master.mp4"
            cmd_f = f"""ffmpeg -y -i "{v_mudo}" -i "{audio}" -filter_complex_script taller/subs_filter.txt -c:v libx264 -preset fast -crf 26 -c:a copy -threads 1 -t {dur} "{final_path}" """
            subprocess.run(cmd_f, shell=True)
            
            if os.path.exists(final_path) and os.path.getsize(final_path) > 1000:
                status.update(label="✅ ¡Proceso 100% Completado!", state="complete")
            else:
                st.error("❌ Error al exportar el vídeo final.")
                st.stop()
        
        st.markdown('<div class="info-card">🎉 VÍDEO EXPORTADO. Haz clic en los tres puntitos para descargar.</div>', unsafe_allow_html=True)
        with open(final_path, 'rb') as video_file:
            video_bytes = video_file.read()
        st.video(video_bytes)
