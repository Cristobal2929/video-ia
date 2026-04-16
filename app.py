import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil, math, random, gc
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V114", layout="centered")

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

st.markdown('<div class="pro-title">FÉNIX STUDIO V114 📸</div>', unsafe_allow_html=True)

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

# API de Pexels (Gratuita y estable para fotos)
PEXELS_API = "Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ"

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

tema = st.text_input("🧠 Tema del vídeo:", placeholder="Ej: Hábitos de éxito")
color_sub = st.selectbox("🎨 Color de los Subtítulos:", ["yellow", "white", "#00FFD1"])
# Filtro para asegurar la belleza de la foto
filtro_belleza = "luxury cinematic portrait lighting 8k"

if st.button("🚀 CREAR OBRA MAESTRA (FOTOS PREMIUM)"):
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
                guion = "El éxito es la suma de pequeños esfuerzos repetidos día tras día. No te rindas nunca."
            
            guion = " ".join(guion.split()[:60])
            
            st.markdown('<div class="msg">🎙️ Grabando voz HD...</div>', unsafe_allow_html=True)
            audio = "taller/audio.mp3"
            subprocess.run(f'edge-tts --voice es-MX-JorgeNeural --rate=+10% --text "{guion}" --write-media "{audio}"', shell=True)
            
            if not os.path.exists(audio) or os.path.getsize(audio) < 100:
                subprocess.run(f'ffmpeg -y -f lavfi -i anullsrc=r=44100:cl=mono -t 15 -acodec libmp3lame "{audio}"', shell=True)

            try: dur = float(subprocess.check_output(f'ffprobe -i "{audio}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
            except: dur = 15.0
            if dur > 30.0: dur = 30.0

            n_clips = math.ceil(dur / 3.5)
            if n_clips > 10: n_clips = 10 
            t_clip = dur / n_clips
            
            clips = []
            palabras_guion_final = guion.split()
            chunk_size = max(len(palabras_guion_final) // n_clips, 1)

            # --- FASE 1: DESCARGA DE FOTOS HERMOSAS (PEXELS) ---
            ultima_vid_exitosa = None

            for i in range(n_clips):
                txt_chunk = " ".join(palabras_guion_final[i*chunk_size:(i+1)*chunk_size])
                kw_es = extraer_kw(txt_chunk)
                kw_en = traducir_en(kw_es)
                
                st.markdown(f'<div class="msg">📸 Escena {i+1}/{n_clips}: Buscando foto premium "{kw_en.upper()}"...</div>', unsafe_allow_html=True)
                
                img = f"taller/i_{i}.jpg"
                vid = f"taller/v_{i}.mp4"
                
                exito_foto = False
                
                # BUSCADOR DE FOTOS PREMIUM DE PEXELS
                busqueda_completa = f"{kw_en} {filtro_belleza}"
                url_pexels = f"https://api.pexels.com/v1/search?query={urllib.parse.quote(busqueda_completa)}&orientation=portrait&per_page=10"
                
                try:
                    headers = {"Authorization": PEXELS_API}
                    r = requests.get(url_pexels, headers=headers, timeout=10).json()
                    fotos = r.get('photos', [])
                    if fotos:
                        # Elegimos una foto aleatoria de las 10 primeras para dar variedad
                        foto_elegida = random.choice(fotos)
                        # Descargamos la versión grande
                        img_url = foto_elegida['src']['large2x']
                        img_data = requests.get(img_url, timeout=15).content
                        with open(img, 'wb') as f: f.write(img_data)
                        exito_foto = True
                except: pass

                # Convertimos imagen a vídeo con zoom lateral (V58 Style)
                if exito_foto:
                    z_fx = random.choice(["zoompan=z='1.0+0.001*on':x='iw/4-(iw/4/d)*on'", "zoompan=z='1.15-0.001*on':x='(iw/4/d)*on'"])
                    vf = f"scale=1280:2275,{z_fx}:d={int(t_clip*24)}:s=720x1280,format=yuv420p"
                    subprocess.run(f'ffmpeg -y -loop 1 -i "{img}" -vf "{vf}" -t {t_clip} -c:v libx264 -preset ultrafast -r 24 "{vid}"', shell=True)
                
                # PARACAÍDAS ANTI-FALLOS (Clona el anterior o usa fondo de emergencia)
                if not os.path.exists(vid) or os.path.getsize(vid) < 1000:
                    if ultima_vid_exitosa:
                        subprocess.run(f'cp "{ultima_vid_exitosa}" "{vid}"', shell=True)
                    else:
                        subprocess.run(f'ffmpeg -y -f lavfi -i color=c=#1A1A1A:s=720x1280:d={t_clip}:r=24 -c:v libx264 -preset ultrafast -pix_fmt yuv420p "{vid}"', shell=True)

                if os.path.exists(vid):
                    clips.append(os.path.abspath(vid).replace('\\', '/'))
                    ultima_vid_exitosa = vid

                if os.path.exists(img): os.remove(img)
                gc.collect()

            # --- FASE 2: ENSAMBLAJE V58 MUDO ---
            st.markdown('<div class="msg">🎬 Ensamblando metraje base...</div>', unsafe_allow_html=True)
            with open("taller/lista.txt", "w") as f:
                for c in clips: f.write(f"file '{c}'\n")
            
            mudo = "taller/mudo.mp4"
            subprocess.run(f'ffmpeg -y -f concat -safe 0 -i taller/lista.txt -c copy "{mudo}"', shell=True)
            
            # --- FASE 3: SUBTÍTULOS DOBLE CAPA V58 ---
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
            
            # COMANDO FINAL SEGURO (threads 1 para no saturar RAM)
            subprocess.run(f'ffmpeg -y -i "{mudo}" -i "{audio}" -filter_complex_script taller/subs_filter.txt -c:v libx264 -preset ultrafast -crf 28 -threads 1 -t {dur} "{final}"', shell=True)
            
            if os.path.exists(final):
                st.markdown('<div class="info-card">🏆 VÍDEO COMPLETADO: FOTOS PREMIUM + MOTOR V58</div>', unsafe_allow_html=True)
                with open(final, "rb") as f: st.video(f.read())
                st.balloons()
            else:
                st.error("❌ Ocurrió un error en el ensamblado final.")
