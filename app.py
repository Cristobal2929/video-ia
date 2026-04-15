import streamlit as st
import os, time, random, subprocess, re, requests

st.set_page_config(page_title="Fénix Sub Fix", layout="centered")
st.markdown("<style>.stApp {background: #0d1117; color: white;}</style>", unsafe_allow_html=True)

# Función para limpiar el texto y que los subs no se corten
def limpiar_vtt_a_srt(vtt_file, srt_file):
    with open(vtt_file, 'r', encoding='utf-8') as f:
        content = f.read()
    # Eliminar cabecera WEBVTT
    content = re.sub(r'WEBVTT\n\n', '', content)
    # Cambiar puntos por comas en tiempos
    content = content.replace('.', ',')
    with open(srt_file, 'w', encoding='utf-8') as f:
        f.write(content)

st.title("🦅 Fénix: Corrección Total de Subs")

with st.sidebar:
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.color_picker("🎨 Color Sub", "#FFFF00")
    hc = color_sub.lstrip('#')
    ass_col = f"&H00{hc[4:6]}{hc[2:4]}{hc[0:2]}"

if user_input := st.chat_input("Nicho..."):
    st_text = st.empty()
    subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.* outro.mp4 temp.mp4 final.mp4 lista.txt", shell=True)
    
    # PASO 1: AUDIO
    st_text.write("🎙️ Generando audio y tiempos...")
    guion = f"Mira este video sobre {user_input}. Es algo que no te puedes perder. Presta mucha atención hasta el final porque lo mejor está por llegar ahora mismo."
    subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --text "{guion}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
    limpiar_vtt_a_srt("t.vtt", "t.srt")
    
    # PASO 2: VÍDEOS
    url = f"https://api.pexels.com/videos/search?query={user_input}&per_page=4&orientation=portrait"
    res = requests.get(url, headers={"Authorization": pexels_key.strip()}).json()
    v_list = res.get('videos', [])
    for i, v in enumerate(v_list):
        with open(f"clip_{i}.mp4", 'wb') as f: f.write(requests.get(v['video_files'][0]['link']).content)

    # PASO 3: PROCESADO CLIP A CLIP
    for i in range(len(v_list)):
        st_text.write(f"✂️ Formateando escena {i+1}...")
        subprocess.run(f'ffmpeg -y -i "clip_{i}.mp4" -vf "scale=480:854:force_original_aspect_ratio=increase,crop=480:854,fps=25" -an -c:v libx264 -preset ultrafast "p_{i}.mp4"', shell=True)
    
    # Outro largo (5 segundos) para que los subs tengan "pista de aterrizaje"
    subprocess.run('ffmpeg -y -f lavfi -i color=c=black:s=480x854:d=5:r=25 -vf "drawtext=text=\'FENIX STUDIO\':fontcolor=white:fontsize=40:x=(w-tw)/2:y=(h-th)/2" -c:v libx264 -preset ultrafast outro.mp4', shell=True)
    
    with open("lista.txt", "w") as f:
        for i in range(len(v_list)): f.write(f"file 'p_{i}.mp4'\n")
        f.write("file 'outro.mp4'\n")
    subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)

    # PASO 4: MEZCLA FINAL (EL CAMBIO CLAVE)
    st_text.write("🧪 Aplicando subtítulos dinámicos...")
    v_final = f"output/v_{int(time.time())}.mp4"
    
    # Estilo: Reducimos un poco el tamaño para que no se salga de los márgenes
    est = f"Fontname=Impact,FontSize=26,PrimaryColour={ass_col},Outline=3,BorderStyle=1,Alignment=2,MarginV=160"
    
    # Usamos -fflags +genpts para reconstruir los tiempos del vídeo y que no se corten los subs
    cmd = (
        f'ffmpeg -y -fflags +genpts -i base.mp4 -i t.mp3 -vf "subtitles=t.srt:force_style=\'{est}\'" '
        f'-c:v libx264 -preset ultrafast -c:a aac -af "volume=2.5" '
        f'-map 0:v:0 -map 1:a:0 -shortest "{v_final}"'
    )
    subprocess.run(cmd, shell=True)
    
    if os.path.exists(v_final):
        st.video(v_final)
        st.success("✅ ¡Subtítulos corregidos!")
