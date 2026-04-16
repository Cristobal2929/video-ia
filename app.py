import streamlit as st
import os, subprocess, re, urllib.parse, shutil, math, gc
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V134 FIX", layout="centered")

components.html("<script>if('wakeLock' in navigator){navigator.wakeLock.request('screen');}</script>", height=0)

st.markdown("""
<style>
.stApp { background:#000; color:#fff; }
.pro-title { font-size:40px;font-weight:900;text-align:center;
background:-webkit-linear-gradient(45deg,#00FFD1,#FFD700);
-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.msg { color:#00FFD1;font-family:monospace;margin-bottom:8px;border-left:3px solid #FFD700;padding-left:10px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V134 FIX 🔥</div>', unsafe_allow_html=True)

PEXELS_API = "TU_API_AQUI"

def limpiar(txt):
    txt = re.sub(r'(?i)(assistant|analysis|thought|reasoning).*', '', txt)
    txt = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ.,!¿? ]', '', txt)
    return txt.strip()

def preparar():
    if os.path.exists("taller"): shutil.rmtree("taller")
    os.makedirs("taller", exist_ok=True)
    subprocess.run("pkill ffmpeg", shell=True)

tema = st.text_input("🧠 Tema")

if st.button("🚀 CREAR VIDEO REAL"):
    if not tema:
        st.error("Pon un tema")
    else:
        preparar()
        log = st.container()

        with log:
            st.markdown('<div class="msg">🧠 Generando guion...</div>', unsafe_allow_html=True)

            try:
                raw = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote(tema)}").text
                guion = limpiar(raw)
            except:
                guion = "Empieza hoy, no mañana."

            # VOZ
            voz = "taller/voz.mp3"
            subprocess.run(f'edge-tts --voice es-MX-JorgeNeural --text "{guion}" --write-media "{voz}"', shell=True)

            dur = float(subprocess.check_output(
                f'ffprobe -i "{voz}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))

            # 🎵 MUSICA (FIJA Y SEGURA)
            st.markdown('<div class="msg">🎵 Generando música segura...</div>', unsafe_allow_html=True)

            music = "taller/music.mp3"

            # música sintética SIEMPRE FUNCIONA
            subprocess.run(
                f'ffmpeg -y -f lavfi -i "sine=frequency=440:duration={dur}" -filter:a "volume=0.05" {music}',
                shell=True
            )

            # 🎥 VIDEO (MEJORADO)
            clips = []
            n = min(math.ceil(dur/3), 10)
            t = dur/n

            headers = {"Authorization": PEXELS_API}

            for i in range(n):
                st.markdown(f'<div class="msg">🎥 Clip {i+1}</div>', unsafe_allow_html=True)

                raw = f"taller/raw{i}.mp4"
                out = f"taller/v{i}.mp4"

                try:
                    url = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(tema)}&orientation=portrait&per_page=2"
                    r = requests.get(url, headers=headers).json()

                    v_url = r['videos'][0]['video_files'][-1]['link']

                    with requests.get(v_url, stream=True) as rr:
                        with open(raw, "wb") as f:
                            shutil.copyfileobj(rr.raw, f)

                    subprocess.run(
                        f'ffmpeg -y -stream_loop -1 -i "{raw}" -t {t} '
                        f'-vf "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280" '
                        f'{out}',
                        shell=True
                    )

                except:
                    # FONDO DECENTE (NO NEGRO)
                    subprocess.run(
                        f'ffmpeg -y -f lavfi -i color=c=#222222:s=720x1280:d={t} {out}',
                        shell=True
                    )

                clips.append(out)

            # CONCAT
            with open("taller/lista.txt","w") as f:
                for c in clips:
                    f.write(f"file '{os.path.abspath(c)}'\n")

            subprocess.run('ffmpeg -y -f concat -safe 0 -i taller/lista.txt -c copy taller/video.mp4', shell=True)

            # MIX AUDIO
            final = "taller/final.mp4"

            subprocess.run(
                f'ffmpeg -y -i taller/video.mp4 -i {voz} -i {music} '
                f'-filter_complex "[1:a]volume=1[a1];[2:a]volume=0.1[a2];[a1][a2]amix=inputs=2" '
                f'-shortest {final}',
                shell=True
            )

            if os.path.exists(final):
                st.success("🔥 VIDEO GENERADO (YA FUNCIONA)")
                st.video(open(final,"rb").read())
