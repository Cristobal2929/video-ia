import streamlit as st
import os, time, random, subprocess, re, urllib.parse
import requests
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(page_title="Fénix Viral PRO V20", layout="centered")

st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #0B0F19 0%, #1A2235 100%); color: #F8FAFC; }
.pro-title { font-size: 42px; font-weight: 900; background: -webkit-linear-gradient(45deg, #00C6FF, #0072FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX AI STUDIO v20 PRO REAL</div>', unsafe_allow_html=True)

CACHE="cache"
OUT="output"
os.makedirs(CACHE, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

# ---------- UTILS ----------
def run(cmd):
    try:
        subprocess.run(cmd, shell=True, check=True)
    except Exception as e:
        print("CMD ERROR:", e)

def time_to_sec(t):
    h, m, s = t.strip().split(':')
    if '.' in s:
        s, ms = s.split('.')
        ms = int(ms)/1000
    else:
        ms = 0
    return int(h)*3600 + int(m)*60 + int(s) + ms

def clean(txt):
    txt = txt.replace("'", "")
    return re.sub(r'[^\w\s]', '', txt).upper()

# ---------- GUION PRO ----------
def generar_guion(tema):
    bloques = [
        f"Nadie te contó esto sobre {tema}.",
        "Lo que estás a punto de escuchar cambia completamente la perspectiva.",
        "La mayoría de personas comete este error sin darse cuenta.",
        "Y por eso nunca avanzan.",
        "Pero hay un detalle que lo cambia todo.",
        "Los que entienden esto empiezan a ver resultados.",
        "No es magia. Es lógica aplicada correctamente.",
        "Cuando todos hacen lo mismo tú haces lo contrario.",
        "Ahí está la ventaja real.",
        "Ahora que lo sabes úsalo."
    ]
    return " ".join(bloques)

# ---------- MUSICA ----------
def get_music():
    path = os.path.join(CACHE, "music.mp3")
    if os.path.exists(path):
        return path
    try:
        url = "https://cdn.pixabay.com/download/audio/2022/03/15/audio_c8b7c0d1b7.mp3"
        r = requests.get(url, timeout=10)
        with open(path, "wb") as f:
            f.write(r.content)
        return path
    except:
        return None

# ---------- PEXELS ----------
def buscar_video(q, key):
    try:
        url=f"https://api.pexels.com/videos/search?query={urllib.parse.quote(q)}&per_page=10"
        r=requests.get(url,headers={"Authorization":key},timeout=5).json()
        for v in r.get("videos",[]):
            for f in v["video_files"]:
                if f["height"]>=1280:
                    return f["link"]
    except:
        return None

def buscar_imagen(q, key):
    try:
        url=f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5"
        r=requests.get(url,headers={"Authorization":key},timeout=5).json()
        if r.get("photos"):
            return r["photos"][0]["src"]["original"]
    except:
        return None

def descargar(url, name):
    path=os.path.join(CACHE,name)
    if os.path.exists(path):
        return path
    try:
        r=requests.get(url,timeout=10)
        with open(path,"wb") as f:
            f.write(r.content)
        return path
    except:
        return None

# ---------- UI ----------
with st.sidebar:
    key = st.text_input("API Pexels", type="password")

# ---------- MAIN ----------
if prompt := st.chat_input("Tema del vídeo"):
    try:
        guion = generar_guion(prompt)
        st.write("🧠 Generando vídeo PRO...")

        # AUDIO VOZ
        run(f'edge-tts --voice es-ES-AlvaroNeural --rate=-5% --text "{guion}" --write-media t.mp3 --write-subtitles t.vtt')

        escenas=[]
        if os.path.exists("t.vtt"):
            with open("t.vtt") as f:
                l=f.readlines()
                for i in range(len(l)):
                    if "-->" in l[i]:
                        try:
                            s=time_to_sec(l[i].split(" --> ")[0])
                            e=time_to_sec(l[i].split(" --> ")[1])
                            txt=clean(l[i+1]) if i+1<len(l) else ""
                            escenas.append((s,e,txt))
                        except:
                            pass

        if not escenas:
            escenas=[(0,5,clean(guion))]

        # ---------- CLIPS ----------
        def clip(i,esc):
            dur=max(esc[1]-esc[0],2)

            queries=[prompt, esc[2], "cinematic", "abstract"]

            video=None
            for q in queries:
                video=buscar_video(q,key)
                if video:
                    break

            if video:
                f=descargar(video,f"v{i}.mp4")
                if f:
                    run(f'ffmpeg -y -i "{f}" -vf "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,fps=30" -t {dur} c{i}.mp4')
                    return f"c{i}.mp4"

            # fallback imagen
            img=None
            for q in queries:
                img=buscar_imagen(q,key)
                if img:
                    break

            if img:
                f=descargar(img,f"i{i}.jpg")
                if f:
                    run(f'ffmpeg -y -loop 1 -i "{f}" -c:v libx264 -t {dur} -vf "scale=720:1280" c{i}.mp4')
                    return f"c{i}.mp4"

            # fallback negro
            run(f'ffmpeg -y -f lavfi -i color=c=black:s=720x1280:d={dur} c{i}.mp4')
            return f"c{i}.mp4"

        with ThreadPoolExecutor(max_workers=4) as ex:
            clips=list(ex.map(lambda x: clip(*x), enumerate(escenas)))

        # CONCAT
        with open("list.txt","w") as f:
            for c in clips:
                f.write(f"file '{c}'\n")

        run("ffmpeg -y -f concat -safe 0 -i list.txt -c copy base.mp4")

        # ---------- SUBTITULOS ----------
        filtros=[]
        for esc in escenas:
            filtros.append(
                f"drawtext=text='{esc[2]}':fontcolor=yellow:fontsize=48:borderw=3:bordercolor=black:x=(w-text_w)/2:y=h-200:enable='between(t,{esc[0]},{esc[1]})'"
            )

        with open("subs.txt","w") as f:
            f.write(",".join(filtros))

        # ---------- AUDIO ----------
        music = get_music()

        if music:
            run(f'ffmpeg -y -i t.mp3 -i "{music}" -filter_complex "[0:a]volume=2[a];[1:a]volume=0.2[b];[a][b]amix=inputs=2:duration=first:dropout_transition=2" audio.mp3')
        else:
            run("cp t.mp3 audio.mp3")

        # ---------- FINAL ----------
        out=f"{OUT}/video_{int(time.time())}.mp4"
        run(f'ffmpeg -y -i base.mp4 -i audio.mp3 -filter_complex_script subs.txt -shortest "{out}"')

        if os.path.exists(out):
            st.success("🔥 VIDEO PRO REAL GENERADO")
            st.video(out)

    except Exception as e:
        st.error(str(e))
