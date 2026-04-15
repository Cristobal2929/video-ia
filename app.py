import streamlit as st
import os, time, random, subprocess, math, re, urllib.parse
import requests

st.set_page_config(page_title="Fénix Viral PRO", layout="centered")

# --- INTERFAZ PROFESIONAL ---
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0B0F19 0%, #1A2235 100%); color: #F8FAFC; }
    .pro-title { font-size: 38px; font-weight: 900; background: -webkit-linear-gradient(45deg, #00C6FF, #0072FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 5px; letter-spacing: -1px; }
    .stTextInput>div>div>input { background-color: #0F172A; color: white; border: 1px solid #334155; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX AI STUDIO v12.0</div>', unsafe_allow_html=True)
st.markdown('<div class="pro-subtitle">Cerebro Universal • Escritura Creativa Ilimitada</div>', unsafe_allow_html=True)

# --- TRADUCTOR Y LIMPIEZA ---
def limpiar_texto_final(texto):
    # Eliminar cualquier rastro de IA o código
    texto = re.sub(r'http\S+', '', texto)
    texto = re.sub(r'[^\w\s]', '', texto).upper()
    # Quitar tildes para que la voz no haga cosas raras
    texto = texto.replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U').replace('Ñ', 'N')
    return " ".join(texto.split())

def detectar_nicho(tema):
    t = tema.lower()
    if any(w in t for w in ["miedo", "terror", "creepy"]): return "TERROR"
    if any(w in t for w in ["dinero", "negocio", "invertir"]): return "NEGOCIOS"
    return "MISTERIO"

# --- EL CEREBRO UNIVERSAL (Llamada a IA Real con Leyes de Estilo) ---
def redactar_guion_unico(orden_usuario, nicho):
    semilla = random.randint(1, 999999)
    
    # Instrucciones maestras para que use TODO el castellano
    prompt_maestro = f"""
    ERES UN MAESTRO DE LA NARRATIVA CASTELLANA Y GUIONISTA VIRAL.
    TAREA: Escribe una historia UNICA, CREATIVA y ESPECTACULAR sobre: '{orden_usuario}'.
    
    REGLAS DE ORO:
    1. Usa un vocabulario rico y variado. Nada de plantillas. Inventa una trama desde cero.
    2. Empieza con un GANCHO BRUTAL que atrape en el primer segundo.
    3. Desarrolla la historia con tension, dando detalles curiosos o datos sorprendentes.
    4. El tono debe ser humano, carismatico y muy fluido.
    5. Termina con un cierre epico y añade 'SIGUENOS PARA MAS {nicho}'.
    
    RESTRICCIONES TECNICAS:
    - TODO EN MAYUSCULAS.
    - CERO PUNTOS Y CERO COMAS.
    - CERO TILDES.
    - MINIMO 130 PALABRAS.
    - SOLO ESCRIBE EL CONTENIDO DE LA HISTORIA.
    """
    
    try:
        # Intentamos con el motor más creativo
        url = f"https://text.pollinations.ai/{urllib.parse.quote(prompt_maestro)}?seed={semilla}&model=openai"
        res = requests.get(url, timeout=25)
        if res.status_code == 200 and len(res.text) > 100 and "<html" not in res.text.lower():
            return limpiar_texto_final(res.text)
    except:
        pass
    
    # Respaldo de emergencia (Lego mejorado) si la IA se cae
    return f"SABES QUE TIENE EN COMUN TODO EL MUNDO CUANDO HABLAMOS DE {orden_usuario.upper()} CASI NADIE SE ATREVE A DECIR LA VERDAD PERO HOY VAMOS A ROMPER EL SILENCIO RESULTA QUE EXISTE UN DETALLE QUE CAMBIA POR COMPLETO LO QUE CONOCEMOS Y ES QUE LA LOGICA QUE NOS ENSEÑARON NO SIRVE PARA NADA CUANDO ENTIENDES ESTE SECRETO TU FORMA DE VER LA REALIDAD SE TRANSFORMA AL INSTANTE SIGUENOS PARA MAS {nicho}"

def time_to_sec(t_str):
    try:
        t_str = t_str.strip().split(' ')[0].replace(',', '.')
        partes = t_str.split(':')
        if len(partes) == 3: return float(partes[0])*3600 + float(partes[1])*60 + float(partes[2])
        elif len(partes) == 2: return float(partes[0])*60 + float(partes[1])
        else: return float(partes[0])
    except: return 0

# --- PANEL DE CONTROL ---
with st.sidebar:
    st.header("⚙️ Agencia Pro")
    pexels_key = st.text_input("🔑 Pexels API Key:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.selectbox("🎨 Color Subtítulos", ["yellow", "white", "cyan", "#00FF00"])

if orden := st.chat_input("Dime CUALQUIER tema y crearé un guion único en castellano..."):
    with st.status(f"🚀 Cerebro Universal pensando en '{orden}'...", expanded=True) as status:
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.mp3 t.vtt music.mp3 final.mp4 temp_a.mp3 lista.txt subs_filter.txt", shell=True)
        
        nicho = detectar_nicho(orden)
        guion = redactar_guion_unico(orden, nicho)
        
        # 1. Audio
        status.write("✍️ Guion único en castellano redactado.")
        subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --rate=-10% --text "{guion}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
        
        # 2. Análisis de escenas para Pexels (Palabra por palabra)
        escenas = []
        with open('t.vtt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i in range(len(lines)):
                if "-->" in lines[i]:
                    start = time_to_sec(lines[i].split(" --> ")[0])
                    end = time_to_sec(lines[i].split(" --> ")[1])
                    txt = lines[i+1].strip().upper()
                    palabras = [p for p in txt.split() if len(p) > 4]
                    keyword = palabras[-1] if palabras else orden
                    escenas.append({"start": start, "end": end, "text": txt, "keyword": keyword})

        # 3. Motor Visual Sincronizado
        status.write("🎞️ Buscando visuales para este guion específico...")
        clips_finales = []
        last_clip = None
        
        for i, escena in enumerate(escenas):
            dur = escena["end"] - escena["start"]
            if dur <= 0: continue
            
            # Buscador en inglés para máxima calidad
            query = escena["keyword"].lower()
            v_url = None
            try:
                # Intentamos buscar el concepto de la escena
                r = requests.get(f"https://api.pexels.com/videos/search?query={query}&per_page=3&orientation=portrait", headers={"Authorization": pexels_key.strip()}, timeout=5).json()
                if r.get('videos'):
                    v_url = random.choice(r['videos'])['video_files'][0]['link']
            except: pass
            
            try:
                if not v_url: raise Exception()
                with open(f"clip_{i}.mp4", 'wb') as f: f.write(requests.get(v_url, timeout=10).content)
                subprocess.run(f'ffmpeg -y -i "clip_{i}.mp4" -vf "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,fps=30" -an -c:v libx264 -preset ultrafast -t {dur + 0.2} "p_{i}.mp4"', shell=True)
                last_clip = f"p_{i}.mp4"
            except:
                if last_clip: subprocess.run(f"cp {last_clip} p_{i}.mp4", shell=True)
                else: subprocess.run(f'ffmpeg -y -f lavfi -i color=c=black:s=720x1280:d=2:r=30 -c:v libx264 -preset ultrafast p_{i}.mp4', shell=True)
            clips_finales.append(f"p_{i}.mp4")

        # 4. Filtro de Subtítulos Pro
        subs_cmd = []
        for i, escena in enumerate(escenas):
            subs_cmd.append(f"drawtext=text='{escena['text']}':fontcolor={color_sub}:fontsize=32:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:borderw=3:bordercolor=black:shadowcolor=black:shadowx=2:shadowy=2:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{escena['start']},{escena['end']})'")
        with open("subs_filter.txt", "w") as f: f.write(",\n".join(subs_cmd))

        # 5. Master Final
        with open("lista.txt", "w") as f:
            for c in clips_finales: f.write(f"file '{c}'\n")
        
        subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)
        subprocess.run(f'ffmpeg -y -f lavfi -i "sine=f=70:d=60" -filter_complex "[0:a]volume=0.1" music.mp3', shell=True)
        subprocess.run(f'ffmpeg -y -i t.mp3 -i music.mp3 -filter_complex "[0:a]volume=3.0[v];[1:a]volume=0.2[m];[v][m]amix=inputs=2:duration=first" temp_a.mp3', shell=True)
        
        v_final = f"output/v_{int(time.time())}.mp4"
        subprocess.run(f'ffmpeg -y -i base.mp4 -i temp_a.mp3 -filter_complex_script subs_filter.txt -c:v libx264 -preset ultrafast -b:v 2500k -shortest "{v_final}"', shell=True)
        
        if os.path.exists(v_final):
            st.success("✅ Obra maestra finalizada.")
            st.video(v_final)
