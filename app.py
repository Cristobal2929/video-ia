import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil, math, random, gc
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V177", layout="centered")
components.html("<script>if('wakeLock' in navigator){navigator.wakeLock.request('screen');}</script>", height=0)

st.markdown("""
<style>
    .stApp { background: #000000; color: #FFFFFF; }
    .pro-title { font-size: 42px; font-weight: 900; background: -webkit-linear-gradient(45deg, #00FFD1, #FFD700); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; text-transform: uppercase; margin-bottom: 20px;}
    .msg { color: #00FFD1; font-family: 'Courier New', monospace; font-size: 14px; margin-bottom: 8px; border-left: 3px solid #FFD700; padding-left: 12px; }
    .stButton>button { width: 100%; background: linear-gradient(45deg, #00FFD1, #0088ff); color: white; border: none; font-weight: 900; height: 55px; border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V177 🦅💎</div>', unsafe_allow_html=True)

@st.cache_resource
def get_font():
    p = "font.ttf"
    if not os.path.exists(p):
        r = requests.get("https://github.com/matomo-org/travis-scripts/raw/master/fonts/Arial.ttf")
        with open(p, "wb") as f: f.write(r.content)
    return "font.ttf"

PEXELS_API = "Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ"

MUSICA_FINAL = [
    "https://cdn.pixabay.com/download/audio/2021/05/20/audio_f31f9b3b8e.mp3?filename=dance-playful-night-51078.mp3",
    "https://upload.wikimedia.org/wikipedia/commons/4/4c/A_Hero_Steps_Forward.mp3"
]

def purificar_guion(t):
    if any(x in t.lower() for x in ["<div", "doctype", "html"]):
        return "La disciplina es el puente entre tus metas y tus logros."
    return re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ.,! ]', '', t).strip()

f_abs = get_font()
tema = st.text_input("🧠 Tema del vídeo:", placeholder="Ej: Éxito y Riqueza...")
color_sub = st.selectbox("🎨 Color Subtítulos:", ["yellow", "white", "#00FFD1"])

if st.button("🚀 CREAR VÍDEO SEGURO V177"):
    if not tema: st.error("Escribe un tema")
    else:
        if os.path.exists("taller"): shutil.rmtree("taller")
        os.makedirs("taller", exist_ok=True)
        
        log = st.container()
        with log:
            st.markdown('<div class="msg">📝 Redactando guion limpio...</div>', unsafe_allow_html=True)
            try:
                g_raw = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote(tema + '. Solo español. Max 70 palabras.')}").text
                guion = purificar_guion(g_raw)
            except: guion = "El éxito es para los que no se rinden."

            audio_voz = "taller/voz.mp3"
            subprocess.run(f'edge-tts --voice es-MX-JorgeNeural --text "{guion}" --write-media "{audio_voz}"', shell=True)
            
            st.markdown('<div class="msg">🎵 Mezclando banda sonora...</div>', unsafe_allow_html=True)
            musica = "taller/bg.mp3"
            r_m = requests.get(random.choice(MUSICA_FINAL))
            with open(musica, "wb") as f: f.write(r_m.content)
            
            dur = float(subprocess.check_output(f'ffprobe -i "{audio_voz}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
            mezcla = "taller/mezcla.mp3"
            subprocess.run(f'ffmpeg -y -i "{audio_voz}" -i "{musica}" -filter_complex "[1:a]volume=0.10,afade=t=out:st={dur-2}:d=2[m];[0:a][m]amix=inputs=2:duration=first" "{mezcla}" > /dev/null 2>&1', shell=True)

            palabras = guion.upper().split()
            n_clips = min(math.ceil(dur / 3.0), 12)
            t_clip = dur / n_clips
            clips = []

            for i in range(n_clips):
                frag = " ".join(palabras[i*len(palabras)//n_clips : (i+1)*len(palabras)//n_clips])
                kw = f"{frag} luxury lifestyle"
                st.markdown(f'<div class="msg">🎥 Escena {i+1}: Buscando vídeos de "{frag[:20]}..."</div>', unsafe_allow_html=True)
                
                vid = f"taller/v_{i}.mp4"
                try:
                    h = {"Authorization": PEXELS_API}
                    res = requests.get(f"https://api.pexels.com/videos/search?query={urllib.parse.quote(kw)}&orientation=portrait&per_page=1", headers=h).json()
                    v_url = res['videos'][0]['video_files'][0]['link']
                    
                    sub_split = [palabras[j:j+2] for j in range(i*len(palabras)//n_clips, (i+1)*len(palabras)//n_clips, 2)]
                    t_p = t_clip / max(len(sub_split), 1)
                    draws = []
                    for k, p in enumerate(sub_split):
                        t_txt = " ".join(p)
                        if len(t_txt) > 10: # Doble línea si es largo
                            draws.append(f"drawtext=text='{p[0]}':fontfile='{f_abs}':fontcolor={color_sub}:fontsize=70:borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2-45:enable='between(t,{k*t_p},{(k+1)*t_p})'")
                            draws.append(f"drawtext=text='{p[1]}':fontfile='{f_abs}':fontcolor={color_sub}:fontsize=70:borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2+45:enable='between(t,{k*t_p},{(k+1)*t_p})'")
                        else:
                            draws.append(f"drawtext=text='{t_txt}':fontfile='{f_abs}':fontcolor={color_sub}:fontsize=70:borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{k*t_p},{(k+1)*t_p})'")
                    
                    vf = f"scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1,{','.join(draws)}"
                    subprocess.run(f'ffmpeg -y -i "{v_url}" -t {t_clip} -vf "{vf}" -c:v libx264 -preset ultrafast -an "{vid}" > /dev/null 2>&1', shell=True)
                    clips.append(os.path.abspath(vid))
                except: pass

            with open("taller/lista.txt", "w") as f:
                for c in clips: f.write(f"file '{c}'\n")
            
            final = "taller/master.mp4"
            subprocess.run(f'ffmpeg -y -f concat -safe 0 -i taller/lista.txt -i "{mezcla}" -map 0:v -map 1:a -c:v libx264 -preset ultrafast -t {dur} "{final}" > /dev/null 2>&1', shell=True)
            
            if os.path.exists(final):
                st.video(final)
