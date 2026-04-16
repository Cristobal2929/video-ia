import streamlit as st
import os, time, subprocess, re, urllib.parse, shutil, math, random, gc
import requests

st.set_page_config(page_title="Fénix Studio V98", layout="centered")

st.markdown("""
<style>
    .stApp { background: #000000; color: #FFFFFF; }
    .pro-title { font-size: 38px; font-weight: 900; background: -webkit-linear-gradient(45deg, #FFD700, #00FFD1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; text-transform: uppercase;}
    .msg { color: #00FFD1; font-family: monospace; font-size: 14px; margin-bottom: 5px; border-left: 3px solid #FFD700; padding-left: 10px; }
    .stButton>button { width: 100%; background: linear-gradient(45deg, #00FFD1, #0088ff); color: white; border: none; font-weight: bold; border-radius: 10px; height: 50px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX STUDIO V98 🎥</div>', unsafe_allow_html=True)

# Fuente robusta del sistema
f_abs = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def preparar():
    if os.path.exists("taller"): shutil.rmtree("taller")
    os.makedirs("taller", exist_ok=True)
    subprocess.run("pkill ffmpeg", shell=True)

tema = st.text_input("🧠 Tema del vídeo:", placeholder="Ej: El secreto de la riqueza")
dur_opcion = st.selectbox("⏱️ Cantidad de Escenas:", ["Corto (4 escenas)", "Medio (8 escenas)", "Largo (12 escenas)"])

if st.button("🚀 CREAR VÍDEO (CON TRUCO DE ESPERA)"):
    if not tema:
        st.error("Escribe un tema")
    else:
        preparar()
        n_escenas = 4 if "Corto" in dur_opcion else (8 if "Medio" in dur_opcion else 12)
        
        # 1. Guion IA
        st.markdown('<div class="msg">📝 Redactando guion único...</div>', unsafe_allow_html=True)
        guion_url = f"https://text.pollinations.ai/{urllib.parse.quote('Guion TikTok '+tema+'. Solo texto del locutor, 70 palabras.')}"
        guion = requests.get(guion_url).text
        guion = re.sub(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ.,! ]', '', guion).strip()
        
        # 2. Audio Blindado
        st.markdown('<div class="msg">🎙️ Grabando voz...</div>', unsafe_allow_html=True)
        audio = "taller/a.mp3"
        subprocess.run(f'edge-tts --voice es-MX-JorgeNeural --text "{guion}" --write-media "{audio}"', shell=True)
        
        dur = 15.0
        try: dur = float(subprocess.check_output(f'ffprobe -i "{audio}" -show_entries format=duration -v quiet -of csv="p=0"', shell=True))
        except: pass
        
        # 3. Escenas con el TRUCO DE ESPERA
        clips = []
        words = guion.split()
        t_escena = dur / n_escenas
        planos = ["cinematic close up", "dramatic lighting", "wide shot luxury", "hyperrealistic details"]

        for i in range(n_escenas):
            # EL TRUCO DE DAYRON: Esperar 4 segundos antes de cada imagen
            st.markdown(f'<div class="msg">🎬 Escena {i+1}: Esperando seguridad (4s)...</div>', unsafe_allow_html=True)
            time.sleep(4.0)
            
            kw = words[min(i*5, len(words)-1)]
            img = f"taller/i_{i}.jpg"
            vid = f"taller/v_{i}.mp4"
            
            prompt = f"{kw} {tema}, {random.choice(planos)}, 8k, hyperrealistic, masterpiece, cinematic"
            url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=720&height=1280&nologo=true&seed={random.randint(1,9999)}"
            
            exito = False
            try:
                r = requests.get(url, timeout=25)
                if r.status_code == 200:
                    with open(img, 'wb') as f: f.write(r.content)
                    z_fx = random.choice(["1.0+0.001*on", "1.2-0.001*on"])
                    vf = f"scale=800:1422,zoompan=z='{z_fx}':d={int(t_escena*24)}:s=720x1280:fps=24,format=yuv420p"
                    subprocess.run(f'ffmpeg -y -loop 1 -i "{img}" -vf "{vf}" -t {t_escena} -c:v libx264 -preset ultrafast -crf 28 "{vid}"', shell=True)
                    if os.path.exists(vid): 
                        clips.append(f"v_{i}.mp4")
                        exito = True
            except: pass
            
            if not exito:
                st.write("⚠️ Fallo de servidor, clonando escena anterior...")
                if i > 0: clips.append(clips[-1])
            
            if os.path.exists(img): os.remove(img)
            gc.collect()

        # 4. Unión y Master Final
        st.markdown('<div class="msg">🎞️ Uniendo piezas finales...</div>', unsafe_allow_html=True)
        with open("taller/l.txt", "w") as f:
            for c in clips: f.write(f"file '{c}'\n")
        
        mudo = "taller/m.mp4"
        subprocess.run(f'ffmpeg -y -f concat -safe 0 -i taller/l.txt -c copy "{mudo}"', shell=True)
        
        final = "taller/final.mp4"
        # Subtítulos Amarillos Grandes (Estilo V58)
        txt_f = f"drawtext=text='{guion[:45].upper()}...':fontcolor=yellow:fontsize=60:fontfile='{f_abs}':x=(w-tw)/2:y=(h-th)/2:borderw=4:bordercolor=black"
        subprocess.run(f'ffmpeg -y -i "{mudo}" -i "{audio}" -vf "{txt_f}" -c:v libx264 -preset fast -t {dur} "{final}"', shell=True)
        
        if os.path.exists(final):
            st.markdown('<div style="text-align:center; padding:10px; color:#00FFD1;">✅ VÍDEO COMPLETADO CON ÉXITO</div>', unsafe_allow_html=True)
            st.video(final)
            st.balloons()
