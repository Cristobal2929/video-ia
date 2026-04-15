import streamlit as st
import os, time, random, subprocess, re, requests

st.set_page_config(page_title="Fénix Viral Studio Pro", layout="centered")
st.markdown("<style>.stApp {background: #0d1117; color: white;}</style>", unsafe_allow_html=True)

def generar_guion_pro(tema):
    t = tema.lower()
    if any(word in t for word in ["terror", "miedo", "paranormal"]):
        hooks = ["¿Alguna vez has sentido que alguien te observa?", "Hay secretos que es mejor no desenterrar."]
        cuerpo = f"En los rincones más oscuros de {tema}, la realidad se distorsiona. Sombras que cobran vida propia, esperando el momento exacto para manifestarse."
        cierre = "No apagues la luz esta noche."
    elif any(word in t for word in ["coche", "motor", "velocidad"]):
        hooks = [f"El mundo de {tema} no es para cualquiera.", "La potencia sin control no sirve de nada."]
        cuerpo = f"Cuando hablamos de {tema}, hablamos de ingeniería pura. Cada pieza diseñada para llevar el límite un paso más allá, quemando asfalto."
        cierre = "Si amas la velocidad, dale a seguir."
    else:
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
            palabras = lines[i+1].strip().upper().split()
            for j in range(0, len(palabras), 2):
                dupla = " ".join(palabras[j:j+2])
                srt_content.append(f"{index}\n{tiempo}\n{dupla}\n")
                index += 1
    with open(srt_file, 'w', encoding='utf-8') as f: f.write("\n".join(srt_content))

st.title("🦅 Fénix Studio: Subtítulos Top")

with st.sidebar:
    st.header("Personalización")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.color_picker("🎨 Color de Letra", "#FFFF00") # Amarillo por defecto
    hc = color_sub.lstrip('#')
    # Convertimos a formato ASS (BGR)
    ass_col = f"&H00{hc[4:6]}{hc[2:4]}{hc[0:2]}"

if user_input := st.chat_input("¿Qué vídeo grabamos hoy?"):
    with st.status("🎬 Editando con estética pro...", expanded=True) as status:
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.* outro.mp4 temp_v.mp4", shell=True)
        
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
            status.write(f"🎞️ Procesando escena {i+1}...")
            with open(f"clip_{i}.mp4", 'wb') as f: f.write(requests.get(v['video_files'][0]['link']).content)
            subprocess.run(f'ffmpeg -y -i "clip_{i}.mp4" -vf "scale=480:854:force_original_aspect_ratio=increase,crop=480:854,fps=25" -an -c:v libx264 -preset ultrafast "p_{i}.mp4"', shell=True)
            os.remove(f"clip_{i}.mp4")
        
        subprocess.run('ffmpeg -y -f lavfi -i color=c=black:s=480x854:d=2:r=25 -vf "drawtext=text=\'FENIX STUDIO 🦅\':fontcolor=white:fontsize=40:x=(w-tw)/2:y=(h-th)/2" -c:v libx264 -preset ultrafast outro.mp4', shell=True)
        
        with open("lista.txt", "w") as f:
            for i in range(len(vids)): f.write(f"file 'p_{i}.mp4'\n")
            f.write("file 'outro.mp4'\n")
        subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)

        # 3. MEZCLA FINAL CON ESTILO "BONITO"
        status.write("✨ Aplicando diseño de subtítulos...")
        subprocess.run(f'ffmpeg -y -i base.mp4 -i t.mp3 -c:v copy -c:a aac -shortest temp_v.mp4', shell=True)
        
        # ESTILO DETALLADO:
        # BorderStyle=1 (Contorno), Outline=3 (Grosor borde), Shadow=2 (Sombra), MarginV=350 (Un poco más arriba del centro)
        estilo_pro = (
            f"Fontname=Impact,FontSize=34,PrimaryColour={ass_col},"
            f"OutlineColour=&H000000,BorderStyle=1,Outline=3,Shadow=2,"
            f"Alignment=2,MarginV=350"
        )
        
        cmd = f'ffmpeg -y -i temp_v.mp4 -vf "subtitles=t.srt:force_style=\'{estilo_pro}\'" -c:v libx264 -preset ultrafast "{v_final}"'
        subprocess.run(cmd, shell=True)
        
        if os.path.exists(v_final):
            st.video(v_final)
            st.success("🔥 ¡Vídeo con subtítulos pro terminado!")
            st.balloons()
