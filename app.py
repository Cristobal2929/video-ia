import streamlit as st
import os, time, random, subprocess, re, requests

st.set_page_config(page_title="Fénix Studio Pro", layout="centered", page_icon="🎬")

st.markdown("<style>.stApp {background: linear-gradient(135deg, #0f172a, #1e293b); color: white;}</style>", unsafe_allow_html=True)

TRADUCTOR = {
    "coche": "luxury cars", "terror": "horror creepy", "negocio": "business", 
    "dinero": "cash money", "amor": "romantic", "espacio": "galaxy"
}

def obtener_duracion(archivo):
    # Usa ffprobe para saber los segundos exactos del audio
    cmd = f"ffprobe -i {archivo} -show_entries format=duration -v quiet -of csv='p=0'"
    resultado = subprocess.check_output(cmd, shell=True)
    return float(resultado)

def buscar_y_descargar_exacto(query, api_key, segundos_totales):
    busqueda_real = next((v for k, v in TRADUCTOR.items() if k in query.lower()), query)
    # Pedimos muchos resultados para tener de donde elegir
    url = f"https://api.pexels.com/videos/search?query={busqueda_real}&per_page=40&orientation=portrait"
    descargados = []
    segundos_acumulados = 0
    
    try:
        res = requests.get(url, headers={"Authorization": api_key.strip()})
        videos = res.json().get('videos', [])
        random.shuffle(videos)
        
        for i, v in enumerate(videos):
            if segundos_acumulados >= segundos_totales:
                break
            
            duracion_clip = v.get('duration', 10)
            link = v['video_files'][0]['link']
            nombre = f"clip_{i}.mp4"
            
            with open(nombre, 'wb') as f:
                f.write(requests.get(link).content)
            
            descargados.append(nombre)
            segundos_acumulados += duracion_clip
            
        return descargados
    except:
        return []

with st.sidebar:
    st.title("⚙️ Ajustes")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.color_picker("🎨 Color Sub", "#00FFFF")
    hc = color_sub.lstrip('#')
    ass_color = f"&H00{hc[4:6]}{hc[2:4]}{hc[0:2]}"
    voz = st.selectbox("🗣️ Voz", ["es-ES-AlvaroNeural", "es-MX-JorgeNeural"])

st.title("🎬 Fénix AI: Duración Inteligente")

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [{"role": "assistant", "content": "¡Hola! Escribe un guion de la duración que quieras. Yo buscaré los vídeos necesarios para cubrirlo todo sin repetir."}]

for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "video" in msg:
            with open(msg["video"], "rb") as f:
                st.video(f.read())
                st.download_button(f"📥 Descargar Vídeo ({msg['duracion']}s)", f, file_name="Fenix_Pro.mp4")

if user_input := st.chat_input("Pega tu historia aquí..."):
    st.session_state.mensajes.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.status("🎯 Calculando montaje perfecto...", expanded=True) as status:
            uid = int(time.time())
            v_final = f"output/v_{uid}.mp4"
            
            status.write("🔊 Generando audio...")
            subprocess.run(f'edge-tts --voice {voz} --text "{user_input}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
            
            duracion_audio = obtener_duracion("t.mp3")
            status.write(f"⏱️ El vídeo durará {duracion_audio:.1f} segundos.")
            
            status.write("🌎 Buscando clips únicos para cubrir el tiempo...")
            clips = buscar_y_descargar_exacto(user_input, pexels_key, duracion_audio)
            
            if clips:
                status.write(f"🎞️ Procesando {len(clips)} clips únicos...")
                for i, c in enumerate(clips):
                    subprocess.run(f'ffmpeg -y -i "{c}" -vf "scale=480:854:force_original_aspect_ratio=increase,crop=480:854,fps=30" -c:v libx264 -preset ultrafast -crf 30 "p_{i}.mp4"', shell=True)
                
                with open("lista.txt", "w") as f:
                    for i in range(len(clips)): f.write(f"file 'p_{i}.mp4'\n")
                
                status.write("🎬 Uniendo y ajustando al audio...")
                # Unimos todos los clips descargados
                subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)
                
                # Montaje final con subtítulos (sin repetir, cortado al audio)
                est = f"Fontname=Impact,FontSize=26,PrimaryColour={ass_color},Outline=2,Alignment=2,MarginV=120"
                cmd = f'ffmpeg -y -i base.mp4 -i t.mp3 -vf "subtitles=t.vtt:force_style=\'{est}\'" -c:v libx264 -preset superfast -shortest "{v_final}"'
                subprocess.run(cmd, shell=True)
                
                st.session_state.mensajes.append({
                    "role": "assistant", 
                    "content": f"✅ Montaje finalizado con {len(clips)} escenas únicas.", 
                    "video": v_final,
                    "duracion": round(duracion_audio, 1)
                })
                st.rerun()
            else:
                st.error("No se pudieron obtener clips.")
