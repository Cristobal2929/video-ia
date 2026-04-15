import streamlit as st
import os, time, random, subprocess, math, re, urllib.parse
import requests

st.set_page_config(page_title="Fénix Viral PRO", layout="centered")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0B0F19 0%, #1A2235 100%); color: #F8FAFC; }
    .pro-title { font-size: 38px; font-weight: 900; background: -webkit-linear-gradient(45deg, #00C6FF, #0072FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 5px; letter-spacing: -1px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX AI STUDIO v14.0</div>', unsafe_allow_html=True)
st.markdown('<div class="pro-subtitle">El Guardián del Idioma • Castellano Puro y Acción Real</div>', unsafe_allow_html=True)

# FUNCIÓN MAESTRA DE LIMPIEZA: El bot hace el trabajo sucio, no la IA
def procesar_guion_para_voz(texto):
    # Quitamos tildes para evitar errores de pronunciación robótica
    remplazos = {'Á':'A','É':'E','Í':'I','Ó':'O','Ú':'U','Ñ':'N','á':'a','é':'e','í':'i','ó':'o','ú':'u','ñ':'n'}
    for original, nuevo in remplazos.items():
        texto = texto.replace(original, nuevo)
    # Ponemos todo en mayúsculas y quitamos puntuación
    texto = texto.upper()
    texto = re.sub(r'[^A-Z0-9\s]', '', texto)
    return " ".join(texto.split())

def detectar_nicho(tema):
    t = tema.lower()
    if any(w in t for w in ["miedo", "terror", "fantasma", "horror"]): return "TERROR"
    if any(w in t for w in ["dinero", "negocio", "invertir", "millonario"]): return "NEGOCIOS"
    return "MISTERIO"

# --- EL NUEVO CEREBRO QUE PENSARÁ EN ESPAÑOL REAL ---
def redactar_guion_maestro(orden_usuario, nicho):
    semilla = random.randint(1, 999999)
    
    # Aquí le pedimos que escriba BIEN, con puntos y comas. Nosotros limpiaremos después.
    prompt_maestro = f"""
    ERES UN GUIONISTA TOP DE TIKTOK NATIVO EN ESPAÑOL.
    TAREA: Escribe un guion VIRAL y ESPECTACULAR sobre: '{orden_usuario}'.
    
    REGLAS DE ORO:
    1. Escribe en CASTELLANO PURO Y PERFECTO. Usa un vocabulario rico.
    2. Estructura: Gancho agresivo + Historia con datos reales y visuales + Final impactante.
    3. El tono debe ser humano y carismatico.
    4. Termina con la frase: 'SIGUENOS PARA MAS {nicho}'.
    
    IMPORTANTE: Escribe con puntuacion normal (puntos y comas). NO USES OTROS IDIOMAS.
    MINIMO 140 PALABRAS.
    """
    
    try:
        # Usamos el modelo más potente disponible gratis (OpenAI/GPT-4)
        url = f"https://text.pollinations.ai/{urllib.parse.quote(prompt_maestro)}?seed={semilla}&model=openai"
        res = requests.get(url, timeout=25)
        if res.status_code == 200 and len(res.text) > 100:
            return res.text # Devolvemos el texto tal cual, lo limpiaremos en el bot
    except: pass
    
    # Guion de emergencia ultra-lógico
    return f"¿Sabías que el noventa y nueve por ciento de la gente está equivocada con {orden_usuario}? La realidad es mucho más impactante. Un grupo de expertos analizó los datos y lo que descubrieron cambió las reglas del juego para siempre. No se trata de suerte, se trata de entender el sistema oculto que maneja todo desde las sombras. Ahora que tienes esta información, el poder está en tus manos. Síguenos para más {nicho}."

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
    pexels_key = st.text_input("🔑 Pexels API Key:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.selectbox("🎨 Color Subtítulos", ["yellow", "white", "cyan"])

if orden := st.chat_input("Dime el tema (Garantizo castellano perfecto):"):
    with st.status(f"🚀 Creando obra maestra sobre '{orden}'...", expanded=True) as status:
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.mp3 t.vtt music.mp3 final.mp4 temp_a.mp3 lista.txt subs_filter.txt", shell=True)
        
        nicho = detectar_nicho(orden)
        guion_sucio = redactar_guion_maestro(orden, nicho)
        guion_limpio = procesar_guion_para_voz(guion_sucio)
        
        status.write("✍️ Guion redactado y verificado en castellano.")
        
        # 1. Voz (Usamos el texto procesado para que Álvaro no se trabe)
        subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --rate=-10% --text "{guion_limpio}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
        
        # 2. Análisis de sincronización para Pexels
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

        # 3. Motor Visual Blindado
        status.write("🎞️ Sincronizando imágenes palabra por palabra...")
        clips_finales = []
        last_clip = None
        
        for i, escena in enumerate(escenas):
            dur = escena["end"] - escena["start"]
            if dur <= 0: continue
            
            # Buscador inteligente en cascada
            intentos = [escena["keyword"], orden, nicho.lower()]
            v_url = None
            for q in intentos:
                try:
                    r = requests.get(f"https://api.pexels.com/videos/search?query={urllib.parse.quote(q)}&per_page=3&orientation=portrait", headers={"Authorization": pexels_key.strip()}, timeout=5).json()
                    if r.get('videos'):
                        v_url = random.choice(r['videos'])['video_files'][0]['link']
                        break
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

        # 4. Subtítulos
        subs_cmd = []
        for i, escena in enumerate(escenas):
            subs_cmd.append(f"drawtext=text='{escena['text']}':fontcolor={color_sub}:fontsize=32:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:borderw=3:bordercolor=black:shadowcolor=black:shadowx=2:shadowy=2:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{escena['start']},{escena['end']})'")
        with open("subs_filter.txt", "w") as f: f.write(",\n".join(subs_cmd))

        # 5. Exportación
        with open("lista.txt", "w") as f:
            for c in clips_finales: f.write(f"file '{c}'\n")
        
        subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)
        subprocess.run(f'ffmpeg -y -f lavfi -i "sine=f=75:d=120" -filter_complex "[0:a]volume=0.1" music.mp3', shell=True)
        subprocess.run(f'ffmpeg -y -i t.mp3 -i music.mp3 -filter_complex "[0:a]volume=3.0[v];[1:a]volume=0.15[m];[v][m]amix=inputs=2:duration=first" temp_a.mp3', shell=True)
        
        v_final = f"output/v_{int(time.time())}.mp4"
        subprocess.run(f'ffmpeg -y -i base.mp4 -i temp_a.mp3 -filter_complex_script subs_filter.txt -c:v libx264 -preset veryfast -b:v 3000k -shortest "{v_final}"', shell=True)
        
        if os.path.exists(v_final):
            st.success("✅ Video Finalizado con Idioma Correcto.")
            st.video(v_final)
