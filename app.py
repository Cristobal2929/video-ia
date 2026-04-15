import streamlit as st
import os, time, random, subprocess, re, requests

st.set_page_config(page_title="Fénix Studio Ultra", layout="centered", page_icon="🎬")
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

def buscar_vids(keywords, api_key):
    desc = []
    for i, word in enumerate(keywords):
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
    with st.status("🦅 El Fénix está creando tu vídeo...", expanded=True):
        # 1. Limpieza
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.* outro.mp4 music.mp3", shell=True)
        
        guion, keys = crear_guion_y_keywords(user_input)
        v_final = f"output/v_{int(time.time())}.mp4"
        
        # 2. Voz y Duración
        subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --text "{guion}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
        dur = float(subprocess.check_output("ffprobe -i t.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True))
        
        # 3. Clips
        clips = buscar_vids(keys, pexels_key)
        if clips:
            transformar_srt("t.vtt", "t.srt")
            for i, c in enumerate(clips):
                subprocess.run(f'ffmpeg -y -i "{c}" -vf "scale=480:854:force_original_aspect_ratio=increase,crop=480:854,fps=25" -an -c:v libx264 -preset ultrafast "p_{i}.mp4"', shell=True)
            
            # 4. Sello Final (Outro de 2.5 seg)
            subprocess.run('ffmpeg -y -f lavfi -i color=c=black:s=480x854:d=2.5:r=25 -vf "drawtext=text=\'FENIX STUDIO 🦅\':fontcolor=white:fontsize=45:x=(w-tw)/2:y=(h-th)/2" -c:v libx264 -preset ultrafast outro.mp4', shell=True)
            
            with open("lista.txt", "w") as f:
                for i in range(len(clips)): f.write(f"file 'p_{i}.mp4'\n")
                f.write("file 'outro.mp4'\n")
            
            subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)
            
            # 5. Música de Fondo (Descarga rápida de Bensound o similar)
            m_url = "https://www.bensound.com/bensound-music/bensound-creativeminds.mp3"
            try:
                with open("music.mp3", "wb") as f: f.write(requests.get(m_url, timeout=5).content)
            except:
                # Si falla la descarga, genera un silencio para que no rompa el comando
                subprocess.run('ffmpeg -y -f lavfi -i anullsrc=r=44100:cl=mono -t 30 music.mp3', shell=True)

            # 6. Mezcla Maestra: Voz + Música + Subtítulos + Sello
            est = f"Fontname=Impact,FontSize=32,PrimaryColour={ass_col},Outline=4,Alignment=2,MarginV=140"
            cmd = (
                f'ffmpeg -y -i base.mp4 -i t.mp3 -i music.mp3 -filter_complex '
                f'"[1:a]volume=3.0[v];[2:a]volume=0.2,afade=t=out:st={dur}:d=2[m];[v][m]amix=inputs=2:duration=first" '
                f'-vf "subtitles=t.srt:force_style=\'{est}\'" '
                f'-c:v libx264 -preset ultrafast -shortest -c:a aac -b:a 128k "{v_final}"'
            )
            subprocess.run(cmd, shell=True)
            
            if os.path.exists(v_final):
                st.video(v_final)
                st.balloons()
