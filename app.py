import streamlit as st
import os, time, random, subprocess, re, requests

st.set_page_config(page_title="Fénix Viral Studio", layout="centered")
st.markdown("<style>.stApp {background: #0d1117; color: white;}</style>", unsafe_allow_html=True)

def generar_guion_pro(tema):
    t = tema.lower()
    if "terror" in t:
        return "Hay lugares que esconden secretos oscuros. Sombras que te observan desde el silencio de una casa abandonada. Lo que veras hoy te quitara el sueño."
    return f"¿Sabias esto sobre {tema}? El mundo esconde secretos que pocos conocen. Prepárate porque esto te va a volar la cabeza."

st.title("🎬 Fénix Studio: Subtítulos Garantizados")

with st.sidebar:
    st.header("Personalización")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.selectbox("🎨 Color Texto", ["yellow", "white", "red", "cyan"])

if user_input := st.chat_input("Dime el tema..."):
    with st.status("🎬 Creando vídeo con subtítulos directos...", expanded=True) as status:
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.* outro.mp4 final.mp4", shell=True)
        
        guion = generar_guion_pro(user_input)
        v_final = f"output/v_{int(time.time())}.mp4"
        
        # 1. Voz
        status.write("🎙️ Grabando voz...")
        subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --text "{guion}" --write-media "t.mp3"', shell=True)
        
        # 2. Clips
        url = f"https://api.pexels.com/videos/search?query={user_input}&per_page=4&orientation=portrait"
        res = requests.get(url, headers={"Authorization": pexels_key.strip()}).json()
        vids = res.get('videos', [])
        
        for i, v in enumerate(vids):
            status.write(f"🎞️ Procesando escena {i+1}...")
            with open(f"clip_{i}.mp4", 'wb') as f: f.write(requests.get(v['video_files'][0]['link']).content)
            # Formateamos y quitamos audio original
            subprocess.run(f'ffmpeg -y -i "clip_{i}.mp4" -vf "scale=480:854:force_original_aspect_ratio=increase,crop=480:854,fps=25" -an -c:v libx264 -preset ultrafast "p_{i}.mp4"', shell=True)
        
        # Outro
        subprocess.run('ffmpeg -y -f lavfi -i color=c=black:s=480x854:d=2:r=25 -vf "drawtext=text=\'FENIX STUDIO 🦅\':fontcolor=white:fontsize=40:x=(w-tw)/2:y=(h-th)/2" -c:v libx264 -preset ultrafast outro.mp4', shell=True)
        
        with open("lista.txt", "w") as f:
            for i in range(len(vids)): f.write(f"file 'p_{i}.mp4'\n")
            f.write("file 'outro.mp4'\n")
        subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)

        # 3. MEZCLA FINAL: Dibujamos el texto palabra por palabra
        status.write("✨ Escribiendo subtítulos en el vídeo...")
        
        # Dividimos el guion en trozos para que no sea una línea gigante
        palabras = guion.upper().split()
        segmentos = [" ".join(palabras[i:i+3]) for i in range(0, len(palabras), 3)]
        
        # Creamos el filtro de texto dinámico (Alex Hormozi Style)
        filter_text = ""
        dur_segmento = 2.0 # Cada 3 palabras duran 2 segundos en pantalla
        for i, seg in enumerate(segmentos):
            start = i * dur_segmento
            end = start + dur_segmento
            # Dibujamos cada trozo con borde y sombra
            filter_text += f"drawtext=text='{seg}':fontcolor={color_sub}:fontsize=35:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:borderw=3:bordercolor=black:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{start},{end})',"
        
        filter_text = filter_text.rstrip(',')
        
        # Comando final: Une el vídeo base con el audio y le dibuja el texto encima
        cmd = f'ffmpeg -y -i base.mp4 -i t.mp3 -vf "{filter_text}" -c:v libx264 -preset ultrafast -c:a aac -map 0:v:0 -map 1:a:0 -shortest "{v_final}"'
        subprocess.run(cmd, shell=True)
        
        if os.path.exists(v_final):
            st.video(v_final)
            st.success("🔥 ¡VÍDEO CON SUBTÍTULOS ASEGURADOS!")
        else:
            st.error("Error al generar. Inténtalo de nuevo.")
