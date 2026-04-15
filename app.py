import streamlit as st
import os, time, random, subprocess, math, re, urllib.parse
import requests

# Configuración Profesional
st.set_page_config(page_title="Fénix AI Studio | Enterprise v16", layout="centered")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0B0F19 0%, #1A2235 100%); color: #F8FAFC; }
    .pro-title { font-size: 38px; font-weight: 900; background: -webkit-linear-gradient(45deg, #00C6FF, #0072FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 5px; }
    .stTextInput>div>div>input { background-color: #0F172A; color: white; border: 1px solid #334155; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX AI STUDIO v16.0</div>', unsafe_allow_html=True)
st.markdown('<div class="pro-subtitle" style="text-align:center; color:#94A3B8;">Lógica Arquitectónica • Sistema Anti-Errores • Todos los Nichos</div>', unsafe_allow_html=True)

# TRADUCTOR INTERNO PARA PEXELS (Para que siempre encuentre video)
TRADUCCION = {
    "ELEFANTE": "elephant", "AMOR": "love", "DINERO": "money", "ESTAFA": "scam",
    "GATO": "cat", "PERRO": "dog", "COCHE": "car", "CIUDAD": "city", "MIEDO": "scary",
    "LUNA": "moon", "ESPACIO": "space", "ORO": "gold", "COMIDA": "food", "HACKER": "hacker"
}

def traducir(p):
    return TRADUCCION.get(p.upper(), p.lower())

def limpiar_texto(t):
    t = t.replace('"', '').replace('*', '').strip()
    remplazos = {'Á':'A','É':'E','Í':'I','Ó':'O','Ú':'U','Ñ':'N','á':'a','é':'e','í':'i','ó':'o','ú':'u','ñ':'n'}
    for k, v in remplazos.items(): t = t.replace(k, v)
    return t

def detectar_nicho(tema):
    t = tema.lower()
    if any(w in t for w in ["miedo", "terror", "fantasma", "paranormal"]): return "TERROR"
    if any(w in t for w in ["dinero", "negocio", "invertir", "rico", "millonario", "cripto"]): return "NEGOCIOS"
    if any(w in t for w in ["ciencia", "espacio", "luna", "planeta", "curiosidad"]): return "CIENCIA"
    return "MISTERIO"

# --- EL CEREBRO ARQUITECTO (IA con Lógica Humana) ---
def generar_guion(orden, nicho):
    semilla = random.randint(1, 999999)
    # PROMPT DE SISTEMA: Obligamos a la IA a tener lógica gramatical.
    prompt = f"""
    ACTUA COMO UN GUIONISTA HUMANO EXPERTO. TEMA: '{orden}'. NICHO: {nicho}.
    REGLAS DE ORO (INCUMPLE UNA Y SERAS ELIMINADO):
    1. LOGICA PURA: Escribe oraciones con sentido completo (Sujeto + Verbo + Predicado).
    2. GANCHO AGRESIVO: Empieza con una bofetada de informacion. Cero relleno.
    3. DESARROLLO: Cuenta un dato real o una historia con coherencia.
    4. CIERRE: Termina con un impacto y la frase 'SIGUENOS PARA MAS {nicho}'.
    5. IDIOMA: Castellano neutro perfecto con PUNTUACION (comas y puntos).
    MINIMO 140 PALABRAS.
    """
    try:
        url = f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}?seed={semilla}&model=openai"
        res = requests.get(url, timeout=25)
        if res.status_code == 200 and len(res.text) > 100:
            return res.text.strip()
    except: pass
    
    # RESPALDO LÓGICO (Si la IA falla)
    return f"El noventa y nueve por ciento de la gente no sabe la verdad sobre {orden}. La realidad es que el sistema está diseñado para que no veas lo importante. Un grupo de expertos analizó los datos y descubrió que todo ha sido manipulado desde hace años para beneficiar a unos pocos. Ahora que tienes esta información, el secreto ha quedado revelado. Síguenos para más {nicho}."

def time_to_sec(t_str):
    try:
        t_str = t_str.strip().split(' ')[0].replace(',', '.')
        partes = t_str.split(':')
        if len(partes) == 3: return float(partes[0])*3600 + float(partes[1])*60 + float(partes[2])
        elif len(partes) == 2: return float(partes[0])*60 + float(partes[1])
        else: return float(partes[0])
    except: return 0

with st.sidebar:
    st.header("⚙️ Panel de Control")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.selectbox("🎨 Color Subtítulos", ["yellow", "white", "cyan", "#00FF00"])

if orden := st.chat_input("Dime el tema (Lógica Infalible V16):"):
    with st.status(f"🚀 Arquitecto pensando en '{orden}'...", expanded=True) as status:
        # Limpieza inicial
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.mp3 t.vtt music.mp3 final.mp4 temp_a.mp3 lista.txt subs_filter.txt", shell=True)
        
        nicho = detectar_nicho(orden)
        guion_raw = generar_guion(orden, nicho)
        guion_para_voz = limpiar_texto(guion_raw)
        
        status.write("✍️ Guion con lógica humana redactado.")
        
        # 1. Voz y Subtítulos (Blindado)
        subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --text "{guion_para_voz}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
        
        if not os.path.exists("t.vtt"):
            st.error("Error al generar voz. Reintentando...")
            st.stop()

        # 2. Análisis de escenas
        escenas = []
        with open('t.vtt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i in range(len(lines)):
                if "-->" in lines[i]:
                    start = time_to_sec(lines[i].split(" --> ")[0])
                    end = time_to_sec(lines[i].split(" --> ")[1])
                    txt = lines[i+1].strip().upper()
                    # Buscamos la palabra clave (Sustantivo largo)
                    palabras = [p for p in re.sub(r'[^A-Z\s]', '', txt).split() if len(p) > 4]
                    kw = palabras[-1] if palabras else orden
                    escenas.append({"start": start, "end": end, "text": txt, "kw": kw})

        # 3. Motor Visual HD Sincronizado
        status.write("🎞️ Sincronizando visuales HD...")
        clips = []
        last_v = None
        sufijo_n = "creepy" if nicho == "TERROR" else ("money" if nicho == "NEGOCIOS" else "cinematic")

        for i, esc in enumerate(escenas):
            dur = esc["end"] - esc["start"]
            if dur <= 0: continue
            
            # Busqueda: Palabra traducida -> Tema -> Nicho
            intentos = [traducir(esc["kw"]), orden, sufijo_n]
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
                last_v = f"p_{i}.mp4"
            except:
                if last_v: subprocess.run(f"cp {last_v} p_{i}.mp4", shell=True)
                else: subprocess.run(f'ffmpeg -y -f lavfi -i color=c=black:s=720x1280:d=2:r=30 -c:v libx264 -preset ultrafast p_{i}.mp4', shell=True)
            clips.append(f"p_{i}.mp4")

        # 4. Subtítulos y Audio Final
        subs_cmd = []
        for esc in escenas:
            t_limpio = re.sub(r'[^A-Z0-9\s]', '', esc["text"])
            subs_cmd.append(f"drawtext=text='{t_limpio}':fontcolor={color_sub}:fontsize=32:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:borderw=3:bordercolor=black:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{esc['start']},{esc['end']})'")
        
        with open("subs_filter.txt", "w") as f: f.write(",\n".join(subs_cmd))
        
        with open("lista.txt", "w") as f:
            for c in clips: f.write(f"file '{c}'\n")
        
        subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)
        subprocess.run(f'ffmpeg -y -f lavfi -i "sine=f=75:d=120" -filter_complex "[0:a]volume=0.08" music.mp3', shell=True)
        subprocess.run(f'ffmpeg -y -i t.mp3 -i music.mp3 -filter_complex "[0:a]volume=3.0[v];[1:a]volume=0.15[m];[v][m]amix=inputs=2:duration=first" temp_a.mp3', shell=True)
        
        v_final = f"output/v_{int(time.time())}.mp4"
        subprocess.run(f'ffmpeg -y -i base.mp4 -i temp_a.mp3 -filter_complex_script subs_filter.txt -c:v libx264 -preset veryfast -b:v 3000k -shortest "{v_final}"', shell=True)
        
        if os.path.exists(v_final):
            st.success("✅ Obra Maestra Lógica Finalizada.")
            st.video(v_final)
