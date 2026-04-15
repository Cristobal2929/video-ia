import streamlit as st
import os, time, random, subprocess, re, requests

st.set_page_config(page_title="Fénix Paso a Paso", layout="centered")
st.markdown("<style>.stApp {background: #0d1117; color: white;}</style>", unsafe_allow_html=True)

def buscar_vids(query, api_key, status):
    status.write("🎞️ Etapa 2: Buscando escenas en Pexels...")
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=6&orientation=portrait"
    desc = []
    try:
        res = requests.get(url, headers={"Authorization": api_key.strip()}, timeout=10).json()
        vids = res.get('videos', [])
        for i, v in enumerate(vids):
            status.write(f"📥 Descargando clip {i+1} de {len(vids)}...")
            with open(f"clip_{i}.mp4", 'wb') as f: f.write(requests.get(v['video_files'][0]['link']).content)
            desc.append(f"clip_{i}.mp4")
        return desc
    except: return []

st.title("🦅 Fénix Studio: Edición por Etapas")

with st.sidebar:
    st.header("Ajustes")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.color_picker("🎨 Color Sub", "#FFFF00")
    hc = color_sub.lstrip('#')
    ass_col = f"&H00{hc[4:6]}{hc[2:4]}{hc[0:2]}"

if user_input := st.chat_input("Dime el nicho (Terror, Humor, Coches...)"):
    progress = st.progress(0)
    status_text = st.empty()
    
    with st.container():
        # Limpieza inicial
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.* outro.mp4 final.mp4 temp_v.mp4 bg.mp3", shell=True)
        
        # PASO 1: AUDIO Y GUION
        status_text.write("🎙️ PASO 1: Generando narración y subtítulos...")
        guion = f"El mundo de {user_input} es impresionante. Prepárate para descubrir detalles que te volarán la cabeza. Esto es Fénix Studio."
        subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --text "{guion}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
        subprocess.run("ffmpeg -y -i t.vtt t.srt", shell=True)
        dur = float(subprocess.check_output("ffprobe -i t.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True))
        progress.progress(25)

        # PASO 2: VÍDEOS
        clips = buscar_vids(user_input, pexels_key, status_text)
        progress.progress(50)

        if clips:
            # PASO 3: PROCESADO INDIVIDUAL
            status_text.write("✂️ PASO 3: Formateando clips individualmente...")
            for i, c in enumerate(clips):
                subprocess.run(f'ffmpeg -y -i "{c}" -vf "scale=480:854:force_original_aspect_ratio=increase,crop=480:854,fps=25" -an -c:v libx264 -preset ultrafast "p_{i}.mp4"', shell=True)
            
            # Sello Final
            subprocess.run('ffmpeg -y -f lavfi -i color=c=black:s=480x854:d=2:r=25 -vf "drawtext=text=\'FENIX STUDIO 🦅\':fontcolor=white:fontsize=40:x=(w-tw)/2:y=(h-th)/2" -c:v libx264 -preset ultrafast outro.mp4', shell=True)
            
            with open("lista.txt", "w") as f:
                for i in range(len(clips)): f.write(f"file 'p_{i}.mp4'\n")
                f.write("file 'outro.mp4'\n")
            subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy temp_v.mp4', shell=True)
            progress.progress(75)

            # PASO 4: MEZCLA FINAL
            status_text.write("🧪 PASO 4: Mezcla maestra de audio y vídeo...")
            v_final = f"output/v_{int(time.time())}.mp4"
            est = f"Fontname=Impact,FontSize=32,PrimaryColour={ass_col},Outline=4,Alignment=2,MarginV=150"
            
            # Descargamos música rápida
            m_url = "https://www.bensound.com/bensound-music/bensound-evolution.mp3"
            requests.get(m_url, timeout=5) # Solo para asegurar conexión
            subprocess.run(f'curl -L {m_url} -o bg.mp3', shell=True)

            cmd = f'ffmpeg -y -i temp_v.mp4 -i t.mp3 -i bg.mp3 -filter_complex "[1:a]volume=2.5[v];[2:a]volume=0.15,afade=t=out:st={dur}:d=2[m];[v][m]amix=inputs=2:duration=first" -vf "subtitles=t.srt:force_style=\'{est}\'" -c:v libx264 -preset ultrafast -shortest -c:a aac "{v_final}"'
            subprocess.run(cmd, shell=True)
            
            if os.path.exists(v_final):
                progress.progress(100)
                status_text.write("🔥 ¡Producción finalizada!")
                st.video(v_final)
                st.balloons()
