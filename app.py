import streamlit as st
import os, time, random, subprocess, math, re, urllib.parse
import requests
import concurrent.futures

st.set_page_config(page_title="Fénix Viral PRO | Titanium", layout="centered")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0B0F19 0%, #1A2235 100%); color: #F8FAFC; }
    .pro-title { font-size: 42px; font-weight: 900; background: -webkit-linear-gradient(45deg, #FFD700, #FF8C00); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 5px; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); }
    .stTextInput>div>div>input { background-color: #0F172A; color: white; border: 1px solid #FFD700; border-radius: 8px; font-weight: bold; }
    .stSelectbox>div>div>div { background-color: #0F172A; color: white; border: 1px solid #334155; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX AI STUDIO v18.0</div>', unsafe_allow_html=True)
st.markdown('<div class="pro-subtitle" style="text-align:center; color:#94A3B8; margin-bottom: 30px;">Edición Paralela • Modularidad Infinita • Subtítulos TikTok Pro</div>', unsafe_allow_html=True)

# --- TRADUCTOR QUIRÚRGICO ---
TRADUCCION = {
    "ELEFANTE": "elephant", "AMOR": "love", "DINERO": "money", "ESTAFA": "scam",
    "GATO": "cat", "PERRO": "dog", "COCHE": "car", "CIUDAD": "city", "MIEDO": "scary",
    "LUNA": "moon", "ESPACIO": "space", "ORO": "gold", "COMIDA": "food", "HACKER": "hacker",
    "FUEGO": "fire", "AGUA": "water", "BOSQUE": "forest", "TIEMPO": "clock", "MUNDO": "world",
    "MISTERIO": "mystery", "VERDAD": "truth", "GOBIERNO": "government", "MILLONARIO": "wealth"
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
    if any(w in t for w in ["dinero", "negocio", "invertir", "rico", "millonario", "cripto", "empresa"]): return "NEGOCIOS"
    if any(w in t for w in ["ciencia", "espacio", "luna", "planeta", "curiosidad"]): return "CIENCIA"
    if any(w in t for w in ["salud", "dieta", "ejercicio", "fitness"]): return "SALUD"
    return "UNIVERSAL"

# --- MOTOR DE LEGOS GRAMATICALES (Infinitas historias, 100% lógicas) ---
def generar_guion_modular(tema, nicho):
    tema = tema.upper()
    v = {
        "tema": tema,
        "año": random.choice(["2008", "2015", "hace un par de años", "1999", "2020", "el año pasado"]),
        "porcentaje": random.choice(["99", "95", "90", "85"]),
        "locura": random.choice(["una verdadera locura", "algo brutal", "un descubrimiento perturbador", "algo que te dejará sin palabras"])
    }

    if nicho == "NEGOCIOS":
        gancho = random.choice([
            "El {porcentaje} por ciento de la gente pierde todo su dinero con {tema} porque no entienden esta trampa.",
            "Te están robando en tu propia cara con {tema} y ni siquiera te has dado cuenta."
        ])
        nudo = random.choice([
            "En {año}, las grandes élites diseñaron un sistema oculto para que el ciudadano común fracasara estrepitosamente.",
            "Todo empezó en {año}, cuando los bancos decidieron mantener a la gente ignorante para multiplicar sus propias ganancias."
        ])
        giro = random.choice([
            "Pero un analista financiero filtró la fórmula real y es {locura}.",
            "Sin embargo, un joven descubrió una falla en este sistema y reventó el mercado con un método que es {locura}."
        ])
        cierre = random.choice([
            "La clave está en hacer lo contrario a la masa. Ahora que sabes esto, el sistema ya no puede robarte. Síguenos para más negocios.",
            "Consiste en buscar donde nadie más mira. El sistema está roto, es tu turno de aprovecharlo. Síguenos para más finanzas."
        ])
    elif nicho == "TERROR":
        gancho = random.choice([
            "No mires este vídeo de noche si le temes a {tema}.",
            "Esta es la historia más perturbadora y real jamás contada sobre {tema}."
        ])
        nudo = random.choice([
            "Todo el mundo piensa que es un invento de internet, pero en {año} la policía encontró algo horrible en un lugar abandonado.",
            "Durante años, la gente hablaba en susurros sobre lo que pasó en {año}. Mandaron a un equipo a investigar, pero desaparecieron sin dejar rastro."
        ])
        giro = random.choice([
            "Las grabaciones de seguridad mostraron {locura}. El gobierno clasificó los vídeos, pero alguien logró filtrarlos en la web profunda.",
            "Cuando los encontraron, habían perdido la cordura. Descubrieron que habían despertado a algo oscuro y fue {locura}."
        ])
        cierre = random.choice([
            "Lo más aterrador no es que haya pasado, sino que esa cosa sigue suelta. Si escuchas un ruido hoy, no abras la puerta. Síguenos para más terror.",
            "La verdad es tan fuerte que la borraron de los medios, pero el mal nunca desaparece. Mira detrás de ti ahora mismo. Síguenos para más misterios."
        ])
    else: # UNIVERSAL & MISTERIO
        gancho = random.choice([
            "Te apuesto lo que quieras a que no sabías esto sobre {tema}.",
            "Te han mentido descaradamente toda tu vida sobre {tema}."
        ])
        nudo = random.choice([
            "Casi todo el mundo cree que es algo totalmente normal, pero hay un detalle oculto que muy pocos conocen desde {año}.",
            "Los libros de historia te cuentan una versión recortada porque decidieron que no estabas listo para asimilar la verdad."
        ])
        giro = random.choice([
            "Alguien se dio cuenta de un patrón que nadie más había visto y resultó ser {locura}.",
            "Pero un investigador rompió su contrato y filtró unos archivos que demuestran {locura}."
        ])
        cierre = random.choice([
            "Este simple detalle cambia por completo la forma en la que deberíamos verlo. La próxima vez, no vas a poder ignorarlo. Síguenos para más curiosidades.",
            "El {porcentaje} por ciento todavía se cree el cuento oficial, pero las pruebas no dejan lugar a dudas. Despierta de una vez. Síguenos para más secretos."
        ])
    
    return f"{gancho} {nudo} {giro} {cierre}".format(**v)

def time_to_sec(t_str):
    try:
        t_str = t_str.strip().split(' ')[0].replace(',', '.')
        partes = t_str.split(':')
        if len(partes) == 3: return float(partes[0])*3600 + float(partes[1])*60 + float(partes[2])
        elif len(partes) == 2: return float(partes[0])*60 + float(partes[1])
        else: return float(partes[0])
    except: return 0

# --- FUNCIÓN DE DESCARGA PARALELA (Magia de Velocidad) ---
def procesar_clip(i, esc, pexels_key, orden, sufijo_n, clip_duration):
    intentos = [traducir(esc["kw"]), orden, sufijo_n, "cinematic"]
    v_url = None
    for q in intentos:
        try:
            r = requests.get(f"https://api.pexels.com/videos/search?query={urllib.parse.quote(q)}&per_page=5&orientation=portrait", headers={"Authorization": pexels_key.strip()}, timeout=5).json()
            if r.get('videos'):
                v_url = random.choice(r['videos'])['video_files'][0]['link']
                break
        except: pass
    
    clip_name = f"clip_{i}.mp4"
    out_name = f"p_{i}.mp4"
    try:
        if not v_url: raise Exception()
        with open(clip_name, 'wb') as f: f.write(requests.get(v_url, timeout=10).content)
        # Recorte y escalado ultrafast
        subprocess.run(f'ffmpeg -y -i "{clip_name}" -vf "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,fps=30" -an -c:v libx264 -preset ultrafast -t {clip_duration} "{out_name}"', shell=True)
        return out_name
    except:
        # Fallback a fondo negro seguro
        subprocess.run(f'ffmpeg -y -f lavfi -i color=c=black:s=720x1280:d={clip_duration}:r=30 -c:v libx264 -preset ultrafast "{out_name}"', shell=True)
        return out_name

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2111/2111432.png", width=50)
    st.header("⚙️ Motor Titanium")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.selectbox("🎨 Color de Letra", ["yellow", "white", "cyan", "#00FF00"])
    st.markdown("---")
    st.success("Hilos Múltiples: ACTIVADO ⚡")
    st.success("Subtítulos Pro: ACTIVADO 🎬")

if orden := st.chat_input("Dime tu tema (Prepárate para la velocidad x100):"):
    with st.status(f"🚀 Fabricando Máster Titanium sobre '{orden}'...", expanded=True) as status:
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.mp3 t.vtt music.mp3 final.mp4 temp_a.mp3 lista.txt subs_filter.txt", shell=True)
        
        tema_limpio = limpiar_orden(orden)
        nicho = detectar_nicho(orden)
        
        # 1. Guion Modular Infinito
        guion_con_puntuacion = generar_guion_modular(tema_limpio, nicho)
        status.write("🧠 Lego Gramatical ensamblado a la perfección.")
        
        # 2. Voz Natural
        subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --rate=0% --text "{guion_con_puntuacion}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
        
        if not os.path.exists("t.vtt"):
            st.error("Error en la síntesis de voz. Reintenta.")
            st.stop()

        # 3. Análisis
        escenas = []
        with open('t.vtt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i in range(len(lines)):
                if "-->" in lines[i]:
                    start_sec = time_to_sec(lines[i].split(" --> ")[0])
                    end_sec = time_to_sec(lines[i].split(" --> ")[1])
                    txt = lines[i+1].strip()
                    txt_limpio = re.sub(r'[^A-Za-zÁÉÍÓÚáéíóúÑñ0-9\s]', '', txt)
                    palabras = [p for p in txt_limpio.split() if len(p) > 3]
                    kw = palabras[-1] if palabras else tema_limpio
                    escenas.append({"start": start_sec, "end": end_sec, "text": txt_limpio.upper(), "kw": kw})

        # 4. Descarga Paralela de Vídeos (VELOCIDAD X100)
        status.write("⚡ Descargando y procesando imágenes en paralelo...")
        sufijo_n = "creepy" if nicho == "TERROR" else ("money" if nicho == "NEGOCIOS" else "cinematic")
        
        clips_ordenados = [None] * len(escenas)
        
        # Usamos 3 trabajadores (hilos) para no saturar la memoria del servidor pero ir 3 veces más rápido
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futuros = {executor.submit(procesar_clip, i, esc, pexels_key, tema_limpio, sufijo_n, esc["end"] - esc["start"] + 0.1): i for i, esc in enumerate(escenas)}
            for futuro in concurrent.futures.as_completed(futuros):
                indice = futuros[futuro]
                clips_ordenados[indice] = futuro.result()

        clips_finales = [c for c in clips_ordenados if c is not None]

        # 5. Subtítulos TIKTOK PRO (Caja translúcida para legibilidad perfecta)
        status.write("🎬 Aplicando efectos cinematográficos y subtítulos Pro...")
        subs_cmd = []
        for esc in escenas:
            t_render = esc["text"].replace('Á','A').replace('É','E').replace('Í','I').replace('Ó','O').replace('Ú','U').replace('Ñ','N').replace("'", "")
            # MAGIA: box=1:boxcolor=black@0.6 crea el fondo oscuro de TikTok. borderw=2 da un perfil sutil.
            subs_cmd.append(f"drawtext=text='{t_render}':fontcolor={color_sub}:fontsize=38:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:box=1:boxcolor=black@0.6:boxborderw=10:borderw=2:bordercolor=black:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{esc['start']},{esc['end']})'")
        
        with open("subs_filter.txt", "w") as f: f.write(",\n".join(subs_cmd))
        with open("lista.txt", "w") as f:
            for c in clips_finales: f.write(f"file '{c}'\n")
        
        # 6. Ensamblaje Final Ultra Rápido
        subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)
        subprocess.run(f'ffmpeg -y -f lavfi -i "sine=f=65:d=120" -filter_complex "[0:a]volume=0.04" music.mp3', shell=True)
        subprocess.run(f'ffmpeg -y -i t.mp3 -i music.mp3 -filter_complex "[0:a]volume=3.0[v];[1:a]volume=0.1[m];[v][m]amix=inputs=2:duration=first" temp_a.mp3', shell=True)
        
        v_final = f"output/v_{int(time.time())}.mp4"
        # Bitrate a 3500k para calidad cristalina
        subprocess.run(f'ffmpeg -y -i base.mp4 -i temp_a.mp3 -filter_complex_script subs_filter.txt -c:v libx264 -preset veryfast -b:v 3500k -shortest "{v_final}"', shell=True)
        
        if os.path.exists(v_final):
            st.success("✅ VÍDEO TITANIUM GENERADO CON ÉXITO.")
            st.video(v_final)
            st.balloons()
