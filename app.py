import streamlit as st
import os, time, random, subprocess, re, urllib.parse
import requests
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(page_title="Fénix Viral PRO V18.2", layout="centered")

st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #0B0F19 0%, #1A2235 100%); color: #F8FAFC; }
.pro-title { font-size: 40px; font-weight: 900; background: -webkit-linear-gradient(45deg, #00C6FF, #0072FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX AI STUDIO v18.2 ULTRA</div>', unsafe_allow_html=True)

CACHE = "cache"
OUT = "output"
os.makedirs(CACHE, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

# -------- UTILS --------
def run(cmd):
    try:
        subprocess.run(cmd, shell=True, check=True)
    except:
        pass

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

# -------- IA --------
def nicho(t):
    t=t.lower()
    if "dinero" in t: return "money"
    if "miedo" in t: return "horror"
    return "viral"

def guion(t):
    hooks = [
        f"Nadie te contó esto de {t}",
        f"Esto está pasando con {t}",
        f"No deberías ver esto sobre {t}"
    ]
    return random.choice(hooks) + ". Esto cambiará todo."

# -------- PEXELS --------
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

# -------- UI --------
with st.sidebar:
    key = st.text_input("API Pexels", type="password")

# -------- MAIN --------
if prompt := st.chat_input("Tema del vídeo"):
    try:
        texto = guion(prompt)
        st.write("🧠", texto)

        # AUDIO
        run(f'edge-tts --voice es-ES-AlvaroNeural --text "{texto}" --write-media t.mp3 --write-subtitles t.vtt')

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
            escenas=[(0,5,clean(texto))]

        # -------- CLIPS --------
        def clip(i,esc):
            dur=max(esc[1]-esc[0],2)

            queries=[prompt, esc[2], nicho(prompt)]

            video=None
            for q in queries:
                video=buscar_video(q,key)
                if video: break

            if video:
                f=descargar(video,f"v{i}.mp4")
                if f:
                    run(f'ffmpeg -y -i "{f}" -vf "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280" -t {dur} c{i}.mp4')
                    return f"c{i}.mp4"

            # fallback imagen
            img=None
            for q in queries:
                img=buscar_imagen(q,key)
                if img: break

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

        # FINAL
        out=f"{OUT}/video_{int(time.time())}.mp4"
        run(f'ffmpeg -y -i base.mp4 -i t.mp3 -shortest "{out}"')

        if os.path.exists(out):
            st.success("🔥 VIDEO PRO GENERADO")
            st.video(out)

    except Exception as e:
        st.error(str(e))
