import streamlit as st
import os, time, random, subprocess, re, requests

st.set_page_config(page_title="Fénix Master Pro", layout="centered")
st.markdown("<style>.stApp {background: #0d1117; color: white;}</style>", unsafe_allow_html=True)

st.title("🦅 Fénix Studio: Subtítulos Fix")

with st.sidebar:
    st.header("Ajustes")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.color_picker("🎨 Color Sub", "#FFFF00")
    hc = color_sub.lstrip('#')
    ass_col = f"&H00{hc[4:6]}{hc[2:4]}{hc[0:2]}"

if user_input := st.chat_input("Nicho..."):
    prog = st.progress(0)
    st_text = st.empty()
    
    subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.* outro.mp4 temp_v.mp4 final_v.mp4 lista.txt", shell=True)
    
    # --- PASO 1: AUDIO ---
    st_text.write("🎙️ PASO 1: Generando voz...")
    guion = f"Descubre el increíble mundo de {user_input}. Una experiencia única que solo verás aquí en Fénix Studio. Prepárate para lo mejor porque esto acaba de empezar."
    subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --text "{guion}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
    # Convertimos VTT a SRT asegurando que no haya caracteres raros
    subprocess.run("ffmpeg -y -i t.vtt t.srt", shell=True)
    # Sacamos la duración exacta del audio
    dur_audio = float(subprocess.check_output("ffprobe -i t.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True))
    prog.progress(20)

    # --- PASO 2: DESCARGA ---
    st_text.write("🎞️ PASO 2: Descargando escenas...")
    url = f"https://api.pexels.com/videos/search?query={user_input}&per_page=4&orientation=portrait"
    try:
        res = requests.get(url, headers={"Authorization": pexels_key.strip()}, timeout=10).json()
        v_list = res.get('videos', [])
        for i, v in enumerate(v_list):
            with open(f"clip_{i}.mp4", 'wb') as f: f.write(requests.get(v['video_files'][0]['link']).content)
        prog.progress(40)

        # --- PASO 3: PROCESADO ---
        st_text.write("✂️ PASO 3: Formateando escenas...")
        for i in range(len(v_list)):
            subprocess.run(f'ffmpeg -y -i "clip_{i}.mp4" -vf "scale=480:854:force_original_aspect_ratio=increase,crop=480:854,fps=25" -an -c:v libx264 -preset ultrafast "p_{i}.mp4"', shell=True)
        
        # Outro un pelín más largo para que no corte la última palabra
        subprocess.run('ffmpeg -y -f lavfi -i color=c=black:s=480x854:d=3:r=25 -vf "drawtext=text=\'FENIX STUDIO 🦅\':fontcolor=white:fontsize=40:x=(w-tw)/2:y=(h-th)/2" -c:v libx264 -preset ultrafast outro.mp4', shell=True)
        
        with open("lista.txt", "w") as f:
            for i in range(len(v_list)): f.write(f"file 'p_{i}.mp4'\n")
            f.write("file 'outro.mp4'\n")
        
        subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)
        prog.progress(70)

        # --- PASO 4: MEZCLA FINAL (EL FIX) ---
        st_text.write("🧪 PASO 4: Aplicando subtítulos completos...")
        v_final = f"output/v_{int(time.time())}.mp4"
        
        # Estilo de subtítulos un poco más pequeño (28 en vez de 32) para que quepan bien
        est = f"Fontname=Impact,FontSize=28,PrimaryColour={ass_col},Outline=3,Alignment=2,MarginV=140"
        
        # El truco: Usamos -filter_complex para asegurar que el audio y el vídeo se mezclan sin cortes
        # Forzamos la duración con -shortest pero le damos un pequeño margen al vídeo base
        cmd = (
            f'ffmpeg -y -i base.mp4 -i t.mp3 -vf "subtitles=t.srt:force_style=\'{est}\'" '
            f'-c:v libx264 -preset ultrafast -crf 23 '
            f'-c:a aac -b:a 128k -af "volume=2.5" '
            f'-map 0:v:0 -map 1:a:0 -shortest "{v_final}"'
        )
        subprocess.run(cmd, shell=True)
        
        if os.path.exists(v_final):
            prog.progress(100)
            st_text.write("✨ ¡Vídeo con subtítulos completos!")
            st.video(v_final)
            st.balloons()
    except Exception as e:
        st.error(f"Error: {e}")
