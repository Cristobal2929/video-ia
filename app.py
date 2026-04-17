import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil, math, random, gc
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V160", layout="centered")
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

st.markdown('<div class="pro-title">FÉNIX STUDIO V160 🎭🎧</div>', unsafe_allow_html=True)

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

def limpiar_texto_tts(t):
    t = re.sub(r'(tool_calls|recalc|words|assistant|reasoning|thought|count|slightly|above|remove|piece|adjust|instruction|script|here|is|english)', '', t, flags=re.I)
    t = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ.,! ]', '', t)
    return re.sub(r'\s+', ' ', t).strip()

def extraer_kw(texto, i):
    t = texto.lower()
    if any(x in t for x in ["dinero", "banco", "millonario", "negocio"]): return "luxury money"
    if any(x in t for x in ["gym", "fuerte", "entrenar"]): return "fitness motivation"
    if any(x in t for x in ["coche", "velocidad", "ferrari"]): return "supercar cinematic"
    fallbacks = ["success luxury", "modern office", "private jet", "rolex watch", "city skyscraper"]
    return fallbacks[i % len(fallbacks)]

def preparar():
    if os.path.exists("taller"): shutil.rmtree("taller")
    os.makedirs("taller", exist_ok=True)
    subprocess.run("pkill ffmpeg", shell=True)

f_abs = get_font()
tema = st.text_input("🧠 Tema del vídeo:", placeholder="Ej: Negocios online")
color_sub = st.selectbox("🎨 Color Subtítulos:", ["yellow", "white", "#00FFD1"])

if st.button("🚀 CREAR VÍDEO COMPLETO (CON MÚSICA)"):
    if not tema: st.error("⚠️ Escribe un tema")
    else:
        preparar()
        log = st.container()
        
        with log:
            st.markdown('<div class="msg">📝 Redactando guion de alto impacto...</div>', unsafe_allow_html=True)
            p_g = f"Escribe una frase de éxito sobre {tema} para TikTok. Solo español. Maximo 75 palabras."
            try:
                g_raw = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote(p_g)}", timeout=20).text
                guion = limpiar_texto_tts(g_raw)
            except: guion = "La disciplina es el puente entre tus metas y tus logros."
            if len(guion) < 5: guion = "Enfócate en el proceso y los resultados llegarán solos."
            
            st.markdown('<div class="msg">🎙️ Generando voz de Jorge...</div>', unsafe_allow_html=True)
            audio_voz = "taller/voz.mp3"
            subprocess.run(f'edge-tts --voice es-MX-JorgeNeural --text "{guion}" --write-media "{audio_voz}"', shell=True)
            
            # EL HACK DE LA MÚSICA (V160)
            st.markdown('<div class="msg">🎵 Descargando banda sonora en modo incógnito...</div>', unsafe_allow_html=True)
            musica_file = "taller/bg.mp3"
            headers_music = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            urls_musica = [
                "https://www.chosic.com/wp-content/uploads/2021/07/Inspirational-Cinematic-Background.mp3",
                "https://www.chosic.com/wp-content/uploads/2021/05/The-Epic-Hero.mp3"
            ]
            
            for u_m in urls_musica:
                try:
                    r_m = requests.get(u_m, headers=headers_music, timeout=10)
                    # Comprobamos que de verdad sea un audio pesando más de 100KB
                    if r_m.status_code == 200 and len(r_m.content) > 100000:
                        with open(musica_file, "wb") as f: f.write(r_m.content)
                        break
                except: pass

            try: dur = float(subprocess.check_output(f'ffprobe -i "{audio_voz}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
            except: dur = 15.0

            st.markdown('<div class="msg">🎧 Mezclando audio y música...</div>', unsafe_allow_html=True)
            audio_mezcla = "taller/mezcla.mp3"
            fade_st = max(0, dur - 2)
            
            if os.path.exists(musica_file):
                subprocess.run(f'ffmpeg -y -i "{audio_voz}" -i "{musica_file}" -filter_complex "[1:a]volume=0.15,afade=t=out:st={fade_st}:d=2[m];[0:a][m]amix=inputs=2:duration=first" -c:a libmp3lame -threads 1 "{audio_mezcla}"', shell=True)

            if not os.path.exists(audio_mezcla) or os.path.getsize(audio_mezcla) == 0:
                if os.path.exists(audio_voz): shutil.copy(audio_voz, audio_mezcla)
                else: subprocess.run(f'ffmpeg -y -f lavfi -i anullsrc=r=44100:cl=stereo -t {dur} -c:a libmp3lame "{audio_mezcla}"', shell=True)

            palabras_puras = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ ]', '', guion).upper().split()
            n_clips = min(math.ceil(dur / 3.5), 10) 
            t_clip = dur / n_clips
            clips = []
            chunk_size = max(len(palabras_puras) // n_clips, 1)

            for i in range(n_clips):
                pal_clip = palabras_puras[i*chunk_size:(i+chunk_size)] if i < n_clips-1 else palabras_puras[i*chunk_size:]
                txt_c = " ".join(pal_clip)
                kw = extraer_kw(txt_c, i)
                st.markdown(f'<div class="msg">🎥 Escena {i+1}/{n_clips}: Procesando "{kw.upper()}"...</div>', unsafe_allow_html=True)
                
                raw_vid, vid = f"taller/r_{i}.mp4", f"taller/v_{i}.mp4"
                exito = False
                try:
                    h = {"Authorization": PEXELS_API}
                    u_p = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(kw)}&orientation=portrait&per_page=1"
                    v_url = requests.get(u_p, headers=h, timeout=10).json()['videos'][0]['video_files'][0]['link']
                    with open(raw_vid, 'wb') as f: f.write(requests.get(v_url).content)
                    subprocess.run(f'ffmpeg -y -stream_loop -1 -i "{raw_vid}" -t {t_clip} -vf "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1,format=yuv420p" -c:v libx264 -preset ultrafast -r 24 -an -threads 1 "{vid}"', shell=True)
                    if os.path.exists(vid): exito = True
                except: pass

                if not exito:
                    subprocess.run(f'ffmpeg -y -f lavfi -i color=c=#1A1A1A:s=720x1280:d={t_clip}:r=24 -c:v libx264 -preset ultrafast -an -threads 1 "{vid}"', shell=True)

                clips.append(os.path.abspath(vid).replace('\\', '/'))
                if os.path.exists(raw_vid): os.remove(raw_vid)

            st.markdown('<div class="msg">🎬 Ensamblando bloques...</div>', unsafe_allow_html=True)
            with open("taller/lista.txt", "w") as f:
                for c in clips: f.write(f"file '{c}'\n")
            
            mudo = "taller/mudo.mp4"
            subprocess.run(f'ffmpeg -y -f concat -safe 0 -i taller/lista.txt -c copy "{mudo}"', shell=True)
            
            chunks_sub = [palabras_puras[j:j+2] for j in range(0, len(palabras_puras), 2)]
            t_ch = dur / max(len(chunks_sub), 1)
            subs = [f"drawtext=text='{' '.join(p)}':fontfile='{f_abs}':fontcolor={color_sub}:fontsize=70:borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{j*t_ch},{(j+1)*t_ch})'" for j, p in enumerate(chunks_sub)]
            with open("taller/s.txt", "w") as f: f.write(",\n".join(subs))
            
            final = "taller/master.mp4"
            subprocess.run(f'ffmpeg -y -i "{mudo}" -i "{audio_mezcla}" -filter_script:v taller/s.txt -map 0:v:0 -map 1:a:0 -c:v libx264 -preset ultrafast -crf 28 -c:a copy -threads 1 -t {dur} "{final}"', shell=True)
            
            if os.path.exists(final):
                st.markdown('<div class="info-card">🏆 VÍDEO 100% COMPLETADO Y CON MÚSICA</div>', unsafe_allow_html=True)
                with open(final, "rb") as f: st.video(f.read())
                st.balloons()
            else:
                st.error("❌ Fallo en masterizado final.")
