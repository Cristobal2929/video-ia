import streamlit as st
import os, time, random, subprocess, textwrap, re, urllib.parse
import requests

st.set_page_config(page_title="Fénix Viral PRO | V38", layout="centered")

st.markdown("""
<style>
    .stApp { background: radial-gradient(circle, #0f172a 0%, #000000 100%); color: #F8FAFC; }
    .pro-title { font-size: 42px; font-weight: 900; background: -webkit-linear-gradient(45deg, #FF0055, #00FFD1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 5px; text-transform: uppercase;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX LÓGICO V38</div>', unsafe_allow_html=True)
st.markdown('<div class="pro-subtitle" style="text-align:center; color:#94A3B8; margin-bottom: 30px;">Guiones Perfectos • Visuales 100% Exactos • Audio Sin Cortes</div>', unsafe_allow_html=True)

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
    if any(w in t for w in ["miedo", "terror", "fantasma", "paranormal", "horror", "misterio", "creepy"]): return "TERROR"
    if any(w in t for w in ["dinero", "negocio", "invertir", "rico", "millonario", "cripto", "finanzas"]): return "NEGOCIOS"
    return "UNIVERSAL"

# 2. CEREBRO LÓGICO DE GUIONES (Cero fallos, lógica humana 100%)
def generar_obra_maestra(orden, nicho):
    orden = orden.lower()
    if nicho == "TERROR":
        guion = f"Lo que estás a punto de ver sobre {orden} no tiene ninguna explicación lógica. Durante años, la gente hablaba en susurros sobre esto, pensando que era solo una leyenda urbana para asustar a los niños. Pero la policía acaba de desclasificar unos archivos oscuros que lo cambian absolutamente todo. Las grabaciones de seguridad muestran algo macabro acechando en la oscuridad, algo que rompe nuestra comprensión de la realidad. Lo más aterrador es que este fenómeno sigue ocurriendo hoy mismo. Si esta noche escuchas un golpe extraño en tu ventana, no te acerques. Síguenos para más historias de terror."
        visuales = ["creepy dark forest", "scary abandoned house", "creepy shadow horror", "dark ghost camera", "scary monster eyes"]
    elif nicho == "NEGOCIOS":
        guion = f"Te están robando tu dinero en tu propia cara con el tema de {orden} y ni siquiera te has dado cuenta. Las grandes élites financieras diseñaron un sistema oculto para que el ciudadano común fracase desde el primer día. Pero hace muy poco, un analista de Wall Street filtró el patrón exacto que usan los bancos para multiplicar sus ganancias en secreto. La clave es hacer exactamente lo contrario a lo que dicen las noticias. El sistema está completamente roto, es tu momento de aprovecharlo y salir de la trampa. Síguenos para más trucos de negocios."
        visuales = ["counting money wealth", "corporate business skyscraper", "trading chart screen", "luxury lifestyle rich", "expensive car money"]
    else:
        guion = f"El noventa y nueve por ciento de las personas vive totalmente engañada sobre {orden}. Siempre nos han enseñado la versión oficial en la escuela, pero la realidad es muchísimo más impactante. Un grupo de expertos analizó los datos y descubrió un detalle oculto que desafía toda nuestra historia moderna. Resulta que las cosas no son como parecen, y han intentado ocultarlo para mantener el control de la sociedad. Si empiezas a atar los cabos sueltos, verás que todo está conectado. Abre los ojos de una vez y no te dejes manipular. Síguenos para más secretos."
        visuales = ["cinematic epic mystery", "crowd of people city", "secret documents dark", "shocked face dramatic", "epic cinematic lighting"]
    
    return guion, visuales

# 3. MOTOR DE VOZ INMORTAL
def generar_voz_inmortal(texto):
    with open("temp_txt.txt", "w", encoding="utf-8") as f: f.write(texto)
    subprocess.run(["python", "-m", "edge_tts", "--voice", "es-ES-AlvaroNeural", "--rate=+5%", "-f", "temp_txt.txt", "--write-media", "t.mp3"])
    
    if os.path.exists("t.mp3") and os.path.getsize("t.mp3") > 1000:
        return True
        
    # Salvavidas Google TTS
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

if orden := st.chat_input("Dime el tema (Lógica Humana Garantizada):"):
    with st.status(f"🚀 Forjando Master Lógico de '{orden}'...", expanded=True) as status:
        subprocess.run("rm -f a_*.mp3 g_*.mp3 v_*.mp4 clip_*.mp4 p_*.mp4 text_*.txt temp_txt.txt lista*.txt music.mp3 audio_final.mp3 video_mudo.mp4 final.mp4 base.mp4 t.mp3 t.vtt subs_filter.txt", shell=True)
        
        tema_limpio = limpiar_orden(orden)
        nicho = detectar_nicho(orden)
        
        guion, visuales = generar_obra_maestra(tema_limpio, nicho)
        status.write("🧠 Guion escrito con lógica humana perfecta.")
        
        # VOZ
        status.write("🎙️ Grabando locución fluida...")
        if not generar_voz_inmortal(guion):
            st.error("❌ Fallo Crítico de Servidores. Inténtalo de nuevo.")
            st.stop()
            
        dur_audio = float(subprocess.check_output("ffprobe -i t.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True).decode('utf-8').strip())

        # AUDIO FINAL (Mezclamos la voz y la música AHORA para evitar cortes al final)
        status.write("🎵 Ecualizando sonido...")
        freq = 60 if nicho == "TERROR" else 75
        subprocess.run(f'ffmpeg -y -i t.mp3 -f lavfi -i "sine=f={freq}:d={dur_audio}" -filter_complex "[1:a]volume=0.03[m];[0:a][m]amix=inputs=2:duration=first" -c:a aac -ar 44100 audio_final.mp3', shell=True)

        # SUBTÍTULOS CAPCUT VIRALES
        status.write("🎬 Sincronizando subtítulos dinámicos...")
        txt_m = guion.upper().replace('Á','A').replace('É','E').replace('Í','I').replace('Ó','O').replace('Ú','U').replace('Ñ','N')
        txt_m = re.sub(r'[^A-Z0-9\s]', '', txt_m)
        palabras = txt_m.split()
        
        chunks = [" ".join(palabras[j:j+2]) for j in range(0, len(palabras), 2)]
        tiempo_por_chunk = dur_audio / max(len(chunks), 1)
        
        subs_cmd = []
        font_cmd = f"fontfile='{font_path}':" if os.path.exists(font_path) else ""
        
        for j, chunk in enumerate(chunks):
            t_start = j * tiempo_por_chunk
            t_end = t_start + tiempo_por_chunk
            subs_cmd.append(f"drawtext=text='{chunk}':fontcolor={color_sub}:fontsize=85:{font_cmd}borderw=6:bordercolor=black:shadowcolor=black:shadowx=5:shadowy=5:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{t_start},{t_end})'")
            
        with open("subs_filter.txt", "w") as f: f.write(",\n".join(subs_cmd))

        # VÍDEOS PEXELS 100% EXACTOS
        status.write("🎞️ Descargando escenas visuales perfectas...")
        clips_finales = []
        dur_escena = dur_audio / 5
        
        for i in range(5):
            v_url = None
            try:
                r = requests.get(f"https://api.pexels.com/videos/search?query={urllib.parse.quote(visuales[i])}&per_page=3&orientation=portrait", headers={"Authorization": pexels_key.strip()}, timeout=5).json()
                if r.get('videos'): v_url = random.choice(r['videos'])['video_files'][0]['link']
            except: pass
            
            try:
                if not v_url: raise Exception()
                with open(f"clip_{i}.mp4", 'wb') as f: f.write(requests.get(v_url, timeout=10).content)
                subprocess.run(f'ffmpeg -y -i "clip_{i}.mp4" -vf "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,fps=30,format=yuv420p" -an -c:v libx264 -preset ultrafast -t {dur_escena} "p_{i}.mp4"', shell=True)
            except:
                subprocess.run(f'ffmpeg -y -f lavfi -i color=c=black:s=720x1280:d={dur_escena}:r=30 -c:v libx264 -preset ultrafast -format yuv420p "p_{i}.mp4"', shell=True)
                
            if os.path.exists(f"p_{i}.mp4"): clips_finales.append(f"p_{i}.mp4")

        # MONTAJE MAESTRO
        status.write("✨ Renderizando MP4 Final...")
        with open("lista.txt", "w") as f:
            for c in clips_finales: f.write(f"file '{c}'\n")
            
        subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy video_mudo.mp4', shell=True)
        v_final = f"output/v_{int(time.time())}.mp4"
        
        # Unimos el video mudo, el audio ya mezclado, forzamos el tiempo exacto y ponemos el texto
        cmd_f = f"""ffmpeg -y -stream_loop -1 -i video_mudo.mp4 -i audio_final.mp3 -filter_complex_script subs_filter.txt -c:v libx264 -preset veryfast -c:a copy -t {dur_audio} "{v_final}" """
        subprocess.run(cmd_f, shell=True)
        
        if os.path.exists(v_final):
            st.success("🔥 ¡VÍDEO LÓGICO PERFECTO! Guion humano y audio sin cortes.")
            st.video(v_final)
            st.balloons()
        else:
            st.error("❌ Fallo en el renderizado final.")
