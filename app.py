import streamlit as st
import os, time, random, subprocess, re, requests

st.set_page_config(page_title="Fénix Viral Studio", layout="centered")
st.markdown("<style>.stApp {background: #0d1117; color: white;}</style>", unsafe_allow_html=True)

def obtener_historia_bomba(tema):
    t = tema.lower()
    # LÓGICA DE TERROR REAL
    if "terror" in t or "miedo" in t or "paranormal" in t:
        return {
            "guion": "HAY ALGO DEBAJO DE TU CAMA QUE SOLO APARECE CUANDO CIERRAS LOS OJOS. NO ES TU IMAGINACION ES UNA SOMBRA QUE SE ALIMENTA DE TU MIEDO.",
            "keys": ["scary monster", "dark room", "creepy shadow", "scared person"]
        }
    # LÓGICA DE COCHES
    elif "coche" in t or "motor" in t:
        return {
            "guion": "ESTE MOTOR FUE PROHIBIDO POR SER DEMASIADO RAPIDO PARA LAS CALLES. SI ACELERAS A FONDO EL TIEMPO PARECE DETENERSE POR COMPLETO.",
            "keys": ["fast car racing", "engine engine", "speedometer", "luxury sport car"]
        }
    # LÓGICA DE ESPACIO
    elif "espacio" in t or "nasa" in t or "planeta" in t:
        return {
            "guion": "EL ESPACIO NO ESTA VACIO. HAY SONIDOS QUE LA NASA NO PUEDE EXPLICAR Y QUE PARECEN GRITOS PROVENIENTES DE AGUJEROS NEGROS.",
            "keys": ["outer space", "black hole", "galaxy", "astronaut"]
        }
    # GENÉRICO INTELIGENTE
    return {
        "guion": f"LO QUE NADIE TE CUENTA SOBRE {t.upper()} ES QUE ESCONDE UN SECRETO QUE PODRIA CAMBIAR TU VIDA. PRESTATE ATENCION AL FINAL.",
        "keys": [t, "secret mystery", "detective", "explosion"]
    }

st.title("🦅 Fénix Viral Studio")

with st.sidebar:
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.selectbox("🎨 Color Texto", ["yellow", "white", "cyan"])

if user_input := st.chat_input("Dime el tema (Terror, Coches, Espacio...)"):
    with st.status("🚀 Sincronizando imágenes y guion...", expanded=True) as status:
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.mp3 t.vtt outro.mp4", shell=True)
        
        info = obtener_historia_bomba(user_input)
        guion = info["guion"]
        keywords = info["keys"]
        v_final = f"output/v_{int(time.time())}.mp4"
        
        # 1. Voz
        status.write("🎙️ Grabando voz...")
        subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --text "{guion}" --write-media "t.mp3"', shell=True)
        dur_audio = float(subprocess.check_output("ffprobe -i t.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True))
        
        # 2. Clips (Uno por cada palabra clave específica)
        processed_clips = []
        for i, key in enumerate(keywords):
            status.write(f"🎞️ Buscando clip real de: {key}...")
            url = f"https://api.pexels.com/videos/search?query={key}&per_page=1&orientation=portrait"
            res = requests.get(url, headers={"Authorization": pexels_key.strip()}).json()
            if res.get('videos'):
                v_url = res['videos'][0]['video_files'][0]['link']
                with open(f"clip_{i}.mp4", 'wb') as f: f.write(requests.get(v_url).content)
                subprocess.run(f'ffmpeg -y -i "clip_{i}.mp4" -vf "scale=480:854:force_original_aspect_ratio=increase,crop=480:854,fps=25" -an -c:v libx264 -preset ultrafast "p_{i}.mp4"', shell=True)
                processed_clips.append(f"p_{i}.mp4")
        
        # Sello Final
        subprocess.run('ffmpeg -y -f lavfi -i color=c=black:s=480x854:d=2:r=25 -vf "drawtext=text=\'FENIX STUDIO 🦅\':fontcolor=white:fontsize=40:x=(w-tw)/2:y=(h-th)/2" -c:v libx264 -preset ultrafast outro.mp4', shell=True)
        
        with open("lista.txt", "w") as f:
            for p in processed_clips: f.write(f"file '{p}'\n")
            f.write("file 'outro.mp4'\n")
        subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)

        # 3. SUBTÍTULOS DINÁMICOS
        status.write("✨ Dibujando subtítulos pro...")
        palabras = guion.split()
        segmentos = [" ".join(palabras[i:i+2]) for i in range(0, len(palabras), 2)]
        dur_seg = dur_audio / len(segmentos)
        
        filter_complex = ""
        for i, seg in enumerate(segmentos):
            start = i * dur_seg
            end = (i + 1) * dur_seg
            filter_complex += f"drawtext=text='{seg}':fontcolor={color_sub}:fontsize=36:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:borderw=4:bordercolor=black:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{start},{end})',"
        
        filter_complex = filter_complex.rstrip(',')
        
        cmd = f'ffmpeg -y -i base.mp4 -i t.mp3 -vf "{filter_complex}" -c:v libx264 -preset ultrafast -c:a aac -map 0:v:0 -map 1:a:0 -shortest "{v_final}"'
        subprocess.run(cmd, shell=True)
        
        if os.path.exists(v_final):
            st.video(v_final)
            st.success("🔥 ¡VÍDEO COHERENTE TERMINADO!")
