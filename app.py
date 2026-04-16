import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil, math, random, gc
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V106", layout="centered")

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

st.markdown('<div class="pro-title">FÉNIX STUDIO V106 🧩</div>', unsafe_allow_html=True)

@st.cache_resource
def get_font():
    p = "Arial_Pro.ttf"
    if not os.path.exists(p):
        try:
            r = requests.get("https://github.com/matomo-org/travis-scripts/raw/master/fonts/Arial.ttf")
            with open(p, "wb") as f: f.write(r.content)
        except: pass
    return os.path.abspath(p)

f_abs = get_font()

def traducir_en(palabra):
    try:
        url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(palabra)}&langpair=es|en"
        return requests.get(url, timeout=5).json()['responseData']['translatedText']
    except: return palabra

def extraer_kw(texto):
    palabras = re.sub(r'[^\w\s]', '', texto).split()
    utiles = [p for p in palabras if len(p) > 4]
    return max(utiles, key=len) if utiles else "cinematic"

def preparar():
    if os.path.exists("taller"): shutil.rmtree("taller")
    os.makedirs("taller", exist_ok=True)
    subprocess.run("pkill ffmpeg", shell=True)

tema = st.text_input("🧠 ¿De qué trata el vídeo?:", placeholder="Ej: Las leyes del éxito millonario")
color_sub = st.selectbox("🎨 Color de los Subtítulos:", ["yellow", "white", "#00FFD1"])
estilo_v = st.text_input("🎨 Filtro de Imagen IA:", value="Luxury Cinematic 8k photography")

if st.button("🚀 CREAR OBRA MAESTRA (MOTOR V106)"):
    if not tema: st.error("⚠️ Escribe un tema, jefe.")
    else:
        preparar()
        log = st.container()
        
        with log:
            st.markdown('<div class="msg">📝 Redactando guion (blindado)...</div>', unsafe_allow_html=True)
            prompt_g = f"Escribe un guion corto para TikTok sobre {tema}. Solo el texto, maximo 50 palabras, sin emojis."
            try:
                guion_raw = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote(prompt_g)}", timeout=15).text
                guion = re.sub(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ.,! ]', '', guion_raw).strip()
            except:
                guion = "El éxito requiere disciplina y constancia. Nunca te rindas y sigue luchando por tus metas diarias."
            
            lista_palabras_guion = guion.split()
            if len(lista_palabras_guion) > 60:
                guion = " ".join(lista_palabras_guion[:60])
            
            st.markdown('<div class="msg">🎙️ Grabando voz de alta fidelidad...</div>', unsafe_allow_html=True)
            audio = "taller/audio.mp3"
            subprocess.run(f'edge-tts --voice es-MX-JorgeNeural --rate=+10% --text "{guion}" --write-media "{audio}"', shell=True)
            
            dur = 15.0
            try: dur = float(subprocess.check_output(f'ffprobe -i "{audio}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
            except: pass
            if dur > 30.0: dur = 30.0

            n_clips = math.ceil(dur / 3.5)
            if n_clips > 10: n_clips = 10 
            t_clip = dur / n_clips
            
            # PRECALCULAR TIEMPOS DE SUBTÍTULOS PARA FRAGMENTAR
            palabras_sub = re.sub(r'[^\w\s]', '', guion.upper()).split()
            chunks_sub = [palabras_sub[j:j+2] for j in range(0, len(palabras_sub), 2)]
            t_por_chunk = dur / max(len(chunks_sub), 1)

            clips = []
            palabras_guion_final = guion.split()
            chunk_size = max(len(palabras_guion_final) // n_clips, 1)

            for i in range(n_clips):
                t_start_clip = i * t_clip
                t_end_clip = (i + 1) * t_clip
                
                txt_chunk = " ".join(palabras_guion_final[i*chunk_size:(i+1)*chunk_size])
                kw_es = extraer_kw(txt_chunk)
                kw_en = traducir_en(kw_es)
                
                st.markdown(f'<div class="msg">📸 Escena {i+1}/{n_clips}: IA + Tatuando subtítulos "{kw_en.upper()}"...</div>', unsafe_allow_html=True)
                
                img = f"taller/i_{i}.jpg"
                vid = f"taller/v_{i}.mp4"
                
                exito_ia = False
                for intento in range(2):
                    seed = random.randint(1, 999999)
                    url_ia = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(kw_en+' '+estilo_v)}?width=720&height=1280&nologo=true&seed={seed}"
                    try:
                        time.sleep(3) 
                        r = requests.get(url_ia, timeout=30)
                        if r.status_code == 200 and len(r.content) > 5000:
                            with open(img, 'wb') as f: f.write(r.content)
                            exito_ia = True
                            break
                    except: pass

                if exito_ia:
                    # EXTRAER SOLO LOS SUBTÍTULOS DE ESTA ESCENA
                    clip_subs = []
                    for j, p_list in enumerate(chunks_sub):
                        ts = j * t_por_chunk
                        te = ts + t_por_chunk
                        # Si el subtítulo cae dentro de esta escena
                        if ts < t_end_clip and te > t_start_clip:
                            l_ts = max(0.0, ts - t_start_clip)
                            l_te = min(t_clip, te - t_start_clip)
                            
                            if len(p_list) == 2 and (len(p_list[0]) + len(p_list[1]) > 10):
                                clip_subs.append(f"drawtext=text='{p_list[0]}':fontcolor={color_sub}:fontsize=65:fontfile='{f_abs}':borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2-45:enable='between(t,{l_ts},{l_te})'")
                                clip_subs.append(f"drawtext=text='{p_list[1]}':fontcolor={color_sub}:fontsize=65:fontfile='{f_abs}':borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2+45:enable='between(t,{l_ts},{l_te})'")
                            else:
                                frase = " ".join(p_list)
                                clip_subs.append(f"drawtext=text='{frase}':fontcolor={color_sub}:fontsize=65:fontfile='{f_abs}':borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{l_ts},{l_te})'")

                    z_fx = random.choice([
                        f"zoompan=z='1.0+0.001*on':x='iw/4-(iw/4/d)*on':s=720x1280",
                        f"zoompan=z='1.15-0.001*on':x='(iw/4/d)*on':s=720x1280"
                    ])
                    
                    # CONSTRUIR EL FILTRO FRAGMENTADO
                    vf = f"scale=1280:2275,{z_fx},format=yuv420p"
                    if clip_subs:
                        vf += "," + ",".join(clip_subs)
                        
                    subprocess.run(f'ffmpeg -y -loop 1 -i "{img}" -vf "{vf}" -t {t_clip} -c:v libx264 -preset ultrafast -threads 1 -r 24 "{vid}"', shell=True)
                    if os.path.exists(vid): clips.append(f"v_{i}.mp4")
                
                if os.path.exists(img): os.remove(img)
                gc.collect() # Libera RAM en cada vuelta

            st.markdown('<div class="msg">🎬 Ensamblado instantáneo (Cero RAM)...</div>', unsafe_allow_html=True)
            with open("taller/lista.txt", "w") as f:
                for c in clips: f.write(f"file '{c}'\n")
            
            mudo = "taller/mudo.mp4"
            subprocess.run(f'ffmpeg -y -f concat -safe 0 -i taller/lista.txt -c copy "{mudo}"', shell=True)
            
            final = "taller/master.mp4"
            # EL TRUCO MAGISTRAL: Como los subtítulos ya están pegados en las imágenes, 
            # este paso solo tiene que copiar y pegar el audio. ¡Tarda 1 segundo y no gasta RAM!
            subprocess.run(f'ffmpeg -y -i "{mudo}" -i "{audio}" -c:v copy -c:a aac -shortest "{final}"', shell=True)
            
            if os.path.exists(final):
                st.markdown('<div class="info-card">🏆 VÍDEO COMPLETADO: RENDIMIENTO PERFECTO</div>', unsafe_allow_html=True)
                with open(final, "rb") as f: st.video(f.read())
                st.balloons()
            else:
                st.error("❌ Error inesperado. Revisa tu conexión.")
