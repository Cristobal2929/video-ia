import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil, math, random, gc
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V127", layout="centered")

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

st.markdown('<div class="pro-title">FÉNIX STUDIO V127 💎</div>', unsafe_allow_html=True)

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
        return requests.get(url, timeout=5).json()['responseData']['translatedText']
    except: return palabra

def extraer_kw(texto):
    palabras = re.sub(r'[^\w\s]', '', texto).split()
    utiles = [p for p in palabras if len(p) > 4]
    return max(utiles, key=len) if utiles else "success"

def preparar():
    if os.path.exists("taller"): shutil.rmtree("taller")
    os.makedirs("taller", exist_ok=True)
    subprocess.run("pkill ffmpeg", shell=True)

tema = st.text_input("🧠 Tema del vídeo:", placeholder="Ej: Secretos de la riqueza")
color_sub = st.selectbox("🎨 Color de los Subtítulos:", ["yellow", "white", "#00FFD1"])

if st.button("🚀 CREAR OBRA MAESTRA (LUJO 8K)"):
    if not tema: st.error("⚠️ Escribe un tema, jefe.")
    else:
        preparar()
        log = st.container()
        
        with log:
            # --- 1. GUION EXPERTO (V124) ---
            st.markdown('<div class="msg">📝 IA redactando guion estructurado...</div>', unsafe_allow_html=True)
            
            prompt_g = f"Actua como experto en TikTok. Escribe un guion COMPLETO sobre {tema}. Estructura estricta: 1) Gancho agresivo, 2) Contenido directo y rapido, 3) Cierre final contundente. El texto DEBE tener un final claro y no quedar a medias. Maximo 65 palabras totales. Sin emojis. Solo el texto."
            
            try:
                guion_raw = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote(prompt_g)}", timeout=15).text
                guion = re.sub(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ.,! ]', '', guion_raw).strip()
            except:
                guion = "Te están mintiendo. El éxito no es suerte, es estrategia. Primero, educa tu mente. Segundo, ahorra e invierte. Tercero, trabaja en silencio. Si aplicas esto hoy, tu vida cambiará para siempre."
            
            lista_palabras = guion.split()
            if len(lista_palabras) > 75: guion = " ".join(lista_palabras[:75]) + "."
            
            # --- 2. VOZ HD ---
            st.markdown('<div class="msg">🎙️ Grabando voz HD...</div>', unsafe_allow_html=True)
            audio = "taller/audio.mp3"
            subprocess.run(f'edge-tts --voice es-MX-JorgeNeural --rate=+10% --text "{guion}" --write-media "{audio}"', shell=True)
            
            dur = 15.0
            try: dur = float(subprocess.check_output(f'ffprobe -i "{audio}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
            except: pass
            
            n_clips = math.ceil(dur / 3.5)
            t_clip = dur / n_clips
            clips = []
            palabras_guion_final = guion.split()
            chunk_size = max(len(palabras_guion_final) // n_clips, 1)

            ultima_vid_exitosa = None

            # --- 3. CAZADOR DE VÍDEOS LUJO 8K (V58 MEJORADO) ---
            for i in range(n_clips):
                txt_chunk = " ".join(palabras_guion_final[i*chunk_size:(i+1)*chunk_size])
                kw_en = traducir_en(extraer_kw(txt_chunk))
                
                # OPTIMIZACIÓN 8K: Añadimos keywords de ultra calidad
                prompt_visual_8k = f"{kw_en} 8k ultra hd highly detailed cinematic lighting unreal engine style"
                
                st.markdown(f'<div class="msg">🎥 Escena {i+1}/{n_clips}: Buscando metraje 8K de "{kw_en.upper()}"...</div>', unsafe_allow_html=True)
                
                raw_vid = f"taller/raw_{i}.mp4"
                vid = f"taller/v_{i}.mp4"
                exito_vid = False

                try:
                    headers = {"Authorization": PEXELS_API}
                    # Buscamos vídeos portrait con el prompt 8K
                    url_p = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(prompt_visual_8k)}&orientation=portrait&per_page=5"
                    r_p = requests.get(url_p, headers=headers, timeout=10).json()
                    
                    if r_p.get('videos'):
                        video_url = None
                        video_elegido = random.choice(r_p['videos'])
                        archivos = video_elegido.get('video_files', [])
                        
                        # FILTRO ESTRICTO DE CALIDAD: Buscamos HD o superior obligatoriamente
                        for arch in archivos:
                            if arch['quality'] == 'hd' or arch['height'] >= 1280:
                                video_url = arch['link']
                                break
                        if not video_url and archivos:
                            video_url = archivos[0]['link']
                            
                        if video_url:
                            vid_data = requests.get(video_url, timeout=20).content
                            with open(raw_vid, 'wb') as f: f.write(vid_data)
                            exito_vid = True
                except: pass

                if exito_vid and os.path.exists(raw_vid):
                    # Recorte perfecto V58
                    vf_crop = "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1,format=yuv420p"
                    subprocess.run(f'ffmpeg -y -stream_loop -1 -i "{raw_vid}" -t {t_clip} -vf "{vf_crop}" -c:v libx264 -preset ultrafast -r 24 "{vid}"', shell=True)
                
                if not os.path.exists(vid) or os.path.getsize(vid) < 1000:
                    if ultima_vid_exitosa:
                        subprocess.run(f'cp "{ultima_vid_exitosa}" "{vid}"', shell=True)
                    else:
                        subprocess.run(f'ffmpeg -y -f lavfi -i color=c=#1A1A1A:s=720x1280:d={t_clip}:r=24 -c:v libx264 -preset ultrafast -pix_fmt yuv420p "{vid}"', shell=True)

                if os.path.exists(vid):
                    clips.append(os.path.abspath(vid).replace('\\', '/'))
                    ultima_vid_exitosa = vid

                if os.path.exists(raw_vid): os.remove(raw_vid)
                gc.collect()

            # --- 4. ENSAMBLAJE V58 ---
            st.markdown('<div class="msg">🎬 Ensamblando los recortes...</div>', unsafe_allow_html=True)
            with open("taller/lista.txt", "w") as f:
                for c in clips: f.write(f"file '{c}'\n")
            
            mudo = "taller/mudo.mp4"
            subprocess.run(f'ffmpeg -y -f concat -safe 0 -i taller/lista.txt -c copy "{mudo}"', shell=True)
            
            # --- 5. SUBTÍTULOS V58 ---
            st.markdown('<div class="msg">✨ Tatuando subtítulos V58...</div>', unsafe_allow_html=True)
            palabras_sub = re.sub(r'[^\w\s]', '', guion.upper()).split()
            chunks_sub = [palabras_sub[j:j+2] for j in range(0, len(palabras_sub), 2)]
            t_por_chunk = dur / max(len(chunks_sub), 1)
            
            f_str = f"fontfile='{f_abs}':" if os.path.exists(f_abs) else ""
            subs_cmd = []

            for j, p_list in enumerate(chunks_sub):
                ts, te = j * t_por_chunk, (j + 1) * t_por_chunk
                if len(p_list) == 2 and (len(p_list[0]) + len(p_list[1]) > 10):
                    subs_cmd.append(f"drawtext=text='{p_list[0]}':fontcolor={color_sub}:fontsize=70:{f_str}borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2-45:enable='between(t,{ts},{te})'")
                    subs_cmd.append(f"drawtext=text='{p_list[1]}':fontcolor={color_sub}:fontsize=70:{f_str}borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2+45:enable='between(t,{ts},{te})'")
                else:
                    frase = " ".join(p_list)
                    subs_cmd.append(f"drawtext=text='{frase}':fontcolor={color_sub}:fontsize=70:{f_str}borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{ts},{te})'")
            
            with open("taller/subs_filter.txt", "w") as f: f.write(",\n".join(subs_cmd))
            
            final = "taller/master.mp4"
            subprocess.run(f'ffmpeg -y -i "{mudo}" -i "{audio}" -filter_complex_script taller/subs_filter.txt -c:v libx264 -preset ultrafast -crf 28 -threads 1 -t {dur} "{final}"', shell=True)
            
            if os.path.exists(final):
                st.markdown('<div class="info-card">🏆 VÍDEO COMPLETADO: CALIDAD LUJO 8K + V58</div>', unsafe_allow_html=True)
                with open(final, "rb") as f: st.video(f.read())
                st.balloons()
            else:
                st.error("❌ Ocurrió un error. Vuelve a intentarlo.")
