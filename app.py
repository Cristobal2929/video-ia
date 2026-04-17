import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil, math, random, gc
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V154", layout="centered")
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

st.markdown('<div class="pro-title">FÉNIX STUDIO V154 ⚙️💎</div>', unsafe_allow_html=True)

@st.cache_resource
def get_font():
    p = "font.ttf"
    if not os.path.exists(p):
        try:
            r = requests.get("https://github.com/matomo-org/travis-scripts/raw/master/fonts/Arial.ttf")
            with open(p, "wb") as f: f.write(r.content)
        except: pass
    return os.path.abspath(p).replace('\\', '/')

f_abs = get_font()
PEXELS_API = "Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ"

def traducir_en(palabra):
    try:
        url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(palabra)}&langpair=es|en"
        res = requests.get(url, timeout=5).json()['responseData']['translatedText']
        # Limpieza extrema para que el traductor no meta puntos ni comas raras
        return re.sub(r'[^a-zA-Z0-9 ]', '', res)
    except: return palabra

def extraer_kw(texto):
    palabras = re.sub(r'[^\w\s]', '', texto).split()
    utiles = [p for p in palabras if len(p) > 4]
    kw = max(utiles, key=len) if utiles else "luxury"
    return re.sub(r'[^a-zA-Z0-9 ]', '', kw)

def preparar():
    if os.path.exists("taller"): shutil.rmtree("taller")
    os.makedirs("taller", exist_ok=True)
    subprocess.run("pkill ffmpeg", shell=True)

tema = st.text_input("🧠 Tema del vídeo:", placeholder="Ej: Hábitos de éxito")
color_sub = st.selectbox("🎨 Color de los Subtítulos:", ["yellow", "white", "#00FFD1"])

if st.button("🚀 CREAR VÍDEO (ENGRANAJE PERFECTO)"):
    if not tema: st.error("⚠️ Escribe un tema")
    else:
        preparar()
        log = st.container()
        
        with log:
            st.markdown('<div class="msg">📝 IA redactando guion puro...</div>', unsafe_allow_html=True)
            prompt_g = f"Escribe UNICAMENTE el texto que debe decir el locutor sobre {tema}. No añadas notas, ni instrucciones. Solo el mensaje en español fluido. Maximo 85 palabras."
            
            try:
                guion_raw = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote(prompt_g)}", timeout=20).text
                guion = re.sub(r'tool_calls|recalc|words|assistant|reasoning|thought|count|slightly|above|remove|piece|adjust', '', guion_raw, flags=re.I)
                guion = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ.,! ]', '', guion).strip()
            except:
                guion = "El éxito se construye con paciencia y disciplina. Empieza hoy mismo tu camino a la cima."
            
            if not guion: guion = "La disciplina es el puente entre tus metas y tus logros."
            
            st.markdown('<div class="msg">🎙️ Grabando voz y descargando música...</div>', unsafe_allow_html=True)
            audio_voz = "taller/voz.mp3"
            subprocess.run(f'edge-tts --voice es-MX-JorgeNeural --rate=+0% --text "{guion}" --write-media "{audio_voz}"', shell=True)
            
            musica_file = "taller/bg.mp3"
            r_m = requests.get("https://www.chosic.com/wp-content/uploads/2021/07/Inspirational-Cinematic-Background.mp3")
            with open(musica_file, "wb") as f: f.write(r_m.content)

            try: dur = float(subprocess.check_output(f'ffprobe -i "{audio_voz}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
            except: dur = 20.0

            st.markdown('<div class="msg">🎧 Mezclando pista de audio maestra...</div>', unsafe_allow_html=True)
            audio = "taller/audio.mp3"
            fade_st = max(0, dur - 2)
            subprocess.run(f'ffmpeg -y -i "{audio_voz}" -i "{musica_file}" -filter_complex "[1:a]volume=0.15,afade=t=out:st={fade_st}:d=2[m];[0:a][m]amix=inputs=2:duration=first" -c:a libmp3lame -threads 1 "{audio}"', shell=True)

            n_clips = min(math.ceil(dur / 3.2), 15) 
            t_clip = dur / n_clips
            clips = []
            palabras_guion = guion.split()
            chunk_size = max(len(palabras_guion) // n_clips, 1)
            ultima_vid_exitosa = None

            for i in range(n_clips):
                txt_chunk = " ".join(palabras_guion[i*chunk_size:(i+1)*chunk_size])
                kw_en = traducir_en(extraer_kw(txt_chunk))
                st.markdown(f'<div class="msg">🎥 Escena {i+1}/{n_clips}: Limpiando vídeo de "{kw_en.upper()}"...</div>', unsafe_allow_html=True)
                
                raw_vid, vid = f"taller/raw_{i}.mp4", f"taller/v_{i}.mp4"
                exito_vid = False
                try:
                    headers = {"Authorization": PEXELS_API}
                    url_p = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(kw_en+' luxury 8k')}&orientation=portrait&per_page=3"
                    r_p = requests.get(url_p, headers=headers, timeout=12).json()
                    if r_p.get('videos'):
                        v_url = r_p['videos'][0]['video_files'][0]['link']
                        with open(raw_vid, 'wb') as f: f.write(requests.get(v_url).content)
                        exito_vid = True
                except: pass

                if exito_vid:
                    vf = "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1,format=yuv420p"
                    # LA CLAVE: -an (quita audio fantasma) y -r 24 (iguala frames)
                    subprocess.run(f'ffmpeg -y -stream_loop -1 -i "{raw_vid}" -t {t_clip} -vf "{vf}" -c:v libx264 -preset ultrafast -r 24 -an -threads 1 "{vid}"', shell=True)
                
                if not os.path.exists(vid):
                    if ultima_vid_exitosa: 
                        subprocess.run(f'cp "{ultima_vid_exitosa}" "{vid}"', shell=True)
                    else: 
                        subprocess.run(f'ffmpeg -y -f lavfi -i color=c=#1A1A1A:s=720x1280:d={t_clip}:r=24 -c:v libx264 -preset ultrafast -pix_fmt yuv420p -an -threads 1 "{vid}"', shell=True)

                clips.append(os.path.abspath(vid).replace('\\', '/'))
                ultima_vid_exitosa = vid
                if os.path.exists(raw_vid): os.remove(raw_vid)
                gc.collect()

            st.markdown('<div class="msg">🎬 Ensamblando bloques idénticos...</div>', unsafe_allow_html=True)
            with open("taller/lista.txt", "w") as f:
                for c in clips: f.write(f"file '{c}'\n")
            
            mudo = "taller/mudo.mp4"
            subprocess.run(f'ffmpeg -y -f concat -safe 0 -i taller/lista.txt -c copy "{mudo}"', shell=True)
            
            pal_sub = re.sub(r'[^\w\s]', '', guion.upper()).split()
            chunks = [pal_sub[j:j+2] for j in range(0, len(pal_sub), 2)]
            t_ch = dur / max(len(chunks), 1)
            f_s = f"fontfile='{f_abs}':" if os.path.exists(f_abs) else ""
            subs = []
            for j, p in enumerate(chunks):
                ts, te = j * t_ch, (j + 1) * t_ch
                if len(p) == 2 and (len(p[0])+len(p[1]) > 10):
                    subs.append(f"drawtext=text='{p[0]}':fontcolor={color_sub}:fontsize=70:{f_s}borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2-45:enable='between(t,{ts},{te})'")
                    subs.append(f"drawtext=text='{p[1]}':fontcolor={color_sub}:fontsize=70:{f_s}borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2+45:enable='between(t,{ts},{te})'")
                else:
                    subs.append(f"drawtext=text='{' '.join(p)}':fontcolor={color_sub}:fontsize=70:{f_s}borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{ts},{te})'")
            
            with open("taller/s.txt", "w") as f: f.write(",\n".join(subs))
            final = "taller/master.mp4"
            
            # COMANDO FINAL ASEGURADO (Copiar audio para evitar conflictos)
            subprocess.run(f'ffmpeg -y -i "{mudo}" -i "{audio}" -filter_complex_script taller/s.txt -map 0:v -map 1:a -c:v libx264 -preset ultrafast -crf 28 -c:a copy -threads 1 -t {dur} "{final}"', shell=True)
            
            if os.path.exists(final):
                st.markdown('<div class="info-card">🏆 VÍDEO COMPLETO (¡ENGRANAJE PERFECTO!)</div>', unsafe_allow_html=True)
                with open(final, "rb") as f: st.video(f.read())
                st.balloons()
            else:
                st.error("❌ Error de renderizado final.")
