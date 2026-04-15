import streamlit as st
import os, time, random, subprocess, math, re, urllib.parse
import requests

st.set_page_config(page_title="Fénix Viral PRO | V21", layout="centered")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0B0F19 0%, #1A2235 100%); color: #F8FAFC; }
    .pro-title { font-size: 38px; font-weight: 900; background: -webkit-linear-gradient(45deg, #00C6FF, #00FF7F); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 5px; }
    .stTextInput>div>div>input { background-color: #0F172A; color: white; border: 1px solid #00FF7F; border-radius: 8px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX AI STUDIO v21.0</div>', unsafe_allow_html=True)
st.markdown('<div class="pro-subtitle" style="text-align:center; color:#94A3B8; margin-bottom: 30px;">Edición Nube • Base de Datos Maestra • Cero Archivos Temporales</div>', unsafe_allow_html=True)

TRADUCCION = {
    "ELEFANTE": "elephant", "AMOR": "love", "DINERO": "money", "ESTAFA": "scam",
    "GATO": "cat", "PERRO": "dog", "COCHE": "car", "CIUDAD": "city", "MIEDO": "scary",
    "LUNA": "moon", "ESPACIO": "space", "ORO": "gold", "COMIDA": "food", "HACKER": "hacker",
    "FUEGO": "fire", "AGUA": "water", "BOSQUE": "forest", "TIEMPO": "clock", "MUNDO": "world"
}

def traducir(p): return TRADUCCION.get(p.upper(), p.lower())

def limpiar_orden(orden):
    basura = ["hazme", "haz", "arme", "asme", "dame", "dime", "un", "una", "el", "la", "los", "las", "video", "quiero", "sobre", "de", "del", "que", "hable", "como", "para"]
    orden_limpia = re.sub(r'[^A-Za-zÁÉÍÓÚáéíóúÑñ0-9\s]', '', orden)
    palabras = orden_limpia.lower().split()
    limpias = [p for p in palabras if p not in basura and len(p) > 3]
    return " ".join(limpias) if limpias else orden_limpia

def detectar_nicho(tema):
    t = tema.lower()
    if any(w in t for w in ["miedo", "terror", "fantasma", "paranormal", "horror"]): return "TERROR"
    if any(w in t for w in ["dinero", "negocio", "invertir", "rico", "millonario", "cripto", "empresa"]): return "NEGOCIOS"
    if any(w in t for w in ["ciencia", "espacio", "luna", "planeta", "curiosidad"]): return "CIENCIA"
    if any(w in t for w in ["salud", "dieta", "ejercicio", "fitness"]): return "SALUD"
    return "UNIVERSAL"

def generar_guion_modular(tema, nicho):
    tema = tema.upper()
    v = {
        "tema": tema,
        "año": random.choice(["2008", "2015", "hace un par de años", "1999", "2020", "el año pasado"]),
        "porcentaje": random.choice(["99", "95", "90", "85"]),
        "locura": random.choice(["una verdadera locura", "algo brutal", "un descubrimiento perturbador", "algo que te dejara sin palabras"])
    }

    if nicho == "NEGOCIOS":
        gancho = random.choice(["El {porcentaje} por ciento de la gente pierde todo su dinero con {tema} porque no entienden esta trampa.", "Te estan robando en tu propia cara con {tema} y ni siquiera te has dado cuenta."])
        nudo = random.choice(["En {año}, las grandes elites diseñaron un sistema oculto para que el ciudadano comun fracasara estrepitosamente.", "Todo empezo en {año}, cuando los bancos decidieron mantener a la gente ignorante para multiplicar sus propias ganancias."])
        giro = random.choice(["Pero un analista financiero filtro la formula real y es {locura}.", "Sin embargo, un joven descubrio una falla en este sistema y revento el mercado con un metodo que es {locura}."])
        cierre = random.choice(["La clave esta en hacer lo contrario a la masa. Ahora que sabes esto, el sistema ya no puede robarte. Siguenos para mas negocios.", "Consiste en buscar donde nadie mas mira. El sistema esta roto, es tu turno de aprovecharlo. Siguenos para mas finanzas."])
    elif nicho == "TERROR":
        gancho = random.choice(["No mires este video de noche si le temes a {tema}.", "Esta es la historia mas perturbadora y real jamas contada sobre {tema}."])
        nudo = random.choice(["Todo el mundo piensa que es un invento de internet, pero en {año} la policia encontro algo horrible en un lugar abandonado.", "Durante años, la gente hablaba en susurros sobre lo que paso en {año}. Mandaron a un equipo a investigar, pero desaparecieron sin dejar rastro."])
        giro = random.choice(["Las grabaciones de seguridad mostraron {locura}. El gobierno clasifico los videos, pero alguien logro filtrarlos en la web profunda.", "Cuando los encontraron, habian perdido la cordura. Descubrieron que habian despertado a algo oscuro y fue {locura}."])
        cierre = random.choice(["Lo mas aterrador no es que haya pasado, sino que esa cosa sigue suelta. Si escuchas un ruido hoy, no abras la puerta. Siguenos para mas terror.", "La verdad es tan fuerte que la borraron de los medios, pero el mal nunca desaparece. Mira detras de ti ahora mismo. Siguenos para mas misterios."])
    else: 
        gancho = random.choice(["Te apuesto lo que quieras a que no sabias esto sobre {tema}.", "Te han mentido descaradamente toda tu vida sobre {tema}."])
        nudo = random.choice(["Casi todo el mundo cree que es algo totalmente normal, pero hay un detalle oculto que muy pocos conocen desde {año}.", "Los libros de historia te cuentan una version recortada porque decidieron que no estabas listo para asimilar la verdad."])
        giro = random.choice(["Alguien se dio cuenta de un patron que nadie mas habia visto y resulto ser {locura}.", "Pero un investigador rompio su contrato y filtro unos archivos que demuestran {locura}."])
        cierre = random.choice(["Este simple detalle cambia por completo la forma en la que deberiamos verlo. La proxima vez, no vas a poder ignorarlo. Siguenos para mas curiosidades.", "El {porcentaje} por ciento todavia se cree el cuento oficial, pero las pruebas no dejan lugar a dudas. Despierta de una vez. Siguenos para mas secretos."])
    
    guion_final = f"{gancho} {nudo} {giro} {cierre}".format(**v)
    return guion_final

def time_to_sec(t_str):
    try:
        t_str = t_str.strip().split(' ')[0].replace(',', '.')
        partes = t_str.split(':')
        if len(partes) == 3: return float(partes[0])*3600 + float(partes[1])*60 + float(partes[2])
        elif len(partes) == 2: return float(partes[0])*60 + float(partes[1])
        else: return float(partes[0])
    except: return 0

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2111/2111432.png", width=50)
    st.header("⚙️ Configuración")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.selectbox("🎨 Color de Letra", ["yellow", "white", "cyan"])

if orden := st.chat_input("Dime tu tema (Versión Anti-Streamlit Cloud):"):
    with st.status(f"🚀 Procesando '{orden}' de forma nativa...", expanded=True) as status:
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.mp3 t.vtt music.mp3 final.mp4 temp_a.mp3 lista.txt subs_filter.txt", shell=True)
        
        tema_limpio = limpiar_orden(orden)
        nicho = detectar_nicho(orden)
        
        guion_seguro = generar_guion_modular(tema_limpio, nicho)
        status.write("🧠 Guion generado con éxito.")
        
        # SÚPER LIMPIEZA DEL TEXTO PARA LA TERMINAL DE STREAMLIT
        guion_escapado = guion_seguro.replace('"', '').replace("'", "").replace('`', '').replace('%', ' por ciento')
        
        exito_voz = False
        for i in range(3):
            # Inyección directa de texto sin usar archivos .txt temporales
            subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --text "{guion_escapado}" --write-media t.mp3 --write-subtitles t.vtt', shell=True)
            if os.path.exists("t.vtt") and os.path.getsize("t.vtt") > 0:
                exito_voz = True
                break
            time.sleep(2)
            
        if not exito_voz:
            st.error("🚨 Los servidores de Microsoft rechazaron la conexión. Por favor, dale al botón de enviar otra vez.")
            st.stop()

        status.write("🎙️ Audio procesado correctamente.")

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

        status.write("🎞️ Buscando y recortando vídeos...")
        clips_finales = []
        sufijo_n = "creepy" if nicho == "TERROR" else ("money" if nicho == "NEGOCIOS" else "cinematic")
        last_clip = None

        for i, esc in enumerate(escenas):
            dur = esc["end"] - esc["start"]
            if dur <= 0: continue
            
            intentos = [traducir(esc["kw"]), tema_limpio, sufijo_n, "cinematic"]
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
                last_clip = f"p_{i}.mp4"
            except:
                if last_clip: subprocess.run(f"cp {last_clip} p_{i}.mp4", shell=True)
                else: subprocess.run(f'ffmpeg -y -f lavfi -i color=c=black:s=720x1280:d={dur + 0.1}:r=30 -c:v libx264 -preset ultrafast p_{i}.mp4', shell=True)
            
            clips_finales.append(f"p_{i}.mp4")

        status.write("🎬 Aplicando texto y montando...")
        subs_cmd = []
        for esc in escenas:
            t_render = esc["text"].replace('Á','A').replace('É','E').replace('Í','I').replace('Ó','O').replace('Ú','U').replace('Ñ','N').replace("'", "")
            subs_cmd.append(f"drawtext=text='{t_render}':fontcolor={color_sub}:fontsize=38:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:box=1:boxcolor=black@0.6:boxborderw=10:borderw=2:bordercolor=black:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{esc['start']},{esc['end']})'")
        
        with open("subs_filter.txt", "w") as f: f.write(",\n".join(subs_cmd))
        with open("lista.txt", "w") as f:
            for c in clips_finales: f.write(f"file '{c}'\n")
        
        subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)
        subprocess.run(f'ffmpeg -y -f lavfi -i "sine=f=65:d=120" -filter_complex "[0:a]volume=0.04" music.mp3', shell=True)
        subprocess.run(f'ffmpeg -y -i t.mp3 -i music.mp3 -filter_complex "[0:a]volume=3.0[v];[1:a]volume=0.1[m];[v][m]amix=inputs=2:duration=first" temp_a.mp3', shell=True)
        
        v_final = f"output/v_{int(time.time())}.mp4"
        subprocess.run(f'ffmpeg -y -i base.mp4 -i temp_a.mp3 -filter_complex_script subs_filter.txt -c:v libx264 -preset ultrafast -b:v 2500k -shortest "{v_final}"', shell=True)
        
        if os.path.exists(v_final):
            st.success("✅ VÍDEO SEGURO CREADO.")
            st.video(v_final)
            st.balloons()
