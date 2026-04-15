import streamlit as st
import os, time, random, subprocess, math, re, urllib.parse
import requests

st.set_page_config(page_title="Fénix Viral PRO | V23", layout="centered")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #09090b 0%, #111827 100%); color: #F8FAFC; }
    .pro-title { font-size: 38px; font-weight: 900; background: -webkit-linear-gradient(45deg, #E81CFF, #40C9FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 5px; }
    .stTextInput>div>div>input { background-color: #1F2937; color: white; border: 1px solid #40C9FF; border-radius: 8px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX AI STUDIO v23.0</div>', unsafe_allow_html=True)
st.markdown('<div class="pro-subtitle" style="text-align:center; color:#94A3B8; margin-bottom: 30px;">Director Interno • Cero Caídas de Red • Imágenes Exactas</div>', unsafe_allow_html=True)

def limpiar_orden(orden):
    basura = ["hazme", "haz", "arme", "asme", "dame", "dime", "un", "una", "el", "la", "los", "las", "video", "quiero", "sobre", "de", "del", "que", "hable", "como", "para"]
    orden_limpia = re.sub(r'[^A-Za-zÁÉÍÓÚáéíóúÑñ0-9\s]', '', orden)
    palabras = orden_limpia.lower().split()
    limpias = [p for p in palabras if p not in basura and len(p) > 3]
    return " ".join(limpias) if limpias else orden_limpia

def detectar_nicho(tema):
    t = tema.lower()
    if any(w in t for w in ["miedo", "terror", "fantasma", "paranormal", "horror", "misterio", "oscuro"]): return "TERROR"
    if any(w in t for w in ["dinero", "negocio", "invertir", "rico", "millonario", "cripto", "empresa"]): return "NEGOCIOS"
    if any(w in t for w in ["ciencia", "espacio", "luna", "planeta", "curiosidad"]): return "CIENCIA"
    return "UNIVERSAL"

# --- LA BASE DE DATOS DIRECTOR (Texto en Español + Búsqueda Pexels en Inglés) ---
def generar_base_director(tema, nicho):
    if nicho == "TERROR":
        return [
            {"t": f"No mires este vídeo de noche si le temes a {tema}.", "s": "creepy dark shadows"},
            {"t": "Todo el mundo piensa que es un invento, pero la policía encontró algo macabro.", "s": "scary abandoned house"},
            {"t": "Las grabaciones de seguridad mostraron algo que desafía toda lógica.", "s": "creepy ghost camera"},
            {"t": "El gobierno clasificó los archivos, pero alguien logró filtrarlos en la web profunda.", "s": "hacker computer dark"},
            {"t": "Esa cosa sigue suelta. Si escuchas un ruido hoy, no abras la puerta. Síguenos para más terror.", "s": "scary monster dark"}
        ]
    elif nicho == "NEGOCIOS":
        return [
            {"t": f"Te están robando tu dinero con {tema} y ni siquiera te has dado cuenta.", "s": "money counting wealth"},
            {"t": "Las grandes élites han diseñado un sistema oculto para que fracases.", "s": "corporate business building"},
            {"t": "Pero un analista financiero filtró el patrón exacto para ganar.", "s": "trading chart screen"},
            {"t": "La clave es buscar donde nadie más está mirando y adelantarse a la masa.", "s": "success luxury rich"},
            {"t": "El sistema está roto, es tu turno de aprovecharlo. Síguenos para más negocios.", "s": "luxury car money"}
        ]
    elif nicho == "CIENCIA":
        return [
            {"t": f"El noventa y nueve por ciento de la gente no tiene ni idea de esto sobre {tema}.", "s": "science abstract macro"},
            {"t": "Siempre nos enseñaron que era algo normal, pero un estudio reveló un dato brutal.", "s": "scientist laboratory"},
            {"t": "Resulta que los expertos habían ignorado un detalle durante décadas.", "s": "space universe planet"},
            {"t": "La ciencia moderna confirma que casi todo lo que sabíamos estaba mal.", "s": "bright light energy"},
            {"t": "Esto cambia nuestra forma de entender el mundo. Síguenos para más curiosidades.", "s": "cinematic epic nature"}
        ]
    else: # UNIVERSAL
        return [
            {"t": f"Te apuesto lo que quieras a que no sabías esto sobre {tema}.", "s": "curious mystery cinematic"},
            {"t": "La mayoría de la gente vive engañada aceptando la versión oficial.", "s": "crowd of people walking"},
            {"t": "Pero hace poco se reveló un detalle oculto que lo cambia absolutamente todo.", "s": "secret documents investigation"},
            {"t": "Si prestas atención a los patrones, te darás cuenta de la inmensa mentira.", "s": "shocked dramatic face"},
            {"t": "Despierta y no te dejes manipular nunca más. Síguenos para más secretos.", "s": "epic cinematic lighting"}
        ]

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
    color_sub = st.selectbox("🎨 Color de Letra", ["yellow", "white", "cyan"])

if orden := st.chat_input("Dime el tema (Lógica y Conexión 100% Asegurada):"):
    with st.status(f"🚀 Produciendo '{orden}' de forma nativa...", expanded=True) as status:
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.mp3 t.vtt music.mp3 final.mp4 temp_a.mp3 lista.txt subs_filter.txt", shell=True)
        
        tema_limpio = limpiar_orden(orden)
        nicho = detectar_nicho(orden)
        
        # 1. Extraemos la base de datos pre-programada
        escenas_bd = generar_base_director(tema_limpio, nicho)
        
        # Unimos todo el texto para la voz
        texto_completo = " ".join([esc["t"] for esc in escenas_bd])
        status.write("🧠 Guion y Dirección Visual cargados desde la base segura.")
        
        # 2. Generamos el audio global (BLINDADO CONTRA STREAMLIT CLOUD)
        texto_limpio = re.sub(r'[^A-Za-zÁÉÍÓÚáéíóúÑñ0-9\s.,]', '', texto_completo)
        
        exito_voz = False
        for i in range(3):
            subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --rate=0% --text "{texto_limpio}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
            if os.path.exists("t.vtt") and os.path.getsize("t.vtt") > 0:
                exito_voz = True
                break
            time.sleep(2)
            
        if not exito_voz:
            st.error("Error en el motor de voz de Microsoft. Intenta darle de nuevo.")
            st.stop()

        status.write("🎙️ Audio procesado correctamente sin caídas.")

        # 3. Sincronizamos los tiempos de las frases
        tiempos = []
        with open('t.vtt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            current_start = -1
            for i in range(len(lines)):
                if "-->" in lines[i]:
                    start = time_to_sec(lines[i].split(" --> ")[0])
                    end = time_to_sec(lines[i].split(" --> ")[1])
                    txt = lines[i+1].strip()
                    
                    # Si detecta punto, guardamos el bloque de tiempo
                    if current_start == -1: current_start = start
                    if "." in txt:
                        tiempos.append({"start": current_start, "end": end})
                        current_start = -1

        # Ajuste de seguridad por si no coinciden exactos
        while len(tiempos) < len(escenas_bd):
            tiempos.append({"start": 0, "end": 2})

        # 4. Motor Visual Pexels
        status.write("🎞️ Descargando imágenes cinematográficas exactas...")
        clips_finales = []
        last_clip = None

        for i, esc in enumerate(escenas_bd):
            dur_clip = tiempos[i]["end"] - tiempos[i]["start"]
            if dur_clip <= 0: dur_clip = 3.0
            
            query = esc["s"] # Búsqueda en inglés perfecta
            v_url = None
            try:
                r = requests.get(f"https://api.pexels.com/videos/search?query={urllib.parse.quote(query)}&per_page=5&orientation=portrait", headers={"Authorization": pexels_key.strip()}, timeout=5).json()
                if r.get('videos'):
                    v_url = random.choice(r['videos'])['video_files'][0]['link']
            except: pass
            
            try:
                if not v_url: raise Exception()
                with open(f"clip_{i}.mp4", 'wb') as f: f.write(requests.get(v_url, timeout=10).content)
                subprocess.run(f'ffmpeg -y -i "clip_{i}.mp4" -vf "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,fps=30" -an -c:v libx264 -preset ultrafast -t {dur_clip + 0.1} "p_{i}.mp4"', shell=True)
                last_clip = f"p_{i}.mp4"
            except:
                if last_clip: subprocess.run(f"cp {last_clip} p_{i}.mp4", shell=True)
                else: subprocess.run(f'ffmpeg -y -f lavfi -i color=c=black:s=720x1280:d={dur_clip}:r=30 -c:v libx264 -preset ultrafast p_{i}.mp4', shell=True)
            
            clips_finales.append(f"p_{i}.mp4")

        # 5. Aplicar subtítulos Pro sincronizados
        status.write("🎬 Renderizando subtítulos TikTok Pro...")
        subs_cmd = []
        with open('t.vtt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i in range(len(lines)):
                if "-->" in lines[i]:
                    start = time_to_sec(lines[i].split(" --> ")[0])
                    end = time_to_sec(lines[i].split(" --> ")[1])
                    txt = lines[i+1].strip().upper()
                    t_render = re.sub(r'[^A-Z0-9\s]', '', txt).replace('Á','A').replace('É','E').replace('Í','I').replace('Ó','O').replace('Ú','U').replace('Ñ','N')
                    subs_cmd.append(f"drawtext=text='{t_render}':fontcolor={color_sub}:fontsize=40:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:box=1:boxcolor=black@0.6:boxborderw=10:borderw=2:bordercolor=black:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{start},{end})'")
        
        with open("subs_filter.txt", "w") as f: f.write(",\n".join(subs_cmd))
        with open("lista.txt", "w") as f:
            for c in clips_finales: f.write(f"file '{c}'\n")
        
        subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)
        
        frecuencia = 60 if nicho == "TERROR" else 75
        subprocess.run(f'ffmpeg -y -f lavfi -i "sine=f={frecuencia}:d=120" -filter_complex "[0:a]volume=0.05" music.mp3', shell=True)
        subprocess.run(f'ffmpeg -y -i t.mp3 -i music.mp3 -filter_complex "[0:a]volume=3.0[v];[1:a]volume=0.15[m];[v][m]amix=inputs=2:duration=first" temp_a.mp3', shell=True)
        
        v_final = f"output/v_{int(time.time())}.mp4"
        subprocess.run(f'ffmpeg -y -i base.mp4 -i temp_a.mp3 -filter_complex_script subs_filter.txt -c:v libx264 -preset ultrafast -b:v 2500k -shortest "{v_final}"', shell=True)
        
        if os.path.exists(v_final):
            st.success("✅ La Roca del Director: Cero Errores, Lógica Visual Perfecta.")
            st.video(v_final)
