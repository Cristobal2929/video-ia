import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil, math, random, gc
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V179", layout="centered")
components.html("<script>if('wakeLock' in navigator){navigator.wakeLock.request('screen');}</script>", height=0)

st.markdown("""
<style>
    .stApp { background: #000000; color: #FFFFFF; }
    .pro-title { font-size: 42px; font-weight: 900; background: -webkit-linear-gradient(45deg, #FF3E3E, #00FFD1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; text-transform: uppercase; margin-bottom: 20px;}
    .msg { color: #00FFD1; font-family: 'Courier New', monospace; font-size: 14px; margin-bottom: 8px; border-left: 3px solid #FF3E3E; padding-left: 12px; }
    .info-card { padding: 15px; border-radius: 12px; background: #0f172a; border: 1px solid #FF3E3E; text-align: center; color: #00FFD1; margin-top: 25px; font-weight: bold;}
    .stButton>button { width: 100%; background: linear-gradient(45deg, #FF3E3E, #0088ff); color: white; border: none; font-weight: 900; height: 55px; border-radius: 12px; font-size: 18px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V179 🦅🧠</div>', unsafe_allow_html=True)

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

def obtener_datos_tema(t_input):
    t = t_input.lower()
    
    # DICCIONARIO TERROR
    if any(x in t for x in ["miedo", "terror", "horror", "oscuro", "hospital", "sangre", "paranormal", "fantasma", "asustar", "creepy"]):
        return {
            "tipo": "terror",
            "voz": "es-ES-AlvaroNeural",
            "musica": ["https://freepd.com/music/Horror%20Ambience.mp3", "https://freepd.com/music/Deep%20Space.mp3"],
            "kws": ["scary dark", "abandoned building", "creepy forest", "horror night", "dark shadows", "spooky"],
            "fallback": "En el silencio de la noche, las sombras susurran verdades que nadie quiere escuchar."
        }
    # DICCIONARIO GYM / SALUD / DIETAS (¡El que falló antes!)
    elif any(x in t for x in ["gym", "entrenar", "fuerte", "disciplina", "fitness", "dieta", "kilos", "peso", "adelgazar", "nutricion", "salud", "ejercicio", "rutina", "cuerpo", "musculo"]):
        return {
            "tipo": "salud y fitness",
            "voz": "es-MX-JorgeNeural",
            "musica": ["https://cdn.pixabay.com/download/audio/2021/11/25/audio_91b12b556b.mp3?filename=powerful-beat-12179.mp3", "https://freepd.com/music/The%20Crown.mp3"],
            "kws": ["gym workout", "healthy food", "running athlete", "fitness motivation", "diet fruit", "heavy weights"],
            "fallback": "Tu cuerpo es tu templo. La disciplina en tu mesa es la victoria en tu espejo."
        }
    # DICCIONARIO NEGOCIOS (Por defecto si no es nada de lo anterior)
    else:
        return {
            "tipo": "negocio",
            "voz": "es-MX-JorgeNeural",
            "musica": ["https://cdn.pixabay.com/download/audio/2021/05/20/audio_f31f9b3b8e.mp3?filename=dance-playful-night-51078.mp3", "https://upload.wikimedia.org/wikipedia/commons/4/4c/A_Hero_Steps_Forward.mp3"],
            "kws": ["luxury lifestyle", "dubai skyline", "private jet", "expensive supercar", "modern mansion", "money wealth"],
            "fallback": "El éxito no es un accidente, es el resultado de la disciplina y el trabajo constante."
        }

def purificar_guion(t, fallback_text):
    if any(x in t.lower() for x in ["<div", "doctype", "html", "class="]):
        return fallback_text
    return re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ.,! ]', '', t).strip()

def preparar():
    if os.path.exists("taller"): shutil.rmtree("taller")
    os.makedirs("taller", exist_ok=True)
    subprocess.run("pkill ffmpeg", shell=True)

f_abs = get_font()
tema = st.text_input("🧠 Tema del vídeo:", placeholder="Ej: Dietas para perder peso... o Negocios de lujo...")
color_sub = st.selectbox("🎨 Color Subtítulos:", ["yellow", "white", "#FF3E3E", "#00FFD1"])

if st.button("🚀 CREAR VÍDEO CON CEREBRO EXPANDIDO V179"):
    if not tema: st.error("⚠️ Escribe un tema primero")
    else:
        preparar()
        datos_tema = obtener_datos_tema(tema)
        
        log = st.container()
        with log:
            st.markdown(f'<div class="msg">🤖 Modo activado: {datos_tema["tipo"].upper()}</div>', unsafe_allow_html=True)
            st.markdown('<div class="msg">📝 Redactando guion temático...</div>', unsafe_allow_html=True)
            try:
                g_raw = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote('Escribe una frase para TikTok sobre: ' + tema + '. Solo español. Maximo 70 palabras.')}", timeout=25).text
                guion = purificar_guion(g_raw, datos_tema["fallback"])
            except: guion = datos_tema["fallback"]

            st.markdown('<div class="msg">🎙️ Grabando voz perfecta...</div>', unsafe_allow_html=True)
            audio_voz = "taller/voz.mp3"
            subprocess.run(f'edge-tts --voice {datos_tema["voz"]} --text "{guion}" --write-media "{audio_voz}"', shell=True)
            
            st.markdown('<div class="msg">🎵 Descargando atmósfera de audio...</div>', unsafe_allow_html=True)
            musica_file = "taller/bg.mp3"
            try:
                r_m = requests.get(random.choice(datos_tema["musica"]), timeout=15)
                if r_m.status_code == 200:
                    with open(musica_file, "wb") as f: f.write(r_m.content)
            except: pass

            try: dur = float(subprocess.check_output(f'ffprobe -i "{audio_voz}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
            except: dur = 15.0

            st.markdown('<div class="msg">🎧 Mezclando pista de audio...</div>', unsafe_allow_html=True)
            audio_mezcla = "taller/mezcla.mp3"
            fade_st = max(0, dur - 2)
            vol = "0.08" if datos_tema["tipo"] == "terror" else "0.10"
            if os.path.exists(musica_file):
                subprocess.run(f'ffmpeg -y -i "{audio_voz}" -i "{musica_file}" -filter_complex "[1:a]volume={vol},afade=t=out:st={fade_st}:d=2[m];[0:a][m]amix=inputs=2:duration=first" -c:a libmp3lame "{audio_mezcla}" > /dev/null 2>&1', shell=True)
            if not os.path.exists(audio_mezcla) or os.path.getsize(audio_mezcla) < 1000:
                shutil.copy(audio_voz, audio_mezcla)

            palabras = guion.upper().split()
            n_clips = min(math.ceil(dur / 3.0), 12)
            t_clip = dur / n_clips
            clips = []

            for i in range(n_clips):
                kw = random.choice(datos_tema["kws"])
                st.markdown(f'<div class="msg">🎥 Escena {i+1}: Buscando vídeos reales de "{kw}"...</div>', unsafe_allow_html=True)
                
                vid = f"taller/v_{i}.mp4"
                try:
                    h = {"Authorization": PEXELS_API}
                    res = requests.get(f"https://api.pexels.com/videos/search?query={urllib.parse.quote(kw)}&orientation=portrait&per_page=15", headers=h).json()
                    
                    v_url = None
                    for v_item in res.get('videos', []):
                        if v_item['duration'] > 3:
                            v_url = v_item['video_files'][0]['link']
                            break
                    if not v_url: v_url = res['videos'][0]['video_files'][0]['link']

                    sub_split = [palabras[j:j+2] for j in range(i*len(palabras)//n_clips, (i+1)*len(palabras)//n_clips, 2)]
                    t_p = t_clip / max(len(sub_split), 1)
                    draws = []
                    for k, p in enumerate(sub_split):
                        t_txt = " ".join(p)
                        if len(t_txt) > 10:
                            draws.append(f"drawtext=text='{p[0]}':fontfile='{f_abs}':fontcolor={color_sub}:fontsize=70:borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2-45:enable='between(t,{k*t_p},{(k+1)*t_p})'")
                            if len(p) > 1:
                                draws.append(f"drawtext=text='{p[1]}':fontfile='{f_abs}':fontcolor={color_sub}:fontsize=70:borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2+45:enable='between(t,{k*t_p},{(k+1)*t_p})'")
                        else:
                            draws.append(f"drawtext=text='{t_txt}':fontfile='{f_abs}':fontcolor={color_sub}:fontsize=70:borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{k*t_p},{(k+1)*t_p})'")
                    
                    vf = f"scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1,{','.join(draws)}"
                    subprocess.run(f'ffmpeg -y -ss {random.randint(0,2)} -i "{v_url}" -t {t_clip} -vf "{vf}" -c:v libx264 -preset ultrafast -an "{vid}" > /dev/null 2>&1', shell=True)
                    clips.append(os.path.abspath(vid))
                except: pass

            with open("taller/lista.txt", "w") as f:
                for c in clips: f.write(f"file '{c}'\n")
            
            final = "taller/master.mp4"
            subprocess.run(f'ffmpeg -y -f concat -safe 0 -i taller/lista.txt -i "{audio_mezcla}" -map 0:v -map 1:a -c:v libx264 -preset ultrafast -t {dur} "{final}" > /dev/null 2>&1', shell=True)
            
            if os.path.exists(final):
                st.markdown('<div class="info-card">🏆 VÍDEO 100% COHERENTE COMPLETADO</div>', unsafe_allow_html=True)
                with open(final, "rb") as f: st.video(f.read())
