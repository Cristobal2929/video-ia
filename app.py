import streamlit as st
import os, time, random, subprocess, re, requests

st.set_page_config(page_title="Fénix Viral Studio Pro", layout="centered")
st.markdown("<style>.stApp {background: #0d1117; color: white;}</style>", unsafe_allow_html=True)

# --- MOTOR DE GENERACIÓN DE GUIONES UNIVERSAL ---
def generar_guion_pro(tema):
    t = tema.lower()
    
    # Estructuras lógicas por nicho
    if any(word in t for word in ["terror", "miedo", "paranormal", "fantasma"]):
        hooks = ["¿Alguna vez has sentido que alguien te observa cuando estás solo?", "Hay secretos que es mejor no desenterrar.", "Lo que vas a escuchar hoy te hará mirar debajo de tu cama."]
        cuerpo = f"En los rincones más oscuros de {tema}, la realidad se distorsiona. Se dice que en lugares abandonados, el tiempo se detiene y las sombras cobran vida propia, esperando el momento exacto para manifestarse."
        cierre = "No apagues la luz esta noche. Síguenos para más terror real."
        
    elif any(word in t for word in ["coche", "motor", "velocidad", "f1"]):
        hooks = [f"El mundo de {tema} no es para cualquiera.", "¿Sabías que este motor puede desafiar las leyes de la física?", "La potencia sin control no sirve de nada."]
        cuerpo = f"Cuando hablamos de {tema}, hablamos de ingeniería pura. Cada pieza está diseñada para llevar el límite un paso más allá, quemando asfalto y liberando adrenalina en cada segundo de aceleración."
        cierre = "Si amas la velocidad, dale al botón de seguir."

    elif any(word in t for word in ["dinero", "lujo", "millonario", "negocio"]):
        hooks = [f"¿Quieres saber cómo funciona realmente el mundo de {tema}?", "La mayoría de la gente ignora esto sobre el éxito.", "El secreto de la riqueza está frente a tus ojos."]
        cuerpo = f"Dominar {tema} requiere una mentalidad diferente. No se trata de trabajar más, sino de trabajar mejor, entendiendo que cada decisión cuenta para construir un imperio desde cero."
        cierre = "Aprende a dominar el juego. Síguenos."

    else:
        # Generador Genérico Inteligente para cualquier otro tema
        hooks = [f"¿Sabías esto sobre {tema}?", f"Lo que nadie te cuenta de {tema} es asombroso.", f"Prepárate para descubrir la verdad sobre {tema}."]
        cuerpo = f"El impacto de {tema} en nuestra vida cotidiana es mucho más grande de lo que imaginamos. Desde sus orígenes ocultos hasta los detalles que lo hacen único, este mundo nunca deja de sorprendernos por su complejidad."
        cierre = f"Si quieres descubrir más sobre {tema}, quédate con nosotros."

    return f"{random.choice(hooks)} {cuerpo} {cierre}"

# --- CONVERSOR DE SUBTÍTULOS DINÁMICOS (2 PALABRAS) ---
def generar_srt_dinamico(vtt_file, srt_file):
    with open(vtt_file, 'r', encoding='utf-8') as f: lines = f.readlines()
    srt_content = []
    index = 1
    for i in range(len(lines)):
        if "-->" in lines[i]:
            tiempo = lines[i].replace('.', ',')
            # Extraemos el texto y lo limpiamos
            texto = lines[i+1].strip().upper()
            palabras = texto.split()
            # Dividimos en bloques de 2 palabras (Estilo Viral)
            for j in range(0, len(palabras), 2):
                dupla = " ".join(palabras[j:j+2])
                srt_content.append(f"{index}\n{tiempo}\n{dupla}\n")
                index += 1
    with open(srt_file, 'w', encoding='utf-8') as f: f.write("\n".join(srt_content))

st.title("🦅 Fénix Viral Studio")

with st.sidebar:
    st.header("Estética del Vídeo")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.color_picker("🎨 Color Sub", "#FFFF00")
    hc = color_sub.lstrip('#')
    ass_col = f"&H00{hc[4:6]}{hc[2:4]}{hc[0:2]}"

if user_input := st.chat_input("¿Qué tema quieres hoy? (Ej: Supervivencia, Espacio, Roma...)"):
    with st.status("🎬 Generando contenido de alta retención...", expanded=True) as status:
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.* outro.mp4 temp_v.mp4 final.mp4", shell=True)
        
        # 1. Crear Guion Maestro
        guion = generar_guion_pro(user_input)
        v_final = f"output/v_{int(time.time())}.mp4"
        
        # 2. Voz y Tiempos
        status.write("🎙️ Grabando locución profesional...")
        subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --text "{guion}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
        generar_srt_dinamico("t.vtt", "t.srt")
        
        # 3. Clips de Pexels
        status.write(f"🎞️ Buscando visuales para {user_input}...")
        url = f"https://api.pexels.com/videos/search?query={user_input}&per_page=6&orientation=portrait"
        res = requests.get(url, headers={"Authorization": pexels_key.strip()}).json()
        vids = res.get('videos', [])
        
        processed_clips = []
        for i, v in enumerate(vids):
            status.write(f"✂️ Procesando escena {i+1}...")
            with open(f"clip_{i}.mp4", 'wb') as f: f.write(requests.get(v['video_files'][0]['link']).content)
            subprocess.run(f'ffmpeg -y -i "clip_{i}.mp4" -vf "scale=480:854:force_original_aspect_ratio=increase,crop=480:854,fps=25" -an -c:v libx264 -preset ultrafast "p_{i}.mp4"', shell=True)
            processed_clips.append(f"p_{i}.mp4")
            os.remove(f"clip_{i}.mp4")
        
        # Sello Final
        subprocess.run('ffmpeg -y -f lavfi -i color=c=black:s=480x854:d=2:r=25 -vf "drawtext=text=\'FENIX STUDIO 🦅\':fontcolor=white:fontsize=40:x=(w-tw)/2:y=(h-th)/2" -c:v libx264 -preset ultrafast outro.mp4', shell=True)
        
        with open("lista.txt", "w") as f:
            for p in processed_clips: f.write(f"file '{p}'\n")
            f.write("file 'outro.mp4'\n")
        
        subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)

        # 4. Mezcla Final Paso a Paso (Anti-RAM)
        status.write("🧪 Mezclando audio y subtítulos centrales...")
        # Paso A: Audio
        subprocess.run(f'ffmpeg -y -i base.mp4 -i t.mp3 -c:v copy -c:a aac -shortest temp_v.mp4', shell=True)
        # Paso B: Subtítulos en el centro (MarginV=427 es el centro de 854)
        est = f"Fontname=Impact,FontSize=34,PrimaryColour={ass_col},Outline=4,BorderStyle=1,Alignment=2,MarginV=427"
        cmd = f'ffmpeg -y -i temp_v.mp4 -vf "subtitles=t.srt:force_style=\'{est}\'" -c:v libx264 -preset ultrafast "{v_final}"'
        subprocess.run(cmd, shell=True)
        
        if os.path.exists(v_final):
            st.video(v_final)
            st.success("🔥 ¡Vídeo terminado para cualquier nicho!")
            st.balloons()
