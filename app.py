import streamlit as st
import os, subprocess, re, urllib.parse, shutil, math, gc
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
    .video-container { border: 3px solid #00FFD1; border-radius: 15px; padding: 10px; background: #111; }
    .error-log { background: #330000; color: #FFAAAA; padding: 12px; border-radius: 8px; font-family: monospace; font-size: 13px; white-space: pre-wrap; max-height: 300px; overflow-y: auto; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V142 🦅🎬🎵</div>', unsafe_allow_html=True)

PEXELS_API = "Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ"

def limpiar_texto(t):
    t = re.sub(r'tool_calls|recalc|words|assistant|reasoning|thought|count|slightly|above|remove|piece|adjust|instruction|spanish|user|wants|script', '', t, flags=re.I)
    return re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ.,! ]', '', t).strip()

def preparar():
    if os.path.exists("taller"): shutil.rmtree("taller")
    os.makedirs("taller", exist_ok=True)
    subprocess.run("pkill ffmpeg", shell=True, stderr=subprocess.DEVNULL)
    gc.collect()

tema = st.text_input("🧠 Tema del vídeo:", placeholder="Ej: La mentalidad del 1%")
estilo_m = st.selectbox("🎵 Música de Fondo:", ["Epic", "Cinematic", "Dark", "Motivational"])

if st.button("🚀 CREAR VÍDEO (VÍDEOS REALES + MÚSICA)"):
    if not tema:
        st.error("Escribe un tema")
        st.stop()

    preparar()
    log = st.container()
    with log:
        # Verificar ffmpeg
        try:
            ffmpeg_check = subprocess.run(["which", "ffmpeg"], capture_output=True, text=True)
            if not ffmpeg_check.stdout.strip():
                st.error("❌ FFmpeg no está instalado en el servidor. Crea un archivo **packages.txt** en la raíz con la palabra `ffmpeg` y haz Reboot de la app.")
                st.stop()
            st.success("✅ FFmpeg detectado")
        except:
            st.error("Error al verificar FFmpeg")
            st.stop()

        # 1. Guion y voz (sin cambios)
        st.markdown('<div class="msg">📝 Redactando guion viral...</div>', unsafe_allow_html=True)
        p = f"Escribe UNICAMENTE el guion para TikTok sobre {tema}. Estructura: Gancho con historia, pasos y cierre. Maximo 90 palabras."
        try:
            g_raw = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote(p)}", timeout=15).text
            guion = limpiar_texto(g_raw)
        except: 
            guion = "El éxito real requiere disciplina inquebrantable."

        audio_voz = "taller/voz.mp3"
        subprocess.run(f'edge-tts --voice es-MX-JorgeNeural --text "{guion}" --write-media "{audio_voz}"', shell=True)

        # 2. Música
        st.markdown('<div class="msg">🎵 Sincronizando banda sonora...</div>', unsafe_allow_html=True)
        musica_file = "taller/bg.mp3"
        m_url = "https://www.chosic.com/wp-content/uploads/2021/07/Inspirational-Cinematic-Background.mp3"
        if estilo_m == "Epic": m_url = "https://www.chosic.com/wp-content/uploads/2021/05/The-Epic-Hero.mp3"
        elif estilo_m == "Dark": m_url = "https://www.chosic.com/wp-content/uploads/2021/10/Shadows.mp3"
        with open(musica_file, "wb") as f: 
            f.write(requests.get(m_url).content)

        try: 
            dur = float(subprocess.check_output(f'ffprobe -i "{audio_voz}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True).decode().strip())
        except: 
            dur = 25.0

        # 3. Clips (reducido a 12 máx para ahorrar RAM)
        n_clips = min(math.ceil(dur / 3.5), 12)
        # ... (el resto del código de clips se mantiene igual que antes, lo omito aquí por brevedad pero cópialo de la versión anterior)

        # 4. ENSAMBLADO CON DEPURACIÓN COMPLETA
        st.markdown('<div class="msg">🎬 Masterizando con música...</div>', unsafe_allow_html=True)

        with open("taller/lista.txt", "w") as f:
            for c in clips: f.write(f"file '{c}'\n")

        mudo = "taller/mudo.mp4"
        subprocess.run(f'ffmpeg -y -f concat -safe 0 -i taller/lista.txt -c copy "{mudo}"', shell=True)

        voz_temp = "taller/voz_temp.mp4"
        subprocess.run(f'ffmpeg -y -i "{mudo}" -i "{audio_voz}" -c:v libx264 -preset veryfast -threads 2 -c:a aac -b:a 128k -shortest -pix_fmt yuv420p "{voz_temp}"', shell=True)

        final = "taller/master.mp4"
        fade_st = max(0, dur - 2)

        cmd = f'ffmpeg -y -i "{voz_temp}" -i "{musica_file}" -filter_complex "[1:a]volume=0.12,afade=t=out:st={fade_st}:d=2[music];[0:a][music]amix=inputs=2:duration=first:dropout_transition=2[aout]" -map 0:v -map "[aout]" -c:v libx264 -preset veryfast -threads 2 -crf 23 -pix_fmt yuv420p -c:a aac -b:a 160k -shortest "{final}"'

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            st.markdown(f'<div class="error-log">❌ ERROR EN FFmpeg (código {result.returncode}):\n\n{result.stderr[-2000:]}</div>', unsafe_allow_html=True)
            st.error("Fallo en la mezcla final. Copia el error de arriba y pégamelo aquí para arreglarlo.")
        else:
            # Limpieza y mostrar vídeo
            for f in ["taller/mudo.mp4", "taller/voz_temp.mp4"] + [f"taller/v_{i}.mp4" for i in range(n_clips)]:
                if os.path.exists(f): 
                    try: os.remove(f)
                    except: pass
            gc.collect()

            st.markdown('<div class="msg">🏆 ¡VÍDEO COMPLETADO!</div>', unsafe_allow_html=True)
            st.markdown('<div class="video-container">', unsafe_allow_html=True)
            st.video(final)
            st.markdown('</div>', unsafe_allow_html=True)

            with open(final, "rb") as file:
                st.download_button("⬇️ Descargar vídeo", data=file, file_name=f"fenix_{tema[:30]}.mp4", mime="video/mp4")

        st.success("Proceso terminado.")
