import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil, math, random, gc
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V181", layout="centered")
components.html("<script>if('wakeLock' in navigator){navigator.wakeLock.request('screen');}</script>", height=0)

st.markdown("""
<style>
    .stApp { background: #000000; color: #FFFFFF; }
    .pro-title { font-size: 42px; font-weight: 900; background: -webkit-linear-gradient(45deg, #00FFD1, #FFD700); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; text-transform: uppercase; margin-bottom: 20px;}
    .msg { color: #00FFD1; font-family: 'Courier New', monospace; font-size: 14px; margin-bottom: 8px; border-left: 3px solid #FFD700; padding-left: 12px; }
    .info-card { padding: 15px; border-radius: 12px; background: #0f172a; border: 1px solid #00FFD1; text-align: center; color: #00FFD1; margin-top: 25px; font-weight: bold;}
    .stButton>button { width: 100%; background: linear-gradient(45deg, #00FFD1, #0088ff); color: white; border: none; font-weight: 900; height: 55px; border-radius: 12px; font-size: 18px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V181 🦅🔥</div>', unsafe_allow_html=True)

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

# MÚSICA 100% WIKIMEDIA (Imposible que falle la descarga)
MUSICA_NEGOCIO = [
    "https://upload.wikimedia.org/wikipedia/commons/4/4c/A_Hero_Steps_Forward.mp3",
    "https://upload.wikimedia.org/wikipedia/commons/c/c5/Winds_Of_Stories.mp3"
]

MUSICA_TERROR = [
    "https://upload.wikimedia.org/wikipedia/commons/2/23/Closer_to_the_Void.mp3"
]

def obtener_datos_tema(t_input):
    t = t_input.lower()
    if any(x in t for x in ["miedo", "terror", "horror", "oscuro", "hospital", "paranormal"]):
        return {
            "tipo": "terror",
            "voz": "es-ES-AlvaroNeural",
            "musica": MUSICA_TERROR,
            "kws": ["scary dark", "abandoned building", "creepy forest", "dark shadows"],
            "fallback": "En el silencio de la noche, las sombras susurran verdades que nadie quiere escuchar."
        }
    else:
        return {
            "tipo": "negocio",
            "voz": "es-MX-JorgeNeural",
            "musica": MUSICA_NEGOCIO,
            "kws": ["luxury lifestyle", "dubai skyline", "private jet", "expensive supercar", "modern mansion"],
            "fallback": "El éxito no es un accidente, es el resultado de la disciplina y el trabajo constante todos los días de tu vida."
        }

def purificar_guion(t, fallback_text):
    if any(x in t.lower() for x in ["<div", "doctype", "html", "class="]):
        return fallback_text
    
    texto_limpio = t
    cortes = ["support pollinations", "powered by", "free text api", "coffee to keep"]
    for corte in cortes:
        if corte.lower() in texto_limpio.lower():
            texto_limpio = texto_limpio[:texto_limpio.lower().index(corte.lower())]

    texto_limpio = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ.,! ]', '', texto_limpio).strip()
    if len(texto_limpio) < 15: # Exigimos que sea una frase con cara y ojos, no tres palabras
        return fallback_text
    return texto_limpio

def preparar():
    if os.path.exists("taller"): shutil.rmtree("taller")
    os.makedirs("taller", exist_ok=True)
    subprocess.run("pkill ffmpeg", shell=True)

f_abs = get_font()
tema = st.text_input("🧠 Tema del vídeo:", placeholder="Ej: El camino al éxito...")
color_sub = st.selectbox("🎨 Color Subtítulos:", ["yellow", "white", "#00FFD1"])

if st.button("🚀 CREAR VÍDEO (GUIÓN NATURAL)"):
    if not tema: st.error("⚠️ Escribe un tema primero")
    else:
        preparar()
        datos_tema = obtener_datos_tema(tema)
        
        log = st.container()
        with log:
            st.markdown('<div class="msg">📝 Exigiendo a la IA un guion épico y con sentido...</div>', unsafe_allow_html=True)
            try:
                # PROMPT MEJORADO: Le exigimos frases fluidas y con sentido
                prompt = f"Escribe un guion fluido, épico y con mucho sentido para TikTok sobre: {tema}. Redacta frases completas, con una narrativa natural, no palabras sueltas. Solo español. Maximo 60 palabras."
                g_raw = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}", timeout=25).text
                guion = purificar_guion(g_raw, datos_tema["fallback"])
            except: guion = datos_tema["fallback"]

            st.markdown('<div class="msg">🎙️ Grabando voz de Jorge...</div>', unsafe_allow_html=True)
            audio_voz = "taller/voz.mp3"
            subprocess.run(f'edge-tts --voice {datos_tema["voz"]} --text "{guion}" --write-media "{audio_voz}"', shell=True)
            
            st.markdown('<div class="msg">🎵 Descargando banda sonora desde Wikipedia...</div>', unsafe_allow_html=True)
            musica_file = "taller/bg.mp3"
            exito_musica = False
            try:
                # Damos más tiempo para asegurar que descargue la música (timeout=20)
                r_m = requests.get(random.choice(datos_tema["musica"]), headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
                if r_m.status_code == 200 and len(r_m.content) > 100000:
                    with open(musica_file, "wb") as f: f.write(r_m.content)
                    exito_musica = True
            except: pass

            try: dur = float(subprocess.check_output(f'ffprobe -i "{audio_voz}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
            except: dur = 15.0

            st.markdown('<div class="msg">🎧 Mezclando audio maestro...</div>', unsafe_allow_html=True)
            audio_mezcla = "taller/mezcla.mp3"
            fade_st = max(0, dur - 2)
            vol = "0.08" if datos_tema["tipo"] == "terror" else "0.10"
            
            if exito_musica:
                subprocess.run(f'ffmpeg -y -i "{audio_voz}" -i "{musica_file}" -filter_complex "[1:a]volume={vol},afade=t=out:st={fade_st}:d=2[m];[0:a][m]amix=inputs=2:duration=first" -c:a libmp3lame "{audio_mezcla}" > /dev/null 2>&1', shell=True)
            else:
                st.markdown('<div class="msg" style="color:orange;">⚠️ Falló el servidor de música, usando solo voz para salvar el vídeo.</div>', unsafe_allow_html=True)
                shutil.copy(audio_voz, audio_mezcla)

            palabras = guion.upper().split()
            n_clips = min(math.ceil(dur / 3.0), 12)
            t_clip = dur / n_clips
            clips = []

            for i in range(n_clips):
                kw = random.choice(datos_tema["kws"])
                st.markdown(f'<div class="msg">🎥 Escena {i+1}: Recortando vídeos de "{kw}"...</div>', unsafe_allow_html=True)
                
                vid = f"taller/v_{i}.mp4"
                try:
                    h = {"Authorization": PEXELS_API}
                    res = requests.get(f"https://api.pexels.com/videos/search?query={urllib.parse.quote(kw)}&orientation=portrait&per_page=15", headers=h).json()
                    
                    videos_validos = [v for v in res.get('videos', []) if v.get('duration', 0) > 3]
                    v_url = random.choice(videos_validos)['video_files'][0]['link'] if videos_validos else res['videos'][0]['video_files'][0]['link']

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
                st.markdown('<div class="info-card">🏆 VÍDEO COMPLETO Y CON SENTIDO</div>', unsafe_allow_html=True)
                with open(final, "rb") as f: st.video(f.read())
