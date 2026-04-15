import streamlit as st
import os, time, random, subprocess, re, requests

st.set_page_config(page_title="Fénix Chat AI", layout="centered", page_icon="💬")

st.markdown("<style>.main {background-color: #0d1117; color: white;}</style>", unsafe_allow_html=True)

# DICCIONARIO DE TRADUCCIÓN PARA PEXELS
TRADUCTOR = {
    "coche": "cars", "coches": "luxury cars", "auto": "sports car",
    "negocio": "business", "dinero": "money", "invertir": "trading",
    "comida": "healthy food", "dieta": "fitness food", "ejercicio": "gym",
    "historia": "ancient history", "misterio": "mystery", "espacio": "galaxy"
}

def limpiar_tema(texto):
    texto = texto.lower()
    # Buscamos si alguna de nuestras palabras clave está en lo que escribió el usuario
    for esp, eng in TRADUCTOR.items():
        if esp in texto:
            return eng
    # Si no encuentra nada, limpia palabras comunes y usa el resto
    limpio = re.sub(r'quiero|un|video|de|sobre|hazme|haz|crea|un|una', '', texto).strip()
    return limpio if limpio else "abstract"

def generar_guion_inteligente(tema):
    tema_l = tema.lower()
    if "coche" in tema_l or "auto" in tema_l:
        return "El rugido del motor, el brillo de la carrocería y la sensación de libertad absoluta. Un coche no es solo transporte, es una declaración de intenciones. ¿Estás listo para el siguiente nivel?"
    elif "negocio" in tema_l or "dinero" in tema_l:
        return "La libertad financiera no es un sueño, es un plan. Con disciplina, estrategia y la mentalidad correcta, el éxito está a tu alcance. Empieza hoy a construir tu imperio."
    else:
        return f"Bienvenidos a este nuevo vídeo sobre {tema}. Hoy vamos a profundizar en lo que hace que este tema sea tan especial e inspirador para todos nosotros."

def buscar_y_descargar_pexels(query, api_key, output_filename="clip_base.mp4"):
    # Limpiamos el tema antes de buscar
    busqueda_real = limpiar_tema(query)
    url = f"https://api.pexels.com/videos/search?query={busqueda_real}&per_page=20&orientation=portrait"
    headers = {"Authorization": api_key.strip()}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code != 200: return f"Error API {res.status_code}"
        data = res.json()
        if not data.get('videos'): return f"No encontré vídeos de '{busqueda_real}'"
        
        # Elegimos uno al azar de los resultados para que no siempre sea el mismo
        video_info = random.choice(data['videos'])
        archivos = video_info['video_files']
        link_descarga = next((a['link'] for a in archivos if 480 <= a['height'] <= 1920), archivos[0]['link'])
        
        r = requests.get(link_descarga, stream=True)
        with open(output_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024*1024):
                if chunk: f.write(chunk)
        return True
    except Exception as e: return str(e)

def transformar_srt(vtt_path, srt_path):
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
                w = re.sub(r'[.,;!¡¿?]', '', clean[i+1].strip()).upper().split()
                if not w: continue
                step = (e - s) / max(len(w), 1)
                for j in range(0, len(w), 2):
                    g = w[j:j+2]
                    srt_f.append(f"{cnt}\n{format_t(s+int(j*step))} --> {format_t(s+int((j+len(g))*step))}\n{' '.join(g)}\n")
                    cnt += 1
        with open(srt_path, 'w', encoding='utf-8') as f: f.write("\n".join(srt_f))
        return True
    except: return False

with st.sidebar:
    st.header("⚙️ Ajustes")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.color_picker("🎨 Color Sub", "#00FFFF")
    hc = color_sub.lstrip('#')
    ass_color = f"&H00{hc[4:6]}{hc[2:4]}{hc[0:2]}"
    voz = st.selectbox("🗣️ Voz", ["es-ES-AlvaroNeural", "es-MX-JorgeNeural"])

st.title("💬 Fénix AI Chat")

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [{"role": "assistant", "content": "¡Hola! Pídeme lo que quieras. Ej: 'Hazme un vídeo de coches deportivos'"}]

for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "video" in msg: st.video(msg["video"])

if user_input := st.chat_input("¿De qué trata el vídeo hoy?"):
    st.session_state.mensajes.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)

    with st.chat_message("assistant"):
        # Lógica de guion
        guion_final = generar_guion_inteligente(user_input) if len(user_input) < 80 else user_input
        
        with st.status(f"🔍 Analizando tema y buscando vídeos...", expanded=True) as status:
            status.write("🔊 Grabando voz...")
            subprocess.run(f'edge-tts --voice {voz} --text "{guion_final}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
            
            # Aquí está la magia: pasamos el mensaje completo y el bot extraerá el tema
            res_pex = buscar_y_descargar_pexels(user_input, pexels_key, "clip_base.mp4")
            
            if res_pex is True and transformar_srt("t.vtt", "t.srt"):
                status.write("🎬 Renderizando edición final...")
                est = f"Fontname=Impact,FontSize=26,PrimaryColour={ass_color},Outline=2,Alignment=2,MarginV=120"
                cmd = f'ffmpeg -y -stream_loop -1 -i "clip_base.mp4" -i t.mp3 -vf "scale=480:854:force_original_aspect_ratio=increase,crop=480:854,subtitles=t.srt:force_style=\'{est}\'" -c:v libx264 -preset superfast -crf 30 -threads 1 -pix_fmt yuv420p -c:a aac -shortest "video_final.mp4"'
                subprocess.run(cmd, shell=True)
                
                if os.path.exists("video_final.mp4"):
                    st.video("video_final.mp4")
                    st.session_state.mensajes.append({"role": "assistant", "content": f"✅ Vídeo listo. Tema detectado: **{limpiar_tema(user_input)}**", "video": "video_final.mp4"})
                    status.update(label="✅ Producción terminada", state="complete")
                else: st.error("Fallo al crear el archivo de vídeo.")
            else:
                st.error(f"❌ Error en búsqueda: {res_pex}")
