import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil, math, random, gc
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="Fénix Studio V141", layout="centered")
components.html("<script>if('wakeLock' in navigator){navigator.wakeLock.request('screen');}</script>", height=0)

st.markdown("""
<style>
    .stApp { background: #000000; color: #FFFFFF; }
    .pro-title { font-size: 42px; font-weight: 900; background: -webkit-linear-gradient(45deg, #00FFD1, #FFD700); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; text-transform: uppercase; margin-bottom: 20px;}
    .msg { color: #00FFD1; font-family: 'Courier New', monospace; font-size: 14px; margin-bottom: 8px; border-left: 3px solid #FFD700; padding-left: 12px; }
    .stButton>button { width: 100%; background: linear-gradient(45deg, #00FFD1, #0088ff); color: white; border: none; font-weight: 900; height: 55px; border-radius: 12px; font-size: 18px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V141 🛡️🎸</div>', unsafe_allow_html=True)

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

def limpiar_texto(t):
    t = re.sub(r'tool_calls|recalc|words|assistant|reasoning|thought|count|slightly|above|remove|piece|adjust|instruction|spanish|user|wants|script', '', t, flags=re.I)
    return re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ.,! ]', '', t).strip()

def preparar():
    if os.path.exists("taller"): shutil.rmtree("taller")
    os.makedirs("taller", exist_ok=True)
    subprocess.run("pkill ffmpeg", shell=True)

tema = st.text_input("🧠 Tema del vídeo:", placeholder="Ej: Éxito financiero")

if st.button("🚀 CREAR VÍDEO (SIN FALLOS DE MÚSICA)"):
    if not tema: st.error("Escribe un tema")
    else:
        preparar()
        log = st.container()
        with log:
            # 1. GUION Y VOZ
            st.markdown('<div class="msg">📝 Redactando guion fluido...</div>', unsafe_allow_html=True)
            p = f"Escribe UNICAMENTE el texto para TikTok sobre {tema}. Sin notas. Solo español. Maximo 80 palabras."
            try:
                g_raw = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote(p)}", timeout=15).text
                guion = limpiar_texto(g_raw)
            except: guion = "El éxito se basa en la disciplina constante."

            audio_voz = "taller/voz.mp3"
            subprocess.run(f'edge-tts --voice es-MX-JorgeNeural --text "{guion}" --write-media "{audio_voz}"', shell=True)
            
            try: dur = float(subprocess.check_output(f'ffprobe -i "{audio_voz}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
            except: dur = 15.0

            # 2. GENERACIÓN DE ESCENAS (LIGERO E IMAGEN)
            n_clips = min(math.ceil(dur / 4.0), 10)
            t_clip = dur / n_clips
            clips = []
            palabras = guion.split()
            chunk = max(len(palabras) // n_clips, 1)
            
            for i in range(n_clips):
                txt_part = " ".join(palabras[i*chunk:(i+1)*chunk])
                st.markdown(f'<div class="msg">📸 Escena {i+1}/{n_clips}: Generando imagen...</div>', unsafe_allow_html=True)
                img, vid = f"taller/i_{i}.jpg", f"taller/v_{i}.mp4"
                
                try:
                    url_ia = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(txt_part[:20]+' luxury cinematic 8k')}?width=720&height=1280&nologo=true"
                    with open(img, 'wb') as f: f.write(requests.get(url_ia, timeout=10).content)
                    z_fx = "zoompan=z='1.0+0.001*on':x='iw/4-(iw/4/d)*on'"
                    vf = f"scale=1280:2275,{z_fx}:d={int(t_clip*25)}:s=720x1280,format=yuv420p"
                    subprocess.run(f'ffmpeg -y -loop 1 -i "{img}" -vf "{vf}" -t {t_clip} -c:v libx264 -preset ultrafast "{vid}"', shell=True)
                except:
                    subprocess.run(f'ffmpeg -y -f lavfi -i color=c=#000000:s=720x1280:d={t_clip}:r=25 -c:v libx264 -preset ultrafast "{vid}"', shell=True)
                
                clips.append(os.path.abspath(vid))
                if os.path.exists(img): os.remove(img)

            # 3. ENSAMBLADO FINAL (VOZ PURA + VÍDEO)
            # Para que no pete, primero vamos a asegurar el video con voz.
            st.markdown('<div class="msg">🎬 Ensamblando máster final...</div>', unsafe_allow_html=True)
            with open("taller/lista.txt", "w") as f:
                for c in clips: f.write(f"file '{c}'\n")
            
            mudo = "taller/mudo.mp4"
            subprocess.run(f'ffmpeg -y -f concat -safe 0 -i taller/lista.txt -c copy "{mudo}"', shell=True)
            
            pal_sub = guion.upper().split()
            chunks = [pal_sub[j:j+2] for j in range(0, len(pal_sub), 2)]
            t_ch = dur / max(len(chunks), 1)
            f_s = f"fontfile='{f_abs}':" if os.path.exists(f_abs) else ""
            subs = [f"drawtext=text='{' '.join(p)}':fontcolor=yellow:fontsize=65:{f_s}borderw=4:bordercolor=black:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{j*t_ch},{(j+1)*t_ch})'" for j, p in enumerate(chunks)]
            with open("taller/s.txt", "w") as f: f.write(",\n".join(subs))
            
            final = "taller/master.mp4"
            # Comando ultra-ligero: Solo Video + Voz + Subtítulos
            subprocess.run(f'ffmpeg -y -i "{mudo}" -i "{audio_voz}" -filter_complex_script taller/s.txt -map 0:v -map 1:a -c:v libx264 -preset ultrafast -crf 30 -t {dur} "{final}"', shell=True)
            
            if os.path.exists(final):
                st.markdown('<div class="info-card">🏆 VÍDEO FINALIZADO SIN PETAR</div>', unsafe_allow_html=True)
                with open(final, "rb") as f: st.video(f.read())
