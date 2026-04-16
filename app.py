import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil, math, random, gc
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V136", layout="centered")

components.html("<script>if('wakeLock' in navigator){navigator.wakeLock.request('screen');}</script>", height=0)

st.markdown("""
<style>
    .stApp { background: #000000; color: #FFFFFF; }
    .pro-title { font-size: 42px; font-weight: 900; background: -webkit-linear-gradient(45deg, #00FFD1, #FFD700); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; text-transform: uppercase; margin-bottom: 20px;}
    .msg { color: #00FFD1; font-family: 'Courier New', monospace; font-size: 14px; margin-bottom: 8px; border-left: 3px solid #FFD700; padding-left: 12px; }
    .stButton>button { width: 100%; background: linear-gradient(45deg, #00FFD1, #0088ff); color: white; border: none; font-weight: 900; height: 55px; border-radius: 12px; font-size: 18px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V136 ✂️🎵</div>', unsafe_allow_html=True)

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

def extraer_kw_dinamico(texto, index):
    t = texto.lower()
    if any(x in t for x in ["dinero", "banco", "saldo"]): return "luxury money gold"
    if any(x in t for x in ["gym", "fuerte", "entrenar"]): return "fitness training dark"
    if any(x in t for x in ["coche", "ferrari", "velocidad"]): return "supercar cinematic"
    if any(x in t for x in ["despertar", "mañana", "luz"]): return "sunrise nature motivation"
    fallbacks = ["success luxury", "millionaire lifestyle", "modern mansion", "rolex watch", "office skyscraper"]
    return fallbacks[index % len(fallbacks)]

def preparar():
    if os.path.exists("taller"): shutil.rmtree("taller")
    os.makedirs("taller", exist_ok=True)
    subprocess.run("pkill ffmpeg", shell=True)

tema = st.text_input("🧠 Tema del vídeo:", placeholder="Ej: Hábitos de poder")
voz = st.selectbox("🎙️ Voz:", ["es-MX-JorgeNeural", "es-ES-AlvaroNeural"])

if st.button("🚀 CREAR VÍDEO (MÚSICA RECORTADA)"):
    if not tema: st.error("⚠️ Escribe un tema")
    else:
        preparar()
        log = st.container()
        with log:
            st.markdown('<div class="msg">📝 IA redactando y bajando música...</div>', unsafe_allow_html=True)
            p = f"Escribe UNICAMENTE el texto para TikTok sobre {tema}. Sin notas. Solo español fluido. Maximo 90 palabras."
            try:
                g_raw = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote(p)}", timeout=20).text
                guion = re.sub(r'tool_calls|recalc|words|assistant|reasoning|thought|count|slightly|above|remove|piece|adjust', '', g_raw, flags=re.I)
                guion = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ.,! ]', '', guion).strip()
            except: guion = "La disciplina vence al talento siempre."

            audio = "taller/audio.mp3"
            subprocess.run(f'edge-tts --voice {voz} --rate=+0% --text "{guion}" --write-media "{audio}"', shell=True)
            
            musica = "taller/bg.mp3"
            r_m = requests.get("https://www.chosic.com/wp-content/uploads/2021/07/Inspirational-Cinematic-Background.mp3")
            with open(musica, "wb") as f: f.write(r_m.content)

            try: dur = float(subprocess.check_output(f'ffprobe -i "{audio}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
            except: dur = 20.0

            n_clips = min(math.ceil(dur / 3.2), 15)
            t_clip = dur / n_clips
            clips = []
            palabras = guion.split()
            chunk = max(len(palabras) // n_clips, 1)
            ultima = None

            for i in range(n_clips):
                txt = " ".join(palabras[i*chunk:(i+1)*chunk])
                kw = extraer_kw_dinamico(txt, i)
                st.markdown(f'<div class="msg">🎥 Escena {i+1}/{n_clips}: "{kw.upper()}"...</div>', unsafe_allow_html=True)
                raw, vid = f"taller/r_{i}.mp4", f"taller/v_{i}.mp4"
                exito = False
                try:
                    h = {"Authorization": PEXELS_API}
                    url = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(kw)}&orientation=portrait&per_page=3"
                    r_p = requests.get(url, headers=h, timeout=12).json()
                    if r_p.get('videos'):
                        v_link = r_p['videos'][0]['video_files'][0]['link']
                        with open(raw, 'wb') as f: f.write(requests.get(v_link).content)
                        exito = True
                except: pass

                if exito:
                    vf = "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1,format=yuv420p"
                    subprocess.run(f'ffmpeg -y -stream_loop -1 -i "{raw}" -t {t_clip} -vf "{vf}" -c:v libx264 -preset ultrafast -r 24 "{vid}"', shell=True)
                else:
                    if ultima: subprocess.run(f'cp "{ultima}" "{vid}"', shell=True)
                    else: subprocess.run(f'ffmpeg -y -f lavfi -i color=c=#111827:s=720x1280:d={t_clip}:r=24 -c:v libx264 -preset ultrafast "{vid}"', shell=True)
                
                clips.append(os.path.abspath(vid).replace('\\', '/'))
                ultima = vid
                if os.path.exists(raw): os.remove(raw)

            st.markdown('<div class="msg">🎬 Recortando canción y ensamblando...</div>', unsafe_allow_html=True)
            with open("taller/lista.txt", "w") as f:
                for c in clips: f.write(f"file '{c}'\n")
            
            mudo = "taller/mudo.mp4"
            subprocess.run(f'ffmpeg -y -f concat -safe 0 -i taller/lista.txt -c copy "{mudo}"', shell=True)
            
            # SUBTÍTULOS V58
            pal_sub = re.sub(r'[^\w\s]', '', guion.upper()).split()
            chunks = [pal_sub[j:j+2] for j in range(0, len(pal_sub), 2)]
            t_ch = dur / max(len(chunks), 1)
            f_s = f"fontfile='{f_abs}':" if os.path.exists(f_abs) else ""
            subs = []
            for j, p in enumerate(chunks):
                ts, te = j * t_ch, (j + 1) * t_ch
                subs.append(f"drawtext=text='{' '.join(p)}':fontcolor=yellow:fontsize=70:{f_s}borderw=5:bordercolor=black:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{ts},{te})'")
            
            with open("taller/s.txt", "w") as f: f.write(",\n".join(subs))
            
            # --- MEZCLA FINAL: Recortamos música al tiempo exacto (duration=first) y añadimos fade out ---
            final = "taller/master.mp4"
            fade_start = max(0, dur - 2)
            cmd = f'ffmpeg -y -i "{mudo}" -i "{audio}" -i "{musica}" -filter_complex "[2:a]volume=0.15,afade=t=out:st={fade_start}:d=2[bg];[1:a][bg]amix=inputs=2:duration=first[a];[0:v]filter_complex_script=taller/s.txt[v]" -map "[v]" -map "[a]" -c:v libx264 -preset ultrafast -t {dur} "{final}"'
            subprocess.run(cmd, shell=True)
            
            if os.path.exists(final):
                st.markdown('<div class="info-card">🏆 VÍDEO CON MÚSICA SINCRONIZADA COMPLETADO</div>', unsafe_allow_html=True)
                with open(final, "rb") as f: st.video(f.read())
