import streamlit as st
import os, time, random, subprocess, re, requests

st.set_page_config(page_title="Fénix AI Studio", layout="centered")
st.markdown("<style>.stApp {background: #0d1117; color: white;}</style>", unsafe_allow_html=True)

# --- CONEXIÓN CON IA PARA GUIONES ---
def obtener_guion_ia(tema):
    try:
        # Usamos una API de texto gratuita para generar la historia
        prompt = f"Escribe una historia viral muy corta (máximo 40 palabras) de {tema} que enganche desde la primera frase. Todo en MAYÚSCULAS y sin puntos ni comas raros."
        # Intentamos usar un servicio de inferencia gratuito
        url = f"https://sentence.fineshopdesign.com/api/ai?prompt={prompt}"
        res = requests.get(url, timeout=10).json()
        guion = res.get("reply", "").upper()
        if len(guion) < 10: raise Exception("IA lenta")
        return guion
    except:
        # Guion de emergencia si la IA falla
        return f"SABIAS QUE EL MUNDO DE {tema.upper()} ESCONDE UN SECRETO QUE PODRIA CAMBIAR TU VIDA PARA SIEMPRE PRESTA ATENCION AL FINAL."

st.title("🦅 Fénix AI: Guiones Infinitos")

with st.sidebar:
    st.header("Ajustes")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.selectbox("🎨 Color Texto", ["yellow", "white", "cyan"])

if user_input := st.chat_input("¿De qué quieres el vídeo hoy? (La IA creará la historia)"):
    with st.status("🧠 La IA está redactando tu historia viral...", expanded=True) as status:
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.mp3 music.mp3 final.mp4", shell=True)
        
        # 1. La IA escribe el guion
        guion = obtener_guion_ia(user_input)
        status.write(f"✍️ Guion generado: {guion[:50]}...")
        
        # 2. Voz y Música
        subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --text "{guion}" --write-media "t.mp3"', shell=True)
        dur_audio = float(subprocess.check_output("ffprobe -i t.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True))
        
        # Música de fondo
        m_url = "https://www.bensound.com/bensound-music/bensound-creepy.mp3" if "terror" in user_input.lower() else "https://www.bensound.com/bensound-music/bensound-evolution.mp3"
        subprocess.run(f'curl -L {m_url} -o music.mp3', shell=True)

        # 3. Clips con Zoom Dinámico
        # Sacamos palabras clave del guion generado por la IA
        palabras_clave = user_input.split() + ["mystery", "dark", "cinematic"]
        processed_clips = []
        for i in range(4):
            key = random.choice(palabras_clave)
            status.write(f"🎞️ Buscando visual para: {key}...")
            url = f"https://api.pexels.com/videos/search?query={key}&per_page=1&orientation=portrait"
            res = requests.get(url, headers={"Authorization": pexels_key.strip()}).json()
            if res.get('videos'):
                v_url = res['videos'][0]['video_files'][0]['link']
                with open(f"clip_{i}.mp4", 'wb') as f: f.write(requests.get(v_url).content)
                subprocess.run(f'ffmpeg -y -i "clip_{i}.mp4" -vf "scale=8000:-1,zoompan=z=\'min(zoom+0.0015,1.5)\':d=125:x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):s=480x854,fps=25" -an -c:v libx264 -preset ultrafast -t {dur_audio/4} "p_{i}.mp4"', shell=True)
                processed_clips.append(f"p_{i}.mp4")

        # 4. Unión y Subtítulos
        with open("lista.txt", "w") as f:
            for p in processed_clips: f.write(f"file '{p}'\n")
        subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)

        status.write("✨ Mezclando todo...")
        palabras = guion.split()
        segmentos = [" ".join(palabras[i:i+2]) for i in range(0, len(palabras), 2)]
        dur_seg = dur_audio / len(segmentos)
        
        filter_complex = ""
        for i, seg in enumerate(segmentos):
            start = i * dur_seg
            end = (i + 1) * dur_seg
            filter_complex += f"drawtext=text='{seg}':fontcolor={color_sub}:fontsize=40:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:borderw=4:bordercolor=black:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{start},{end})',"
        
        v_final = f"output/v_{int(time.time())}.mp4"
        cmd = (
            f'ffmpeg -y -i base.mp4 -i t.mp3 -i music.mp3 -filter_complex '
            f'"[1:a]volume=2.5[v];[2:a]volume=0.2,afade=t=out:st={dur_audio-2}:d=2[m];[v][m]amix=inputs=2:duration=first" '
            f'-vf "{filter_complex.rstrip(",")}" -c:v libx264 -preset ultrafast -c:a aac -shortest "{v_final}"'
        )
        subprocess.run(cmd, shell=True)
        
        if os.path.exists(v_final):
            st.video(v_final)
            st.success("🔥 ¡VÍDEO CREADO POR IA!")
