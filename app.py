import streamlit as st
import os, time, random, subprocess, re, requests

st.set_page_config(page_title="Fénix Studio AI", layout="centered", page_icon="🎬")

st.markdown("""
    <style>
    .main {background-color: #0d1117; color: white;}
    .stHeader {text-align: center; background: #1c2128; padding: 30px; border-radius: 20px; border: 1px solid #30363d; margin-bottom: 20px;}
    .stButton>button {background: linear-gradient(90deg, #6366f1, #a855f7); color: white; border: none; font-weight: bold; border-radius: 12px; height: 3.5em; width: 100%; transition: 0.3s;}
    .stButton>button:hover {transform: scale(1.02); box-shadow: 0 5px 15px rgba(168, 85, 247, 0.4);}
    h1 {background: -webkit-linear-gradient(#fff, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
    </style>
""", unsafe_allow_html=True)

def buscar_y_descargar_pexels(query, api_key, output_filename="clip_base.mp4"):
    # Buscamos directamente lo que escribas en la caja (funciona mejor en inglés)
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=15&orientation=portrait"
    headers = {"Authorization": api_key.strip()}

    try:
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            return f"Acceso denegado. Revisa la clave. (Error {res.status_code})"
            
        data = res.json()
        if not data.get('videos') or len(data['videos']) == 0:
            return f"Pexels no encontró vídeos para la búsqueda: '{query}'"
            
        video_info = random.choice(data['videos'])
        archivos = video_info['video_files']
        link_descarga = None
        
        for archivo in archivos:
            if archivo['file_type'] == 'video/mp4' and 480 <= archivo['height'] <= 1920:
                link_descarga = archivo['link']
                break
                
        if not link_descarga:
            link_descarga = archivos[0]['link']

        r = requests.get(link_descarga, stream=True)
        with open(output_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024*1024):
                if chunk: f.write(chunk)
        return True
    except Exception as e:
        return f"Error interno: {str(e)}"

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

st.markdown('<div class="stHeader"><h1>🎬 FÉNIX AI STUDIO</h1><p>Producción 100% Autónoma</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Configuración")
    
    pexels_key = st.text_input("🔑 Tu Clave API de Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    
    st.markdown("---")
    
    # NUEVA CAJA PARA BUSCAR CUALQUIER COSA
    tema_fondo = st.text_input("🔍 ¿Qué vídeo quieres de fondo?", value="luxury car", help="Escribe en INGLÉS para obtener resultados mucho mejores (ej: sports car, money, gym...)")
    
    color_sub = st.color_picker("🎨 Color Subtítulos", "#00FFFF")
    hc = color_sub.lstrip('#')
    ass_color = f"&H00{hc[4:6]}{hc[2:4]}{hc[0:2]}"
    voz = st.selectbox("🗣️ Voz", ["es-ES-AlvaroNeural", "es-MX-JorgeNeural"])

guion_final = st.text_area("✍️ Guion:", placeholder="Escribe o pega aquí el guion para tu vídeo...", height=150)

if st.button("🚀 INICIAR PRODUCCIÓN AUTOMÁTICA"):
    if not pexels_key:
        st.error("⚠️ Falta la clave de Pexels.")
    elif not guion_final:
        st.warning("⚠️ Primero escribe un guion en la caja.")
    elif not tema_fondo:
        st.warning("⚠️ Escribe de qué quieres que trate el vídeo de fondo.")
    else:
        uid = int(time.time())
        os.makedirs("output", exist_ok=True)
        final_p = f"output/video_{uid}.mp4"
        clip_base = "clip_base.mp4"
        
        with st.status("💎 Fabricando Vídeo Automático...", expanded=True) as status:
            status.write("🔊 Generando voz neural...")
            subprocess.run(f'edge-tts --voice {voz} --text "{guion_final}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
            
            # Ahora busca tu palabra clave exacta
            status.write(f"🌍 Buscando vídeos de '{tema_fondo}' en Pexels...")
            
            resultado_pexels = buscar_y_descargar_pexels(tema_fondo, pexels_key, clip_base)
            
            if resultado_pexels is True:
                if transformar_srt("t.vtt", "t.srt"):
                    status.write("🎬 Editando y uniendo capas...")
                    est = f"Fontname=Impact,FontSize=26,PrimaryColour={ass_color},Outline=2,Alignment=2,MarginV=120"
                    
                    cmd = f'ffmpeg -y -stream_loop -1 -i "{clip_base}" -i t.mp3 -vf "scale=480:854:force_original_aspect_ratio=increase,crop=480:854,subtitles=t.srt:force_style=\'{est}\'" -c:v libx264 -preset superfast -crf 30 -threads 1 -max_muxing_queue_size 1024 -pix_fmt yuv420p -c:a aac -shortest "{final_p}"'
                    
                    subprocess.run(cmd, shell=True)
                    
                    if os.path.exists(final_p):
                        st.video(final_p)
                        with open(final_p, 'rb') as f:
                            st.download_button("📥 DESCARGAR VIDEO", f.read(), file_name=f"Fenix_Auto_{uid}.mp4")
                        status.update(label="✅ ¡Vídeo Creado con Éxito!", state="complete")
                    else:
                        st.error("❌ Fallo en la edición. Inténtalo de nuevo.")
            else:
                st.error(f"❌ {resultado_pexels}")
