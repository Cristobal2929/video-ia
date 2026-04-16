import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil, math, random, gc
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V117", layout="centered")

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

st.markdown('<div class="pro-title">FÉNIX STUDIO V117 🏦</div>', unsafe_allow_html=True)

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
    return max(utiles, key=len) if utiles else "cinematic"

def preparar():
    if os.path.exists("taller"): shutil.rmtree("taller")
    os.makedirs("taller", exist_ok=True)
    subprocess.run("pkill ffmpeg", shell=True)

tema = st.text_input("🧠 Tema del vídeo:", placeholder="Ej: Mentalidad de tiburón")
color_sub = st.selectbox("🎨 Color de los Subtítulos:", ["yellow", "white", "#00FFD1"])

if st.button("🚀 CREAR VÍDEO (BANCO DE IA)"):
    if not tema: st.error("⚠️ Escribe un tema, jefe.")
    else:
        preparar()
        log = st.container()
        
        with log:
            st.markdown('<div class="msg">📝 IA redactando guion...</div>', unsafe_allow_html=True)
            prompt_g = f"Escribe un guion motivador para TikTok sobre {tema}. Solo el texto, maximo 50 palabras, sin emojis."
            try:
                guion_raw = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote(prompt_g)}", timeout=10).text
                guion = re.sub(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ.,! ]', '', guion_raw).strip()
            except:
                guion = "El éxito es constancia. Levántate, lucha por tus sueños y no mires atrás. Tú puedes."
                
            guion = " ".join(guion.split()[:60])
            
            st.markdown('<div class="msg">🎙️ Grabando voz HD...</div>', unsafe_allow_html=True)
            audio = "taller/audio.mp3"
            subprocess.run(f'edge-tts --voice es-MX-JorgeNeural --rate=+10% --text "{guion}" --write-media "{audio}"', shell=True)
            
            if not os.path.exists(audio) or os.path.getsize(audio) < 100:
                subprocess.run(f'ffmpeg -y -f lavfi -i anullsrc=r=44100:cl=mono -t 15 -acodec libmp3lame "{audio}"', shell=True)

            try: dur = float(subprocess.check_output(f'ffprobe -i "{audio}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
            except: dur = 15.0
            
            n_clips = math.ceil(dur / 3.5)
            if n_clips > 10: n_clips = 10 
            t_clip = dur / n_clips
            
            clips = []
            palabras_guion = guion.split()
            chunk_size = max(len(palabras_guion) // n_clips, 1)
            ultima_vid_exitosa = None

            for i in range(n_clips):
                txt_chunk = " ".join(palabras_guion[i*chunk_size:(i+1)*chunk_size])
                kw_en = traducir_en(extraer_kw(txt_chunk))
                st.markdown(f'<div class="msg">📸 Escena {i+1}/{n_clips}: Explorando Banco IA para "{kw_en.upper()}"...</div>', unsafe_allow_html=True)
                
                img = f"taller/i_{i}.jpg"
                vid = f"taller/v_{i}.mp4"
                exito_imagen = False

                # --- MOTOR 1: BANCO DE IMÁGENES IA (LEXICA) ---
                try:
                    lexica_url = f"https://lexica.art/api/v1/search?q={urllib.parse.quote(kw_en + ' luxury cinematic masterpiece')}"
                    r_lex = requests.get(lexica_url, timeout=10).json()
                    if r_lex.get('images'):
                        # Coge una imagen aleatoria entre las 8 mejores
                        img_url = random.choice(r_lex['images'][:8])['src']
                        with open(img, 'wb') as f: f.write(requests.get(img_url, timeout=10).content)
                        exito_imagen = True
                except: pass

                # --- MOTOR 2: PEXELS (FILTRADO POR ARTE IA) ---
                if not exito_imagen:
                    st.markdown('<div class="msg">🔄 Buscando en reserva de Pexels IA...</div>', unsafe_allow_html=True)
                    try:
                        headers = {"Authorization": PEXELS_API}
                        url_p = f"https://api.pexels.com/v1/search?query={urllib.parse.quote(kw_en+' ai generated art')}&orientation=portrait&per_page=5"
                        r_p = requests.get(url_p, headers=headers, timeout=10).json()
                        if r_p.get('photos'):
                            img_url = random.choice(r_p['photos'])['src']['large2x']
                            with open(img, 'wb') as f: f.write(requests.get(img_url, timeout=10).content)
                            exito_imagen = True
                    except: pass

                # RENDERIZAR CLIP CON ZOOM LATERAL V58
                if exito_imagen:
                    z_fx = random.choice(["zoompan=z='1.0+0.001*on':x='iw/4-(iw/4/d)*on'", "zoompan=z='1.15-0.001*on':x='(iw/4/d)*on'"])
                    vf = f"scale=1280:2275,{z_fx}:d={int(t_clip*24)}:s=720x1280,format=yuv420p"
                    subprocess.run(f'ffmpeg -y -loop 1 -i "{img}" -vf "{vf}" -t {t_clip} -c:v libx264 -preset ultrafast -r 24 "{vid}"', shell=True)
                
                # PARACAÍDAS FINAL
                if not os.path.exists(vid) or os.path.getsize(vid) < 1000:
                    if ultima_vid_exitosa: subprocess.run(f'cp "{ultima_vid_exitosa}" "{vid}"', shell=True)
                    else: subprocess.run(f'ffmpeg -y -f lavfi -i color=c=#1A1A1A:s=720x1280:d={t_clip}:r=24 -c:v libx264 -preset ultrafast -pix_fmt yuv420p "{vid}"', shell=True)

                if os.path.exists(vid):
                    clips.append(os.path.abspath(vid).replace('\\', '/'))
                    ultima_vid_exitosa = vid
                if os.path.exists(img): os.remove(img)
                gc.collect()

            st.markdown('<div class="msg">🎬 Ensamblando y tatuando subtítulos V58...</div>', unsafe_allow_html=True)
            with open("taller/lista.txt", "w") as f:
                for c in clips: f.write(f"file '{c}'\n")
            
            mudo = "taller/mudo.mp4"
            subprocess.run(f'ffmpeg -y -f concat -safe 0 -i taller/lista.txt -c copy "{mudo}"', shell=True)
            
            # SUBTÍTULOS V58
            pal_sub = re.sub(r'[^\w\s]', '', guion.upper()).split()
            chunks = [pal_sub[j:j+2] for j in range(0, len(pal_sub), 2)]
            t_ch = dur / max(len(chunks), 1)
            f_str = f"fontfile='{f_abs}':" if os.path.exists(f_abs) else ""
            subs = []
            for j, p in enumerate(chunks):
                ts, te = j * t_ch, (j + 1) * t_ch
                if len(p) == 2 and (len(p[0])+len(p[1]) > 10):
                    subs.append(f"drawtext=text='{p[0]}':fontcolor={color_sub}:fontsize=70:{f_str}borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2-45:enable='between(t,{ts},{te})'")
                    subs.append(f"drawtext=text='{p[1]}':fontcolor={color_sub}:fontsize=70:{f_str}borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2+45:enable='between(t,{ts},{te})'")
                else:
                    subs.append(f"drawtext=text='{' '.join(p)}':fontcolor={color_sub}:fontsize=70:{f_str}borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{ts},{te})'")
            
            with open("taller/s.txt", "w") as f: f.write(",\n".join(subs))
            
            final = "taller/master.mp4"
            subprocess.run(f'ffmpeg -y -i "{mudo}" -i "{audio}" -filter_complex_script taller/s.txt -c:v libx264 -preset ultrafast -crf 28 -threads 1 -t {dur} "{final}"', shell=True)
            
            if os.path.exists(final):
                st.markdown('<div class="info-card">🏆 VÍDEO COMPLETADO (BANCO DE IA)</div>', unsafe_allow_html=True)
                with open(final, "rb") as f: st.video(f.read())
                st.balloons()
