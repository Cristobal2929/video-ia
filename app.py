import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil, math, random, gc
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V185", layout="centered")
components.html("<script>if('wakeLock' in navigator){navigator.wakeLock.request('screen');}</script>", height=0)

st.markdown("""
<style>
    .stApp { background: #000000; color: #FFFFFF; }
    .pro-title { font-size: 42px; font-weight: 900; background: -webkit-linear-gradient(45deg, #00FFD1, #FFD700); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; text-transform: uppercase; margin-bottom: 20px;}
    .msg { color: #00FFD1; font-family: 'Courier New', monospace; font-size: 14px; margin-bottom: 8px; border-left: 3px solid #FFD700; padding-left: 12px; }
    .info-card { padding: 15px; border-radius: 12px; background: #0f172a; border: 1px solid #00FFD1; text-align: center; color: #00FFD1; margin-top: 25px; font-weight: bold;}
    .stButton>button { width: 100%; background: linear-gradient(45deg, #00FFD1, #0088ff); color: white; border: none; font-weight: 900; height: 55px; border-radius: 12px; font-size: 18px;}
    .stTextArea>div>div>textarea, .stTextInput>div>div>input { background-color: #1a1a1a; color: white; border: 1px solid #00FFD1; border-radius: 8px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V185 🦅⚙️</div>', unsafe_allow_html=True)

@st.cache_resource
def get_font():
    p = "font.ttf"
    if not os.path.exists(p):
        try:
            r = requests.get("https://github.com/matomo-org/travis-scripts/raw/master/fonts/Arial.ttf")
            with open(p, "wb") as f: f.write(r.content)
        except: pass
    return "font.ttf"

PEXELS_API = "Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ"

def descargar_musica(ruta, lista_urls):
    random.shuffle(lista_urls)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    for url in lista_urls:
        try:
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code == 200 and len(r.content) > 100000:
                with open(ruta, "wb") as f: f.write(r.content)
                return True
        except: pass
    return False

def limpiar_texto(t):
    # Anticódigo y Spam de IA
    texto_limpio = t
    cortes = ["support pollinations", "powered by", "free text api", "tool_calls", "doctype", "html"]
    for corte in cortes:
        if corte.lower() in texto_limpio.lower():
            texto_limpio = texto_limpio[:texto_limpio.lower().index(corte.lower())]

    t = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ.,! ]', '', texto_limpio)
    return re.sub(r'\s+', ' ', t).strip()

def preparar():
    if os.path.exists("taller"): shutil.rmtree("taller")
    os.makedirs("taller", exist_ok=True)
    subprocess.run("pkill ffmpeg", shell=True)

f_abs = get_font()

# INTERFAZ FUSIONADA
categoria = st.selectbox("🎬 Temática General (Voz y Música):", ["Negocios / Éxito", "Gym / Motivación", "Terror / Misterio"])
color_sub = st.selectbox("🎨 Color Subtítulos:", ["yellow", "white", "#00FFD1", "#FF3E3E"])
tema_prompt = st.text_input("🧠 Tema para que la IA escriba el guion:", placeholder="Ej: Hábitos de éxito")
guion_personalizado = st.text_area("📝 O pega tu propio guion EXACTO:", placeholder="Si pegas un texto aquí, el bot lo usará sin importar lo que ponga arriba.", height=100)

if st.button("🚀 CREAR VÍDEO (NÚCLEO V169)"):
    preparar()
    log = st.container()
    with log:
        # 1. AJUSTES SEGÚN CATEGORÍA
        if categoria == "Terror / Misterio":
            voz_ia = "es-ES-AlvaroNeural"
            musica_lista = ["https://freepd.com/music/Horror%20Ambience.mp3", "https://freepd.com/music/Deep%20Space.mp3"]
            kws = ["scary dark", "abandoned building", "creepy forest"]
            fallback = "El miedo es solo una ilusión, pero las sombras siempre estarán ahí para recordarte lo que ocultas."
        elif categoria == "Gym / Motivación":
            voz_ia = "es-MX-JorgeNeural"
            musica_lista = ["https://freepd.com/music/Vopna.mp3", "https://freepd.com/music/Epic%20Boss%20Battle.mp3"]
            kws = ["gym workout", "fitness motivation", "heavy weights training"]
            fallback = "Nadie va a hacer el trabajo por ti. Levántate y suda hasta que te sientas orgulloso."
        else:
            voz_ia = "es-MX-JorgeNeural"
            musica_lista = ["https://upload.wikimedia.org/wikipedia/commons/4/4c/A_Hero_Steps_Forward.mp3", "https://upload.wikimedia.org/wikipedia/commons/c/c5/Winds_Of_Stories.mp3"]
            kws = ["luxury lifestyle", "dubai skyline", "private jet", "expensive supercar"]
            fallback = "La disciplina es el puente entre tus metas y tus logros. Ve a por todas."

        # 2. SELECCIÓN DEL GUION
        if guion_personalizado.strip():
            st.markdown('<div class="msg">📝 Usando tu guion manual...</div>', unsafe_allow_html=True)
            guion = limpiar_texto(guion_personalizado)
        elif tema_prompt.strip():
            st.markdown('<div class="msg">📝 Redactando guion con IA...</div>', unsafe_allow_html=True)
            p_g = f"Escribe una historia o frase motivacional sobre {tema_prompt}. Solo español. Maximo 75 palabras."
            try:
                g_raw = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote(p_g)}", timeout=20).text
                guion = limpiar_texto(g_raw)
                if len(guion.split()) < 5: guion = fallback
            except: guion = fallback
        else:
            guion = fallback

        st.markdown('<div class="msg">🎙️ Grabando voz...</div>', unsafe_allow_html=True)
        audio_voz = "taller/voz.mp3"
        subprocess.run(f'edge-tts --voice {voz_ia} --text "{guion}" --write-media "{audio_voz}"', shell=True)
        
        st.markdown('<div class="msg">🎵 Descargando música segura...</div>', unsafe_allow_html=True)
        musica_file = "taller/bg.mp3"
        descargar_musica(musica_file, musica_lista)

        try: dur = float(subprocess.check_output(f'ffprobe -i "{audio_voz}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
        except: dur = 15.0

        st.markdown('<div class="msg">🎧 Mezclando audio (Motor V169)...</div>', unsafe_allow_html=True)
        audio_mezcla = "taller/mezcla.mp3"
        fade_st = max(0, dur - 2)
        if os.path.exists(musica_file):
            # CÓDIGO INTACTO V169
            subprocess.run(f'ffmpeg -y -i "{audio_voz}" -i "{musica_file}" -filter_complex "[1:a]volume=0.10,afade=t=out:st={fade_st}:d=2[m];[0:a][m]amix=inputs=2:duration=first" -c:a libmp3lame -threads 1 "{audio_mezcla}" > /dev/null 2>&1', shell=True)
        
        if not os.path.exists(audio_mezcla) or os.path.getsize(audio_mezcla) < 1000:
            shutil.copy(audio_voz, audio_mezcla)

        palabras_puras = guion.upper().split()
        n_clips = min(math.ceil(dur / 3.0), 12) 
        t_clip = dur / n_clips
        clips = []
        chunk_size = max(len(palabras_puras) // n_clips, 1)
        videos_usados = [] # MEMORIA PARA NO REPETIR

        for i in range(n_clips):
            kw = random.choice(kws)
            st.markdown(f'<div class="msg">🎥 Escena {i+1}/{n_clips}: Descargando y tatuando "{kw}"...</div>', unsafe_allow_html=True)
            
            raw_vid, vid = f"taller/r_{i}.mp4", f"taller/v_{i}.mp4"
            
            pal_clip = palabras_puras[i*chunk_size:(i+1)*chunk_size] if i < n_clips-1 else palabras_puras[i*chunk_size:]
            chunks_sub = [pal_clip[j:j+2] for j in range(0, len(pal_clip), 2)]
            t_pair = t_clip / max(len(chunks_sub), 1)
            text_filters = []
            
            for j, p in enumerate(chunks_sub):
                ts, te = j * t_pair, (j + 1) * t_pair
                if len(p) == 2 and (len(p[0]) + len(p[1]) > 10):
                    text_filters.append(f"drawtext=text='{p[0]}':fontfile='{f_abs}':fontcolor={color_sub}:fontsize=70:borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2-45:enable='between(t,{ts},{te})'")
                    text_filters.append(f"drawtext=text='{p[1]}':fontfile='{f_abs}':fontcolor={color_sub}:fontsize=70:borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2+45:enable='between(t,{ts},{te})'")
                else:
                    text_filters.append(f"drawtext=text='{' '.join(p)}':fontfile='{f_abs}':fontcolor={color_sub}:fontsize=70:borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{ts},{te})'")

            vf_script = ",".join(text_filters)
            with open(f"taller/f_{i}.txt", "w") as f: f.write(f"scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1,format=yuv420p,{vf_script}")

            try:
                h = {"Authorization": PEXELS_API}
                res = requests.get(f"https://api.pexels.com/videos/search?query={urllib.parse.quote(kw)}&orientation=portrait&per_page=15", headers=h, timeout=10).json()
                
                # SELECCIÓN ANTI-REPETICIÓN
                validos = [v for v in res.get('videos', []) if v.get('duration', 0) > 3 and v.get('id') not in videos_usados]
                if validos: v_elegido = random.choice(validos)
                else: v_elegido = res['videos'][0]
                
                videos_usados.append(v_elegido['id'])
                v_url = v_elegido['video_files'][0]['link']
                
                # DESCARGA LOCAL (El secreto de la V169)
                with open(raw_vid, 'wb') as f: f.write(requests.get(v_url, timeout=15).content)
                subprocess.run(f'ffmpeg -y -stream_loop -1 -i "{raw_vid}" -t {t_clip} -filter_script:v taller/f_{i}.txt -c:v libx264 -preset ultrafast -r 24 -an -threads 1 "{vid}" > /dev/null 2>&1', shell=True)
            except:
                subprocess.run(f'ffmpeg -y -f lavfi -i color=c=#1A1A1A:s=720x1280:d={t_clip}:r=24 -vf "format=yuv420p,{vf_script}" -c:v libx264 -preset ultrafast -an -threads 1 "{vid}" > /dev/null 2>&1', shell=True)

            clips.append(os.path.abspath(vid).replace('\\', '/'))
            if os.path.exists(raw_vid): os.remove(raw_vid)
            gc.collect()

        st.markdown('<div class="msg">🎬 Ensamblado final...</div>', unsafe_allow_html=True)
        with open("taller/lista.txt", "w") as f:
            for c in clips: f.write(f"file '{c}'\n")
        
        final = "taller/master.mp4"
        subprocess.run(f'ffmpeg -y -f concat -safe 0 -i taller/lista.txt -i "{audio_mezcla}" -map 0:v -map 1:a -c:v libx264 -preset ultrafast -crf 28 -c:a aac -threads 1 -t {dur} "{final}" > /dev/null 2>&1', shell=True)
        
        if os.path.exists(final):
            st.markdown('<div class="info-card">🏆 VÍDEO ESTABLE V185 COMPLETADO</div>', unsafe_allow_html=True)
            with open(final, "rb") as f: st.video(f.read())
            st.balloons()
