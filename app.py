import streamlit as st
import os, time, random, subprocess, re, requests

st.set_page_config(page_title="Fénix Studio Pro", layout="centered", page_icon="🎬")
st.markdown("<style>.stApp {background: linear-gradient(135deg, #0f172a, #1e293b); color: white;}</style>", unsafe_allow_html=True)

# --- CEREBRO DE HISTORIAS LARGAS ---
HISTORIAS = {
    "terror": "La noche caía pesada sobre la vieja mansión. Las sombras parecían cobrar vida propia en las esquinas de las habitaciones vacías. Cada crujido de la madera sonaba como un grito ahogado en el silencio. No había escapatoria, el frío calaba los huesos mientras una presencia invisible observaba desde la oscuridad más profunda. Algo se movía bajo la cama, algo que no pertenecía a este mundo, esperando el momento exacto para atrapar a su próxima víctima.",
    "coche": "La ingeniería perfecta se encuentra con la adrenalina pura. Imagina recorrer la carretera a toda velocidad, sintiendo el rugido de quinientos caballos de fuerza bajo el capó. El diseño aerodinámico corta el viento mientras las luces de la ciudad se difuminan en un rastro de colores. Esto no es solo un vehículo, es una obra de arte en movimiento, una máquina diseñada para aquellos que no aceptan límites.",
    "negocio": "El camino hacia el éxito financiero requiere más que solo sueños; requiere una estrategia implacable y una ejecución perfecta. Los grandes imperios no se construyeron en un día, se forjaron en las horas de sacrificio y en la toma de decisiones audaces. Si quieres cambiar tu futuro, debes empezar a invertir en tu activo más valioso: tu propia mente. El mercado no espera a nadie, es hora de tomar tu lugar en la cima."
}

def obtener_duracion(archivo):
    cmd = f"ffprobe -i {archivo} -show_entries format=duration -v quiet -of csv='p=0'"
    return float(subprocess.check_output(cmd, shell=True))

def buscar_y_descargar_exacto(query, api_key, segundos_totales):
    busqueda_real = "horror creepy" if "terror" in query.lower() else "luxury cars" if "coche" in query.lower() else "business"
    url = f"https://api.pexels.com/videos/search?query={busqueda_real}&per_page=40&orientation=portrait"
    descargados = []
    segundos_acumulados = 0
    try:
        res = requests.get(url, headers={"Authorization": api_key.strip()})
        videos = res.json().get('videos', [])
        random.shuffle(videos)
        for i, v in enumerate(videos):
            if segundos_acumulados >= segundos_totales: break
            link = v['video_files'][0]['link']
            nombre = f"clip_{i}.mp4"
            with open(nombre, 'wb') as f: f.write(requests.get(link).content)
            descargados.append(nombre)
            segundos_acumulados += v.get('duration', 10)
        return descargados
    except: return []

with st.sidebar:
    st.title("⚙️ Ajustes")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.color_picker("🎨 Color Sub", "#00FFFF")
    hc = color_sub.lstrip('#')
    ass_color = f"&H00{hc[4:6]}{hc[2:4]}{hc[0:2]}"
    voz = st.selectbox("🗣️ Voz", ["es-ES-AlvaroNeural", "es-MX-JorgeNeural"])

st.title("🎬 Fénix AI: Cine Automático")

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [{"role": "assistant", "content": "¡Hola! Pídeme un tema (ej: 'terror') y yo escribiré una historia larga y haré el montaje."}]

for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "video" in msg:
            with open(msg["video"], "rb") as f:
                st.video(f.read())

if user_input := st.chat_input("Dime el tema o pega tu guion..."):
    st.session_state.mensajes.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)

    with st.chat_message("assistant"):
        # ¿El usuario solo dio un tema corto? Expandimos con una historia real
        guion_final = user_input
        if len(user_input) < 50:
            for k, v in HISTORIAS.items():
                if k in user_input.lower():
                    guion_final = v
                    break

        with st.status("🎬 Produciendo película completa...", expanded=True) as status:
            uid = int(time.time())
            v_final = f"output/v_{uid}.mp4"
            subprocess.run(f'edge-tts --voice {voz} --text "{guion_final}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
            
            duracion_audio = obtener_duracion("t.mp3")
            clips = buscar_y_descargar_exacto(user_input, pexels_key, duracion_audio)
            
            if clips:
                for i, c in enumerate(clips):
                    subprocess.run(f'ffmpeg -y -i "{c}" -vf "scale=480:854:force_original_aspect_ratio=increase,crop=480:854,fps=30" -c:v libx264 -preset ultrafast -crf 30 "p_{i}.mp4"', shell=True)
                with open("lista.txt", "w") as f:
                    for i in range(len(clips)): f.write(f"file 'p_{i}.mp4'\n")
                subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)
                
                est = f"Fontname=Impact,FontSize=26,PrimaryColour={ass_color},Outline=2,Alignment=2,MarginV=120"
                cmd = f'ffmpeg -y -i base.mp4 -i t.mp3 -vf "subtitles=t.vtt:force_style=\'{est}\'" -c:v libx264 -preset superfast -shortest "{v_final}"'
                subprocess.run(cmd, shell=True)
                
                st.session_state.mensajes.append({"role": "assistant", "content": f"✅ Vídeo de {round(duracion_audio)}s completado.", "video": v_final})
                st.rerun()
