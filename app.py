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

st.markdown('<div class="pro-title">FÉNIX AI STUDIO v13.0</div>', unsafe_allow_html=True)
st.markdown('<div class="pro-subtitle">Cerebro de Acción • Sincronización Visual Infalible</div>', unsafe_allow_html=True)

def limpiar_texto_final(texto):
    # Eliminar basura y dejar solo castellano puro
    texto = re.sub(r'http\S+', '', texto)
    texto = texto.upper()
    # Reemplazos críticos para la voz
    texto = texto.replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U').replace('Ñ', 'N')
    # Quitar símbolos excepto letras y espacios
    texto = re.sub(r'[^A-Z\s]', '', texto)
    return " ".join(texto.split())

def detectar_nicho(tema):
    t = tema.lower()
    if any(w in t for w in ["miedo", "terror", "fantasma", "creepy"]): return "TERROR"
    if any(w in t for w in ["dinero", "negocio", "invertir", "rico", "millonario"]): return "NEGOCIOS"
    return "MISTERIO"

# --- EL NUEVO CEREBRO DE ACCIÓN ---
def redactar_guion_unico(orden_usuario, nicho):
    semilla = random.randint(1, 999999)
    
    # Prompt diseñado para que la IA escriba cosas que se puedan VER
    prompt_maestro = f"""
    ERES UN GUIONISTA VIRAL EXPERTO EN RETENCION. 
    TAREA: Escribe una historia UNICA sobre: '{orden_usuario}'.
    
    ESTILO OBLIGATORIO:
    1. Usa un lenguaje rico pero basado en ACCIONES Y OBJETOS REALES que se puedan ver (ej: dinero, gente, fuego, ciudad, bosque).
    2. Empieza con un GANCHO AGRESIVO: Una bofetada de informacion en la primera frase.
    3. No uses palabras abstractas o filosoficas que no tengan imagen clara.
    4. Termina con un cierre potente y la frase 'SIGUENOS PARA MAS {nicho}'.
    
    REGLAS TECNICAS:
    - TODO EN MAYUSCULAS. SIN PUNTOS. SIN COMAS. SIN TILDES.
    - MINIMO 130 PALABRAS.
    - SOLO ESCRIBE EL GUION, NADA DE INTRODUCCIONES.
    """
    
    try:
        url = f"https://text.pollinations.ai/{urllib.parse.quote(prompt_maestro)}?seed={semilla}&model=openai"
        res = requests.get(url, timeout=20)
        if res.status_code == 200 and len(res.text) > 80:
            return limpiar_texto_final(res.text)
    except: pass
    
    # Fallback ultra-seguro si la red falla
    return f"EL NOVENTA Y NUEVE POR CIENTO DE LA GENTE NO TIENE NI IDEA DE LO QUE ESTA PASANDO CON {orden_usuario.upper()} PERO LA REALIDAD ES QUE EL SISTEMA ESTA DISEÑADO PARA QUE NO VEAS LA VERDAD UN ANALISTA FILTRO LOS DATOS Y LO QUE ENCONTRO FUE UNA AUTENTICA LOCURA RESULTA QUE CADA MOVIMIENTO HABIA SIDO CALCULADO PARA BENEFICIAR A UNOS POCOS MIENTRAS EL RESTO PERDIA SU TIEMPO Y SU DINERO AHORA QUE CONOCES ESTE SECRETO TIENES EL PODER DE CAMBIAR LAS REGLAS DEL JUEGO SIGUENOS PARA MAS {nicho}"

def time_to_sec(t_str):
    try:
        t_str = t_str.strip().split(' ')[0].replace(',', '.')
        partes = t_str.split(':')
        if len(partes) == 3: return float(partes[0])*3600 + float(partes[1])*60 + float(partes[2])
        elif len(partes) == 2: return float(partes[0])*60 + float(partes[1])
        else: return float(partes[0])
    except: return 0

with st.sidebar:
    st.header("⚙️ Agencia Pro")
    pexels_key = st.text_input("🔑 Pexels API Key:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.selectbox("🎨 Color Subtítulos", ["yellow", "white", "cyan"])

if orden := st.chat_input("Dime el tema (Lógica y Visuales 100% reales):"):
    with st.status(f"🚀 Cerebro de Acción procesando '{orden}'...", expanded=True) as status:
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.mp3 t.vtt music.mp3 final.mp4 temp_a.mp3 lista.txt subs_filter.txt", shell=True)
        
        nicho = detectar_nicho(orden)
        guion = redactar_guion_unico(orden, nicho)
        
        # 1. Voz
        status.write("✍️ Generando guion de alta retención...")
        subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --rate=-10% --text "{guion}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
        
        # 2. Análisis de escenas (Detección de palabras clave para Pexels)
        escenas = []
        with open('t.vtt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i in range(len(lines)):
                if "-->" in lines[i]:
                    start = time_to_sec(lines[i].split(" --> ")[0])
                    end = time_to_sec(lines[i].split(" --> ")[1])
                    txt = lines[i+1].strip().upper()
                    # Buscamos la palabra más sustanciosa
                    palabras = [p for p in txt.split() if len(p) > 4 and p not in ["PORQUE", "CUANDO", "ENTONCES", "SOBRE"]]
                    keyword = palabras[-1] if palabras else orden
                    escenas.append({"start": start, "end": end, "text": txt, "keyword": keyword})

        # 3. Motor de Vídeo Blindado
        status.write("🎞️ Sincronizando metraje con cada palabra clave...")
        clips_finales = []
        last_clip = None
        
        for i, escena in enumerate(escenas):
            dur = escena["end"] - escena["start"]
            if dur <= 0: continue
            
            # Buscador inteligente: Primero palabra clave, si falla el tema, si falla el nicho
            intentos = [escena["keyword"], orden, nicho.lower()]
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
                # Calidad HD 720p 30fps
                subprocess.run(f'ffmpeg -y -i "clip_{i}.mp4" -vf "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,fps=30" -an -c:v libx264 -preset ultrafast -t {dur + 0.2} "p_{i}.mp4"', shell=True)
                last_clip = f"p_{i}.mp4"
            except:
                if last_clip: subprocess.run(f"cp {last_clip} p_{i}.mp4", shell=True)
                else: subprocess.run(f'ffmpeg -y -f lavfi -i color=c=black:s=720x1280:d=2:r=30 -c:v libx264 -preset ultrafast p_{i}.mp4', shell=True)
            clips_finales.append(f"p_{i}.mp4")

        # 4. Subtítulos Cinematográficos
        subs_cmd = []
        for i, escena in enumerate(escenas):
            subs_cmd.append(f"drawtext=text='{escena['text']}':fontcolor={color_sub}:fontsize=32:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:borderw=3:bordercolor=black:shadowcolor=black:shadowx=2:shadowy=2:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{escena['start']},{escena['end']})'")
        with open("subs_filter.txt", "w") as f: f.write(",\n".join(subs_cmd))

        # 5. Exportación
        with open("lista.txt", "w") as f:
            for c in clips_finales: f.write(f"file '{c}'\n")
        
        subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)
        subprocess.run(f'ffmpeg -y -f lavfi -i "sine=f=70:d=60" -filter_complex "[0:a]volume=0.1" music.mp3', shell=True)
        subprocess.run(f'ffmpeg -y -i t.mp3 -i music.mp3 -filter_complex "[0:a]volume=3.0[v];[1:a]volume=0.2[m];[v][m]amix=inputs=2:duration=first" temp_a.mp3', shell=True)
        
        v_final = f"output/v_{int(time.time())}.mp4"
        subprocess.run(f'ffmpeg -y -i base.mp4 -i temp_a.mp3 -filter_complex_script subs_filter.txt -c:v libx264 -preset ultrafast -b:v 3000k -shortest "{v_final}"', shell=True)
        
        if os.path.exists(v_final):
            st.success("✅ Master Finalizado con Éxito.")
            st.video(v_final)
