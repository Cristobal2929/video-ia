import streamlit as st
import os, time, random, subprocess, re, requests

st.set_page_config(page_title="Fénix Studio Pro", layout="centered", page_icon="🎬")
st.markdown("<style>.stApp {background: linear-gradient(135deg, #0f172a, #1e293b); color: white;}</style>", unsafe_allow_html=True)

# --- HISTORIAS ACTUALIZADAS (MÁS DIVERTIDAS) ---
HISTORIAS = {
    "terror": "La noche caía pesada sobre la vieja mansión. Las sombras parecían cobrar vida propia en las esquinas de las habitaciones vacías. Cada crujido de la madera sonaba como un grito ahogado en el silencio. Algo se movía bajo la cama, esperando el momento exacto para arrastrarte hacia el abismo eterno.",
    "coche": "La ingeniería perfecta se encuentra con la adrenalina pura. Imagina recorrer la carretera a toda velocidad, sintiendo el rugido de quinientos caballos de fuerza bajo el capó. Esto no es solo un vehículo, es una obra de arte en movimiento, una máquina diseñada para aquellos que no aceptan límites.",
    "humor": "La vida es ese chiste que a veces no entiendes hasta que te pasa a ti. ¿Te has fijado que siempre que tienes prisa, el semáforo se pone rojo y la persona de delante camina como si estuviera en un museo? O cuando buscas algo por toda la casa, no lo encuentras, y en cuanto te rindes, aparece justo donde habías mirado mil veces. ¡Es como si los objetos tuvieran vida propia y se estuvieran riendo de nosotros en nuestra cara!",
    "humor_largo": "Si la risa es el mejor remedio, ¡yo debería ser inmortal! ¿Habéis notado que los humanos somos expertos en complicarnos la vida? Compramos comida sana para que se pudra en la nevera mientras pedimos pizza. Vamos al gimnasio una vez al mes y esperamos salir como supermodelos. Y lo mejor de todo es cuando intentas parecer inteligente y te chocas con una puerta de cristal que estaba demasiado limpia. La vida no es perfecta, pero al menos es divertidísima si sabes de qué reírte. ¡Relájate y disfruta del caos!"
}

def traducir_tema(tema):
    tema = tema.lower()
    diccionario = {
        "motos": "motorcycles", "humor": "funny videos fails", "terror": "horror movie clips",
        "coches": "sports car", "dinero": "luxury life money", "gatos": "funny cats",
        "perros": "funny dogs", "espacio": "galaxy stars", "comida": "delicious food"
    }
    return diccionario.get(tema, tema)

def generar_guion_universal(tema, largo=False):
    t_key = tema.lower()
    # Si el tema es humor, usamos el nuevo guion gracioso
    if "humor" in t_key or "risa" in t_key:
        return HISTORIAS["humor_largo"] if largo else HISTORIAS["humor"]
    
    # Si es terror o coches, lo mismo
    if "terror" in t_key or "miedo" in t_key:
        return HISTORIAS["terror"]
    if "coche" in t_key:
        return HISTORIAS["coche"]
    
    # Para cualquier otro tema, un guion dinámico
    if largo:
        return f"Bienvenidos a este vídeo increíble sobre {tema}. Seguramente has pensado mucho en esto, pero hoy vamos a verlo desde una perspectiva totalmente diferente. Prepárate para descubrir detalles que te dejarán con la boca abierta y escenas que no verás en ningún otro sitio. ¡Vamos allá!"
    else:
        return f"Hoy exploramos el mundo de {tema}. Un tema apasionante lleno de sorpresas y momentos únicos que no te puedes perder. ¡Mira esto!"

def transformar_srt_profesional(vtt_path, srt_path):
    try:
        def parse_t(t):
            p = t.split(':')
            return int(p[-3])*3600000 + int(p[-2])*60000 + int(float(p[-1].replace(',','.'))*1000)
        def format_t(ms):
            return f"{ms//3600000:02d}:{(ms%3600000)//60000:02d}:{(ms%60000)//1000:02d},{ms%1000:03d}"
        with open(vtt_path, 'r', encoding='utf-8') as f: lines = f.readlines()
        clean = [l for l in lines if "-->" in l or (l.strip() and not l.strip().isdigit() and not l.startswith("WEBVTT"))]
        srt_f, cnt = [], 1
        for i in range(0, len(clean), 2):
            if i+1 < len(clean) and "-->" in clean[i]:
                t = clean[i].split(" --> ")
                s, e = parse_t(t[0]), parse_t(t[1])
                palabras = re.sub(r'[.,;!¡¿?]', '', clean[i+1].strip()).upper().split()
                if not palabras: continue
                ms_p = (e - s) / len(palabras)
                for j in range(0, len(palabras), 2):
                    g = palabras[j:j+2]
                    srt_f.append(f"{cnt}\n{format_t(s+int(j*ms_p))} --> {format_t(s+int((j+len(g))*ms_p))}\n{' '.join(g)}\n")
                    cnt += 1
        with open(srt_path, 'w', encoding='utf-8') as f: f.write("\n".join(srt_f))
        return True
    except: return False

def obtener_duracion(archivo):
    cmd = f"ffprobe -i {archivo} -show_entries format=duration -v quiet -of csv='p=0'"
    return float(subprocess.check_output(cmd, shell=True))

def buscar_y_descargar_dinamico(query, api_key, segundos_totales):
    tema_limpio = re.sub(r'quiero|un|video|de|sobre|hazme|haz|crea|largo|bastante|mide|dure', '', query.lower()).strip()
    busqueda_ingles = traducir_tema(tema_limpio)
    url = f"https://api.pexels.com/videos/search?query={busqueda_ingles}&per_page=40&orientation=portrait"
    descargados, segundos_acum = [], 0
    try:
        res = requests.get(url, headers={"Authorization": api_key.strip()})
        videos = res.json().get('videos', [])
        random.shuffle(videos)
        for i, v in enumerate(videos):
            if segundos_acum >= segundos_totales + 10: break
            link = v['video_files'][0]['link']
            nombre = f"clip_{i}.mp4"
            with open(nombre, 'wb') as f: f.write(requests.get(link).content)
            descargados.append(nombre)
            segundos_acum += v.get('duration', 8)
        return descargados, tema_limpio
    except: return [], "error"

with st.sidebar:
    st.title("⚙️ Ajustes")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.color_picker("🎨 Color Sub", "#FFFF00")
    hc = color_sub.lstrip('#')
    ass_color = f"&H00{hc[4:6]}{hc[2:4]}{hc[0:2]}"
    voz = st.selectbox("🗣️ Voz", ["es-ES-AlvaroNeural", "es-MX-JorgeNeural"])

st.title("🎬 Fénix Studio Pro")

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [{"role": "assistant", "content": "¡Hola! Ahora mis vídeos de humor son mucho más divertidos. ¡Pruébame!"}]

for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "video" in msg:
            with open(msg["video"], "rb") as f: st.video(f.read())

if user_input := st.chat_input("Dime el tema..."):
    st.session_state.mensajes.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)

    with st.chat_message("assistant"):
        es_largo = any(p in user_input.lower() for p in ["bastante", "largo", "minuto", "mucho"])
        with st.status("🎬 Generando contenido...", expanded=True) as status:
            uid = int(time.time())
            v_final = f"output/v_{uid}.mp4"
            clips, tema_det = buscar_y_descargar_dinamico(user_input, pexels_key, 60 if es_largo else 15)
            guion_final = generar_guion_universal(tema_det, es_largo)
            subprocess.run(f'edge-tts --voice {voz} --text "{guion_final}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
            dur_audio = obtener_duracion("t.mp3")
            if clips:
                transformar_srt_profesional("t.vtt", "t.srt")
                for i, c in enumerate(clips):
                    subprocess.run(f'ffmpeg -y -i "{c}" -vf "scale=480:854:force_original_aspect_ratio=increase,crop=480:854,fps=30" -c:v libx264 -preset ultrafast -crf 30 "p_{i}.mp4"', shell=True)
                with open("lista.txt", "w") as f:
                    for i in range(len(clips)): f.write(f"file 'p_{i}.mp4'\n")
                subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)
                est = f"Fontname=Impact,FontSize=28,PrimaryColour={ass_color},OutlineColour=&H00000000,BorderStyle=1,Outline=3,Shadow=1,Alignment=2,MarginV=140"
                cmd = f'ffmpeg -y -i base.mp4 -i t.mp3 -vf "subtitles=t.srt:force_style=\'{est}\'" -c:v libx264 -preset superfast -shortest "{v_final}"'
                subprocess.run(cmd, shell=True)
                st.session_state.mensajes.append({"role": "assistant", "content": f"✅ ¡Vídeo de humor listo! Duración: {round(dur_audio)}s.", "video": v_final})
                st.rerun()
