import streamlit as st
import os, time, random, subprocess, re, requests

st.set_page_config(page_title="Fénix Viral Studio", layout="centered")
st.markdown("<style>.stApp {background: #0d1117; color: white;}</style>", unsafe_allow_html=True)

def obtener_guion_viral(tema):
    # Generamos un guion con "gancho" inicial (Hook)
    hooks = [
        f"¿Sabías esto sobre {tema}?",
        f"Lo que nadie te cuenta de {tema}...",
        f"Prepárate, porque esto de {tema} te va a volar la cabeza."
    ]
    desarrollo = f"El mundo de {tema} esconde secretos que pocos conocen. Desde detalles que parecen insignificantes hasta grandes hitos que cambiaron las reglas del juego."
    final = f"Si te apasiona {tema}, síguenos para más contenido increíble. ¡No te lo pierdas!"
    
    # Si es un nicho específico, personalizamos un poco más
    t = tema.lower()
    if "terror" in t:
        return "Hay lugares que nunca deberían ser visitados. Sombras que cobran vida cuando apagas la luz y susurros que te llaman por tu nombre desde el pasillo. Lo que vas a ver hoy, te quitará el sueño para siempre."
    if "coche" in t:
        return "El rugido de un motor es música para los oídos. La mezcla perfecta entre ingeniería, potencia y libertad absoluta. Hoy verás máquinas que desafían las leyes de la física sobre el asfalto."
        
    return f"{random.choice(hooks)} {desarrollo} {final}"

def buscar_vids_pro(query, api_key, status):
    status.write(f"🎞️ Buscando escenas virales para: {query}...")
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=12&orientation=portrait"
    desc = []
    try:
        res = requests.get(url, headers={"Authorization": api_key.strip()}, timeout=10).json()
        vids = res.json().get('videos', []) if 'videos' in res else res.get('videos', [])
        random.shuffle(vids)
        for i, v in enumerate(vids[:8]): # Usamos más clips
            with open(f"clip_{i}.mp4", 'wb') as f: f.write(requests.get(v['video_files'][0]['link']).content)
            desc.append(f"clip_{i}.mp4")
        return desc
    except: return []

st.title("🦅 Fénix Viral Studio")

with st.sidebar:
    st.header("Configuración")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.color_picker("🎨 Color Sub", "#FFFF00")
    hc = color_sub.lstrip('#')
    ass_col = f"&H00{hc[4:6]}{hc[2:4]}{hc[0:2]}"

if user_input := st.chat_input("¿De qué nicho quieres el vídeo viral?"):
    with st.status("🎬 Editando vídeo de alto impacto...", expanded=True) as status:
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.* outro.mp4 final.mp4 temp_v.mp4 bg.mp3", shell=True)
        
        guion = obtener_guion_viral(user_input)
        v_final = f"output/v_{int(time.time())}.mp4"
        
        # 1. Voz y Subtítulos Dinámicos
        status.write("🎙️ Grabando voz narrativa...")
        subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --text "{guion}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
        subprocess.run("ffmpeg -y -i t.vtt t.srt", shell=True)
        dur = float(subprocess.check_output("ffprobe -i t.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True))
        
        # 2. Clips con Zoom Dinámico
        clips = buscar_vids_pro(user_input, pexels_key, status)
        if clips:
            status.write("✂️ Aplicando efectos visuales y cortes rápidos...")
            for i, c in enumerate(clips):
                # Aplicamos un pequeño zoom-in dinámico para que la imagen no sea estática
                subprocess.run(f'ffmpeg -y -i "{c}" -vf "scale=800:-1,zoompan=z=\'zoom+0.001\':d=125:x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):s=480x854,fps=25" -an -c:v libx264 -preset ultrafast -t {dur/len(clips)+0.5} "p_{i}.mp4"', shell=True)
            
            # Sello Fénix
            subprocess.run('ffmpeg -y -f lavfi -i color=c=black:s=480x854:d=2:r=25 -vf "drawtext=text=\'FENIX STUDIO 🦅\':fontcolor=white:fontsize=45:x=(w-tw)/2:y=(h-th)/2" -c:v libx264 -preset ultrafast outro.mp4', shell=True)
            
            with open("lista.txt", "w") as f:
                for i in range(len(clips)): f.write(f"file 'p_{i}.mp4'\n")
                f.write("file 'outro.mp4'\n")
            subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy temp_v.mp4', shell=True)
            
            # 3. Música según Nicho
            status.write("🎵 Mezclando música y audio...")
            m_url = "https://www.bensound.com/bensound-music/bensound-evolution.mp3" # Épica/Moderna
            try:
                with open("bg.mp3", "wb") as f: f.write(requests.get(m_url, timeout=5).content)
            except:
                subprocess.run('ffmpeg -y -f lavfi -i anullsrc=r=44100:cl=mono -t 30 bg.mp3', shell=True)

            # 4. Render Final
            est = f"Fontname=Impact,FontSize=32,PrimaryColour={ass_col},Outline=4,Alignment=2,MarginV=150"
            cmd = f'ffmpeg -y -i temp_v.mp4 -i t.mp3 -i bg.mp3 -filter_complex "[1:a]volume=2.5[v];[2:a]volume=0.25,afade=t=out:st={dur}:d=2[m];[v][m]amix=inputs=2:duration=first" -vf "subtitles=t.srt:force_style=\'{est}\'" -c:v libx264 -preset ultrafast -shortest -c:a aac -b:a 128k "{v_final}"'
            subprocess.run(cmd, shell=True)
            
            if os.path.exists(v_final):
                st.video(v_final)
                st.success("🔥 ¡Vídeo Viral Generado!")
                st.balloons()
