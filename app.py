import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil, math, random, gc
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V165", layout="centered")
components.html("<script>if('wakeLock' in navigator){navigator.wakeLock.request('screen');}</script>", height=0)

st.markdown("""
<style>
    .stApp { background: #000000; color: #FFFFFF; }
    .pro-title { font-size: 42px; font-weight: 900; background: -webkit-linear-gradient(45deg, #00FFD1, #FFD700); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; text-transform: uppercase; margin-bottom: 20px;}
    .msg { color: #00FFD1; font-family: 'Courier New', monospace; font-size: 14px; margin-bottom: 8px; border-left: 3px solid #FFD700; padding-left: 12px; }
    .info-card { padding: 15px; border-radius: 12px; background: #0f172a; border: 1px solid #00FFD1; text-align: center; color: #00FFD1; margin-top: 25px; font-weight: bold;}
    .stButton>button { width: 100%; background: linear-gradient(45deg, #00FFD1, #0088ff); color: white; border: none; font-weight: 900; height: 55px; border-radius: 12px; font-size: 18px;}
    .error-box { background: #4a0000; color: #ffcccc; padding: 10px; font-family: monospace; font-size: 10px; border-radius: 5px; margin-top: 10px; white-space: pre-wrap; word-wrap: break-word;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V165 🦅🧠</div>', unsafe_allow_html=True)

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

def limpiar_texto(t):
    t = re.sub(r'(tool_calls|recalc|words|assistant|reasoning|thought|count|slightly|above|remove|piece|adjust|instruction|script)', '', t, flags=re.I)
    t = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ.,! ]', '', t)
    return re.sub(r'\s+', ' ', t).strip()

def extraer_kw(texto, i):
    t = texto.lower()
    if any(x in t for x in ["dinero", "millonario", "negocio"]): return "luxury business"
    if any(x in t for x in ["gym", "fuerte", "disciplina"]): return "fitness motivation"
    fallbacks = ["luxury lifestyle", "modern mansion", "private jet", "rolex", "city night"]
    return fallbacks[i % len(fallbacks)]

def preparar():
    if os.path.exists("taller"): shutil.rmtree("taller")
    os.makedirs("taller", exist_ok=True)
    subprocess.run("pkill ffmpeg", shell=True)

f_abs = get_font()
tema = st.text_input("🧠 Tema del vídeo:", placeholder="Ej: Negocios y Mentalidad")
color_sub = st.selectbox("🎨 Color Subtítulos:", ["yellow", "white", "#00FFD1"])
link_musica = st.text_input("🔗 Enlace MP3 (Opcional):", placeholder="Pega un enlace de FreePD...")

if st.button("🚀 CREAR VÍDEO (MOTOR DISTRIBUIDO)"):
    if not tema: st.error("⚠️ Escribe un tema")
    else:
        preparar()
        log = st.container()
        with log:
            st.markdown('<div class="msg">📝 IA redactando guion...</div>', unsafe_allow_html=True)
            p_g = f"Escribe una frase motivacional de éxito sobre {tema} para TikTok. Solo español. Maximo 80 palabras."
            try:
                g_raw = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote(p_g)}", timeout=20).text
                guion = limpiar_texto(g_raw)
            except: guion = "El éxito es la suma de pequeños esfuerzos diarios."
            
            st.markdown('<div class="msg">🎙️ Grabando voz de Jorge...</div>', unsafe_allow_html=True)
            audio_voz = "taller/voz.mp3"
            subprocess.run(f'edge-tts --voice es-MX-JorgeNeural --text "{guion}" --write-media "{audio_voz}"', shell=True)
            
            st.markdown('<div class="msg">🎵 Procesando banda sonora...</div>', unsafe_allow_html=True)
            musica_file = "taller/bg.mp3"
            exito_musica = False
            
            if link_musica:
                try:
                    r_m = requests.get(link_musica, timeout=15)
                    if r_m.status_code == 200:
                        with open(musica_file, "wb") as f: f.write(r_m.content)
                        exito_musica = True
                        st.markdown('<div class="msg">✅ Música personalizada lista.</div>', unsafe_allow_html=True)
                except: pass

            if not exito_musica:
                try:
                    r_m = requests.get("https://upload.wikimedia.org/wikipedia/commons/4/4c/A_Hero_Steps_Forward.mp3", timeout=15)
                    if r_m.status_code == 200:
                        with open(musica_file, "wb") as f: f.write(r_m.content)
                except: pass

            try: dur = float(subprocess.check_output(f'ffprobe -i "{audio_voz}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
            except: dur = 20.0

            st.markdown('<div class="msg">🎧 Consolidando audio maestro...</div>', unsafe_allow_html=True)
            audio_mezcla = "taller/mezcla.mp3"
            fade_st = max(0, dur - 2)
            if os.path.exists(musica_file):
                subprocess.run(f'ffmpeg -y -i "{audio_voz}" -i "{musica_file}" -filter_complex "[1:a]volume=0.15,afade=t=out:st={fade_st}:d=2[m];[0:a][m]amix=inputs=2:duration=first" -c:a libmp3lame -threads 1 "{audio_mezcla}" > taller/log_audio.txt 2>&1', shell=True)
            else:
                shutil.copy(audio_voz, audio_mezcla)

            # --- MAGIA V165: DISTRIBUCIÓN DE CARGA ---
            palabras_puras = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ ]', '', guion).upper().split()
            n_clips = min(math.ceil(dur / 3.4), 12) 
            t_clip = dur / n_clips
            clips = []
            chunk_size = max(len(palabras_puras) // n_clips, 1)
            f_s = f"fontfile='{f_abs}':" if os.path.exists(f_abs) else ""

            for i in range(n_clips):
                pal_clip = palabras_puras[i*chunk_size:(i+1)*chunk_size] if i < n_clips-1 else palabras_puras[i*chunk_size:]
                txt_c = " ".join(pal_clip)
                kw = extraer_kw(txt_c, i)
                st.markdown(f'<div class="msg">🎥 Escena {i+1}/{n_clips}: Tatuando "{kw.upper()}"...</div>', unsafe_allow_html=True)
                
                raw_vid, vid = f"taller/r_{i}.mp4", f"taller/v_{i}.mp4"
                
                # Preparamos el archivo de subtítulos SOLO para este pequeño clip
                chunks_sub = [pal_clip[j:j+2] for j in range(0, len(pal_clip), 2)]
                t_pair = t_clip / max(len(chunks_sub), 1)
                text_filters = []
                for j, p in enumerate(chunks_sub):
                    ts, te = j * t_pair, (j + 1) * t_pair
                    if len(p) == 2 and (len(p[0]) + len(p[1]) > 10):
                        t0 = p[0].replace("'", "").replace(":", "")
                        t1 = p[1].replace("'", "").replace(":", "")
                        text_filters.append(f"drawtext=text='{t0}':{f_s}fontcolor={color_sub}:fontsize=70:borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2-45:enable='between(t,{ts},{te})'")
                        text_filters.append(f"drawtext=text='{t1}':{f_s}fontcolor={color_sub}:fontsize=70:borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2+45:enable='between(t,{ts},{te})'")
                    else:
                        tj = ' '.join(p).replace("'", "").replace(":", "")
                        text_filters.append(f"drawtext=text='{tj}':{f_s}fontcolor={color_sub}:fontsize=70:borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{ts},{te})'")

                vf_txt = ",".join(text_filters) if text_filters else ""
                vf_base = "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1,format=yuv420p"
                vf_full = f"{vf_base},{vf_txt}" if vf_txt else vf_base
                
                with open(f"taller/f_{i}.txt", "w") as f: f.write(vf_full)

                try:
                    h = {"Authorization": PEXELS_API}
                    u_p = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(kw)}&orientation=portrait&per_page=1"
                    v_url = requests.get(u_p, headers=h, timeout=10).json()['videos'][0]['video_files'][0]['link']
                    with open(raw_vid, 'wb') as f: f.write(requests.get(v_url).content)
                    # Quema el texto en el clip al vuelo
                    subprocess.run(f'ffmpeg -y -stream_loop -1 -i "{raw_vid}" -t {t_clip} -filter_script:v taller/f_{i}.txt -c:v libx264 -preset ultrafast -r 24 -an -threads 1 "{vid}" > taller/log_{i}.txt 2>&1', shell=True)
                except:
                    vf_fall = "format=yuv420p" + (f",{vf_txt}" if vf_txt else "")
                    with open(f"taller/ff_{i}.txt", "w") as f: f.write(vf_fall)
                    subprocess.run(f'ffmpeg -y -f lavfi -i color=c=#1A1A1A:s=720x1280:d={t_clip}:r=24 -filter_script:v taller/ff_{i}.txt -c:v libx264 -preset ultrafast -an -threads 1 "{vid}" > taller/log_{i}.txt 2>&1', shell=True)

                clips.append(os.path.abspath(vid).replace('\\', '/'))
                if os.path.exists(raw_vid): os.remove(raw_vid)
                gc.collect()

            st.markdown('<div class="msg">🎬 Ensamblando al estilo Fénix (A prueba de RAM)...</div>', unsafe_allow_html=True)
            with open("taller/lista.txt", "w") as f:
                for c in clips: f.write(f"file '{c}'\n")
            
            final = "taller/master.mp4"
            # Ensamblado ultraligero: Los clips ya tienen el texto, solo hay que pegarlos con el audio
            cmd_f = f'ffmpeg -y -f concat -safe 0 -i taller/lista.txt -i "{audio_mezcla}" -map 0:v -map 1:a -c:v libx264 -preset ultrafast -crf 28 -c:a aac -threads 1 -t {dur} "{final}" > taller/log_final.txt 2>&1'
            subprocess.run(cmd_f, shell=True)
            
            if os.path.exists(final):
                st.markdown('<div class="info-card">🏆 VÍDEO CON DOBLE LÍNEA Y MÚSICA COMPLETADO</div>', unsafe_allow_html=True)
                with open(final, "rb") as f: st.video(f.read())
                st.balloons()
            else:
                st.error("❌ Fallo en masterizado. Revisa el log.")
                try: 
                    with open("taller/log_final.txt", "r") as f: st.markdown(f'<div class="error-box">{f.read()[-1000:]}</div>', unsafe_allow_html=True)
                except: pass
