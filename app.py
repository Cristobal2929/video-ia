import streamlit as st
import os, time, random, subprocess, textwrap, re, urllib.parse
import requests

st.set_page_config(page_title="Fénix Viral PRO | V40", layout="centered")

st.markdown("""
<style>
    .stApp { background: radial-gradient(circle, #0f172a 0%, #000000 100%); color: #F8FAFC; }
    .pro-title { font-size: 42px; font-weight: 900; background: -webkit-linear-gradient(45deg, #00FFD1, #FF0055); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 5px; text-transform: uppercase;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX ABSOLUTO V40</div>', unsafe_allow_html=True)
st.markdown('<div class="pro-subtitle" style="text-align:center; color:#94A3B8; margin-bottom: 30px;">Tanque Blindado • Cero Errores FFmpeg • Zoom Cinemático</div>', unsafe_allow_html=True)

# 1. DESCARGA DE FUENTE ABSOLUTA
font_path = "Arial.ttf"
if not os.path.exists(font_path):
    try:
        r = requests.get("https://github.com/matomo-org/travis-scripts/raw/master/fonts/Arial.ttf", timeout=5)
        with open(font_path, "wb") as f: f.write(r.content)
    except: pass
font_abs = os.path.abspath(font_path).replace('\\', '/')

def limpiar_orden(orden):
    return re.sub(r'[^A-Za-zÁÉÍÓÚáéíóúÑñ0-9\s]', '', orden).strip()

def detectar_nicho(tema):
    t = tema.lower()
    if any(w in t for w in ["miedo", "terror", "fantasma", "paranormal", "horror", "misterio", "creepy"]): return "TERROR"
    if any(w in t for w in ["dinero", "negocio", "invertir", "rico", "millonario", "cripto", "finanzas"]): return "NEGOCIOS"
    return "UNIVERSAL"

# 2. BASE DE DATOS LÓGICA (ALTA RETENCIÓN)
BASE_DE_DATOS = {
    "TERROR": {
        "ganchos": [
            "No mires este video de noche si le temes a {tema}.",
            "El secreto mas perturbador sobre {tema} acaba de ser filtrado.",
            "Lo que estoy a punto de mostrarte sobre {tema} te helara la sangre."
        ],
        "nudos": [
            "Durante decadas la gente penso que era solo una leyenda urbana para asustar.",
            "Un grupo de investigadores entro al lugar buscando respuestas.",
            "La policia intento clasificar los archivos tras encontrar algo macabro."
        ],
        "giros": [
            "Pero las grabaciones de seguridad mostraron una sombra que desafiaba toda logica.",
            "Al limpiar el audio descubrieron voces pidiendo ayuda desde la oscuridad.",
            "Los documentos revelaron que algo los observaba desde las paredes."
        ],
        "cierres": [
            "Lo mas espeluznante es que esa cosa sigue suelta. Siguenos para mas.",
            "Si esta noche escuchas un ruido en la puerta, no la abras. Siguenos para mas.",
            "Nunca sabremos cuantas victimas mas habra. Mira detras de ti. Siguenos."
        ],
        "visuales": ["creepy dark forest", "scary abandoned house", "creepy shadow horror", "dark ghost camera", "scary monster eyes"]
    },
    "NEGOCIOS": {
        "ganchos": [
            "Te estan robando tu dinero en tu propia cara con {tema}.",
            "El noventa y nueve por ciento fracasa con {tema} por esta trampa.",
            "Si quieres ser millonario tienes que dejar de creer esta mentira sobre {tema}."
        ],
        "nudos": [
            "Las grandes elites diseñaron un sistema oculto para mantenerte pobre.",
            "Nos enseñan en la escuela a ser empleados y no hacer preguntas.",
            "Un ex banquero rompio su contrato y filtro el patron exacto."
        ],
        "giros": [
            "La clave maestra es hacer lo contrario a lo que dicen las noticias.",
            "Descubrieron que comprando activos ocultos generabas ingresos sin esfuerzo.",
            "El truco consiste en crear un imperio desde cero con deuda buena."
        ],
        "cierres": [
            "El sistema esta roto, es tu turno de aprovecharlo. Siguenos para mas.",
            "Deja de cambiar tu tiempo por migajas. Siguenos para mas negocios.",
            "Aplica esta regla hoy y tu cuenta explotara. Siguenos para mas secretos."
        ],
        "visuales": ["counting money wealth", "corporate business skyscraper", "trading chart screen success", "luxury lifestyle rich", "expensive car money rain"]
    },
    "UNIVERSAL": {
        "ganchos": [
            "Te apuesto lo que quieras a que has vivido engañado sobre {tema}.",
            "El secreto mas grande de la historia sobre {tema} acaba de salir a la luz.",
            "Prepárate porque lo que vas a escuchar sobre {tema} te dejara sin palabras."
        ],
        "nudos": [
            "La mayoria de la gente acepta la version oficial sin cuestionar nada.",
            "Durante siglos los libros omitieron la parte mas importante.",
            "Un cientifico decidio investigar por su cuenta y encontro algo alucinante."
        ],
        "giros": [
            "Los resultados confirmaron que nuestra realidad es una simulación.",
            "Resulta que todo estaba friamente calculado por una organización secreta.",
            "Descubrieron que el cerebro humano tiene capacidades ocultas."
        ],
        "cierres": [
            "Una vez que ves la verdad ya no puedes dormirte. Siguenos para mas.",
            "Abre los ojos y no permitas que te sigan manipulando. Siguenos.",
            "Comparte esto con alguien que necesite despertar. Siguenos."
        ],
        "visuales": ["cinematic epic mystery", "crowd of people city", "secret documents dark", "shocked face dramatic", "epic cinematic lighting"]
    }
}

def construir_guion(tema, nicho):
    db = BASE_DE_DATOS[nicho]
    gancho = random.choice(db["ganchos"]).format(tema=tema.upper())
    nudo = random.choice(db["nudos"])
    giro = random.choice(db["giros"])
    cierre = random.choice(db["cierres"])
    return f"{gancho} {nudo} {giro} {cierre}", random.sample(db["visuales"], 5)

# 3. MOTOR DUAL DE VOZ
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

with st.sidebar:
    st.header("⚙️ Configuración")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.selectbox("🎨 Color de Letra", ["yellow", "white", "cyan"])

if orden := st.chat_input("Dime el tema (El Tanque Blindado a tu servicio):"):
    with st.status(f"🚀 Renderizando Master de '{orden}'...", expanded=True) as status:
        subprocess.run("rm -f a_*.mp3 g_*.mp3 v_*.mp4 clip_*.mp4 p_*.mp4 text_*.txt temp_txt.txt lista*.txt music.mp3 audio_final.* video_mudo.mp4 final.mp4 base.mp4 t.mp3", shell=True)
        
        tema_limpio = limpiar_orden(orden)
        nicho = detectar_nicho(orden)
        
        guion, visuales = construir_guion(tema_limpio, nicho)
        status.write("🧠 Guion generado con éxito.")
        
        # VOZ
        status.write("🎙️ Sintetizando audio...")
        if not generar_voz_inmortal(guion):
            st.error("❌ Los servidores de voz no responden. Reintenta.")
            st.stop()
            
        dur_audio = float(subprocess.check_output("ffprobe -i t.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True).decode('utf-8').strip())

        # AUDIO FINAL Y MÚSICA (Arreglado formato a .m4a para que FFmpeg no explote)
        status.write("🎵 Mezclando banda sonora...")
        freq = 60 if nicho == "TERROR" else 75
        subprocess.run(f'ffmpeg -y -i t.mp3 -f lavfi -i "sine=f={freq}:d={dur_audio}" -filter_complex "[1:a]volume=0.03[m];[0:a][m]amix=inputs=2:duration=first" -c:a aac -ar 44100 audio_final.m4a', shell=True)

        if not os.path.exists("audio_final.m4a"):
            st.error("❌ Fallo en la mezcla de audio.")
            st.stop()

        # VÍDEOS PEXELS CON ZOOM CINEMÁTICO (KEN BURNS)
        status.write("🎞️ Obteniendo metraje y aplicando Zoom...")
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
                zoom_dir = random.choice(["zoom+0.0015", "zoom-0.001"])
                subprocess.run(f'ffmpeg -y -i "clip_{i}.mp4" -vf "scale=800:1422,zoompan=z=\'min({zoom_dir},1.5)\':d=300:x=\'iw/2-(iw/zoom/2)\':y=\'ih/2-(ih/zoom/2)\':s=720x1280,format=yuv420p" -an -c:v libx264 -preset ultrafast -t {dur_escena} "p_{i}.mp4"', shell=True)
            except:
                subprocess.run(f'ffmpeg -y -f lavfi -i color=c=black:s=720x1280:d={dur_escena}:r=30 -c:v libx264 -preset ultrafast -format yuv420p "p_{i}.mp4"', shell=True)
                
            if os.path.exists(f"p_{i}.mp4"): clips_finales.append(f"p_{i}.mp4")

        # MONTAJE DE VÍDEO MUDO
        with open("lista.txt", "w") as f:
            for c in clips_finales: f.write(f"file '{c}'\n")
        subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy video_mudo.mp4', shell=True)

        # SUBTÍTULOS DINÁMICOS CAPCUT
        status.write("✨ Renderizado Final Blindado...")
        txt_m = guion.upper().replace('Á','A').replace('É','E').replace('Í','I').replace('Ó','O').replace('Ú','U').replace('Ñ','N')
        txt_m = re.sub(r'[^A-Z0-9\s]', '', txt_m)
        palabras = txt_m.split()
        
        chunks = [" ".join(palabras[j:j+2]) for j in range(0, len(palabras), 2)]
        tiempo_por_chunk = dur_audio / max(len(chunks), 1)
        
        subs_cmd = []
        font_cmd = f"fontfile='{font_abs}':" if os.path.exists(font_path) else ""
        
        for j, chunk in enumerate(chunks):
            t_start = j * tiempo_por_chunk
            t_end = t_start + tiempo_por_chunk
            subs_cmd.append(f"drawtext=text='{chunk}':fontcolor={color_sub}:fontsize=85:{font_cmd}borderw=6:bordercolor=black:shadowcolor=black:shadowx=5:shadowy=5:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{t_start},{t_end})'")
            
        # El comando directo con -vf (Indestructible, no usa filter_complex_script)
        filter_str = ",".join(subs_cmd)
        v_final = f"output/v_{int(time.time())}.mp4"
        
        cmd_f = f"""ffmpeg -y -stream_loop -1 -i video_mudo.mp4 -i audio_final.m4a -vf "{filter_str}" -c:v libx264 -preset veryfast -c:a copy -t {dur_audio} "{v_final}" """
        subprocess.run(cmd_f, shell=True)
        
        if os.path.exists(v_final) and os.path.getsize(v_final) > 1000:
            st.success("🔥 ¡TANQUE BLINDADO COMPLETADO! Ni un solo error de FFmpeg.")
            st.video(v_final)
            st.balloons()
        else:
            st.error("❌ Fallo en el último paso. FFmpeg no pudo generar el archivo.")
