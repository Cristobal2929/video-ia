import streamlit as st
import os, time, random, subprocess, math, re, urllib.parse
import requests

# Configuración Enterprise
st.set_page_config(page_title="Fénix Viral PRO | v15", layout="centered")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0B0F19 0%, #1A2235 100%); color: #F8FAFC; }
    .pro-title { font-size: 38px; font-weight: 900; background: -webkit-linear-gradient(45deg, #00C6FF, #0072FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 5px; letter-spacing: -1px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX AI STUDIO v15.0</div>', unsafe_allow_html=True)
st.markdown('<div class="pro-subtitle">Lógica Gramatical Directa • Castellano Nativo e Infalible</div>', unsafe_allow_html=True)

# Diccionario de traducción rápido para Pexels (Ampliado para más lógica visual)
TRADUCTOR = {
    "AMOR": "love", "ELEFANTE": "elephant", "DINERO": "money", "ESTAFA": "scam",
    "HACKER": "hacker", "GOBIERNOS": "government", "MILLONARIOS": "success",
    "GATO": "cat", "PERRO": "dog", "COCHE": "car", "CIUDAD": "city", "MIEDO": "scary",
    "TRABAJO": "work", "MUNDO": "world", "ESPACIO": "space", "LUNA": "moon",
    "SOL": "sun", "COMIDA": "food", "ORO": "gold", "MUERTE": "death", "VIDA": "life",
    "FUEGO": "fire", "AGUA": "water", "BOSQUE": "forest", "TIEMPO": "time clock"
}

def traducir(palabra):
    return TRADUCTOR.get(palabra.upper(), palabra.lower())

def detectar_nicho(tema):
    t = tema.lower()
    if any(w in t for w in ["miedo", "terror", "fantasma", "horror"]): return "TERROR"
    if any(w in t for w in ["dinero", "negocio", "invertir", "rico", "millonario"]): return "NEGOCIOS"
    return "MISTERIO"

# --- EL CEREBRO DE LÓGICA HUMANA ---
def redactar_guion_logico(orden_usuario, nicho):
    semilla = random.randint(1, 999999)
    
    # Prompt exigente: Puntuación perfecta, oraciones completas, castellano nativo.
    prompt_maestro = f"""
    ERES UN NARRADOR DE HISTORIAS PROFESIONAL NATIVO EN ESPAÑOL.
    TAREA: Escribe una historia fascinante, logica y ESPECTACULAR sobre: '{orden_usuario}'.
    
    REGLAS DE ORO:
    1. Escribe en CASTELLANO PURO Y PERFECTO. Usa un vocabulario rico y natural.
    2. Usa PUNTUACION NORMAL (puntos, comas, interrogaciones). Las oraciones deben ser completas y logicas.
    3. Estructura: Gancho agresivo + Historia intrigante con datos + Final potente.
    4. El tono debe ser humano y carismatico. NO use jerga tecnica innecesaria.
    5. Termina con la frase: 'Síguenos para más {nicho}'.
    
    IMPORTANTE: Escribe con mayusculas y minusculas normales. NO USES OTROS IDIOMAS.
    MINIMO 150 PALABRAS (NECESITO RETENCION LARGA).
    """
    
    try:
        # Usamos GPT-4 de OpenAI como motor principal de lenguaje para máxima lógica.
        url = f"https://text.pollinations.ai/{urllib.parse.quote(prompt_maestro)}?seed={semilla}&model=openai"
        res = requests.get(url, timeout=25)
        if res.status_code == 200 and len(res.text) > 100:
            # Quitamos comillas si las pone la IA
            return res.text.replace('"', '').strip()
    except: pass
    
    return f"¿Alguna vez te has preguntado cuál es el verdadero secreto detrás de {orden_usuario}? Casi todo el mundo está equivocado. La realidad es mucho más impactante de lo que imaginas. Un grupo de expertos analizó los datos y lo que descubrieron cambió las reglas del juego para siempre. No se trata de suerte, se trata de entender el sistema oculto que maneja todo desde las sombras. Ahora que tienes esta información, el poder está en tus manos. Síguenos para más {nicho}."

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
    st.header("⚙️ Agencia Pro")
    pexels_key = st.text_input("🔑 Pexels API Key:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.selectbox("🎨 Color Subtítulos", ["yellow", "white", "cyan"])

if orden := st.chat_input("Dime el tema (Lógica Infalible Garantizada):"):
    with st.status(f"🚀 Creando obra maestra lógica sobre '{orden}'...", expanded=True) as status:
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.mp3 t.vtt music.mp3 final.mp4 temp_a.mp3 lista.txt subs_filter.txt", shell=True)
        
        nicho = detectar_nicho(orden)
        # 1. Generar guion humano completo con puntuación
        guion_raw = redactar_guion_logico(orden, nicho)
        
        status.write("✍️ Guion con lógica gramatical nativa redactado.")
        
        # 2. Voz (Usamos el texto crudo con puntuación para que Álvaro lea perfecto)
        # rate=0% para un ritmo de narración natural
        subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --rate=0% --text "{guion_raw}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
        
        # 3. Análisis de sincronización para Pexels (Palabra por palabra, pero agrupando por "idea")
        escenas = []
        full_text_for_voice = ""
        with open('t.vtt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i in range(len(lines)):
                if "-->" in lines[i]:
                    start = time_to_sec(lines[i].split(" --> ")[0])
                    end = time_to_sec(lines[i].split(" --> ")[1])
                    txt = lines[i+1].strip()
                    full_text_for_voice += txt + " "
                    # Extraer la palabra más importante de la frase corta
                    palabras_limpias = re.sub(r'[^A-Z\s]', '', txt.upper()).split()
                    palabras_utiles = [p for p in palabras_limpias if len(p) > 4 and p not in ["PORQUE", "CUANDO", "ENTONCES"]]
                    keyword = palabras_utiles[-1] if palabras_utiles else orden
                    # Formateamos el texto para los subtítulos (Todo en mayúsculas y sin acentos para Álvaro)
                    subs_txt = re.sub(r'[^A-Z0-9\s]', '', txt.upper())
                    remplazos_sub = {'Á':'A','É':'E','Í':'I','Ó':'O','Ú':'U','Ñ':'N'}
                    for k, v in remplazos_sub.items(): subs_txt = subs_txt.replace(k, v)
                    escenas.append({"start": start, "end": end, "text": subs_txt, "keyword": keyword})

        # 4. Motor Visual Blindado y Sincronizado
        status.write("🎞️ Sincronizando metraje HD con cada frase lógica...")
        clips_finales = []
        last_clip = None
        
        # Prefijos de búsqueda según nicho
        sufijo_nicho = "creepy" if nicho == "TERROR" else ("money" if nicho == "NEGOCIOS" else "cinematic")

        for i, escena in enumerate(escenas):
            dur = escena["end"] - escena["start"]
            if dur <= 0: continue
            
            # Buscador en cascada para garantizar imagen
            query_palabra = traducir(escena["keyword"])
            intentos = [f"{query_palabra} portrait", f"{orden} {sufijo_nicho}", sufijo_nicho]
            v_url = None
            for q in intentos:
                try:
                    r = requests.get(f"https://api.pexels.com/videos/search?query={urllib.parse.quote(q)}&per_page=10&orientation=portrait", headers={"Authorization": pexels_key.strip()}, timeout=5).json()
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
                else: subprocess.run(f'ffmpeg -y -f lavfi -i color=c=black:s=720x1280:d=2:r=30 -c:v libx264 -preset ultrafast p_{i}.mp4', shell=True)
            clips_finales.append(f"p_{i}.mp4")

        # 5. Subtítulos Cinematográficos Sincronizados
        status.write("✨ Montando Master Final en HD...")
        subs_cmd = []
        for i, escena in enumerate(escenas):
            subs_cmd.append(f"drawtext=text='{escena['text']}':fontcolor={color_sub}:fontsize=32:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:borderw=3:bordercolor=black:shadowcolor=black:shadowx=2:shadowy=2:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{escena['start']},{escena['end']})'")
        with open("subs_filter.txt", "w") as f: f.write(",\n".join(subs_cmd))

        # 6. Exportación Final
        with open("lista.txt", "w") as f:
            for c in clips_finales: f.write(f"file '{c}'\n")
        
        subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)
        subprocess.run(f'ffmpeg -y -f lavfi -i "sine=f=75:d=120" -filter_complex "[0:a]volume=0.1" music.mp3', shell=True)
        subprocess.run(f'ffmpeg -y -i t.mp3 -i music.mp3 -filter_complex "[0:a]volume=3.0[v];[1:a]volume=0.15[m];[v][m]amix=inputs=2:duration=first" temp_a.mp3', shell=True)
        
        v_final = f"output/v_{int(time.time())}.mp4"
        subprocess.run(f'ffmpeg -y -i base.mp4 -i temp_a.mp3 -filter_complex_script subs_filter.txt -c:v libx264 -preset veryfast -b:v 3000k -shortest "{v_final}"', shell=True)
        
        if os.path.exists(v_final):
            st.success("✅ Obra Maestra Lógica Finalizada con Éxito.")
            st.video(v_final)
            st.balloons()
