import streamlit as st
import os, time, random, subprocess, re, requests

st.set_page_config(page_title="Fénix Viral Studio", layout="centered")
st.markdown("<style>.stApp {background: #0d1117; color: white;}</style>", unsafe_allow_html=True)

def generar_guion_pro(tema):
    t = tema.lower()
    hooks = [f"¿Sabías esto sobre {tema}?", f"Lo que nadie te cuenta de {tema}."]
    cuerpo = f"El impacto de {tema} en nuestra vida es más grande de lo que imaginas. Detalles que lo hacen único y que nunca dejan de sorprendernos."
    cierre = "Síguenos para descubrir más."
    return f"{random.choice(hooks)} {cuerpo} {cierre}"

def generar_srt_dinamico(vtt_file, srt_file):
    with open(vtt_file, 'r', encoding='utf-8') as f: lines = f.readlines()
    srt_content, index = [], 1
    for i in range(len(lines)):
        if "-->" in lines[i]:
            tiempo = lines[i].replace('.', ',')
            if i+1 < len(lines):
                palabras = lines[i+1].strip().upper().split()
                for j in range(0, len(palabras), 2):
                    dupla = " ".join(palabras[j:j+2])
                    srt_content.append(f"{index}\n{tiempo}\n{dupla}\n")
                    index += 1
    with open(srt_file, 'w', encoding='utf-8') as f: f.write("\n".join(srt_content))

st.title("🦅 Fénix Studio: Subtítulos Pro")

with st.sidebar:
    st.header("Personalización")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.color_picker("🎨 Color Letra", "#FFFF00")
    hc = color_sub.lstrip('#')
    ass_col = f"&H00{hc[4:6]}{hc[2:4]}{hc[0:2]}"

if user_input := st.chat_input("¿Qué vídeo hacemos hoy?"):
    with st.status("🎬 Editando con subtítulos dinámicos...", expanded=True) as status:
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.* outro.mp4 final.mp4 temp_v.mp4", shell=True)
        
        guion = generar_guion_pro(user_input)
        v_final = f"output/v_{int(time.time())}.mp4"
        
        # 1. Audio y Tiempos
        subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --text "{guion}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
        generar_srt_dinamico("t.vtt", "t.srt")
        
        # 2. Clips
        url = f"https://api.pexels.com/videos/search?query={user_input}&per_page=5&orientation=portrait"
        res = requests.get(url, headers={"Authorization": pexels_key.strip()}).json()
        vids = res.get('videos', [])
        
        for i, v in enumerate(vids):
            with open(f"clip_{i}.mp4", 'wb') as f: f.write(requests.get(v['video_files'][0]['link']).content)
            subprocess.run(f'ffmpeg -y -i "clip_{i}.mp4" -vf "scale=480:854:force_original_aspect_ratio=increase,crop=480:854,fps=25" -an -c:v libx264 -preset ultrafast "p_{i}.mp4"', shell=True)
        
        # Outro
        subprocess.run('ffmpeg -y -f lavfi -i color=c=black:s=480x854:d=2:r=25 -vf "drawtext=text=\'FENIX STUDIO 🦅\':fontcolor=white:fontsize=40:x=(w-tw)/2:y=(h-th)/2" -c:v libx264 -preset ultrafast outro.mp4', shell=True)
        
        with open("lista.txt", "w") as f:
            for i in range(len(vids)): f.write(f"file 'p_{i}.mp4'\n")
            f.write("file 'outro.mp4'\n")
        subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)

        # 3. MEZCLA FINAL DEFINITIVA
        status.write("✨ Quemando subtítulos estilo TikTok...")
        
        # Estilo "Bonito": Amarillo con contorno negro y un poco de sombra
        estilo = (
            f"Fontname=Impact,FontSize=32,PrimaryColour={ass_col},"
            "OutlineColour=&H000000,BorderStyle=1,Outline=2.5,Shadow=1.5,"
            "Alignment=2,MarginV=380"
        )
        
        # Mezclamos todo en un solo paso pero con códecs ligeros
        cmd = f'ffmpeg -y -i base.mp4 -i t.mp3 -vf "subtitles=t.srt:force_style=\'{estilo}\'" -c:v libx264 -preset ultrafast -c:a aac -map 0:v:0 -map 1:a:0 -shortest "{v_final}"'
        subprocess.run(cmd, shell=True)
        
        if os.path.exists(v_final):
            st.video(v_final)
            st.success("🔥 ¡Vídeo terminado con subtítulos!")
