import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil, math, random, gc
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V175", layout="centered")
components.html("<script>if('wakeLock' in navigator){navigator.wakeLock.request('screen');}</script>", height=0)

st.markdown("""
<style>
    .stApp { background: #000000; color: #FFFFFF; }
    .pro-title { font-size: 42px; font-weight: 900; background: -webkit-linear-gradient(45deg, #FF3E3E, #00FFD1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; text-transform: uppercase; margin-bottom: 20px;}
    .msg { color: #00FFD1; font-family: 'Courier New', monospace; font-size: 14px; margin-bottom: 8px; border-left: 3px solid #FF3E3E; padding-left: 12px; }
    .stButton>button { width: 100%; background: linear-gradient(45deg, #FF3E3E, #0088ff); color: white; border: none; font-weight: 900; height: 55px; border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V175 🦅🎯</div>', unsafe_allow_html=True)

@st.cache_resource
def get_font():
    p = "font.ttf"
    if not os.path.exists(p):
        r = requests.get("https://github.com/matomo-org/travis-scripts/raw/master/fonts/Arial.ttf")
        with open(p, "wb") as f: f.write(r.content)
    return "font.ttf"

PEXELS_API = "Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ"

def descargar_musica_inteligente(ruta, tema):
    t = tema.lower()
    m_neg = ["https://cdn.pixabay.com/download/audio/2021/05/20/audio_f31f9b3b8e.mp3?filename=dance-playful-night-51078.mp3"]
    m_ter = ["https://freepd.com/music/Horror%20Ambience.mp3", "https://freepd.com/music/Deep%20Space.mp3"]
    url = random.choice(m_ter if any(x in t for x in ["miedo", "terror", "hospital"]) else m_neg)
    try:
        r = requests.get(url, timeout=10)
        with open(ruta, "wb") as f: f.write(r.content)
        return True
    except: return False

def purificar(t):
    if "<div" in t.lower(): return "El silencio del hospital esconde secretos que nadie quiere despertar."
    return re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ.,! ]', '', t).strip()

f_abs = get_font()
tema = st.text_input("🧠 Guion exacto:", placeholder="Ej: Terror en un hospital abandonado...")

if st.button("🚀 GENERAR VÍDEO SINCRONIZADO"):
    if not tema: st.error("Escribe algo")
    else:
        if os.path.exists("taller"): shutil.rmtree("taller")
        os.makedirs("taller", exist_ok=True)
        
        log = st.container()
        with log:
            st.markdown('<div class="msg">📝 Creando historia...</div>', unsafe_allow_html=True)
            try:
                g_raw = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote(tema + '. Solo español. Max 65 palabras.')}").text
                guion = purificar(g_raw)
            except: guion = tema

            audio_voz = "taller/voz.mp3"
            v = "es-ES-AlvaroNeural" if any(x in tema.lower() for x in ["miedo", "terror", "hospital"]) else "es-MX-JorgeNeural"
            subprocess.run(f'edge-tts --voice {v} --text "{guion}" --write-media "{audio_voz}"', shell=True)
            
            musica = "taller/bg.mp3"
            descargar_musica_inteligente(musica, tema)
            
            dur = float(subprocess.check_output(f'ffprobe -i "{audio_voz}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
            mezcla = "taller/mezcla.mp3"
            subprocess.run(f'ffmpeg -y -i "{audio_voz}" -i "{musica}" -filter_complex "[1:a]volume=0.08,afade=t=out:st={dur-2}:d=2[m];[0:a][m]amix=inputs=2:duration=first" "{mezcla}" > /dev/null 2>&1', shell=True)

            palabras = guion.split()
            n_clips = min(math.ceil(dur / 3.0), 10)
            t_clip = dur / n_clips
            clips = []

            for i in range(n_clips):
                frag = " ".join(palabras[i*len(palabras)//n_clips : (i+1)*len(palabras)//n_clips])
                # AJUSTE CLAVE: Buscar exactamente lo que dice el fragmento del guion
                busqueda = f"{frag} horror" if any(x in tema.lower() for x in ["miedo", "terror", "hospital"]) else f"{frag} luxury"
                st.markdown(f'<div class="msg">🎥 Buscando fondo para: "{frag[:30]}..."</div>', unsafe_allow_html=True)
                
                vid = f"taller/v_{i}.mp4"
                try:
                    h = {"Authorization": PEXELS_API}
                    res = requests.get(f"https://api.pexels.com/videos/search?query={urllib.parse.quote(busqueda)}&orientation=portrait&per_page=5", headers=h).json()
                    v_url = random.choice(res['videos'])['video_files'][0]['link']
                    
                    sub = [palabras[j:j+2] for j in range(i*len(palabras)//n_clips, (i+1)*len(palabras)//n_clips, 2)]
                    t_p = t_clip / max(len(sub), 1)
                    filtros = []
                    for k, p in enumerate(sub):
                        filtros.append(f"drawtext=text='{' '.join(p).upper()}':fontfile='{f_abs}':fontcolor=white:fontsize=70:borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{k*t_p},{(k+1)*t_p})'")
                    
                    vf = f"scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1,{','.join(filtros)}"
                    subprocess.run(f'ffmpeg -y -i "{v_url}" -t {t_clip} -vf "{vf}" -c:v libx264 -preset ultrafast -an "{vid}" > /dev/null 2>&1', shell=True)
                    clips.append(os.path.abspath(vid))
                except: pass

            with open("taller/lista.txt", "w") as f:
                for c in clips: f.write(f"file '{c}'\n")
            
            final = "taller/master.mp4"
            subprocess.run(f'ffmpeg -y -f concat -safe 0 -i taller/lista.txt -i "{mezcla}" -map 0:v -map 1:a -c:v libx264 -preset ultrafast -t {dur} "{final}" > /dev/null 2>&1', shell=True)
            
            if os.path.exists(final):
                st.video(final)
