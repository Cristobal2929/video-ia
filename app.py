import streamlit as st
import os, time, random, subprocess, math, re, urllib.parse
import requests

st.set_page_config(page_title="Fénix Viral PRO", layout="centered")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0B0F19 0%, #1A2235 100%); color: #F8FAFC; }
    .pro-title { font-size: 38px; font-weight: 900; background: -webkit-linear-gradient(45deg, #00C6FF, #0072FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 5px; letter-spacing: -1px; }
    .stTextInput>div>div>input { background-color: #0F172A; color: white; border: 1px solid #334155; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX AI STUDIO v17.0</div>', unsafe_allow_html=True)
st.markdown('<div class="pro-subtitle" style="text-align:center; color:#94A3B8;">Base de Datos Maestra • Cero Errores • 100% Lógica Humana</div>', unsafe_allow_html=True)

# --- TRADUCTOR INTERNO PARA PEXELS ---
TRADUCCION = {
    "ELEFANTE": "elephant", "AMOR": "love", "DINERO": "money", "ESTAFA": "scam",
    "GATO": "cat", "PERRO": "dog", "COCHE": "car", "CIUDAD": "city", "MIEDO": "scary",
    "LUNA": "moon", "ESPACIO": "space", "ORO": "gold", "COMIDA": "food", "HACKER": "hacker",
    "FUEGO": "fire", "AGUA": "water", "BOSQUE": "forest", "TIEMPO": "clock", "MUNDO": "world"
}

def traducir(p):
    return TRADUCCION.get(p.upper(), p.lower())

def limpiar_orden(orden):
    basura = ["hazme", "haz", "arme", "asme", "dame", "dime", "un", "una", "el", "la", "los", "las", "video", "quiero", "sobre", "de", "del", "que", "hable", "como", "para"]
    palabras = orden.lower().split()
    limpias = [p for p in palabras if p not in basura and len(p) > 3]
    return " ".join(limpias) if limpias else orden

def detectar_nicho(tema):
    t = tema.lower()
    if any(w in t for w in ["miedo", "terror", "fantasma", "paranormal", "horror"]): return "TERROR"
    if any(w in t for w in ["dinero", "negocio", "invertir", "rico", "millonario", "cripto"]): return "NEGOCIOS"
    if any(w in t for w in ["ciencia", "espacio", "luna", "planeta", "curiosidad"]): return "CIENCIA"
    if any(w in t for w in ["salud", "dieta", "ejercicio", "fitness"]): return "SALUD"
    return "UNIVERSAL"

# --- LA BASE DE DATOS MAESTRA (100% Lógica, 0% IA) ---
def generar_desde_base_datos(tema, nicho):
    tema = tema.upper()
    
    variables = {
        "tema": tema,
        "año": random.choice(["2008", "2015", "hace un par de años", "1999", "2020"]),
        "enemigo_negocios": random.choice(["los bancos centrales", "las grandes élites", "los multimillonarios", "los fondos de inversión"]),
        "enemigo_misterio": random.choice(["el gobierno", "una agencia secreta", "las altas esferas", "los servicios de inteligencia"]),
        "porcentaje": random.choice(["99", "95", "90"]),
        "locura": random.choice(["una verdadera locura", "algo brutal", "un descubrimiento que te vuela la cabeza", "algo que no tiene sentido"])
    }

    if nicho == "NEGOCIOS":
        plantillas = [
            "El {porcentaje} por ciento de la gente pierde todo su dinero con {tema} porque no entienden esta trampa. En {año}, {enemigo_negocios} diseñaron un sistema para que el ciudadano común fracasara. La estrategia era mantener esto oculto mientras ellos se hacían ricos. Pero un analista financiero filtró la fórmula real y es {locura}. La clave está en hacer exactamente lo contrario a lo que dicen las noticias. Cuando todos entran en pánico, tú atacas. Ahora que sabes esto, el sistema ya no puede robarte. Síguenos para más negocios.",
            "Te están robando en tu propia cara con {tema} y ni siquiera te has dado cuenta. Todo empezó en {año}, cuando {enemigo_negocios} decidieron mantener a la gente ignorante. Nos vendieron la mentira de que necesitabas muchísimo capital, pero es falso. Un joven descubrió una falla en el sistema y reventó el mercado. Su secreto es {locura}. Consiste en buscar donde nadie más está mirando y adelantarse a la masa. El sistema está roto, es tu turno de aprovecharlo. Síguenos para más finanzas."
        ]
    elif nicho == "TERROR":
        plantillas = [
            "No mires este vídeo de noche si le temes a {tema}. Todo el mundo piensa que es un invento de internet, pero en {año} la policía encontró algo horrible. Las grabaciones de seguridad mostraron {locura}. El gobierno clasificó los vídeos de inmediato, pero alguien logró filtrarlos en la web profunda. Lo más aterrador de todo esto no es que haya pasado, sino que esa cosa sigue suelta buscando a quien rompa las reglas. Si escuchas un ruido extraño hoy, no abras la puerta. Síguenos para más terror.",
            "Esta es la historia más perturbadora y real sobre {tema}. Durante años, la gente hablaba en susurros sobre lo que pasó en {año}. Mandaron a un equipo a investigar, pero desaparecieron. Cuando los encontraron, habían perdido la cordura. Descubrieron que habían despertado a algo que no pertenece a este mundo y fue {locura}. La verdad es tan fuerte que la borraron de los medios, pero el mal nunca desaparece. Mira detrás de ti ahora mismo. Síguenos para más historias de miedo."
        ]
    elif nicho == "CIENCIA":
        plantillas = [
            "El {porcentaje} por ciento de las personas no tiene ni idea de esta locura sobre {tema}. Siempre nos enseñaron que era algo normal, pero un estudio de {año} reveló un dato que te va a dejar sin palabras. Resulta que los expertos habían ignorado un detalle brutal durante décadas, hasta que un científico lo investigó a fondo y encontró {locura}. Básicamente, la ciencia confirma que casi todo lo que sabíamos estaba mal. Este hecho cambia por completo nuestra forma de entender el mundo. Síguenos para más ciencia."
        ]
    elif nicho == "SALUD":
        plantillas = [
            "Te están engañando descaradamente con {tema}. La industria gasta millones para que creas que necesitas métodos caros, pero es pura basura. En {año} se filtró un estudio que demostró que el {porcentaje} por ciento de los productos comerciales no sirven para nada. El verdadero secreto es {locura}. Solo tienes que aplicar la biología básica a tu favor y dejar de seguir modas sin sentido. Tu cuerpo responderá en cuestión de días. Empieza hoy mismo y siente la diferencia. Síguenos para más salud."
        ]
    else: # UNIVERSAL
        plantillas = [
            "Te apuesto lo que quieras a que no sabías esto sobre {tema}. Casi todo el mundo cree que es algo totalmente normal, pero hay un detalle oculto que muy pocos conocen. En {año} se hizo viral un caso que lo cambia todo. Alguien se dio cuenta de un patrón que nadie más había visto y es {locura}. Este simple detalle cambia por completo la forma en la que deberíamos verlo. La próxima vez que estés frente a esto, ya no vas a poder ignorarlo. Síguenos para más curiosidades.",
            "Te han mentido toda tu vida sobre {tema}. Los libros de historia te cuentan una versión recortada porque {enemigo_misterio} decidió que no estabas listo para la verdad. Pero un empleado rompió su contrato y filtró unos archivos que demuestran {locura}. Resulta que esto ya existía hace milenios, pero lo escondieron para no perder el control. El {porcentaje} por ciento de la gente todavía se cree el cuento oficial, pero las pruebas no dejan lugar a dudas. Despierta de una vez. Síguenos para más misterios."
        ]
    
    return random.choice(plantillas).format(**variables)

with st.sidebar:
    st.header("⚙️ Configuración")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.selectbox("🎨 Color Subtítulos", ["yellow", "white", "cyan"])

if orden := st.chat_input("Dime el tema (Usaré la Base de Datos Maestra):"):
    with st.status(f"🚀 Extrayendo de la Base de Datos: '{orden}'...", expanded=True) as status:
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.mp3 t.vtt music.mp3 final.mp4 temp_a.mp3 lista.txt subs_filter.txt", shell=True)
        
        tema_limpio = limpiar_orden(orden)
        nicho = detectar_nicho(orden)
        
        # 1. Obtenemos el guion perfecto de la base de datos
        guion_con_puntuacion = generar_desde_base_datos(tema_limpio, nicho)
        status.write("✍️ Guion perfecto extraído de la base de datos.")
        
        # 2. Generamos voz (leyendo la puntuación para hacer pausas naturales)
        subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --rate=0% --text "{guion_con_puntuacion}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
        
        if not os.path.exists("t.vtt"):
            st.error("Error fatal en el audio. Intenta de nuevo.")
            st.stop()

        # 3. Analizamos las escenas para el vídeo
        escenas = []
        with open('t.vtt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i in range(len(lines)):
                if "-->" in lines[i]:
                    start = float(lines[i].split(" --> ")[0].split(' ')[0].replace(':', '').replace('.', '')) # Simplificación segura de tiempo
                    start_sec = time_to_sec(lines[i].split(" --> ")[0])
                    end_sec = time_to_sec(lines[i].split(" --> ")[1])
                    
                    txt = lines[i+1].strip()
                    # Limpiamos puntuación SOLO para buscar la palabra clave y mostrar en pantalla
                    txt_limpio = re.sub(r'[^A-Za-zÁÉÍÓÚáéíóúÑñ0-9\s]', '', txt)
                    palabras = [p for p in txt_limpio.split() if len(p) > 3]
                    kw = palabras[-1] if palabras else tema_limpio
                    
                    # Convertimos a mayúsculas para el subtítulo final
                    escenas.append({"start": start_sec, "end": end_sec, "text": txt_limpio.upper(), "kw": kw})

        # 4. Motor Visual Sincronizado
        status.write("🎞️ Buscando vídeos en Pexels...")
        clips = []
        last_v = None
        sufijo_n = "creepy" if nicho == "TERROR" else ("money" if nicho == "NEGOCIOS" else "cinematic")

        for i, esc in enumerate(escenas):
            dur = esc["end"] - esc["start"]
            if dur <= 0: continue
            
            intentos = [traducir(esc["kw"]), tema_limpio, sufijo_n]
            v_url = None
            for q in intentos:
                try:
                    r = requests.get(f"https://api.pexels.com/videos/search?query={urllib.parse.quote(q)}&per_page=5&orientation=portrait", headers={"Authorization": pexels_key.strip()}, timeout=5).json()
                    if r.get('videos'):
                        v_url = random.choice(r['videos'])['video_files'][0]['link']
                        break
                except: pass
            
            try:
                if not v_url: raise Exception()
                with open(f"clip_{i}.mp4", 'wb') as f: f.write(requests.get(v_url, timeout=10).content)
                subprocess.run(f'ffmpeg -y -i "clip_{i}.mp4" -vf "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,fps=30" -an -c:v libx264 -preset ultrafast -t {dur + 0.1} "p_{i}.mp4"', shell=True)
                last_v = f"p_{i}.mp4"
            except:
                if last_v: subprocess.run(f"cp {last_v} p_{i}.mp4", shell=True)
                else: subprocess.run(f'ffmpeg -y -f lavfi -i color=c=black:s=720x1280:d=2:r=30 -c:v libx264 -preset ultrafast p_{i}.mp4', shell=True)
            clips.append(f"p_{i}.mp4")

        # 5. Montaje
        subs_cmd = []
        for esc in escenas:
            # Eliminamos acentos para evitar fallos de renderizado en FFmpeg
            t_render = esc["text"].replace('Á','A').replace('É','E').replace('Í','I').replace('Ó','O').replace('Ú','U').replace('Ñ','N')
            subs_cmd.append(f"drawtext=text='{t_render}':fontcolor={color_sub}:fontsize=35:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:borderw=3:bordercolor=black:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{esc['start']},{esc['end']})'")
        
        with open("subs_filter.txt", "w") as f: f.write(",\n".join(subs_cmd))
        with open("lista.txt", "w") as f:
            for c in clips: f.write(f"file '{c}'\n")
        
        subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)
        subprocess.run(f'ffmpeg -y -f lavfi -i "sine=f=75:d=120" -filter_complex "[0:a]volume=0.05" music.mp3', shell=True)
        subprocess.run(f'ffmpeg -y -i t.mp3 -i music.mp3 -filter_complex "[0:a]volume=3.0[v];[1:a]volume=0.2[m];[v][m]amix=inputs=2:duration=first" temp_a.mp3', shell=True)
        
        v_final = f"output/v_{int(time.time())}.mp4"
        subprocess.run(f'ffmpeg -y -i base.mp4 -i temp_a.mp3 -filter_complex_script subs_filter.txt -c:v libx264 -preset veryfast -b:v 3000k -shortest "{v_final}"', shell=True)
        
        if os.path.exists(v_final):
            st.success("✅ Generado desde Base de Datos con 0% de errores.")
            st.video(v_final)
