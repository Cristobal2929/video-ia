import streamlit as st
import os, time, random, subprocess, math, re, urllib.parse
import requests

st.set_page_config(page_title="Fénix Viral PRO | V22", layout="centered")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #09090b 0%, #111827 100%); color: #F8FAFC; }
    .pro-title { font-size: 38px; font-weight: 900; background: -webkit-linear-gradient(45deg, #E81CFF, #40C9FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 5px; }
    .stTextInput>div>div>input { background-color: #1F2937; color: white; border: 1px solid #E81CFF; border-radius: 8px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX AI STUDIO v22.0</div>', unsafe_allow_html=True)
st.markdown('<div class="pro-subtitle" style="text-align:center; color:#94A3B8; margin-bottom: 30px;">Director de Cine AI • Sincronización Visual Perfecta</div>', unsafe_allow_html=True)

def detectar_nicho(tema):
    t = tema.lower()
    if any(w in t for w in ["miedo", "terror", "fantasma", "paranormal", "horror", "misterio", "oscuro"]): return "TERROR"
    if any(w in t for w in ["dinero", "negocio", "invertir", "rico", "millonario", "cripto", "empresa"]): return "NEGOCIOS"
    if any(w in t for w in ["ciencia", "espacio", "luna", "planeta", "curiosidad"]): return "CIENCIA"
    return "UNIVERSAL"

# --- EL CEREBRO DIRECTOR (Escribe guion y dirige la cámara) ---
def generar_script_y_visuales(orden, nicho):
    semilla = random.randint(1, 999999)
    
    # Instrucción para que la IA devuelva Guion + Búsqueda Visual
    prompt = f"""
    Act as an expert TikTok Video Director. Topic: '{orden}'. Niche: {nicho}.
    Write a 5-part viral script. 
    Format your response EXACTLY as 5 lines using the pipe '|' symbol to separate the Spanish narration and the English visual search term.
    DO NOT ADD ANY OTHER TEXT.
    
    Format:
    [Spanish Narration] | [1 English Keyword for background video]
    
    Example:
    El 99% de las personas ignora este secreto. | secret
    Hace años se descubrió algo en el bosque. | dark forest
    Resulta que todo era una simulación. | matrix computer
    Si miras de cerca, lo entenderás. | eye looking
    Síguenos para más videos. | follow button
    """
    
    try:
        url = f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}?seed={semilla}&model=openai"
        res = requests.get(url, timeout=25)
        if res.status_code == 200 and "|" in res.text:
            return res.text.strip().split('\n')
    except: pass
    
    # Fallback si la IA falla (Garantizamos el formato)
    if nicho == "TERROR":
        return [
            f"Nadie quiere hablar de la verdad sobre {orden}. | scary mysterious",
            "Hace años se encontraron pruebas inquietantes. | abandoned place",
            "Los expertos intentaron ocultar la información al público. | secret files",
            "Pero lo más aterrador es que sigue ocurriendo hoy. | dark shadow",
            "Síguenos para más historias perturbadoras. | scary face"
        ]
    elif nicho == "NEGOCIOS":
        return [
            f"Te están robando tu dinero con {orden} y no lo sabes. | money counting",
            "Los bancos han diseñado un sistema para que fracases. | business building",
            "Pero un experto filtró el patrón exacto para ganar. | hacker computer",
            "La clave es hacer lo contrario a lo que dicen las noticias. | trading chart",
            "Aplica esto hoy y cambia tu vida. Síguenos para más. | luxury car"
        ]
    else:
        return [
            f"Te apuesto lo que quieras a que no sabías esto sobre {orden}. | curious mind",
            "La mayoría de la gente vive engañada por el sistema. | crowd of people",
            "Pero hace poco se reveló un detalle que lo cambia todo. | bright light",
            "Si prestas atención, te darás cuenta de la mentira. | shocked face",
            "Despierta y no te dejes manipular. Síguenos para más secretos. | cinematic epic"
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
    st.image("https://cdn-icons-png.flaticon.com/512/2111/2111432.png", width=50)
    st.header("⚙️ Configuración")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.selectbox("🎨 Color de Letra", ["yellow", "white", "cyan"])

if orden := st.chat_input("Dime tu tema (Competencia directa contra IAs de pago):"):
    with st.status(f"🚀 El Director AI está procesando '{orden}'...", expanded=True) as status:
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.mp3 t.vtt music.mp3 final.mp4 temp_a.mp3 lista.txt subs_filter.txt temp_guion.txt", shell=True)
        
        nicho = detectar_nicho(orden)
        
        # 1. Obtenemos las escenas del Director AI
        lineas_script = generar_script_y_visuales(orden, nicho)
        
        # Separamos el texto de la voz y las búsquedas de vídeo
        texto_completo = ""
        busquedas_visuales = []
        
        for linea in lineas_script:
            if "|" in linea:
                partes = linea.split("|")
                texto_completo += partes[0].strip() + " "
                busquedas_visuales.append(partes[1].strip())
        
        if not texto_completo:
            st.error("Error en la IA. Inténtalo de nuevo.")
            st.stop()
            
        status.write("🧠 Guion y Dirección Visual generados.")
        
        # 2. Generamos el audio global
        texto_limpio = re.sub(r'[^A-Za-zÁÉÍÓÚáéíóúÑñ0-9\s.,]', '', texto_completo)
        with open("temp_guion.txt", "w", encoding="utf-8") as f:
            f.write(texto_limpio)
            
        exito_voz = False
        for i in range(3):
            subprocess.run('edge-tts --voice es-ES-AlvaroNeural --rate=0% -f temp_guion.txt --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
            if os.path.exists("t.vtt") and os.path.getsize("t.vtt") > 0:
                exito_voz = True
                break
            time.sleep(2)
            
        if not exito_voz:
            st.error("Fallo de conexión. Reintenta.")
            st.stop()

        status.write("🎙️ Audio procesado correctamente.")

        # 3. Extraemos el tiempo total y lo dividimos por el número de escenas
        dur_audio = float(subprocess.check_output("ffprobe -i t.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True).decode('utf-8').strip())
        num_escenas = len(busquedas_visuales)
        dur_por_clip = dur_audio / num_escenas

        # 4. Motor Visual Estricto
        status.write("🎞️ Buscando vídeos cinematográficos EXACTOS...")
        clips_finales = []
        
        # Modificadores de nicho para GARANTIZAR que no salgan cosas raras
        sufijos = {
            "TERROR": "creepy dark cinematic horror",
            "NEGOCIOS": "corporate wealth success money",
            "CIENCIA": "science abstract macro",
            "UNIVERSAL": "cinematic epic 4k"
        }
        modificador = sufijos.get(nicho, "cinematic epic 4k")
        last_clip = None

        for i, busqueda in enumerate(busquedas_visuales):
            # Combinamos lo que pide la IA con el modificador estricto del nicho
            query_exacta = f"{busqueda} {modificador}"
            status.write(f"  ► Escena {i+1}: Buscando '{query_exacta}'")
            
            v_url = None
            try:
                r = requests.get(f"https://api.pexels.com/videos/search?query={urllib.parse.quote(query_exacta)}&per_page=5&orientation=portrait", headers={"Authorization": pexels_key.strip()}, timeout=5).json()
                if r.get('videos'):
                    v_url = random.choice(r['videos'])['video_files'][0]['link']
            except: pass
            
            # Procesar Clip
            try:
                if not v_url: raise Exception()
                with open(f"clip_{i}.mp4", 'wb') as f: f.write(requests.get(v_url, timeout=10).content)
                subprocess.run(f'ffmpeg -y -i "clip_{i}.mp4" -vf "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,fps=30" -an -c:v libx264 -preset ultrafast -t {dur_por_clip} "p_{i}.mp4"', shell=True)
                last_clip = f"p_{i}.mp4"
            except:
                if last_clip: subprocess.run(f"cp {last_clip} p_{i}.mp4", shell=True)
                else: subprocess.run(f'ffmpeg -y -f lavfi -i color=c=black:s=720x1280:d={dur_por_clip}:r=30 -c:v libx264 -preset ultrafast p_{i}.mp4', shell=True)
            
            clips_finales.append(f"p_{i}.mp4")

        status.write("🎬 Aplicando subtítulos estilo CapCut...")
        # Generamos los comandos de subtítulos leyendo el VTT original
        subs_cmd = []
        with open('t.vtt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i in range(len(lines)):
                if "-->" in lines[i]:
                    start = time_to_sec(lines[i].split(" --> ")[0])
                    end = time_to_sec(lines[i].split(" --> ")[1])
                    txt = lines[i+1].strip().upper()
                    t_render = re.sub(r'[^A-Z0-9\s]', '', txt).replace('Á','A').replace('É','E').replace('Í','I').replace('Ó','O').replace('Ú','U').replace('Ñ','N')
                    # Subtítulo con caja negra translúcida profesional
                    subs_cmd.append(f"drawtext=text='{t_render}':fontcolor={color_sub}:fontsize=40:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:box=1:boxcolor=black@0.6:boxborderw=10:borderw=2:bordercolor=black:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{start},{end})'")
        
        with open("subs_filter.txt", "w") as f: f.write(",\n".join(subs_cmd))
        with open("lista.txt", "w") as f:
            for c in clips_finales: f.write(f"file '{c}'\n")
        
        # 5. Ensamblaje Final
        subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)
        
        # Música dramática según nicho
        frecuencia = 60 if nicho == "TERROR" else 75
        subprocess.run(f'ffmpeg -y -f lavfi -i "sine=f={frecuencia}:d=120" -filter_complex "[0:a]volume=0.05" music.mp3', shell=True)
        subprocess.run(f'ffmpeg -y -i t.mp3 -i music.mp3 -filter_complex "[0:a]volume=3.0[v];[1:a]volume=0.15[m];[v][m]amix=inputs=2:duration=first" temp_a.mp3', shell=True)
        
        v_final = f"output/v_{int(time.time())}.mp4"
        subprocess.run(f'ffmpeg -y -i base.mp4 -i temp_a.mp3 -filter_complex_script subs_filter.txt -c:v libx264 -preset ultrafast -b:v 2500k -shortest "{v_final}"', shell=True)
        
        if os.path.exists(v_final):
            st.success("✅ VÍDEO NIVEL AGENCIA CREADO. ¡Compara esto con las IAs!")
            st.video(v_final)
