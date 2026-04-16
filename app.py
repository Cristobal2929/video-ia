import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil, math, gc
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V134 PRO", layout="centered")

components.html("<script>if('wakeLock' in navigator){navigator.wakeLock.request('screen');}</script>", height=0)

st.markdown("""
<style>
.stApp { background:#000; color:#fff; }
.pro-title { font-size:42px;font-weight:900;text-align:center;
background:-webkit-linear-gradient(45deg,#00FFD1,#FFD700);
-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.msg { color:#00FFD1;font-family:monospace;margin-bottom:8px;border-left:3px solid #FFD700;padding-left:10px;}
.stButton>button {width:100%;height:55px;font-weight:900;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V134 🔥</div>', unsafe_allow_html=True)

PEXELS_API = "TU_API_AQUI"

def limpiar_guion(txt):
    txt = re.sub(r'(?i)(assistant|analysis|thought|reasoning|tool_calls).*', '', txt)
    txt = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ.,!¿? ]', '', txt)
    return txt.strip()

def traducir(p):
    try:
        url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(p)}&langpair=es|en"
        return requests.get(url, timeout=5).json()['responseData']['translatedText']
    except:
        return p

def extraer_kw(txt):
    palabras = re.findall(r'\w+', txt)
    return max([p for p in palabras if len(p)>4], default="success")

def preparar():
    if os.path.exists("taller"): shutil.rmtree("taller")
    os.makedirs("taller", exist_ok=True)
    subprocess.run("pkill ffmpeg", shell=True)

tema = st.text_input("🧠 Tema del vídeo:")

if st.button("🚀 CREAR VIDEO PRO V134"):

    if not tema:
        st.error("⚠️ Escribe un tema")
    else:
        preparar()
        log = st.container()

        with log:
            st.markdown('<div class="msg">🧠 Generando guion...</div>', unsafe_allow_html=True)

            prompt = f"Escribe un texto motivador en español sobre {tema}. Máximo 80 palabras."

            try:
                raw = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}", timeout=20).text
                guion = limpiar_guion(raw)
            except:
                guion = "El éxito empieza cuando decides no rendirte."

            # VOZ
            st.markdown('<div class="msg">🎙️ Generando voz...</div>', unsafe_allow_html=True)
            voz = "taller/voz.mp3"
            subprocess.run(f'edge-tts --voice es-MX-JorgeNeural --text "{guion}" --write-media "{voz}"', shell=True)

            try:
                dur = float(subprocess.check_output(
                    f'ffprobe -i "{voz}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
            except:
                dur = 20

            # MUSICA
            st.markdown('<div class="msg">🎵 Descargando música...</div>', unsafe_allow_html=True)
            music = "taller/music.mp3"

            try:
                headers = {"Authorization": PEXELS_API}
                q = traducir(tema) + " cinematic music"
                url = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(q)}&per_page=1"

                r = requests.get(url, headers=headers).json()

                if r.get("videos"):
                    m_url = r['videos'][0]['video_files'][0]['link']

                    with requests.get(m_url, stream=True) as rr:
                        with open("taller/music_raw.mp4", "wb") as f:
                            shutil.copyfileobj(rr.raw, f)

                    subprocess.run(f'ffmpeg -y -i taller/music_raw.mp4 -vn -t {dur} -acodec mp3 {music}', shell=True)

            except:
                pass

            if not os.path.exists(music):
                subprocess.run(f'ffmpeg -y -f lavfi -i anullsrc=r=44100:cl=stereo -t {dur} {music}', shell=True)

            # CLIPS
            n = min(math.ceil(dur/3), 15)
            t_clip = dur/n
            clips = []

            palabras = guion.split()
            chunk = max(len(palabras)//n,1)

            headers = {"Authorization": PEXELS_API}

            for i in range(n):
                txt = " ".join(palabras[i*chunk:(i+1)*chunk])
                kw = traducir(extraer_kw(txt))

                st.markdown(f'<div class="msg">🎥 Clip {i+1}/{n}: {kw}</div>', unsafe_allow_html=True)

                raw = f"taller/raw{i}.mp4"
                vid = f"taller/v{i}.mp4"

                try:
                    url = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(kw)}&orientation=portrait&per_page=1"
                    r = requests.get(url, headers=headers).json()

                    if r.get("videos"):
                        v_url = r['videos'][0]['video_files'][0]['link']

                        with requests.get(v_url, stream=True) as rr:
                            with open(raw, "wb") as f:
                                shutil.copyfileobj(rr.raw, f)

                        subprocess.run(
                            f'ffmpeg -y -stream_loop -1 -i "{raw}" -t {t_clip} '
                            f'-vf "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280" '
                            f'-c:v libx264 -preset ultrafast "{vid}"',
                            shell=True
                        )
                except:
                    pass

                if not os.path.exists(vid):
                    subprocess.run(f'ffmpeg -y -f lavfi -i color=c=black:s=720x1280:d={t_clip} "{vid}"', shell=True)

                clips.append(os.path.abspath(vid).replace('\\','/'))

            # CONCAT
            with open("taller/lista.txt","w") as f:
                for c in clips:
                    f.write(f"file '{c}'\n")

            subprocess.run('ffmpeg -y -f concat -safe 0 -i taller/lista.txt -c copy taller/video.mp4', shell=True)

            # MEZCLA AUDIO
            st.markdown('<div class="msg">🎚️ Mezclando audio...</div>', unsafe_allow_html=True)

            final = "taller/final.mp4"

            subprocess.run(
                f'ffmpeg -y -i taller/video.mp4 -i {voz} -i {music} '
                f'-filter_complex "[1:a]volume=1[a1];[2:a]volume=0.2[a2];[a1][a2]amix=inputs=2:duration=first" '
                f'-c:v copy -shortest {final}',
                shell=True
            )

            if os.path.exists(final):
                st.markdown('<div class="msg">🏆 VIDEO COMPLETADO V134</div>', unsafe_allow_html=True)
                with open(final, "rb") as f:
                    st.video(f.read())
