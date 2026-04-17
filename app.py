import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil, math, random, gc
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V169-B", layout="centered")
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

st.markdown('<div class="pro-title">FÉNIX STUDIO V169-B 🦅🎚️</div>', unsafe_allow_html=True)

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

# NUEVO: BIBLIOTECAS DE MÚSICA SEPARADAS POR TEMA
MUSICA_NEGOCIO = [
    "https://cdn.pixabay.com/download/audio/2021/05/20/audio_f31f9b3b8e.mp3?filename=dance-playful-night-51078.mp3",
    "https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0a13f69d2.mp3?filename=inspiring-cinematic-ambient-11619.mp3",
    "https://upload.wikimedia.org/wikipedia/commons/4/4c/A_Hero_Steps_Forward.mp3"
]

MUSICA_TERROR = [
    "https://freepd.com/music/Horror%20Ambience.mp3",
    "https://freepd.com/music/Deep%20Space.mp3",
    "https://upload.wikimedia.org/wikipedia/commons/2/23/Closer_to_the_Void.mp3"
]

# NUEVO: EL SELECTOR INTELIGENTE (Sustituye al antiguo descargar_musica)
def descargar_musica(ruta, tema_usuario):
    t = tema_usuario.lower()
    # Si el usuario escribe algo de miedo, coge la lista de terror. Si no, la de negocios.
    lista_elegida = MUSICA_TERROR if any(x in t for x in ["miedo", "terror", "horror", "oscuro", "paranormal", "hospital"]) else MUSICA_NEGOCIO
    
    random.shuffle(lista_elegida)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    for url in lista_elegida:
        try:
            r = requests.get(url, headers=headers, timeout=12)
            if r.status_code == 200 and len(r.content) > 150000:
                with open(ruta, "wb") as f: f.write(r.content)
                return True
        except: pass
    return False

def limpiar_texto(t):
    t = re.sub(r'(tool_calls|recalc|words|assistant|reasoning|thought|count|slightly|above|remove|piece|adjust|instruction)', '', t, flags=re.I)
    t = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ.,! ]', '', t)
    return re.sub(r'\s+', ' ', t).strip()

def extraer_kw(texto, i):
    t = texto.lower()
    if any(x in t for x in ["dinero", "negocio", "millonario"]): return "luxury business"
    if any(x in t for x in ["gym", "fuerte", "entrenar"]): return "fitness motivation"
    fallbacks = ["luxury lifestyle", "modern mansion", "private jet", "rolex", "city sky"]
    return fallbacks[i % len(fallbacks)]

def preparar():
    if os.path.exists("taller"): shutil.rmtree("taller")
    os.makedirs("taller", exist_ok=True)
    subprocess.run("pkill ffmpeg", shell=True)

f_abs = get_font()
tema = st.text_input("🧠 Tema del vídeo:", placeholder="Ej: Hábitos de éxito")
color_sub = st.selectbox("🎨 Color Subtítulos:", ["yellow", "white", "#00FFD1"])

if st.button("🚀 CREAR VÍDEO (VOLUMEN AJUSTADO)"):
    if not tema: st.error("⚠️ Escribe un tema")
    else:
        preparar()
        log = st.container()
        with log:
            st.markdown('<div class="msg">📝 Redactando guion...</div>', unsafe_allow_html=True)
            p_g = f"Escribe una frase motivacional de éxito sobre {tema} para TikTok. Solo español. Maximo 75 palabras."
            try:
                g_raw = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote(p_g)}", timeout=20).text
                guion = limpiar_texto(g_raw)
            except: guion = "La disciplina es el puente entre tus metas y tus logros."
            
            st.markdown('<div class="msg">🎙️ Grabando voz de Jorge...</div>', unsafe_allow_html=True)
            audio_voz = "taller/voz.mp3"
            subprocess.run(f'edge-tts --voice es-MX-JorgeNeural --text "{guion}" --write-media "{audio_voz}"', shell=True)
            
            st.markdown('<div class="msg">🎵 Descargando música según el tema...</div>', unsafe_allow_html=True)
            musica_file = "taller/bg.mp3"
            # NUEVO: Pasamos el tema a la función para que decida
            descargar_musica(musica_file, tema)

            try: dur = float(subprocess.check_output(f'ffprobe -i "{audio_voz}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
            except: dur = 15.0

            st.markdown('<div class="msg">🎧 Mezclando audio (Música al 10%)...</div>', unsafe_allow_html=True)
            audio_mezcla = "taller/mezcla.mp3"
            fade_st = max(0, dur - 2)
            if os.path.exists(musica_file):
                # AJUSTE: volume=0.10 para que sea más floja la música
                subprocess.run(f'ffmpeg -y -i "{audio_voz}" -i "{musica_file}" -filter_complex "[1:a]volume=0.10,afade=t=out:st={fade_st}:d=2[m];[0:a][m]amix=inputs=2:duration=first" -c:a libmp3lame -threads 1 "{audio_mezcla}" > /dev/null 2>&1', shell=True)
            
            if not os.path.exists(audio_mezcla) or os.path.getsize(audio_mezcla) < 1000:
                shutil.copy(audio_voz, audio_mezcla)

            palabras_puras = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ ]', '', guion).upper().split()
            n_clips = min(math.ceil(dur / 3.0), 12) 
            t_clip = dur / n_clips
            clips = []
            chunk_size = max(len(palabras_puras) // n_clips, 1)

            for i in range(n_clips):
                pal_clip = palabras_puras[i*chunk_size:(i+1)*chunk_size] if i < n_clips-1 else palabras_puras[i*chunk_size:]
                txt_c = " ".join(pal_clip)
                kw = extraer_kw(txt_c, i)
                st.markdown(f'<div class="msg">🎥 Escena {i+1}/{n_clips}: Tatuando "{kw.upper()}"...</div>', unsafe_allow_html=True)
                
                raw_vid, vid = f"taller/r_{i}.mp4", f"taller/v_{i}.mp4"
                
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
                    u_p = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(kw)}&orientation=portrait&per_page=1"
                    v_url = requests.get(u_p, headers=h, timeout=10).json()['videos'][0]['video_files'][0]['link']
                    with open(raw_vid, 'wb') as f: f.write(requests.get(v_url).content)
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
                st.markdown('<div class="info-card">🏆 VÍDEO CON MÚSICA INTELIGENTE COMPLETADO</div>', unsafe_allow_html=True)
                with open(final, "rb") as f: st.video(f.read())
                st.balloons()
