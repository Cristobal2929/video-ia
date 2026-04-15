import streamlit as st
import os, time, random, subprocess, re, requests

st.set_page_config(page_title="Fénix AI Ultra", layout="centered")
st.markdown("<style>.stApp {background: #0d1117; color: white;}</style>", unsafe_allow_html=True)

def obtener_guion_ia(tema):
    try:
        prompt = f"HISTORIA CORTA DE {tema.upper()} PARA TIKTOK. MAXIMO 35 PALABRAS. ENGANCHE FUERTE AL PRINCIPIO. TODO MAYUSCULAS."
        url = f"https://sentence.fineshopdesign.com/api/ai?prompt={prompt}"
        res = requests.get(url, timeout=10).json()
        return res.get("reply", "").upper()
    except:
        return f"SABIAS QUE EL MUNDO DE {tema.upper()} ESCONDE UN SECRETO QUE PODRIA CAMBIAR TU VIDA. PRESTA ATENCION HASTA EL FINAL."

st.title("🦅 Fénix AI: Edición Segura")

with st.sidebar:
    st.header("Ajustes")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.selectbox("🎨 Color Texto", ["yellow", "white", "cyan"])

if user_input := st.chat_input("¿Qué tema grabamos hoy?"):
    with st.status("🧠 La IA está trabajando...", expanded=True) as status:
        # Limpieza profunda
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.mp3 music.mp3 final.mp4 temp_v.mp4 temp_a.mp4", shell=True)
        
        guion = obtener_guion_ia(user_input)
        status.write(f"✍️ Guion: {guion[:40]}...")
        
        # 1. AUDIO (Voz + Música)
        status.write("🎙️ Mezclando audio...")
        subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --text "{guion}" --write-media "t.mp3"', shell=True)
        dur = float(subprocess.check_output("ffprobe -i t.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True))
        
        m_url = "https://www.bensound.com/bensound-music/bensound-creepy.mp3" if "terror" in user_input.lower() else "https://www.bensound.com/bensound-music/bensound-evolution.mp3"
        subprocess.run(f'curl -L {m_url} -o music.mp3', shell=True)
        # Creamos el audio final mezclado primero (menos RAM)
        subprocess.run(f'ffmpeg -y -i t.mp3 -i music.mp3 -filter_complex "[0:a]volume=2.5[v];[1:a]volume=0.2,afade=t=out:st={dur-2}:d=2[m];[v][m]amix=inputs=2:duration=first" temp_a.mp3', shell=True)

        # 2. VÍDEOS (Clip a clip con Zoom)
        processed_clips = []
        keys = user_input.split() + ["cinematic", "mystery"]
        for i in range(3): # Reducimos a 3 clips para que la RAM aguante de sobra
            k = random.choice(keys)
            status.write(f"🎞️ Procesando clip {i+1}...")
            url = f"https://api.pexels.com/videos/search?query={k}&per_page=1&orientation=portrait"
            res = requests.get(url, headers={"Authorization": pexels_key.strip()}).json()
            if res.get('videos'):
                v_url = res['videos'][0]['video_files'][0]['link']
                with open(f"clip_{i}.mp4", 'wb') as f: f.write(requests.get(v_url).content)
                # Zoom simplificado para no petar
                subprocess.run(f'ffmpeg -y -i "clip_{i}.mp4" -vf "scale=1280:-1,zoompan=z=\'min(zoom+0.001,1.3)\':d=125:x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):s=480x854,fps=25" -an -c:v libx264 -preset ultrafast -t {dur/3 + 0.5} "p_{i}.mp4"', shell=True)
                processed_clips.append(f"p_{i}.mp4")

        # UNIÓN MUNDA
        with open("lista.txt", "w") as f:
            for p in processed_clips: f.write(f"file '{p}'\n")
        subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)

        # 3. SUBTÍTULOS (Directos al final)
        status.write("✨ Finalizando con subtítulos...")
        palabras = guion.split()
        segs = [" ".join(palabras[i:i+2]) for i in range(0, len(palabras), 2)]
        dur_s = dur / len(segs)
        
        filter_c = ""
        for i, s in enumerate(segs):
            start, end = i * dur_s, (i + 1) * dur_s
            filter_c += f"drawtext=text='{s}':fontcolor={color_sub}:fontsize=40:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:borderw=4:bordercolor=black:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{start},{end})',"
        
        v_final = f"output/v_{int(time.time())}.mp4"
        # Mezcla final limpia
        cmd = f'ffmpeg -y -i base.mp4 -i temp_a.mp3 -vf "{filter_c.rstrip(",")}" -c:v libx264 -preset ultrafast -shortest "{v_final}"'
        subprocess.run(cmd, shell=True)
        
        if os.path.exists(v_final):
            st.video(v_final)
            st.success("🔥 ¡VÍDEO TERMINADO SIN FALLOS!")
