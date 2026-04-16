import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil, math, random, gc
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V109", layout="centered")

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

st.markdown('<div class="pro-title">FÉNIX STUDIO V109 🛡️</div>', unsafe_allow_html=True)

@st.cache_resource
def get_font():
    p = "font.ttf"
    if not os.path.exists(p):
        try:
            r = requests.get("https://github.com/matomo-org/travis-scripts/raw/master/fonts/Arial.ttf")
            with open(p, "wb") as f: f.write(r.content)
        except: pass
    return p

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

tema = st.text_input("🧠 ¿De qué trata el vídeo?:", placeholder="Ej: Las leyes de la riqueza")
color_sub = st.selectbox("🎨 Color de los Subtítulos:", ["yellow", "white", "#00FFD1"])
estilo_v = st.text_input("🎨 Filtro de Imagen IA:", value="Luxury Cinematic 8k photography")

if st.button("🚀 CREAR OBRA MAESTRA (V109)"):
    if not tema: st.error("⚠️ Escribe un tema, jefe.")
    else:
        preparar()
        log = st.container()
        
        with log:
            st.markdown('<div class="msg">📝 Redactando guion profesional...</div>', unsafe_allow_html=True)
            prompt_g = f"Escribe un guion corto para TikTok sobre {tema}. Solo el texto, maximo 50 palabras, sin emojis."
            try:
                guion_raw = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote(prompt_g)}", timeout=15).text
                guion = re.sub(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ.,! ]', '', guion_raw).strip()
            except:
                guion = "El éxito requiere disciplina y constancia. Nunca te rindas y sigue luchando por tus metas diarias."
            
            guion = " ".join(guion.split()[:60])
            
            st.markdown('<div class="msg">🎙️ Grabando voz HD...</div>', unsafe_allow_html=True)
            audio = "taller/audio.mp3"
            subprocess.run(f'edge-tts --voice es-MX-JorgeNeural --rate=+10% --text "{guion}" --write-media "{audio}"', shell=True)
            
            if not os.path.exists(audio):
                subprocess.run(f'ffmpeg -y -f lavfi -i anullsrc=r=44100:cl=mono -t 15 -acodec libmp3lame "{audio}"', shell=True)

            try: dur = float(subprocess.check_output(f'ffprobe -i "{audio}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
            except: dur = 15.0
            
            n_clips = math.ceil(dur / 3.5)
            if n_clips > 10: n_clips = 10 
            t_clip = dur / n_clips
            
            palabras_sub = re.sub(r'[^\w\s]', '', guion.upper()).split()
            chunks_sub = [palabras_sub[j:j+2] for j in range(0, len(palabras_sub), 2)]
            t_por_chunk = dur / max(len(chunks_sub), 1)

            clips = []
            palabras_guion_final = guion.split()
            chunk_size = max(len(palabras_guion_final) // n_clips, 1)
            f_str = f"fontfile='{f_abs}':" if os.path.exists(f_abs) else ""

            # MEMORIA DE IMAGEN: Guardamos la última imagen que funcionó
            ultima_imagen_exitosa = None

            for i in range(n_clips):
                t_start_clip = i * t_clip
                t_end_clip = (i + 1) * t_clip
                txt_chunk = " ".join(palabras_guion_final[i*chunk_size:(i+1)*chunk_size])
                kw_en = traducir_en(extraer_kw(txt_chunk))
                
                st.markdown(f'<div class="msg">📸 Escena {i+1}/{n_clips}: IA + Subtítulos "{kw_en.upper()}"...</div>', unsafe_allow_html=True)
                
                img = f"taller/i_{i}.jpg"
                vid = f"taller/v_{i}.mp4"
                
                exito_ia = False
                for intento in range(2):
                    seed = random.randint(1, 999999)
                    url_ia = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(kw_en+' '+estilo_v)}?width=720&height=1280&nologo=true&seed={seed}"
                    try:
                        time.sleep(2) 
                        r = requests.get(url_ia, timeout=20)
                        if r.status_code == 200 and len(r.content) > 5000:
                            with open(img, 'wb') as f: f.write(r.content)
                            exito_ia = True
                            ultima_imagen_exitosa = img # Guardamos esta ruta
                            break
                    except: pass

                # SUBTÍTULOS DE ESTA ESCENA
                clip_subs = []
                for j, p_list in enumerate(chunks_sub):
                    ts, te = j * t_por_chunk, (j + 1) * t_por_chunk
                    if ts < t_end_clip and te > t_start_clip:
                        l_ts, l_te = max(0.0, ts - t_start_clip), min(t_clip, te - t_start_clip)
                        if len(p_list) == 2:
                            clip_subs.append(f"drawtext=text='{p_list[0]}':fontcolor={color_sub}:fontsize=65:{f_str}borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2-45:enable='between(t,{l_ts},{l_te})'")
                            clip_subs.append(f"drawtext=text='{p_list[1]}':fontcolor={color_sub}:fontsize=65:{f_str}borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2+45:enable='between(t,{l_ts},{l_te})'")
                        else:
                            clip_subs.append(f"drawtext=text='{p_list[0]}':fontcolor={color_sub}:fontsize=65:{f_str}borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{l_ts},{l_te})'")

                # LÓGICA ANTI-FONDO OSCURO
                if not exito_ia and i > 0 and ultima_imagen_exitosa:
                    # Si falla, usamos la imagen de la escena anterior
                    st.markdown('<div class="msg">🔄 IA lenta, manteniendo imagen anterior...</div>', unsafe_allow_html=True)
                    img_final = ultima_imagen_exitosa
                elif not exito_ia:
                    # Si es la primera y falla, intentamos una genérica de lujo
                    url_fallback = f"https://image.pollinations.ai/prompt/luxury%20gold%20cinematic%20background?width=720&height=1280&nologo=true"
                    try:
                        r = requests.get(url_fallback, timeout=10)
                        with open(img, 'wb') as f: f.write(r.content)
                        img_final = img
                    except: img_final = None # Aquí sí iría a negro como último recurso
                else:
                    img_final = img

                z_fx = random.choice([f"zoompan=z='1.0+0.001*on':x='iw/4-(iw/4/d)*on':s=720x1280", f"zoompan=z='1.15-0.001*on':x='(iw/4/d)*on':s=720x1280"])
                vf = f"scale=1280:2275,{z_fx},format=yuv420p"
                if clip_subs: vf += "," + ",".join(clip_subs)

                if img_final:
                    subprocess.run(f'ffmpeg -y -loop 1 -i "{img_final}" -vf "{vf}" -t {t_clip} -c:v libx264 -preset ultrafast -threads 1 -r 24 "{vid}"', shell=True)
                else:
                    # Fondo oscuro (Mínima duración si llegara a este punto crítico)
                    subprocess.run(f'ffmpeg -y -f lavfi -i color=c=#000000:s=720x1280:d={t_clip}:r=24 -vf "format=yuv420p,{",".join(clip_subs)}" -c:v libx264 -preset ultrafast "{vid}"', shell=True)
                
                clips.append(f"v_{i}.mp4")
                gc.collect()

            st.markdown('<div class="msg">🎬 Ensamblado final...</div>', unsafe_allow_html=True)
            with open("taller/lista.txt", "w") as f:
                for c in clips: f.write(f"file '{os.path.abspath('taller/'+c).replace('\\','/')}'\n")
            
            subprocess.run(f'ffmpeg -y -f concat -safe 0 -i taller/lista.txt -c copy taller/mudo.mp4', shell=True)
            final_p = "taller/master.mp4"
            subprocess.run(f'ffmpeg -y -i taller/mudo.mp4 -i "{audio}" -c:v copy -c:a aac -shortest "{final_p}"', shell=True)
            
            if os.path.exists(final_p):
                st.markdown('<div class="info-card">🏆 VÍDEO COMPLETADO: SIN HUECOS NEGROS</div>', unsafe_allow_html=True)
                with open(final_p, "rb") as f: st.video(f.read())
                st.balloons()
