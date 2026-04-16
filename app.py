import streamlit as st
import os, time, random, subprocess, textwrap, re, urllib.parse
import requests

st.set_page_config(page_title="Fénix Viral PRO | V37", layout="centered")

st.markdown("""
<style>
    .stApp { background: radial-gradient(circle, #0f172a 0%, #000000 100%); color: #F8FAFC; }
    .pro-title { font-size: 42px; font-weight: 900; background: -webkit-linear-gradient(45deg, #00FFD1, #FF0055); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 5px; text-transform: uppercase;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX INMORTAL V37</div>', unsafe_allow_html=True)
st.markdown('<div class="pro-subtitle" style="text-align:center; color:#94A3B8; margin-bottom: 30px;">Motor de Emergencia Google • Sincronización Matemática • Cero Fallos</div>', unsafe_allow_html=True)

# 1. DESCARGA DE FUENTE
font_path = "Arial.ttf"
if not os.path.exists(font_path):
    try:
        r = requests.get("https://github.com/matomo-org/travis-scripts/raw/master/fonts/Arial.ttf", timeout=5)
        with open(font_path, "wb") as f: f.write(r.content)
    except: pass

def limpiar_orden(orden):
    return re.sub(r'[^A-Za-zÁÉÍÓÚáéíóúÑñ0-9\s]', '', orden).strip()

def detectar_nicho(tema):
    t = tema.lower()
    if any(w in t for w in ["miedo", "terror", "fantasma", "paranormal", "horror", "misterio"]): return "TERROR"
    if any(w in t for w in ["dinero", "negocio", "invertir", "rico", "millonario", "cripto"]): return "NEGOCIOS"
    return "UNIVERSAL"

def redactar_guion_ia(orden, nicho):
    semilla = random.randint(1, 999999)
    prompt = f"""
    Actúa como un creador de contenido viral de TikTok. Escribe un guion sobre '{orden}'.
    REGLAS:
    - Gancho agresivo.
    - Frases cortas y con mucho ritmo.
    - NO uses emojis ni hashtags.
    - Exactamente 100 palabras.
    - Termina con: 'Síguenos para más'.
    """
    try:
        url = f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}?seed={semilla}&model=openai"
        res = requests.get(url, timeout=15)
        if res.status_code == 200 and len(res.text) > 50:
            return res.text.replace('"', '').replace("'", "").replace('*', '').strip()
    except: pass
    return f"¿Crees que sabes la verdad sobre {orden}? Piénsalo otra vez. Durante años nos han vendido una mentira gigante y casi todo el mundo se la ha tragado. Pero hace muy poco, un grupo de investigadores filtró los datos reales y lo que descubrieron te dejará la sangre helada. Resulta que cada detalle estaba fríamente calculado para mantenernos en la ignorancia. Si miras de cerca, las señales siempre han estado ahí. Ahora que conoces este secreto, ya no pueden engañarte. Abre los ojos de una vez. Síguenos para más."

# 2. MOTOR DE VOZ INMORTAL (El secreto antibloqueos)
def generar_voz_inmortal(texto):
    # Intentamos Microsoft (Alvaro)
    with open("temp_txt.txt", "w", encoding="utf-8") as f: f.write(texto)
    subprocess.run(["python", "-m", "edge_tts", "--voice", "es-ES-AlvaroNeural", "--rate=+5%", "-f", "temp_txt.txt", "--write-media", "t.mp3"])
    
    if os.path.exists("t.mp3") and os.path.getsize("t.mp3") > 1000:
        return True
        
    # Si Microsoft nos bloquea, entra el Motor de Emergencia Google TTS
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
    st.header("⚙️ Configuración")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.selectbox("🎨 Color de Letra", ["yellow", "white", "#00FFD1", "#FF0055"])

if orden := st.chat_input("Dime el tema (El Inmortal superará los bloqueos):"):
    with st.status(f"🚀 Forjando Master Inmortal de '{orden}'...", expanded=True) as status:
        subprocess.run("rm -f a_*.mp3 g_*.mp3 v_*.mp4 clip_*.mp4 p_*.mp4 text_*.txt temp_txt.txt lista*.txt music.mp3 final.mp4 base.mp4 t.mp3 t.vtt subs_filter.txt", shell=True)
        
        tema_limpio = limpiar_orden(orden)
        nicho = detectar_nicho(orden)
        
        status.write("🧠 Escribiendo guion de IA de alto impacto...")
        guion = redactar_guion_ia(tema_limpio, nicho)
        
        # 3. VOZ
        status.write("🎙️ Sintetizando audio continuo (Buscando servidor libre)...")
        if not generar_voz_inmortal(guion):
            st.error("❌ Fallo Crítico: Ni Microsoft ni Google responden. La nube no tiene conexión.")
            st.stop()
            
        dur_audio = float(subprocess.check_output("ffprobe -i t.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True).decode('utf-8').strip())

        # 4. SINCRONIZACIÓN MATEMÁTICA CAPCUT (Adiós al .vtt)
        status.write("🎬 Calculando tiempos de subtítulos...")
        txt_m = guion.upper().replace('Á','A').replace('É','E').replace('Í','I').replace('Ó','O').replace('Ú','U').replace('Ñ','N')
        txt_m = re.sub(r'[^A-Z0-9\s]', '', txt_m)
        palabras = txt_m.split()
        
        # Extraemos keywords para los vídeos
        palabras_fuertes = [p for p in palabras if len(p) > 4]
        if len(palabras_fuertes) < 5: palabras_fuertes = [tema_limpio] * 5
        keywords_videos = random.sample(palabras_fuertes, 5)
        
        # Cortamos en trozos de 2 palabras
        chunks = [" ".join(palabras[j:j+2]) for j in range(0, len(palabras), 2)]
        tiempo_por_chunk = dur_audio / max(len(chunks), 1)
        
        subs_cmd = []
        font_cmd = f"fontfile='{font_path}':" if os.path.exists(font_path) else ""
        
        for j, chunk in enumerate(chunks):
            t_start = j * tiempo_por_chunk
            t_end = t_start + tiempo_por_chunk
            subs_cmd.append(f"drawtext=text='{chunk}':fontcolor={color_sub}:fontsize=85:{font_cmd}borderw=6:bordercolor=black:shadowcolor=black:shadowx=5:shadowy=5:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{t_start},{t_end})'")
            
        with open("subs_filter.txt", "w") as f: f.write(",\n".join(subs_cmd))

        # 5. VÍDEOS PEXELS (5 Escenas exactas)
        status.write("🎞️ Descargando metraje cinematográfico...")
        clips_finales = []
        dur_escena = dur_audio / 5
        
        for i in range(5):
            kw = keywords_videos[i] + (" dark" if nicho == "TERROR" else "")
            v_url = None
            try:
                r = requests.get(f"https://api.pexels.com/videos/search?query={urllib.parse.quote(kw)}&per_page=3&orientation=portrait", headers={"Authorization": pexels_key.strip()}, timeout=5).json()
                if r.get('videos'): v_url = random.choice(r['videos'])['video_files'][0]['link']
            except: pass
            
            try:
                if not v_url: raise Exception()
                with open(f"clip_{i}.mp4", 'wb') as f: f.write(requests.get(v_url, timeout=10).content)
                subprocess.run(f'ffmpeg -y -i "clip_{i}.mp4" -vf "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,fps=30,format=yuv420p" -an -c:v libx264 -preset ultrafast -t {dur_escena} "p_{i}.mp4"', shell=True)
            except:
                subprocess.run(f'ffmpeg -y -f lavfi -i color=c=black:s=720x1280:d={dur_escena}:r=30 -c:v libx264 -preset ultrafast -format yuv420p "p_{i}.mp4"', shell=True)
                
            if os.path.exists(f"p_{i}.mp4"): clips_finales.append(f"p_{i}.mp4")

        # 6. MONTAJE MAESTRO
        status.write("✨ Fusionando componentes...")
        with open("lista.txt", "w") as f:
            for c in clips_finales: f.write(f"file '{c}'\n")
            
        subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy video_mudo.mp4', shell=True)
        v_final = f"output/v_{int(time.time())}.mp4"
        
        cmd_f = f"""ffmpeg -y -stream_loop -1 -i video_mudo.mp4 -i t.mp3 -filter_complex_script subs_filter.txt -c:v libx264 -preset veryfast -c:a aac -ar 44100 -shortest "{v_final}" """
        subprocess.run(cmd_f, shell=True)
        
        if os.path.exists(v_final):
            st.success("🔥 ¡INMORTAL COMPLETADO! El vídeo se generó con éxito saltándose los bloqueos.")
            st.video(v_final)
            st.balloons()
        else:
            st.error("❌ Fallo en el último paso de renderizado.")
