import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil, math, random, gc
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V142", layout="centered")
components.html("<script>if('wakeLock' in navigator){navigator.wakeLock.request('screen');}</script>", height=0)

st.markdown("""
<style>
    .stApp { background: #000000; color: #FFFFFF; }
    .pro-title { font-size: 42px; font-weight: 900; background: -webkit-linear-gradient(45deg, #00FFD1, #FFD700); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; text-transform: uppercase; margin-bottom: 20px;}
    .msg { color: #00FFD1; font-family: 'Courier New', monospace; font-size: 14px; margin-bottom: 8px; border-left: 3px solid #FFD700; padding-left: 12px; }
    .stButton>button { width: 100%; background: linear-gradient(45deg, #00FFD1, #0088ff); color: white; border: none; font-weight: 900; height: 55px; border-radius: 12px; font-size: 18px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V142 🦅🎬🎵</div>', unsafe_allow_html=True)

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
    t = re.sub(r'tool_calls|recalc|words|assistant|reasoning|thought|count|slightly|above|remove|piece|adjust|instruction|spanish|user|wants|script', '', t, flags=re.I)
    return re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ.,! ]', '', t).strip()

def preparar():
    if os.path.exists("taller"): shutil.rmtree("taller")
    os.makedirs("taller", exist_ok=True)
    subprocess.run("pkill ffmpeg", shell=True)
    gc.collect()

tema = st.text_input("🧠 Tema del vídeo:", placeholder="Ej: La mentalidad del 1%")
estilo_m = st.selectbox("🎵 Música de Fondo:", ["Epic", "Cinematic", "Dark", "Motivational"])

if st.button("🚀 CREAR VÍDEO (VÍDEOS REALES + MÚSICA)"):
    if not tema: 
        st.error("Escribe un tema")
    else:
        preparar()
        log = st.container()
        with log:
            # 1. GUION Y VOZ
            st.markdown('<div class="msg">📝 Redactando guion viral...</div>', unsafe_allow_html=True)
            p = f"Escribe UNICAMENTE el guion para TikTok sobre {tema}. Estructura: Gancho con historia, pasos y cierre. Maximo 90 palabras."
            try:
                g_raw = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote(p)}", timeout=15).text
                guion = limpiar_texto(g_raw)
            except: 
                guion = "El éxito real requiere disciplina inquebrantable."

            audio_voz = "taller/voz.mp3"
            subprocess.run(f'edge-tts --voice es-MX-JorgeNeural --text "{guion}" --write-media "{audio_voz}"', shell=True)
            
            # 2. MÚSICA ESTABLE
            st.markdown('<div class="msg">🎵 Sincronizando banda sonora...</div>', unsafe_allow_html=True)
            musica_file = "taller/bg.mp3"
            m_url = "https://www.chosic.com/wp-content/uploads/2021/07/Inspirational-Cinematic-Background.mp3"
            if estilo_m == "Epic": 
                m_url = "https://www.chosic.com/wp-content/uploads/2021/05/The-Epic-Hero.mp3"
            elif estilo_m == "Dark": 
                m_url = "https://www.chosic.com/wp-content/uploads/2021/10/Shadows.mp3"
            
            with open(musica_file, "wb") as f: 
                f.write(requests.get(m_url).content)

            try: 
                dur = float(subprocess.check_output(f'ffprobe -i "{audio_voz}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
            except: 
                dur = 25.0

            # 3. CAPTURA DE VÍDEOS REALES
            n_clips = min(math.ceil(dur / 3.5), 15)
            t_clip = dur / n_clips
            clips = []
            palabras = guion.split()
            chunk = max(len(palabras) // n_clips, 1)
            ultima = None

            for i in range(n_clips):
                txt_part = " ".join(palabras[i*chunk:(i+1)*chunk])
                st.markdown(f'<div class="msg">🎥 Escena {i+1}/{n_clips}: Vídeo real de "{txt_part[:15]}..."</div>', unsafe_allow_html=True)
                raw, vid = f"taller/r_{i}.mp4", f"taller/v_{i}.mp4"
                exito = False
                try:
                    h = {"Authorization": PEXELS_API}
                    url_p = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(txt_part[:15]+' luxury')}&orientation=portrait&per_page=1"
                    v_link = requests.get(url_p, headers=h, timeout=10).json()['videos'][0]['video_files'][0]['link']
                    with open(raw, 'wb') as f: 
                        f.write(requests.get(v_link, timeout=15).content)
                    vf = "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1,format=yuv420p"
                    subprocess.run(f'ffmpeg -y -stream_loop -1 -i "{raw}" -t {t_clip} -vf "{vf}" -c:v libx264 -preset superfast "{vid}"', shell=True)
                    exito = True
                except:
                    if ultima: 
                        subprocess.run(f'cp "{ultima}" "{vid}"', shell=True)
                    else: 
                        subprocess.run(f'ffmpeg -y -f lavfi -i color=c=#000000:s=720x1280:d={t_clip}:r=24 -c:v libx264 -preset superfast "{vid}"', shell=True)
                
                clips.append(os.path.abspath(vid))
                ultima = vid
                if os.path.exists(raw): 
                    os.remove(raw)
                gc.collect()

            # 4. ENSAMBLADO FINAL CON MÚSICA Y SUBTÍTULOS (OPTIMIZADO - BAJO CONSUMO DE RAM)
            st.markdown('<div class="msg">🎬 Masterizando con música y subtítulos V58 (bajo consumo RAM)...</div>', unsafe_allow_html=True)
            
            with open("taller/lista.txt", "w") as f:
                for c in clips: 
                    f.write(f"file '{c}'\n")
            
            mudo = "taller/mudo.mp4"
            # Concat eficiente
            subprocess.run(f'ffmpeg -y -f concat -safe 0 -i taller/lista.txt -c copy "{mudo}"', shell=True)

            # Añadir voz (re-codificación controlada)
            voz_temp = "taller/voz_temp.mp4"
            subprocess.run(
                f'ffmpeg -y -i "{mudo}" -i "{audio_voz}" -c:v libx264 -preset veryfast -threads 2 '
                f'-c:a aac -b:a 128k -shortest -pix_fmt yuv420p "{voz_temp}"',
                shell=True
            )

            # Mezcla final de música + voz (más ligera)
            final = "taller/master.mp4"
            fade_st = max(0, dur - 2)

            cmd = (
                f'ffmpeg -y -i "{voz_temp}" -i "{musica_file}" '
                f'-filter_complex "[1:a]volume=0.12,afade=t=out:st={fade_st}:d=2[music];'
                f'[0:a][music]amix=inputs=2:duration=first:dropout_transition=2[aout]" '
                f'-map 0:v -map "[aout]" -c:v libx264 -preset veryfast -threads 2 '
                f'-tune fastdecode -crf 23 -pix_fmt yuv420p -c:a aac -b:a 160k -shortest "{final}"'
            )
            subprocess.run(cmd, shell=True)

            # Limpieza agresiva de archivos temporales para liberar RAM
            for f in ["taller/mudo.mp4", "taller/voz_temp.mp4"] + [f"taller/v_{i}.mp4" for i in range(n_clips)]:
                if os.path.exists(f):
                    try: 
                        os.remove(f)
                    except: 
                        pass
            gc.collect()

            if os.path.exists(final):
                st.markdown('<div class="msg">🏆 VÍDEO REAL + MÚSICA COMPLETADO</div>', unsafe_allow_html=True)
                with open(final, "rb") as f: 
                    st.video(f.read())

            # Mensaje final
            st.success("¡Vídeo generado correctamente!")
