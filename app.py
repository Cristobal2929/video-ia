import streamlit as st
import os, time, random, subprocess, re, requests

st.set_page_config(page_title="Fénix Studio AI", layout="centered", page_icon="🎬")

st.markdown("""
    <style>
    .stApp {background: linear-gradient(135deg, #0f172a, #1e293b); color: white;}
    .stChatMessage {background-color: #334155; border-radius: 15px; padding: 15px; border: 1px solid #475569;}
    .stButton>button {border-radius: 20px; font-weight: bold; background: linear-gradient(90deg, #6366f1, #a855f7); color: white; transition: 0.3s;}
    </style>
""", unsafe_allow_html=True)

TRADUCTOR = {
    "coche": "luxury cars", "auto": "sports car", "negocio": "business", 
    "dinero": "cash", "terror": "creepy dark", "miedo": "horror", 
    "amor": "romantic couple", "gato": "funny cats", "espacio": "galaxy universe"
}

def limpiar_tema(texto):
    texto = texto.lower()
    for esp, eng in TRADUCTOR.items():
        if esp in texto: return eng
    limpio = re.sub(r'quiero|un|video|de|sobre|hazme|haz|crea|un|una|para', '', texto).strip()
    return limpio if limpio else "abstract"

def generar_guion_inteligente(tema):
    t = tema.lower()
    if "coche" in t or "auto" in t: return "Siente la velocidad y el lujo. Una máquina perfecta diseñada para dominar el asfalto y robar todas las miradas. El futuro ya está aquí."
    elif "negocio" in t or "dinero" in t: return "El éxito no es casualidad, es estrategia. Mientras otros duermen, tú construyes tu imperio. Toma acción hoy y cambia tu vida."
    elif "terror" in t or "miedo" in t: return "La oscuridad esconde secretos que la mente humana no está preparada para comprender. ¿Te atreves a descubrir lo que acecha en las sombras?"
    elif "amor" in t: return "El amor es la fuerza más poderosa del universo. Capaz de sanar heridas profundas y de conectar dos almas a través del tiempo y el espacio."
    else: return f"Descubre los secretos más increíbles sobre {tema}. Datos fascinantes que cambiarán por completo tu forma de ver el mundo. ¡Presta mucha atención!"

def buscar_multiples_pexels(query, api_key, num_clips=3):
    busqueda_real = limpiar_tema(query)
    url = f"https://api.pexels.com/videos/search?query={busqueda_real}&per_page=15&orientation=portrait"
    headers = {"Authorization": api_key.strip()}
    descargados = []
    try:
        res = requests.get(url, headers=headers)
        if res.status_code != 200: return []
        data = res.json()
        if not data.get('videos'): return []
        
        videos = data['videos']
        random.shuffle(videos) # Mezclamos para que siempre sean distintos
        
        for i, video_info in enumerate(videos[:num_clips]):
            archivos = video_info['video_files']
            link = next((a['link'] for a in archivos if a['file_type'] == 'video/mp4' and 480 <= a['height'] <= 1080), archivos[0]['link'])
            r = requests.get(link, stream=True)
            nombre = f"clip_raw_{i}.mp4"
            with open(nombre, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024*1024):
                    if chunk: f.write(chunk)
            descargados.append(nombre)
        return descargados
    except: return []

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
    st.title("⚙️ Ajustes")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.color_picker("🎨 Color Sub", "#00FFFF")
    hc = color_sub.lstrip('#')
    ass_color = f"&H00{hc[4:6]}{hc[2:4]}{hc[0:2]}"
    voz = st.selectbox("🗣️ Voz", ["es-ES-AlvaroNeural", "es-MX-JorgeNeural"])

st.title("🎬 Fénix AI Montaje PRO")
st.subheader("Generador de clips múltiples")

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [{"role": "assistant", "content": "¡Hola! Pídeme un vídeo (ej: 'vídeo de terror' o 'vídeo de coches de lujo') y haré un montaje espectacular con varios clips combinados."}]

for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "video" in msg:
            with open(msg["video"], "rb") as f:
                st.video(f.read())
                st.download_button("📥 Descargar Montaje Final", f, file_name="Fenix_Montaje.mp4", mime="video/mp4")

if user_input := st.chat_input("¿Qué película montamos hoy?"):
    st.session_state.mensajes.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)

    with st.chat_message("assistant"):
        guion_final = generar_guion_inteligente(user_input) if len(user_input) < 80 else user_input
        
        with st.status(f"🎞️ Creando súper montaje de: {limpiar_tema(user_input)}...", expanded=True) as status:
            uid = int(time.time())
            os.makedirs("output", exist_ok=True)
            v_final = f"output/v_{uid}.mp4"
            
            status.write("🔊 Grabando locutor neural...")
            subprocess.run(f'edge-tts --voice {voz} --text "{guion_final}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
            
            status.write("🌍 Descargando 3 clips diferentes de Pexels...")
            clips_descargados = buscar_multiples_pexels(user_input, pexels_key, 3)
            
            if len(clips_descargados) > 0:
                status.write("⚙️ Formateando clips para el cine (480x854, 30fps)...")
                clips_procesados = []
                for i, clip in enumerate(clips_descargados):
                    out = f"proc_{i}.mp4"
                    cmd_proc = f'ffmpeg -y -i "{clip}" -vf "scale=480:854:force_original_aspect_ratio=increase,crop=480:854,fps=30" -c:v libx264 -preset ultrafast -crf 30 -c:a aac "{out}"'
                    subprocess.run(cmd_proc, shell=True)
                    clips_procesados.append(out)
                
                status.write("🎞️ Uniendo los clips en una sola película...")
                with open("lista.txt", "w") as f:
                    for p in clips_procesados: f.write(f"file '{p}'\n")
                
                subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy montaje_base.mp4', shell=True)
                
                if transformar_srt("t.vtt", "t.srt"):
                    status.write("🎬 Aplicando subtítulos dinámicos...")
                    est = f"Fontname=Impact,FontSize=26,PrimaryColour={ass_color},Outline=2,Alignment=2,MarginV=120"
                    
                    # Ahora usamos el montaje_base.mp4 que contiene los 3 vídeos unidos
                    cmd_final = f'ffmpeg -y -stream_loop -1 -i "montaje_base.mp4" -i t.mp3 -vf "subtitles=t.srt:force_style=\'{est}\'" -c:v libx264 -preset superfast -crf 30 -threads 1 -pix_fmt yuv420p -c:a aac -shortest "{v_final}"'
                    subprocess.run(cmd_final, shell=True)
                    
                    if os.path.exists(v_final):
                        st.session_state.mensajes.append({"role": "assistant", "content": f"✅ ¡Montaje espectacular completado! ({len(clips_procesados)} escenas).", "video": v_final})
                        st.rerun()
                    else: status.error("❌ Falló el renderizado final.")
                else: status.error("❌ Fallaron los subtítulos.")
            else: status.error("❌ No encontré suficientes vídeos para el montaje.")
