import streamlit as st
import os, time, random, subprocess, textwrap, re, urllib.parse
import requests

st.set_page_config(page_title="Fénix Viral PRO | V39", layout="centered")

st.markdown("""
<style>
    .stApp { background: radial-gradient(circle, #0f172a 0%, #000000 100%); color: #F8FAFC; }
    .pro-title { font-size: 42px; font-weight: 900; background: -webkit-linear-gradient(45deg, #00FFD1, #8A2BE2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 5px; text-transform: uppercase;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX LÉXICO V39</div>', unsafe_allow_html=True)
st.markdown('<div class="pro-subtitle" style="text-align:center; color:#94A3B8; margin-bottom: 30px;">Base de Datos Procedural • Guiones Infinitos • Lógica Implacable</div>', unsafe_allow_html=True)

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

# --- LA BASE DE DATOS MAESTRA (SISTEMA LEGO) ---
# Aquí están los bloques de construcción. Combina Ganchos + Nudos + Giros + Cierres = Miles de guiones únicos.
BASE_DE_DATOS = {
    "TERROR": {
        "ganchos": [
            "No mires este video de noche si le temes a {tema}.",
            "El secreto más perturbador sobre {tema} acaba de ser filtrado en internet.",
            "Lo que estoy a punto de mostrarte sobre {tema} te helará la sangre.",
            "La oscura verdad detrás de {tema} que el gobierno no quiere que sepas."
        ],
        "nudos": [
            "Durante décadas la gente pensó que era solo una simple leyenda urbana inventada para asustar.",
            "Un grupo de investigadores entró al lugar con cámaras y micrófonos buscando respuestas.",
            "La policía intentó clasificar los archivos como confidenciales tras encontrar algo macabro.",
            "Todos ignoraban las señales hasta que las desapariciones comenzaron a multiplicarse."
        ],
        "giros": [
            "Pero las grabaciones de seguridad mostraron una sombra aterradora que desafiaba toda lógica humana.",
            "Al limpiar el audio descubrieron voces inhumanas pidiendo ayuda desde la oscuridad más profunda.",
            "Los documentos revelaron que no estaban solos algo los observaba desde las paredes.",
            "Se dieron cuenta de que la criatura se alimentaba directamente del miedo de las personas."
        ],
        "cierres": [
            "Lo más espeluznante es que esa cosa sigue suelta. Síguenos para más terror.",
            "Si esta noche escuchas un ruido extraño en la puerta, no la abras. Síguenos para más historias.",
            "Nunca sabremos cuántas víctimas más habrá. Mira detrás de ti ahora mismo. Síguenos para más."
        ],
        "visuales": ["creepy dark forest", "scary abandoned house", "creepy shadow horror", "dark ghost camera", "scary monster eyes", "paranormal activity dark", "creepy fog night"]
    },
    "NEGOCIOS": {
        "ganchos": [
            "Te están robando tu dinero en tu propia cara con {tema} y ni siquiera lo sabes.",
            "El noventa y nueve por ciento de la gente fracasa con {tema} por culpa de esta trampa.",
            "Si quieres ser millonario tienes que dejar de creer esta mentira sobre {tema}.",
            "Los bancos odian que sepas este secreto prohibido sobre {tema}."
        ],
        "nudos": [
            "Las grandes élites financieras diseñaron un sistema oculto para mantenerte pobre y trabajando.",
            "Nos enseñan en la escuela a ser empleados obedientes y a no hacer las preguntas correctas.",
            "Un ex banquero de Wall Street rompió su contrato de silencio y filtró el patrón exacto.",
            "La inflación y los impuestos están devorando tus ahorros mientras ellos multiplican sus ganancias."
        ],
        "giros": [
            "La clave maestra es hacer exactamente lo contrario a lo que dicen las noticias cada mañana.",
            "Descubrieron que comprando activos ocultos podías generar ingresos pasivos sin esfuerzo.",
            "El truco consiste en apalancarse con el dinero de otros y crear un imperio desde cero.",
            "Resulta que la verdadera riqueza se esconde en mercados que nadie está mirando."
        ],
        "cierres": [
            "El sistema está roto, es tu turno de aprovecharlo. Síguenos para dominar tus finanzas.",
            "Deja de cambiar tu tiempo por migajas y empieza a invertir. Síguenos para más negocios.",
            "Aplica esta regla hoy y tu cuenta bancaria explotará. Síguenos para más secretos de riqueza."
        ],
        "visuales": ["counting money wealth", "corporate business skyscraper", "trading chart screen success", "luxury lifestyle rich", "expensive car money rain", "gold bars wealth", "business handshake"]
    },
    "UNIVERSAL": {
        "ganchos": [
            "Te apuesto lo que quieras a que has vivido engañado toda tu vida sobre {tema}.",
            "El secreto más grande de la historia sobre {tema} acaba de salir a la luz.",
            "Prepárate porque lo que vas a escuchar sobre {tema} te dejará con la boca abierta.",
            "Casi nadie sabe esto, pero la verdad oculta sobre {tema} cambiará tu forma de pensar."
        ],
        "nudos": [
            "La mayoría de la gente acepta la versión oficial sin detenerse a cuestionar los detalles.",
            "Durante siglos los libros de texto omitieron la parte más importante para mantener el control.",
            "Un científico rebelde decidió investigar por su cuenta y encontró algo alucinante.",
            "Parecía un detalle sin importancia hasta que alguien empezó a atar los cabos sueltos."
        ],
        "giros": [
            "Los resultados de laboratorio confirmaron que nuestra realidad es una completa simulación.",
            "Resulta que todo estaba fríamente calculado por una organización que opera en las sombras.",
            "Descubrieron que el cerebro humano tiene la capacidad de alterar la materia con el pensamiento.",
            "Las pruebas demostraron que una civilización mucho más avanzada ya había estado aquí."
        ],
        "cierres": [
            "Una vez que ves la verdad ya no puedes volver a dormirte. Síguenos para más curiosidades.",
            "Abre los ojos y no permitas que te sigan manipulando. Síguenos para descubrir más secretos.",
            "Comparte esto con alguien que necesite despertar de la matriz. Síguenos para más revelaciones."
        ],
        "visuales": ["cinematic epic mystery", "crowd of people city", "secret documents dark", "shocked face dramatic", "epic cinematic lighting", "universe stars space", "abstract glowing lines"]
    }
}

def construir_guion_lego(tema, nicho):
    db = BASE_DE_DATOS[nicho]
    # Extraemos un bloque de cada categoría al azar
    gancho = random.choice(db["ganchos"]).format(tema=tema.upper())
    nudo = random.choice(db["nudos"])
    giro = random.choice(db["giros"])
    cierre = random.choice(db["cierres"])
    
    # Ensamblamos el Frankenstein perfecto
    guion_final = f"{gancho} {nudo} {giro} {cierre}"
    
    # Elegimos 5 visuales aleatorios que encajen perfectos
    visuales = random.sample(db["visuales"], 5)
    
    return guion_final, visuales

# --- MOTOR DE VOZ INMORTAL DUAL ---
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
    st.header("⚙️ Motor Léxico")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.selectbox("🎨 Color de Letra", ["yellow", "white", "#00FFD1", "#FF0055"])

if orden := st.chat_input("Dime el tema (El Motor Léxico construirá la historia):"):
    with st.status(f"🚀 Ensamblando guion viral sobre '{orden}'...", expanded=True) as status:
        subprocess.run("rm -f a_*.mp3 g_*.mp3 v_*.mp4 clip_*.mp4 p_*.mp4 text_*.txt temp_txt.txt lista*.txt music.mp3 audio_final.mp3 video_mudo.mp4 final.mp4 base.mp4 t.mp3 t.vtt subs_filter.txt", shell=True)
        
        tema_limpio = limpiar_orden(orden)
        nicho = detectar_nicho(orden)
        
        guion, visuales = construir_guion_lego(tema_limpio, nicho)
        status.write("🧠 Guion construido mediante bloques lógicos de retención.")
        
        # 1. VOZ DUAL
        status.write("🎙️ Grabando audio ininterrumpido...")
        if not generar_voz_inmortal(guion):
            st.error("❌ Fallo Crítico de Red. Inténtalo de nuevo.")
            st.stop()
            
        dur_audio = float(subprocess.check_output("ffprobe -i t.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True).decode('utf-8').strip())

        # 2. AUDIO FINAL Y MÚSICA PRE-MEZCLADA
        status.write("🎵 Aplicando banda sonora...")
        freq = 60 if nicho == "TERROR" else 75
        subprocess.run(f'ffmpeg -y -i t.mp3 -f lavfi -i "sine=f={freq}:d={dur_audio}" -filter_complex "[1:a]volume=0.03[m];[0:a][m]amix=inputs=2:duration=first" -c:a aac -ar 44100 audio_final.mp3', shell=True)

        # 3. SUBTÍTULOS CAPCUT (2 palabras, gigantes, sin cuadrados)
        status.write("🎬 Diseñando dinámica de subtítulos...")
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

        # 4. DESCARGA PEXELS 100% RELACIONADOS
        status.write("🎞️ Obteniendo metraje visual exacto...")
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

        # 5. RENDERIZADO MAESTRO
        status.write("✨ Renderizando el vídeo viral...")
        with open("lista.txt", "w") as f:
            for c in clips_finales: f.write(f"file '{c}'\n")
            
        subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy video_mudo.mp4', shell=True)
        v_final = f"output/v_{int(time.time())}.mp4"
        
        # Fusión Final Inquebrantable
        cmd_f = f"""ffmpeg -y -stream_loop -1 -i video_mudo.mp4 -i audio_final.mp3 -filter_complex_script subs_filter.txt -c:v libx264 -preset veryfast -c:a copy -t {dur_audio} "{v_final}" """
        subprocess.run(cmd_f, shell=True)
        
        if os.path.exists(v_final):
            st.success("🔥 ¡VÍDEO LÉXICO PERFECTO! Guion lógico y subtítulos dinámicos.")
            st.video(v_final)
            st.balloons()
        else:
            st.error("❌ Fallo crítico en FFmpeg.")
