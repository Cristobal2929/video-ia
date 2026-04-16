import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil, math, random, gc
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V95", layout="centered")

# TRUCO DE HACKER: Mantener la pantalla del móvil encendida durante el proceso
components.html("<script>if('wakeLock' in navigator){navigator.wakeLock.request('screen');}</script>", height=0)

st.markdown("""
<style>
    .stApp { background: #000000; color: #FFFFFF; }
    .pro-title { font-size: 40px; font-weight: 900; background: -webkit-linear-gradient(45deg, #00FFD1, #FFD700); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; text-transform: uppercase; margin-bottom: 20px;}
    .info-card { padding: 15px; border-radius: 10px; background: #0f172a; border: 1px solid #00FFD1; text-align: center; color: #00FFD1; margin-top: 20px;}
    .msg { color: #94A3B8; font-family: monospace; font-size: 14px; margin-bottom: 8px; border-left: 3px solid #00FFD1; padding-left: 10px; }
    .stButton>button { width: 100%; background: linear-gradient(45deg, #00FFD1, #0088ff); color: white; border: none; font-weight: bold; height: 50px; border-radius: 10px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V95 🎥</div>', unsafe_allow_html=True)

@st.cache_resource
def descargar_fuente():
    font_path = "Arial_Pro.ttf"
    if not os.path.exists(font_path):
        try:
            r = requests.get("https://github.com/matomo-org/travis-scripts/raw/master/fonts/Arial.ttf", timeout=10)
            with open(font_path, "wb") as f: f.write(r.content)
        except: pass
    return os.path.abspath(font_path).replace('\\', '/')

font_abs = descargar_fuente()

def traducir_a_ingles(palabra):
    try:
        url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(palabra)}&langpair=es|en"
        return requests.get(url, timeout=5).json()['responseData']['translatedText']
    except: return palabra

def preparar_entorno():
    if os.path.exists("taller"): shutil.rmtree("taller")
    os.makedirs("taller", exist_ok=True)

# INTERFAZ DE USUARIO
tema = st.text_input("🧠 ¿Sobre qué quieres el vídeo?", placeholder="Ej: Las claves para el éxito online")
color_sub = st.selectbox("🎨 Color de los Subtítulos", ["yellow", "white", "#00FFD1"])
n_escenas = st.select_slider("⏱️ Cantidad de Escenas (Variedad)", options=[4, 8, 12, 15], value=8)

if st.button("🚀 INICIAR PRODUCCIÓN EN VIVO"):
    if not tema: 
        st.error("⚠️ Por favor, escribe un tema primero.")
    else:
        preparar_entorno()
        placeholder = st.empty()
        log_container = st.container()

        with log_container:
            # 1. GENERACIÓN DE GUION
            st.markdown('<div class="msg">📝 IA Redactando guion original...</div>', unsafe_allow_html=True)
            prompt = f"Escribe un guion corto para TikTok sobre {tema}. Solo el texto del locutor, sin emojis, 70 palabras."
            try:
                guion = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}", timeout=15).text
                guion = re.sub(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ.,! ]', '', guion).strip()
            except:
                guion = "El éxito no es el final, el fracaso no es fatal, es el coraje para continuar lo que cuenta. Sigue adelante siempre."

            # 2. GENERACIÓN DE VOZ (MOTOR TITANIUM)
            st.markdown('<div class="msg">🎙️ Grabando locución (Microsoft Jorge)...</div>', unsafe_allow_html=True)
            audio_path = "taller/audio.mp3"
            subprocess.run(f'python -m edge_tts --voice es-MX-JorgeNeural --text "{guion}" --write-media "{audio_path}"', shell=True)
            
            duracion_total = 15.0
            try:
                duracion_total = float(subprocess.check_output(f'ffprobe -i "{audio_path}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
            except: pass

            # 3. PRODUCCIÓN DE ESCENAS
            t_por_escena = duracion_total / n_escenas
            dur_frames = int(t_por_escena * 24)
            clips = []
            palabras_clave = guion.split()

            for i in range(n_escenas):
                p_base = palabras_clave[min(i*4, len(palabras_clave)-1)]
                p_en = traducir_a_ingles(p_base)
                st.markdown(f'<div class="msg">📸 Escena {i+1}/{n_escenas}: Renderizando "{p_en.upper()}"...</div>', unsafe_allow_html=True)
                
                img_path = f"taller/i_{i}.jpg"
                vid_path = f"taller/v_{i}.mp4"
                
                # Motor de imagen con Seed para evitar repeticiones
                seed = random.randint(1, 100000)
                ia_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(p_en + ' luxury cinematic hyperrealistic 8k')}?width=720&height=1280&nologo=true&seed={seed}"
                
                try:
                    time.sleep(3.5) # Truco anti-bloqueo
                    r = requests.get(ia_url, timeout=25)
                    with open(img_path, 'wb') as f: f.write(r.content)
                    
                    # Zoom dinámico aleatorio
                    zoom_fx = random.choice(["z='1.0+0.001*on'", "z='1.2-0.001*on'"])
                    vf = f"scale=800:1422,zoompan={zoom_fx}:d={dur_frames}:s=720x1280:fps=24,format=yuv420p"
                    
                    subprocess.run(f'ffmpeg -y -loop 1 -i "{img_path}" -vf "{vf}" -t {t_por_escena} -c:v libx264 -preset superfast -crf 25 "{vid_path}"', shell=True)
                    
                    if os.path.exists(vid_path):
                        clips.append(f"v_{i}.mp4")
                except:
                    if i > 0: clips.append(clips[-1])
                
                if os.path.exists(img_path): os.remove(img_path)
                gc.collect() # Limpieza de memoria tras cada escena

            # 4. MONTAJE FINAL
            st.markdown('<div class="msg">🎬 Uniendo todas las piezas...</div>', unsafe_allow_html=True)
            with open("taller/lista.txt", "w") as f:
                for c in clips: f.write(f"file '{c}'\n")
            
            v_mudo = "taller/mudo.mp4"
            subprocess.run(f'ffmpeg -y -f concat -safe 0 -i taller/lista.txt -c copy "{v_mudo}"', shell=True)
            
            st.markdown('<div class="msg">✨ Aplicando subtítulos dinámicos...</div>', unsafe_allow_html=True)
            master_path = "taller/master.mp4"
            
            # Subtítulos simplificados pero potentes para evitar errores de renderizado
            sub_filter = f"drawtext=text='{guion[:35].upper()}...':fontcolor={color_sub}:fontsize=60:fontfile='{font_abs}':x=(w-tw)/2:y=(h-th)/2:borderw=4:bordercolor=black"
            
            subprocess.run(f'ffmpeg -y -i "{v_mudo}" -i "{audio_path}" -vf "{sub_filter}" -c:v libx264 -preset fast -t {duracion_total} "{master_path}"', shell=True)
            
            if os.path.exists(master_path):
                st.markdown('<div class="info-card">✅ ¡ÉXITO! Tu vídeo ha sido procesado correctamente.</div>', unsafe_allow_html=True)
                with open(master_path, "rb") as f:
                    st.video(f.read())
                st.balloons()
            else:
                st.error("❌ Falló el último paso del renderizado.")
