import streamlit as st
import os, time, random, subprocess, re, requests

st.set_page_config(page_title="Fénix RAM Saver", layout="centered")
st.markdown("<style>.stApp {background: #0d1117; color: white;}</style>", unsafe_allow_html=True)

def buscar_vids(keywords, api_key, status):
    desc = []
    for i, word in enumerate(keywords):
        status.write(f"🔍 Buscando: {word}")
        url = f"https://api.pexels.com/videos/search?query={word}&per_page=1&orientation=portrait"
        try:
            res = requests.get(url, headers={"Authorization": api_key.strip()}, timeout=10).json()
            if res.get('videos'):
                v_url = res['videos'][0]['video_files'][0]['link']
                with open(f"clip_{i}.mp4", 'wb') as f: f.write(requests.get(v_url).content)
                desc.append(f"clip_{i}.mp4")
        except: continue
    return desc

st.title("🎬 Fénix Studio: Optimizado")

with st.sidebar:
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.color_picker("🎨 Color Sub", "#FFFF00")
    hc = color_sub.lstrip('#')
    ass_col = f"&H00{hc[4:6]}{hc[2:4]}{hc[0:2]}"

if user_input := st.chat_input("Tema del vídeo..."):
    with st.status("🦅 Ahorrando RAM para que no falle...", expanded=True) as status:
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.* outro.mp4 final.mp4 temp_v.mp4", shell=True)
        
        # 1. Historia (Lógica fija para no fallar)
        guion = "Todo empezó con un susurro en aquella casa abandonada. Una sombra alta apareció al final del pasillo. El bosque oculta secretos oscuros."
        keys = ["abandoned house", "creepy shadow", "dark hallway", "forest night"]
        v_final = f"output/v_{int(time.time())}.mp4"
        
        # 2. Voz y SRT
        status.write("🎙️ Generando audio...")
        subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --text "{guion}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
        subprocess.run("ffmpeg -y -i t.vtt t.srt", shell=True)
        
        # 3. Preparar clips (Poco a poco)
        clips = buscar_vids(keys, pexels_key, status)
        if clips:
            status.write("✂️ Procesando clips individualmente...")
            for i, c in enumerate(clips):
                subprocess.run(f'ffmpeg -y -i "{c}" -vf "scale=480:854:force_original_aspect_ratio=increase,crop=480:854,fps=25" -an -c:v libx264 -preset superfast "p_{i}.mp4"', shell=True)
            
            # Outro ligero
            subprocess.run('ffmpeg -y -f lavfi -i color=c=black:s=480x854:d=2:r=25 -vf "drawtext=text=\'FENIX STUDIO\':fontcolor=white:fontsize=40:x=(w-tw)/2:y=(h-th)/2" -c:v libx264 -preset superfast outro.mp4', shell=True)
            
            # Unir vídeo MUDO primero (Ahorra mucha RAM)
            with open("lista.txt", "w") as f:
                for i in range(len(clips)): f.write(f"file 'p_{i}.mp4'\n")
                f.write("file 'outro.mp4'\n")
            subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy temp_v.mp4', shell=True)
            
            # 4. PASO FINAL: Mezclar audio y subtítulos al vídeo ya unido
            status.write("🧪 Mezclando audio final (Paso ligero)...")
            est = f"Fontname=Impact,FontSize=30,PrimaryColour={ass_col},Outline=3,Alignment=2,MarginV=140"
            cmd = f'ffmpeg -y -i temp_v.mp4 -i t.mp3 -vf "subtitles=t.srt:force_style=\'{est}\'" -c:v libx264 -preset ultrafast -shortest -c:a aac -af "volume=2.5" "{v_final}"'
            subprocess.run(cmd, shell=True)
            
            if os.path.exists(v_final):
                st.video(v_final)
                st.success("¡CONSEGUIDO!")
            else:
                st.error("Incluso con ahorro de RAM falló. Prueba un tema más corto.")
