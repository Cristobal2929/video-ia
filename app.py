import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil, math, random, gc
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V101", layout="centered")

# Mantener la pantalla encendida para procesos largos
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

st.markdown('<div class="pro-title">FÉNIX STUDIO V101 🎥</div>', unsafe_allow_html=True)

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

tema = st.text_input("🧠 ¿De qué trata el vídeo? (IA Guion):", placeholder="Ej: Las leyes del éxito millonario")
color_sub = st.selectbox("🎨 Color de los Subtítulos:", ["yellow", "white", "#00FFD1"])
estilo_v = st.text_input("🎨 Filtro de Imagen IA:", value="Luxury Cinematic 8k photography")

if st.button("🚀 CREAR OBRA MAESTRA (V58 STYLE)"):
    if not tema: st.error("⚠️ Escribe un tema, jefe.")
    else:
        preparar()
        log = st.container()
        
        with log:
            # 1. GENERACIÓN DE GUION
            st.markdown('<div class="msg">📝 Redactando guion al compás del tema...</div>', unsafe_allow_html=True)
            prompt_g = f"Escribe un guion motivador para TikTok sobre {tema}. Solo el texto del locutor, 75 palabras, sin emojis."
            guion_raw = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote(prompt_g)}").text
            guion = re.sub(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ.,! ]', '', guion_raw).strip()
            
            # 2. VOZ PRO
            st.markdown('<div class="msg">🎙️ Grabando voz de alta fidelidad...</div>', unsafe_allow_html=True)
            audio = "taller/audio.mp3"
            subprocess.run(f'edge-tts --voice es-MX-JorgeNeural --rate=+10% --text "{guion}" --write-media "{audio}"', shell=True)
            
            dur = 15.0
            try:
                dur = float(subprocess.check_output(f'ffprobe -i "{audio}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
            except: pass
            
            # 3. IMÁGENES AL COMPÁS (Escenas de 3.5 segundos)
            n_clips = math.ceil(dur / 3.5)
            t_clip = dur / n_clips
            clips = []
            palabras_guion = guion.split()
            chunk_size = max(len(palabras_guion) // n_clips, 1)

            for i in range(n_clips):
                # Extraer la idea de lo que se está diciendo en este momento
                txt_chunk = " ".join(palabras_guion[i*chunk_size:(i+1)*chunk_size])
                kw_es = extraer_kw(txt_chunk)
                kw_en = traducir_en(kw_es)
                
                st.markdown(f'<div class="msg">📸 Escena {i+1}: IA buscando "{kw_en.upper()}"...</div>', unsafe_allow_html=True)
                
                img = f"taller/i_{i}.jpg"
                vid = f"taller/v_{i}.mp4"
                
                exito_ia = False
                for intento in range(2):
                    seed = random.randint(1, 999999)
                    url_ia = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(kw_en+' '+estilo_v)}?width=720&height=1280&nologo=true&seed={seed}"
                    try:
                        time.sleep(3.5) # Delay para evitar bloqueo
                        r = requests.get(url_ia, timeout=30)
                        if r.status_code == 200 and len(r.content) > 5000:
                            with open(img, 'wb') as f: f.write(r.content)
                            exito_ia = True
                            break
                    except: pass

                if exito_ia:
                    # EFECTO ZOOM LATERAL PRO (Ken Burns mejorado)
                    # Variamos entre zoom in + pan izquierda y zoom out + pan derecha
                    z_fx = random.choice([
                        f"zoompan=z='1.0+0.001*on':x='iw/4-(iw/4/d)*on':s=720x1280",
                        f"zoompan=z='1.15-0.001*on':x='(iw/4/d)*on':s=720x1280"
                    ])
                    vf = f"scale=1280:2275,{z_fx},format=yuv420p"
                    subprocess.run(f'ffmpeg -y -loop 1 -i "{img}" -vf "{vf}" -t {t_clip} -c:v libx264 -preset ultrafast -r 24 "{vid}"', shell=True)
                    if os.path.exists(vid): clips.append(f"v_{i}.mp4")
                
                if os.path.exists(img): os.remove(img)
                gc.collect()

            # 4. UNIÓN Y SUBTÍTULOS DOBLE CAPA (IGUAL QUE V58)
            st.markdown('<div class="msg">🎬 Ensamblando con Subtítulos Dinámicos...</div>', unsafe_allow_html=True)
            with open("taller/lista.txt", "w") as f:
                for c in clips: f.write(f"file '{c}'\n")
            
            mudo = "taller/mudo.mp4"
            subprocess.run(f'ffmpeg -y -f concat -safe 0 -i taller/lista.txt -c copy "{mudo}"', shell=True)
            
            # Cálculo de tiempos para palabras (Doble Capa)
            palabras_sub = re.sub(r'[^\w\s]', '', guion.upper()).split()
            chunks_sub = [palabras_sub[j:j+2] for j in range(0, len(palabras_sub), 2)]
            t_por_chunk = dur / max(len(chunks_sub), 1)
            
            subs_cmd = []
            for j, p_list in enumerate(chunks_sub):
                ts = j * t_por_chunk
                te = ts + t_por_chunk
                if len(p_list) == 2 and (len(p_list[0]) + len(p_list[1]) > 10):
                    # Palabra arriba y palabra abajo
                    subs_cmd.append(f"drawtext=text='{p_list[0]}':fontcolor={color_sub}:fontsize=65:fontfile='{f_abs}':borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2-45:enable='between(t,{ts},{te})'")
                    subs_cmd.append(f"drawtext=text='{p_list[1]}':fontcolor={color_sub}:fontsize=65:fontfile='{f_abs}':borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2+45:enable='between(t,{ts},{te})'")
                else:
                    # Una sola frase o palabra centrada
                    frase = " ".join(p_list)
                    subs_cmd.append(f"drawtext=text='{frase}':fontcolor={color_sub}:fontsize=65:fontfile='{f_abs}':borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{ts},{te})'")
            
            with open("taller/subs_filter.txt", "w") as f: f.write(",\n".join(subs_cmd))
            
            final = "taller/master.mp4"
            subprocess.run(f'ffmpeg -y -i "{mudo}" -i "{audio}" -filter_complex_script taller/subs_filter.txt -c:v libx264 -preset fast -t {dur} "{final}"', shell=True)
            
            if os.path.exists(final):
                st.markdown('<div class="info-card">🏆 VÍDEO COMPLETADO: ESTILO V58 + IA 8K</div>', unsafe_allow_html=True)
                with open(final, "rb") as f: st.video(f.read())
                st.balloons()
