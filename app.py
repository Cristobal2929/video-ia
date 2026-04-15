import streamlit as st
import os, time, random, subprocess, re, requests

st.set_page_config(page_title="Fénix Chat AI", layout="centered", page_icon="💬")

st.markdown("""
    <style>
    .main {background-color: #0d1117; color: white;}
    </style>
""", unsafe_allow_html=True)

def buscar_y_descargar_pexels(query, api_key, output_filename="clip_base.mp4"):
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=15&orientation=portrait"
    headers = {"Authorization": api_key.strip()}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code != 200: return f"Error {res.status_code}"
        data = res.json()
        if not data.get('videos'): return "No hay vídeos"
        video_info = random.choice(data['videos'])
        archivos = video_info['video_files']
        link_descarga = next((a['link'] for a in archivos if a['file_type'] == 'video/mp4' and 480 <= a['height'] <= 1920), archivos[0]['link'])
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

# --- CONFIGURACIÓN LATERAL ---
with st.sidebar:
    st.header("⚙️ Ajustes del Vídeo")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    tema_fondo = st.text_input("🔍 Fondo (en inglés):", value="business", help="Ej: luxury car, gym, money")
    color_sub = st.color_picker("🎨 Color Sub", "#00FFFF")
    hc = color_sub.lstrip('#')
    ass_color = f"&H00{hc[4:6]}{hc[2:4]}{hc[0:2]}"
    voz = st.selectbox("🗣️ Voz", ["es-ES-AlvaroNeural", "es-MX-JorgeNeural"])

# --- INTERFAZ DE CHAT ---
st.title("💬 Fénix AI Chat")

# Inicializamos el historial de mensajes
if "mensajes" not in st.session_state:
    st.session_state.mensajes = [{"role": "assistant", "content": "¡Hola, Dayron! 👋 Configura el fondo en el menú de la izquierda y luego **escribe aquí abajo el guion exacto** que quieres que yo lea en el vídeo."}]

# Mostramos el historial en pantalla
for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "video" in msg:
            st.video(msg["video"])

# --- ENTRADA DEL USUARIO ---
if guion := st.chat_input("Escribe el guion de tu vídeo aquí..."):
    # Mostramos lo que escribió el usuario
    st.session_state.mensajes.append({"role": "user", "content": guion})
    with st.chat_message("user"):
        st.markdown(guion)

    # El bot responde y trabaja
    with st.chat_message("assistant"):
        if not tema_fondo:
            st.error("⚠️ Faltan datos en el menú lateral.")
        else:
            uid = int(time.time())
            os.makedirs("output", exist_ok=True)
            final_p = f"output/video_{uid}.mp4"
            clip_base = f"output/clip_{uid}.mp4"
            
            with st.status("💎 Creando tu vídeo...", expanded=True) as status:
                status.write("🔊 Grabando voz...")
                subprocess.run(f'edge-tts --voice {voz} --text "{guion}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
                
                status.write(f"🌍 Buscando '{tema_fondo}' en internet...")
                res_pex = buscar_y_descargar_pexels(tema_fondo, pexels_key, clip_base)
                
                if res_pex is True and transformar_srt("t.vtt", "t.srt"):
                    status.write("🎬 Editando...")
                    est = f"Fontname=Impact,FontSize=26,PrimaryColour={ass_color},Outline=2,Alignment=2,MarginV=120"
                    cmd = f'ffmpeg -y -stream_loop -1 -i "{clip_base}" -i t.mp3 -vf "scale=480:854:force_original_aspect_ratio=increase,crop=480:854,subtitles=t.srt:force_style=\'{est}\'" -c:v libx264 -preset superfast -crf 30 -threads 1 -pix_fmt yuv420p -c:a aac -shortest "{final_p}"'
                    subprocess.run(cmd, shell=True)
                    
                    if os.path.exists(final_p):
                        st.video(final_p)
                        st.session_state.mensajes.append({"role": "assistant", "content": "¡Aquí tienes tu vídeo! 🚀", "video": final_p})
                        status.update(label="✅ Terminado", state="complete")
                    else:
                        st.error("❌ Fallo en la edición.")
                else:
                    st.error(f"❌ Error: {res_pex}")
