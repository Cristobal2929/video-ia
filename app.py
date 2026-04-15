import streamlit as st
import os, time, random, subprocess, re, requests

st.set_page_config(page_title="Fénix Studio Final", layout="centered")
st.markdown("<style>.stApp {background: #0d1117; color: white;}</style>", unsafe_allow_html=True)

def crear_guion_y_keywords(tema):
    t = tema.lower()
    if "terror" in t:
        guion = "Todo empezó con un susurro en aquella casa abandonada. Una sombra alta apareció al final del pasillo. El bosque oculta secretos oscuros que nadie debería conocer."
        keys = ["abandoned house", "creepy shadow", "dark hallway", "forest night"]
        return guion, keys
    elif "humor" in t:
        guion = "La vida es un chiste constante. ¿Por qué buscamos el móvil con la linterna del móvil encendida? Somos expertos en complicarnos la vida de la forma más tonta posible."
        keys = ["funny accident", "laughing people", "clumsy person", "funny cat"]
        return guion, keys
    return f"Bienvenidos a {tema}. Un viaje increible por detalles que no conocías.", [t, f"{t} cinematic"]

def buscar_vids(keywords, api_key, status):
    desc = []
    for i, word in enumerate(keywords):
        status.write(f"🔍 Buscando imagen para: {word}...")
        url = f"https://api.pexels.com/videos/search?query={word}&per_page=1&orientation=portrait"
        try:
            res = requests.get(url, headers={"Authorization": api_key.strip()}, timeout=10).json()
            if res.get('videos'):
                v_url = res['videos'][0]['video_files'][0]['link']
                with open(f"clip_{i}.mp4", 'wb') as f: f.write(requests.get(v_url).content)
                desc.append(f"clip_{i}.mp4")
        except: continue
    return desc

st.title("🎬 Fénix Studio: Versión Final")

with st.sidebar:
    st.header("Ajustes")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.color_picker("🎨 Color Sub", "#FFFF00")
    hc = color_sub.lstrip('#')
    ass_col = f"&H00{hc[4:6]}{hc[2:4]}{hc[0:2]}"

if user_input := st.chat_input("Dime el tema (Terror, Humor...)"):
    with st.status("🦅 El Fénix está trabajando...", expanded=True) as status:
        # 1. Limpieza
        status.write("🧹 Limpiando mesa de trabajo...")
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.* outro.mp4 music.mp3", shell=True)
        
        guion, keys = crear_guion_y_keywords(user_input)
        v_final = f"output/v_{int(time.time())}.mp4"
        
        # 2. Voz
        status.write("🎙️ Grabando voz del narrador...")
        subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --text "{guion}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
        dur = float(subprocess.check_output("ffprobe -i t.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True))
        
        # 3. Clips
        clips = buscar_vids(keys, pexels_key, status)
        
        if clips:
            status.write("✂️ Ajustando clips y formato...")
            # Transformar SRT (subtítulos)
            with open("t.vtt", 'r') as f: lines = f.readlines()
            # Simplificamos el VTT a SRT básico para evitar errores
            subprocess.run("ffmpeg -y -i t.vtt t.srt", shell=True)
            
            for i, c in enumerate(clips):
                subprocess.run(f'ffmpeg -y -i "{c}" -vf "scale=480:854:force_original_aspect_ratio=increase,crop=480:854,fps=25" -an -c:v libx264 -preset ultrafast "p_{i}.mp4"', shell=True)
            
            # 4. Sello Final
            status.write("🎨 Creando sello Fénix Studio...")
            subprocess.run('ffmpeg -y -f lavfi -i color=c=black:s=480x854:d=2.5:r=25 -vf "drawtext=text=\'FENIX STUDIO 🦅\':fontcolor=white:fontsize=40:x=(w-tw)/2:y=(h-th)/2" -c:v libx264 -preset ultrafast outro.mp4', shell=True)
            
            with open("lista.txt", "w") as f:
                for i in range(len(clips)): f.write(f"file 'p_{i}.mp4'\n")
                f.write("file 'outro.mp4'\n")
            
            subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)
            
            # 5. Música
            status.write("🎵 Añadiendo música de fondo...")
            m_url = "https://www.bensound.com/bensound-music/bensound-creativeminds.mp3"
            try:
                r = requests.get(m_url, timeout=5)
                with open("music.mp3", "wb") as f: f.write(r.content)
            except:
                subprocess.run('ffmpeg -y -f lavfi -i anullsrc=r=44100:cl=mono -t 30 music.mp3', shell=True)

            # 6. Mezcla Final
            status.write("🧪 Mezclando todo el material...")
            est = f"Fontname=Impact,FontSize=30,PrimaryColour={ass_col},Outline=3,Alignment=2,MarginV=140"
            cmd = (
                f'ffmpeg -y -i base.mp4 -i t.mp3 -i music.mp3 -filter_complex '
                f'"[1:a]volume=3.0[v];[2:a]volume=0.2,afade=t=out:st={dur}:d=2[m];[v][m]amix=inputs=2:duration=first" '
                f'-vf "subtitles=t.srt:force_style=\'{est}\'" '
                f'-c:v libx264 -preset ultrafast -shortest -c:a aac -b:a 128k "{v_final}"'
            )
            subprocess.run(cmd, shell=True)
            
            if os.path.exists(v_final):
                status.write("✨ ¡Vídeo completado con éxito!")
                st.video(v_final)
                st.balloons()
            else:
                st.error("❌ Algo falló en la mezcla final.")
