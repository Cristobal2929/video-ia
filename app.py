import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil, math, random, gc
import requests

st.set_page_config(page_title="Fénix Studio V97", layout="centered")

st.markdown("""
<style>
    .stApp { background: #000000; color: #FFFFFF; }
    .pro-title { font-size: 38px; font-weight: 900; background: -webkit-linear-gradient(45deg, #FFD700, #00FFD1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; text-transform: uppercase;}
    .msg { color: #94A3B8; font-family: monospace; font-size: 13px; margin-bottom: 5px; border-left: 2px solid #00FFD1; padding-left: 8px; }
    .stButton>button { width: 100%; background: linear-gradient(45deg, #00FFD1, #0088ff); color: white; border: none; font-weight: bold; border-radius: 8px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V97 🎥</div>', unsafe_allow_html=True)

# Fuente del sistema para no depender de descargas lentas
f_abs = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def preparar():
    if os.path.exists("taller"): shutil.rmtree("taller")
    os.makedirs("taller", exist_ok=True)
    subprocess.run("pkill ffmpeg", shell=True)

tema = st.text_input("🧠 Tema del vídeo:", placeholder="Ej: Las claves del éxito")
dur_opcion = st.selectbox("⏱️ Duración:", ["Corto (4 escenas)", "Largo (8 escenas)"])

if st.button("🚀 CREAR VÍDEO PROFESIONAL"):
    if not tema:
        st.error("Escribe un tema")
    else:
        preparar()
        n_escenas = 4 if "Corto" in dur_opcion else 8
        
        # 1. Guion IA
        guion_url = f"https://text.pollinations.ai/{urllib.parse.quote('Escribe un guion corto de TikTok sobre ' + tema + '. Solo el texto del locutor, 60 palabras.')}"
        guion = requests.get(guion_url).text
        guion = re.sub(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ.,! ]', '', guion).strip()
        
        # 2. Audio
        audio = "taller/a.mp3"
        subprocess.run(f'edge-tts --voice es-MX-JorgeNeural --text "{guion}" --write-media "{audio}"', shell=True)
        dur = 15.0
        try: dur = float(subprocess.check_output(f'ffprobe -i "{audio}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
        except: pass
        
        # 3. Escenas IA de Lujo
        clips = []
        words = guion.split()
        t_escena = dur / n_escenas
        planos = ["cinematic close up", "wide landscape shot", "dramatic lighting portrait", "aerial drone view"]

        for i in range(n_escenas):
            st.write(f"🎬 Generando Escena {i+1}...")
            kw = words[min(i*5, len(words)-1)]
            plano = random.choice(planos)
            img = f"taller/i_{i}.jpg"
            vid = f"taller/v_{i}.mp4"
            
            # Prompt de lujo para que se vea profesional
            prompt = f"{kw} {tema}, {plano}, hyperrealistic, 8k, cinematic, masterpiece"
            url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=540&height=960&nologo=true&seed={random.randint(1,9999)}"
            
            try:
                r = requests.get(url, timeout=20)
                with open(img, 'wb') as f: f.write(r.content)
                
                # Zoom aleatorio (unas veces entra, otras sale)
                z_fx = random.choice(["1.0+0.001*on", "1.2-0.001*on"])
                vf = f"scale=600:1066,zoompan=z='{z_fx}':d={int(t_escena*24)}:s=540x960:fps=24,format=yuv420p"
                subprocess.run(f'ffmpeg -y -loop 1 -i "{img}" -vf "{vf}" -t {t_escena} -c:v libx264 -preset ultrafast -crf 28 "{vid}"', shell=True)
                if os.path.exists(vid): clips.append(f"v_{i}.mp4")
            except:
                if i > 0: clips.append(clips[-1])
            
            if os.path.exists(img): os.remove(img)
            gc.collect()

        # 4. Unión y Master
        with open("taller/l.txt", "w") as f:
            for c in clips: f.write(f"file '{c}'\n")
        
        mudo = "taller/m.mp4"
        subprocess.run(f'ffmpeg -y -f concat -safe 0 -i taller/l.txt -c copy "{mudo}"', shell=True)
        
        final = "taller/final.mp4"
        # Subtítulos Amarillos potentes
        txt_f = f"drawtext=text='{guion[:40].upper()}...':fontcolor=yellow:fontsize=45:x=(w-tw)/2:y=(h-th)/2:borderw=3:bordercolor=black"
        subprocess.run(f'ffmpeg -y -i "{mudo}" -i "{audio}" -vf "{txt_f}" -c:v libx264 -preset fast -t {dur} "{final}"', shell=True)
        
        if os.path.exists(final):
            st.video(final)
            st.balloons()
