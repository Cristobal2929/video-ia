import streamlit as st
import os, time, random, subprocess, textwrap, re, urllib.parse
import requests

st.set_page_config(page_title="Fénix Viral PRO | V36", layout="centered")

st.markdown("""
<style>
    .stApp { background: radial-gradient(circle, #0f172a 0%, #000000 100%); color: #F8FAFC; }
    .pro-title { font-size: 40px; font-weight: 900; background: -webkit-linear-gradient(45deg, #FF0055, #00FFD1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 5px; text-transform: uppercase;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX CINEASTA V36</div>', unsafe_allow_html=True)
st.markdown('<div class="pro-subtitle" style="text-align:center; color:#94A3B8; margin-bottom: 30px;">Guiones de IA Reales • Audio Continuo Sin Cortes • Subtítulos CapCut</div>', unsafe_allow_html=True)

# 1. DESCARGAR FUENTE
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

# 2. CEREBRO DE INTELIGENCIA ARTIFICIAL (Guiones Virales Reales)
def redactar_guion_ia(orden, nicho):
    semilla = random.randint(1, 999999)
    prompt = f"""
    Actúa como un creador de contenido viral de TikTok. Escribe un guion fascinante y espectacular sobre '{orden}'.
    REGLAS:
    - Empieza con un gancho agresivo que genere intriga.
    - Escribe frases cortas y con mucho ritmo.
    - NO uses emojis. NO uses hashtags. SOLO TEXTO.
    - Exactamente 100 palabras.
    - Termina con: 'Síguenos para más'.
    """
    try:
        url = f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}?seed={semilla}&model=openai"
        res = requests.get(url, timeout=15)
        if res.status_code == 200 and len(res.text) > 50:
            return res.text.replace('"', '').replace("'", "").replace('*', '').strip()
    except: pass
    
    # Fallback Viral si la IA falla
    return f"¿Crees que sabes la verdad sobre {orden}? Piénsalo otra vez. Durante años nos han vendido una mentira gigante y casi todo el mundo se la ha tragado. Pero hace muy poco, un grupo de investigadores filtró los datos reales y lo que descubrieron te dejará la sangre helada. Resulta que cada detalle estaba fríamente calculado para mantenernos en la ignorancia. Si miras de cerca, las señales siempre han estado ahí, justo delante de tus narices. Ahora que conoces este secreto, ya no pueden engañarte. Abre los ojos de una vez. Síguenos para más."

def time_to_sec(t_str):
    try:
        t_str = t_str.strip().split(' ')[0].replace(',', '.')
        partes = t_str.split(':')
        if len(partes) == 3: return float(partes[0])*3600 + float(partes[1])*60 + float(partes[2])
        elif len(partes) == 2: return float(partes[0])*60 + float(partes[1])
        else: return float(partes[0])
    except: return 0

with st.sidebar:
    st.header("⚙️ Configuración")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.selectbox("🎨 Color de Letra", ["#FFD700", "white", "#00FFD1"])

if orden := st.chat_input("Dime el tema (Guion IA y Audio Perfecto):"):
    with st.status(f"🚀 Produciendo Máster de '{orden}'...", expanded=True) as status:
        subprocess.run("rm -f a_*.mp3 v_*.mp4 clip_*.mp4 p_*.mp4 text_*.txt temp_txt.txt lista.txt music.mp3 final.mp4 base.mp4 t.mp3 t.vtt subs_filter.txt", shell=True)
        
        tema_limpio = limpiar_orden(orden)
        nicho = detectar_nicho(orden)
        
        status.write("🧠 La IA está escribiendo el guion viral...")
        guion = redactar_guion_ia(tema_limpio, nicho)
        
        # 3. AUDIO CONTINUO (La cura para los cortes de sonido)
        status.write("🎙️ Grabando audio continuo...")
        texto_limpio = re.sub(r'[^A-Za-zÁÉÍÓÚáéíóúÑñ0-9\s.,?!]', '', guion)
        with open("temp_txt.txt", "w", encoding="utf-8") as f: f.write(texto_limpio)
        
        # Generamos un solo audio y un archivo VTT con los tiempos
        subprocess.run(["python", "-m", "edge_tts", "--voice", "es-ES-AlvaroNeural", "--rate=+5%", "-f", "temp_txt.txt", "--write-media", "t.mp3", "--write-subtitles", "t.vtt"])
        
        if not os.path.exists("t.mp3") or os.path.getsize("t.mp3") < 1000:
            st.error("❌ Los servidores de voz están saturados. Inténtalo de nuevo.")
            st.stop()
            
        dur_audio = float(subprocess.check_output("ffprobe -i t.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True).decode('utf-8').strip())

        # 4. SUBTÍTULOS CAPCUT (2 PALABRAS POR PANTALLA, SIN CUADRADOS)
        status.write("🎬 Diseñando subtítulos dinámicos...")
        escenas = []
        subs_cmd = []
        font_cmd = f"fontfile='{font_path}':" if os.path.exists(font_path) else ""
        
        try:
            with open('t.vtt', 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for i in range(len(lines)):
                    if "-->" in lines[i]:
                        start = time_to_sec(lines[i].split(" --> ")[0])
                        end = time_to_sec(lines[i].split(" --> ")[1])
                        txt_original = lines[i+1].strip().upper()
                        
                        # Limpiar texto (sin tildes, sin signos raros)
                        txt_m = txt_original.replace('Á','A').replace('É','E').replace('Í','I').replace('Ó','O').replace('Ú','U').replace('Ñ','N')
                        txt_m = re.sub(r'[^A-Z0-9\s]', '', txt_m)
                        
                        palabras = txt_m.split()
                        if not palabras: continue
                        
                        # Guardamos palabras clave para buscar vídeos
                        kw = [p for p in palabras if len(p) > 4]
                        escenas.append({"keyword": kw[-1] if kw else tema_limpio, "duration": end - start})
                        
                        # Agrupar en trozos de 2 palabras (Efecto Viral)
                        chunks = [" ".join(palabras[j:j+2]) for j in range(0, len(palabras), 2)]
                        tiempo_por_chunk = (end - start) / len(chunks)
                        
                        for j, chunk in enumerate(chunks):
                            t_start = start + (j * tiempo_por_chunk)
                            t_end = t_start + tiempo_por_chunk
                            subs_cmd.append(f"drawtext=text='{chunk}':fontcolor={color_sub}:fontsize=85:{font_cmd}borderw=6:bordercolor=black:shadowcolor=black:shadowx=5:shadowy=5:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{t_start},{t_end})'")
        except: pass
        
        with open("subs_filter.txt", "w") as f: f.write(",\n".join(subs_cmd))

        # 5. VÍDEOS PEXELS
        status.write("🎞️ Buscando vídeos cinematográficos...")
        clips_finales = []
        
        # Si el VTT falló, metemos el tema por defecto
        if not escenas: escenas = [{"keyword": tema_limpio, "duration": dur_audio}]
        
        for i, esc in enumerate(escenas):
            if esc["duration"] <= 0: continue
            
            # Buscar en Pexels
            v_url = None
            try:
                q_busqueda = esc["keyword"] + (" dark" if nicho == "TERROR" else "")
                r = requests.get(f"https://api.pexels.com/videos/search?query={urllib.parse.quote(q_busqueda)}&per_page=3&orientation=portrait", headers={"Authorization": pexels_key.strip()}, timeout=5).json()
                if r.get('videos'): v_url = random.choice(r['videos'])['video_files'][0]['link']
            except: pass
            
            try:
                if not v_url: raise Exception()
                with open(f"clip_{i}.mp4", 'wb') as f: f.write(requests.get(v_url, timeout=10).content)
                subprocess.run(f'ffmpeg -y -i "clip_{i}.mp4" -vf "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,fps=30,format=yuv420p" -an -c:v libx264 -preset ultrafast -t {esc["duration"]} "p_{i}.mp4"', shell=True)
            except:
                subprocess.run(f'ffmpeg -y -f lavfi -i color=c=black:s=720x1280:d={esc["duration"]}:r=30 -c:v libx264 -preset ultrafast -format yuv420p "p_{i}.mp4"', shell=True)
                
            if os.path.exists(f"p_{i}.mp4"): clips_finales.append(f"p_{i}.mp4")

        # 6. MONTAJE MAESTRO
        status.write("✨ Fusionando audio continuo y metraje...")
        with open("lista.txt", "w") as f:
            for c in clips_finales: f.write(f"file '{c}'\n")
            
        # Unimos solo el vídeo (sin audio)
        subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy video_mudo.mp4', shell=True)
        
        v_final = f"output/v_{int(time.time())}.mp4"
        
        # Planche Final: Vídeo mudo + Audio continuo + Subtítulos
        cmd_f = f"""ffmpeg -y -stream_loop -1 -i video_mudo.mp4 -i t.mp3 -filter_complex_script subs_filter.txt -c:v libx264 -preset veryfast -c:a aac -ar 44100 -shortest "{v_final}" """
        subprocess.run(cmd_f, shell=True)
        
        if os.path.exists(v_final):
            st.success("🔥 ¡CINEASTA VIRAL COMPLETADO! Audio perfecto y guion de IA.")
            st.video(v_final)
            st.balloons()
        else:
            st.error("❌ Fallo en el último paso de renderizado.")
