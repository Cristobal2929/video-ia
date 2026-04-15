import streamlit as st
import os, time, random, subprocess, re, urllib.parse
import requests
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(page_title="Fénix Viral PRO V18", layout="centered")

st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #0B0F19 0%, #1A2235 100%); color: #F8FAFC; }
.pro-title { font-size: 40px; font-weight: 900; background: -webkit-linear-gradient(45deg, #00C6FF, #0072FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX AI STUDIO v18.1</div>', unsafe_allow_html=True)

# -------- CONFIG --------
CACHE_DIR = "cache_videos"
OUTPUT_DIR = "output"
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------- UTILS --------
def run_cmd(cmd):
    try:
        subprocess.run(cmd, shell=True, check=True)
    except Exception as e:
        print("CMD ERROR:", e)

def time_to_sec(t):
    t = t.strip()
    h, m, s = t.split(':')

    if '.' in s:
        s, ms = s.split('.')
        ms = int(ms) / 1000
    else:
        ms = 0

    return int(h)*3600 + int(m)*60 + int(s) + ms

def limpiar_texto(texto):
    texto = texto.replace("'", "")
    texto = re.sub(r'[^\w\s]', '', texto)
    return texto.upper()

# -------- IA INTERNA --------
def detectar_nicho(t):
    t = t.lower()
    if "dinero" in t: return "NEGOCIOS"
    if "miedo" in t: return "TERROR"
    if "espacio" in t: return "CIENCIA"
    return "UNIVERSAL"

def generar_guion(tema, nicho):
    hooks = [
        f"No deberías estar viendo esto sobre {tema}",
        f"El secreto oculto de {tema}",
        f"Nadie te contó esto de {tema}"
    ]
    base = random.choice(hooks)

    if nicho == "NEGOCIOS":
        return base + ". El 90% pierde dinero porque sigue a la masa. La clave es hacer lo contrario."

    if nicho == "TERROR":
        return base + ". Lo que ocurrió no debería existir. Y sigue pasando."

    return base + ". Esto cambia todo lo que creías."

# -------- PEXELS --------
def obtener_video(query, api):
    try:
        url = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(query)}&per_page=8"
        r = requests.get(url, headers={"Authorization": api}, timeout=5).json()

        for v in r.get("videos", []):
            for f in v["video_files"]:
                if f["height"] >= 1280:
                    return f["link"]
    except:
        return None

def descargar_video(url, name):
    path = os.path.join(CACHE_DIR, name)
    if os.path.exists(path):
        return path

    try:
        r = requests.get(url, timeout=10)
        with open(path, "wb") as f:
            f.write(r.content)
        return path
    except:
        return None

# -------- UI --------
with st.sidebar:
    api = st.text_input("API Pexels", type="password")

# -------- MAIN --------
if prompt := st.chat_input("Tema del vídeo"):
    try:
        nicho = detectar_nicho(prompt)
        guion = generar_guion(prompt, nicho)

        st.write("🧠 Guion generado:")
        st.write(guion)

        # AUDIO
        run_cmd(f'edge-tts --voice es-ES-AlvaroNeural --text "{guion}" --write-media t.mp3 --write-subtitles t.vtt')

        if not os.path.exists("t.vtt"):
            st.error("Error generando subtítulos")
            st.stop()

        escenas = []
        with open("t.vtt", encoding="utf-8") as f:
            lines = f.readlines()
            for i in range(len(lines)):
                if "-->" in lines[i]:
                    try:
                        start = time_to_sec(lines[i].split(" --> ")[0])
                        end = time_to_sec(lines[i].split(" --> ")[1])

                        if i+1 < len(lines):
                            txt = limpiar_texto(lines[i+1])
                        else:
                            txt = ""

                        escenas.append((start, end, txt))
                    except:
                        continue

        # FALLBACK si no detecta escenas
        if not escenas:
            escenas = [(0, 5, limpiar_texto(guion))]

        # CLIPS PARALELOS
        def make_clip(i, esc):
            dur = max(esc[1] - esc[0], 1)

            v = obtener_video(prompt, api)
            vid = descargar_video(v, f"{i}.mp4") if v else None

            try:
                if vid:
                    run_cmd(f'ffmpeg -y -i "{vid}" -vf "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,fps=30" -t {dur} p_{i}.mp4')
                else:
                    raise Exception()
            except:
                run_cmd(f'ffmpeg -y -f lavfi -i color=c=black:s=720x1280:d={dur}:r=30 p_{i}.mp4')

            return f"p_{i}.mp4"

        with ThreadPoolExecutor(max_workers=4) as ex:
            clips = list(ex.map(lambda x: make_clip(*x), enumerate(escenas)))

        # CONCAT
        with open("lista.txt", "w") as f:
            for c in clips:
                f.write(f"file '{c}'\n")

        run_cmd("ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4")

        # FINAL
        output = f"{OUTPUT_DIR}/video_{int(time.time())}.mp4"
        run_cmd(f'ffmpeg -y -i base.mp4 -i t.mp3 -shortest "{output}"')

        if os.path.exists(output):
            st.success("✅ VIDEO GENERADO V18.1 PRO")
            st.video(output)

    except Exception as e:
        st.error(f"Error: {e}")
