import streamlit as st
import os, time, random, subprocess, re, urllib.parse
import requests

st.set_page_config(page_title="Fénix Viral PRO | V35", layout="centered")

st.markdown("""
<style>
    .stApp { background: radial-gradient(circle, #111827 0%, #000000 100%); color: #F8FAFC; }
    .pro-title { font-size: 42px; font-weight: 900; background: -webkit-linear-gradient(45deg, #FFD700, #FFA500); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 2px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX TIKTOK V35</div>', unsafe_allow_html=True)
st.markdown('<div class="pro-subtitle" style="text-align:center; color:#94A3B8; margin-bottom: 30px;">Subtítulos Dinámicos 2 a 2 • Letra Gigante • Cero Cajas Negras</div>', unsafe_allow_html=True)

# 1. DESCARGA DE FUENTE UNIVERSAL ARIAL BOLD
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
    if any(w in t for w in ["miedo", "terror", "fantasma", "paranormal", "horror", "misterio"]): return "TERROR"
    if any(w in t for w in ["dinero", "negocio", "invertir", "rico", "millonario", "cripto"]): return "NEGOCIOS"
    return "UNIVERSAL"

def generar_master_guion(tema, nicho):
    tema = tema.upper()
    if nicho == "TERROR":
        return [
            {"t": f"No mires este video de noche si le temes a {tema}", "s": "creepy dark shadows horror"},
            {"t": "Todo el mundo piensa que es un invento pero la policia encontro algo macabro", "s": "scary abandoned house dark"},
            {"t": "Las grabaciones de seguridad mostraron algo que rompe la logica humana", "s": "creepy ghost surveillance"},
            {"t": "El gobierno intento ocultarlo pero un informante filtro los videos", "s": "hacker computer screen dark"},
            {"t": "Si escuchas un ruido extraño hoy no abras la puerta Siguenos para mas", "s": "scary monster dark eyes"}
        ]
    elif nicho == "NEGOCIOS":
        return [
            {"t": f"Te estan robando el dinero con {tema} y ni siquiera te has dado cuenta", "s": "counting money wealth"},
            {"t": "Las grandes elites diseñaron un sistema para que fracases desde el principio", "s": "corporate business skyscraper"},
            {"t": "Pero un analista financiero acaba de filtrar el patron exacto para ganar", "s": "trading chart screen success"},
            {"t": "La clave es buscar donde nadie mas mira y adelantarse al resto", "s": "rich lifestyle luxury"},
            {"t": "El sistema esta roto es tu momento de aprovecharlo Siguenos para mas", "s": "luxury car money rain"}
        ]
    else: 
        return [
            {"t": f"Te apuesto lo que quieras a que no sabias la verdad sobre {tema}", "s": "curious mystery cinematic epic"},
            {"t": "La gran mayoria de la gente vive engañada aceptando la version oficial", "s": "crowd of people walking city"},
            {"t": "Pero hace poco tiempo se revelo un detalle oculto que lo cambia todo", "s": "secret documents investigation"},
            {"t": "Si prestas atencion a los pequeños detalles veras la inmensa mentira", "s": "shocked face dramatic lighting"},
            {"t": "Abre los ojos y no te dejes manipular nunca mas Siguenos para mas", "s": "epic cinematic lighting nature"}
        ]

# MOTOR DUAL DE VOZ 
def invocar_voz(texto, archivo):
    texto_limpio = re.sub(r'[^A-Za-zÁÉÍÓÚáéíóúÑñ0-9\s.,]', '', texto)
    with open("spell.txt", "w", encoding="utf-8") as f: f.write(texto_limpio)

    subprocess.run(["python", "-m", "edge_tts", "--voice", "es-ES-AlvaroNeural", "--rate=0%", "-f", "spell.txt", "--write-media", archivo])
    if os.path.exists(archivo) and os.path.getsize(archivo) > 1000: return True
        
    try:
        url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={urllib.parse.quote(texto_limpio)}&tl=es&client=tw-ob"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if r.status_code == 200:
            with open(archivo, 'wb') as f: f.write(r.content)
            return True
    except: pass
    return False

with st.sidebar:
    st.header("⚙️ Motor CapCut")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.selectbox("🎨 Color de Letra", ["yellow", "white", "#00FF00", "cyan"])

if orden := st.chat_input("Dime el tema (Estilo Viral 9 Segundos):"):
    with st.status(f"✨ Creando magia visual sobre '{orden}'...", expanded=True) as status:
        subprocess.run("rm -f a_*.mp3 v_*.mp4 s_*.mp4 spell.txt lista.txt music.mp3 final.mp4 base.mp4", shell=True)
        
        tema_limpio = limpiar_orden(orden)
        nicho = detectar_nicho(orden)
        escenas = generar_master_guion(tema_limpio, nicho)
        
        clips_finales = []
        font_cmd = f"fontfile='{font_path}':" if os.path.exists(font_path) else ""

        for i, esc in enumerate(escenas):
            status.write(f"🎬 Sincronizando Escena Dinámica {i+1}/5...")

            # 1. Voz
            if not invocar_voz(esc["t"], f"a_{i}.mp3"):
                st.error("Servidores de voz caídos. Reintenta.")
                st.stop()
            
            try:
                dur = float(subprocess.check_output(f"ffprobe -i a_{i}.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True).decode('utf-8').strip())
            except: dur = 3.5

            # 2. Pexels (Con fallback de seguridad)
            v_url = None
            try:
                r = requests.get(f"https://api.pexels.com/videos/search?query={urllib.parse.quote(esc['s'])}&per_page=5&orientation=portrait", headers={"Authorization": pexels_key.strip()}, timeout=5).json()
                if r.get('videos'): v_url = random.choice(r['videos'])['video_files'][0]['link']
            except: pass
            
            if not v_url: 
                subprocess.run(f'ffmpeg -y -f lavfi -i color=c=black:s=720x1280:d=1:r=30 -c:v libx264 -preset ultrafast v_{i}.mp4', shell=True)
            else:
                with open(f"v_{i}.mp4", 'wb') as f: f.write(requests.get(v_url, timeout=10).content)

            # 3. EL TRUCO VIRAL: Cortar el texto en trozos de 2 palabras y calcular su tiempo
            txt_m = esc["t"].upper().replace('Á','A').replace('É','E').replace('Í','I').replace('Ó','O').replace('Ú','U').replace('Ñ','N')
            txt_m = re.sub(r'[^A-Z0-9\s]', '', txt_m) # Quitamos TODO rastro de puntos o comas para que no haya errores
            
            palabras = txt_m.split()
            chunks = [" ".join(palabras[j:j+2]) for j in range(0, len(palabras), 2)]
            
            tiempo_por_chunk = dur / max(len(chunks), 1)
            
            # Construimos los filtros de dibujo de texto uno por uno
            filtros_texto = ""
            for j, chunk in enumerate(chunks):
                start_t = j * tiempo_por_chunk
                end_t = (j + 1) * tiempo_por_chunk
                # Letra gigante (75), borde negro grueso (6), sombra para dar profundidad
                filtros_texto += f",drawtext=text='{chunk}':fontcolor={color_sub}:fontsize=80:{font_cmd}borderw=6:bordercolor=black:shadowcolor=black:shadowx=4:shadowy=4:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{start_t},{end_t})'"

            # 4. Renderizado con Zoom y Textos Dinámicos
            zoom_type = random.choice(["zoom+0.002", "zoom-0.001"]) 
            cmd = f"""ffmpeg -y -stream_loop -1 -i v_{i}.mp4 -i a_{i}.mp3 -vf "scale=800:1422,zoompan=z='min({zoom_type},1.5)':d=300:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280,format=yuv420p{filtros_texto}" -c:v libx264 -preset ultrafast -c:a aac -ar 44100 -t {dur} s_{i}.mp4"""
            
            subprocess.run(cmd, shell=True)
            if os.path.exists(f"s_{i}.mp4"): clips_finales.append(f"s_{i}.mp4")

        # 5. Ensamblaje Final
        status.write("✨ Exportando con calidad CapCut...")
        with open("lista.txt", "w") as f:
            for c in clips_finales: f.write(f"file '{c}'\n")
            
        subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)
        
        v_final = f"output/v_{int(time.time())}.mp4"
        freq = 60 if nicho == "TERROR" else 75
        
        cmd_f = f"""ffmpeg -y -i base.mp4 -f lavfi -i "sine=f={freq}:d=120" -filter_complex "[1:a]volume=0.03[m];[0:a][m]amix=inputs=2:duration=first" -c:v copy -c:a aac -ar 44100 "{v_final}" """
        subprocess.run(cmd_f, shell=True)
        
        if os.path.exists(v_final):
            st.success("🔥 ¡VÍDEO VIRAL COMPLETADO! Textos dinámicos garantizados.")
            st.video(v_final)
            st.balloons()
