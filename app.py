import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil, math, random, gc
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V155", layout="centered")
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

st.markdown('<div class="pro-title">FÉNIX STUDIO V155 🦅⚡</div>', unsafe_allow_html=True)

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

def limpiar_texto(t):
    t = re.sub(r'tool_calls|recalc|words|assistant|reasoning|thought|count|slightly|above|remove|piece|adjust|instruction', '', t, flags=re.I)
    return re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ.,! ]', '', t).strip()

def extraer_kw(texto, i):
    t = texto.lower()
    if any(x in t for x in ["dinero", "banco", "millonario"]): return "luxury money"
    if any(x in t for x in ["gym", "fuerte", "entrenar"]): return "fitness motivation"
    if any(x in t for x in ["coche", "velocidad", "ferrari"]): return "supercar cinematic"
    fallbacks = ["success luxury", "modern mansion", "private jet", "rolex watch", "office skyscraper"]
    return fallbacks[i % len(fallbacks)]

def preparar():
    if os.path.exists("taller"): shutil.rmtree("taller")
    os.makedirs("taller", exist_ok=True)
    subprocess.run("pkill ffmpeg", shell=True)

tema = st.text_input("🧠 Tema del vídeo:", placeholder="Ej: Hábitos de titan")
color_sub = st.selectbox("🎨 Color Subtítulos:", ["yellow", "white", "#00FFD1"])

if st.button("🚀 CREAR VÍDEO (CARGA DISTRIBUIDA - ANTI CONGELAMIENTO)"):
    if not tema: st.error("⚠️ Escribe un tema")
    else:
        preparar()
        log = st.container()
        
        with log:
            st.markdown('<div class="msg">📝 IA redactando guion puro...</div>', unsafe_allow_html=True)
            prompt_g = f"Escribe UNICAMENTE el texto que debe decir el locutor sobre {tema}. No añadas notas. Solo español fluido. Maximo 85 palabras."
            
            try:
                guion_raw = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote(prompt_g)}", timeout=20).text
                guion = limpiar_texto(guion_raw)
            except:
                guion = "El éxito se construye con paciencia y disciplina. Empieza hoy mismo tu camino a la cima."
            if not guion: guion = "La constancia vence al talento."
            
            st.markdown('<div class="msg">🎙️ Grabando voz y descargando música...</div>', unsafe_allow_html=True)
            audio_voz = "taller/voz.mp3"
            subprocess.run(f'edge-tts --voice es-MX-JorgeNeural --rate=+0% --text "{guion}" --write-media "{audio_voz}"', shell=True)
            
            musica_file = "taller/bg.mp3"
            r_m = requests.get("https://www.chosic.com/wp-content/uploads/2021/07/Inspirational-Cinematic-Background.mp3")
            with open(musica_file, "wb") as f: f.write(r_m.content)

            try: dur = float(subprocess.check_output(f'ffprobe -i "{audio_voz}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
            except: dur = 20.0

            st.markdown('<div class="msg">🎧 Mezclando pista maestra (Ahorrando memoria)...</div>', unsafe_allow_html=True)
            audio = "taller/mezcla.mp3"
            fade_st = max(0, dur - 2)
            subprocess.run(f'ffmpeg -y -i "{audio_voz}" -i "{musica_file}" -filter_complex "[1:a]volume=0.15,afade=t=out:st={fade_st}:d=2[m];[0:a][m]amix=inputs=2:duration=first" -c:a libmp3lame -threads 1 "{audio}"', shell=True)

            # MAGIA V155: PROCESAMIENTO DISTRIBUIDO CLIP A CLIP
            n_clips = min(math.ceil(dur / 3.2), 15) 
            t_clip = dur / n_clips
            clips = []
            palabras_guion = guion.split()
            chunk_size = max(len(palabras_guion) // n_clips, 1)
            f_s = f"fontfile='{f_abs}':" if os.path.exists(f_abs) else ""
            ultima_vid_exitosa = None

            for i in range(n_clips):
                # Extraemos solo las palabras de este clip
                pal_clip = palabras_guion[i*chunk_size : (i+1)*chunk_size] if i < n_clips - 1 else palabras_guion[i*chunk_size:]
                txt_chunk = " ".join(pal_clip)
                kw_en = extraer_kw(txt_chunk, i)
                st.markdown(f'<div class="msg">🎥 Escena {i+1}/{n_clips}: Tatuando subtítulos en "{kw_en.upper()}"...</div>', unsafe_allow_html=True)
                
                # Creamos los subtítulos relativos SOLO a este clip (0 a 3 segundos)
                chunks_c = [pal_clip[j:j+2] for j in range(0, len(pal_clip), 2)]
                t_pair = t_clip / max(len(chunks_c), 1)
                text_filters = []
                for j, p_par in enumerate(chunks_c):
                    ts, te = j * t_pair, (j + 1) * t_pair
                    txt_draw = ' '.join(p_par).upper().replace("'", "").replace(":", "").replace(",", "").replace(";", "")
                    text_filters.append(f"drawtext=text='{txt_draw}':fontcolor={color_sub}:fontsize=70:{f_s}borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{ts},{te})'")
                
                vf_txt = ",".join(text_filters) if text_filters else ""
                vf_base = "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1,fps=24,format=yuv420p"
                vf_full = f"{vf_base},{vf_txt}" if vf_txt else vf_base
                
                with open(f"taller/f_{i}.txt", "w") as f: f.write(vf_full)

                raw_vid, vid = f"taller/raw_{i}.mp4", f"taller/v_{i}.ts" # Guardamos como TS para que encajen perfectos
                exito_vid = False
                try:
                    headers = {"Authorization": PEXELS_API}
                    url_p = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(kw_en)}&orientation=portrait&per_page=1"
                    r_p = requests.get(url_p, headers=headers, timeout=12).json()
                    v_url = r_p['videos'][0]['video_files'][0]['link']
                    with open(raw_vid, 'wb') as f: f.write(requests.get(v_url).content)
                    
                    # Convertimos, limpiamos audio y tatuamos a la vez (Bajo consumo)
                    subprocess.run(f'ffmpeg -y -stream_loop -1 -i "{raw_vid}" -t {t_clip} -filter_script:v taller/f_{i}.txt -c:v libx264 -preset ultrafast -profile:v baseline -level 3.0 -video_track_timescale 90000 -an -threads 1 "{vid}"', shell=True)
                    exito_vid = True
                except: pass
                
                if not exito_vid:
                    vf_fall = "fps=24,format=yuv420p" + (f",{vf_txt}" if vf_txt else "")
                    with open(f"taller/ff_{i}.txt", "w") as f: f.write(vf_fall)
                    subprocess.run(f'ffmpeg -y -f lavfi -i color=c=#1A1A1A:s=720x1280:d={t_clip}:r=24 -filter_script:v taller/ff_{i}.txt -c:v libx264 -preset ultrafast -profile:v baseline -level 3.0 -video_track_timescale 90000 -an -threads 1 "{vid}"', shell=True)

                clips.append(os.path.abspath(vid).replace('\\', '/'))
                if os.path.exists(raw_vid): os.remove(raw_vid)
                gc.collect() # Liberamos RAM en cada vuelta

            # EL PASO FINAL AHORA GASTA 0% DE MEMORIA
            st.markdown('<div class="msg">🎬 Soldando las piezas terminadas (Cero impacto)...</div>', unsafe_allow_html=True)
            with open("taller/lista.txt", "w") as f:
                for c in clips: f.write(f"file '{c}'\n")
            
            mudo = "taller/mudo.ts"
            subprocess.run(f'ffmpeg -y -f concat -safe 0 -i taller/lista.txt -c copy "{mudo}"', shell=True)
            
            final = "taller/master.mp4"
            # Mezcla instantánea sin re-renderizar
            subprocess.run(f'ffmpeg -y -i "{mudo}" -i "{audio}" -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest -threads 1 "{final}"', shell=True)
            
            if os.path.exists(final):
                st.markdown('<div class="info-card">🏆 VÍDEO MAESTRO COMPLETADO (EL SERVIDOR SOBREVIVIÓ)</div>', unsafe_allow_html=True)
                with open(final, "rb") as f: st.video(f.read())
                st.balloons()
            else:
                st.error("❌ Fénix Caído. Contacta con el equipo.")
