import streamlit as st
import os, time, random, subprocess, textwrap, re, urllib.parse
import requests

st.set_page_config(page_title="Fénix Viral PRO | EL HECHICERO", layout="centered")

# Estética de Élite
st.markdown("""
<style>
    .stApp { background: radial-gradient(circle, #1a1a2e 0%, #16213e 50%, #0f3460 100%); color: #F8FAFC; }
    .pro-title { font-size: 45px; font-weight: 900; background: -webkit-linear-gradient(45deg, #FFD700, #00d2ff, #9d50bb); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 3px; filter: drop-shadow(2px 2px 10px rgba(0,0,0,0.5));}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX HECHICERO V34</div>', unsafe_allow_html=True)
st.markdown('<div class="pro-subtitle" style="text-align:center; color:#94A3B8; margin-bottom: 30px; font-style: italic;">La Versión Verdadera: Magia Cinemática y Estabilidad Absoluta</div>', unsafe_allow_html=True)

# --- INVOCACIÓN DE FUENTES ---
font_path = "Arial.ttf"
if not os.path.exists(font_path):
    try:
        r_font = requests.get("https://github.com/matomo-org/travis-scripts/raw/master/fonts/Arial.ttf", timeout=5)
        with open(font_path, "wb") as f: f.write(r_font.content)
    except: pass

def limpiar_orden(orden):
    return re.sub(r'[^A-Za-zÁÉÍÓÚáéíóúÑñ0-9\s]', '', orden).strip()

def detectar_nicho(tema):
    t = tema.lower()
    if any(w in t for w in ["miedo", "terror", "fantasma", "paranormal", "horror", "misterio", "oscuro"]): return "TERROR"
    if any(w in t for w in ["dinero", "negocio", "invertir", "rico", "millonario", "cripto", "empresa"]): return "NEGOCIOS"
    return "UNIVERSAL"

# --- EL LIBRO DE HECHIZOS (Guiones de Alta Retención) ---
def generar_guion_magico(tema, nicho):
    tema = tema.upper()
    if nicho == "TERROR":
        return [
            {"t": f"No mires este video de noche si le tienes miedo a {tema}.", "s": "creepy dark fog forest"},
            {"t": "Todo el mundo piensa que es un cuento de internet, pero la policia encontro algo macabro.", "s": "scary abandoned asylum"},
            {"t": "Las grabaciones de seguridad revelaron una presencia que desafia toda logica.", "s": "ghost static camera"},
            {"t": "El gobierno intento borrar las pruebas, pero un informante logro filtrar este material.", "s": "secret documents dark"},
            {"t": "Lo peor de todo es que esa cosa sigue ahi fuera. Si escuchas algo hoy, corre. Siguenos para mas.", "s": "creepy shadow monster"}
        ]
    elif nicho == "NEGOCIOS":
        return [
            {"t": f"Te estan robando tu tiempo y tu dinero con {tema} y ni siquiera te has dado cuenta.", "s": "money burn wealth"},
            {"t": "Las grandes elites diseñaron un sistema para que el ciudadano comun fracase siempre.", "s": "dark corporate office"},
            {"t": "Pero un analista financiero acaba de filtrar el patron exacto que usan para ganar.", "s": "stock market data screen"},
            {"t": "La verdadera clave es buscar donde nadie mas esta mirando y adelantarte a la masa.", "s": "luxury life success"},
            {"t": "El sistema esta totalmente roto, es tu momento de aprovecharlo. Siguenos para mas negocios.", "s": "expensive car gold"}
        ]
    else: 
        return [
            {"t": f"Te apuesto lo que quieras a que no sabias la verdad absoluta sobre {tema}.", "s": "mystery cinematic landscape"},
            {"t": "La gran mayoria de la gente vive engañada aceptando la version oficial de los medios.", "s": "crowd people city walking"},
            {"t": "Pero hace muy poco tiempo se revelo un detalle oculto que cambia nuestra historia.", "s": "space nebula cosmic"},
            {"t": "Si prestas atencion a las pequeñas señales, veras la inmensa mentira en la que vivimos.", "s": "eye macro zoom"},
            {"t": "Despierta de una vez y no te dejes manipular nunca mas. Siguenos para descubrir mas secretos.", "s": "epic sunset cinematic"}
        ]

# --- MOTOR DE VOZ FANTASMA (Anti-Baneo) ---
def invocar_voz(texto, archivo):
    texto_limpio = re.sub(r'[^A-Za-zÁÉÍÓÚáéíóúÑñ0-9\s.,]', '', texto)
    with open("spell.txt", "w", encoding="utf-8") as f: f.write(texto_limpio)

    # Hechizo 1: Microsoft
    subprocess.run(["python", "-m", "edge_tts", "--voice", "es-ES-AlvaroNeural", "--rate=0%", "-f", "spell.txt", "--write-media", archivo])
    if os.path.exists(archivo) and os.path.getsize(archivo) > 2000: return True
        
    # Hechizo 2: Google (Salvavidas)
    try:
        url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={urllib.parse.quote(texto_limpio)}&tl=es&client=tw-ob"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if r.status_code == 200:
            with open(archivo, 'wb') as f: f.write(r.content)
            return True
    except: pass
    return False

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3669/3669970.png", width=60)
    st.header("⚙️ Altar del Hechicero")
    pexels_key = st.text_input("🔑 Llave Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.selectbox("🎨 Color de Letra", ["#FFD700", "white", "cyan", "#00FF87"])
    st.caption("Fénix V34 | Modo Dios Activado")

if orden := st.chat_input("Dime el tema y haré magia..."):
    with st.status(f"✨ Invocando el vídeo de '{orden}'...", expanded=True) as status:
        subprocess.run("rm -f a_*.mp3 v_*.mp4 s_*.mp4 text_*.txt spell.txt lista.txt music.mp3 final.mp4 base.mp4", shell=True)
        
        tema_limpio = limpiar_orden(orden)
        nicho = detectar_nicho(orden)
        escenas = generar_guion_magico(tema_limpio, nicho)
        
        clips_finales = []

        for i, esc in enumerate(escenas):
            status.write(f"🔮 Canalizando Escena {i+1}/5...")

            # 1. Voz Indestructible
            if not invocar_voz(esc["t"], f"a_{i}.mp3"):
                st.error("Los servidores de voz están bloqueados. Reintenta en 1 minuto.")
                st.stop()
            
            try:
                dur = float(subprocess.check_output(f"ffprobe -i a_{i}.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True).decode('utf-8').strip())
            except: dur = 3.5

            # 2. Subtítulos de Oro (Sin cuadrados)
            txt_m = esc["t"].upper().replace('Á','A').replace('É','E').replace('Í','I').replace('Ó','O').replace('Ú','U').replace('Ñ','N')
            txt_m = re.sub(r'[^A-Z0-9\s.,]', '', txt_m)
            txt_wrapped = textwrap.fill(txt_m, width=22)
            with open(f"text_{i}.txt", "w", encoding="utf-8", newline='\n') as f: f.write(txt_wrapped)

            # 3. Pexels Dinámico
            v_url = None
            try:
                r = requests.get(f"https://api.pexels.com/videos/search?query={urllib.parse.quote(esc['s'])}&per_page=5&orientation=portrait", headers={"Authorization": pexels_key.strip()}, timeout=5).json()
                if r.get('videos'): v_url = random.choice(r['videos'])['video_files'][0]['link']
            except: pass
            
            if not v_url: # Fallback negro
                subprocess.run(f'ffmpeg -y -f lavfi -i color=c=black:s=720x1280:d=1:r=30 -c:v libx264 -preset ultrafast v_{i}.mp4', shell=True)
            else:
                with open(f"v_{i}.mp4", 'wb') as f: f.write(requests.get(v_url, timeout=10).content)

            # 4. RENDERIZADO MÁGICO (Zoom Cinemático + Formato Universal)
            font_cmd = f"fontfile='{font_path}':" if os.path.exists(font_path) else ""
            zoom_type = random.choice(["zoom+0.002", "zoom-0.001"]) # Mezcla de acercar y alejar cámara
            
            cmd = f"""ffmpeg -y -stream_loop -1 -i v_{i}.mp4 -i a_{i}.mp3 -vf "scale=800:1422,zoompan=z='min({zoom_type},1.5)':d=300:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280,format=yuv420p,drawtext=textfile='text_{i}.txt':fontcolor={color_sub}:fontsize=48:{font_cmd}box=1:boxcolor=black@0.6:boxborderw=15:borderw=2:bordercolor=black:line_spacing=15:x=(w-tw)/2:y=(h-th)/2" -c:v libx264 -preset ultrafast -c:a aac -ar 44100 -t {dur} s_{i}.mp4"""
            subprocess.run(cmd, shell=True)
            if os.path.exists(f"s_{i}.mp4"): clips_finales.append(f"s_{i}.mp4")

        # 5. EL GRAN FINAL
        status.write("🧙‍♂️ Realizando el Ensamblaje Maestro...")
        with open("lista.txt", "w") as f:
            for c in clips_finales: f.write(f"file '{c}'\n")
            
        subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)
        
        v_final = f"output/v_{int(time.time())}.mp4"
        freq = 60 if nicho == "TERROR" else 75
        
        # Música ambiental y sellado de MP4
        cmd_f = f"""ffmpeg -y -i base.mp4 -f lavfi -i "sine=f={freq}:d=120" -filter_complex "[1:a]volume=0.03[m];[0:a][m]amix=inputs=2:duration=first" -c:v copy -c:a aac -ar 44100 "{v_final}" """
        subprocess.run(cmd_f, shell=True)
        
        if os.path.exists(v_final):
            st.success("✨ ¡MAGIA REALIZADA! El Fénix ha renacido con Nivel Agencia.")
            st.video(v_final)
            st.balloons()
