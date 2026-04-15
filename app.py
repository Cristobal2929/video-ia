import streamlit as st
import os, time, random, subprocess, re, requests

st.set_page_config(page_title="Fénix Viral 30s", layout="centered")
st.markdown("<style>.stApp {background: #0d1117; color: white;}</style>", unsafe_allow_html=True)

# --- IA CON GUION LARGO Y COHERENTE ---
def obtener_guion_largo(tema):
    try:
        # Pedimos a la IA una historia de 30 segundos con 4 conceptos clave
        prompt = f"Escribe una historia viral de {tema} para un video de 30 segundos. Debe ser impactante y tener 4 partes claras. Devuelve solo el texto en MAYUSCULAS, sin signos de puntuacion."
        url = f"https://sentence.fineshopdesign.com/api/ai?prompt={prompt}"
        res = requests.get(url, timeout=15).json()
        guion = res.get("reply", "").upper()
        if len(guion) < 50: raise Exception("Muy corto")
        return guion
    except:
        return f"SABIAS QUE EL MUNDO DE {tema.upper()} ESCONDE UN SECRETO QUE HA SIDO GUARDADO POR GENERACIONES. LO QUE ESTAS A PUNTO DE VER NO ES UNA COINCIDENCIA SINO UN PLAN MAESTRO PARA OCULTAR LA VERDAD MAS PERTURBADORA DE NUESTRA ERA. PRESTA MUCHA ATENCION PORQUE ESTO PODRIA CAMBIAR TU FORMA DE VER LA REALIDAD PARA SIEMPRE."

st.title("🦅 Fénix Studio: Viral 30-40s")

with st.sidebar:
    st.header("Ajustes")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.selectbox("🎨 Color Texto", ["yellow", "white", "cyan"])

if user_input := st.chat_input("Dime el tema (Terror, Historia, Espacio...)"):
    with st.status("🧠 La IA está redactando una super historia...", expanded=True) as status:
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.mp3 music.mp3 final.mp4 temp_a.mp3 lista.txt", shell=True)
        
        guion = obtener_guion_largo(user_input)
        status.write(f"✍️ Historia de {user_input} lista.")
        
        # 1. AUDIO LARGO
        status.write("🎙️ Generando voz y ambiente...")
        subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --text "{guion}" --write-media "t.mp3"', shell=True)
        dur = float(subprocess.check_output("ffprobe -i t.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True))
        
        # Generar audio rítmico interno (más estable)
        subprocess.run(f'ffmpeg -y -f lavfi -i "sine=frequency=80:duration={dur+2}" -f lavfi -i "anoisesrc=d={dur+2}:c=pink:a=0.02" -filter_complex "[0:a]volume=0.5[t];[1:a]volume=0.1[n];[t][n]amix=inputs=2:duration=first" music.mp3', shell=True)
        subprocess.run(f'ffmpeg -y -i t.mp3 -i music.mp3 -filter_complex "[0:a]volume=2.8[v];[1:a]volume=0.3[m];[v][m]amix=inputs=2:duration=first" temp_a.mp3', shell=True)

        # 2. ESCENAS COHERENTES (6 clips para 30-40 segundos)
        processed_clips = []
        # Extraemos palabras clave del guion para que las imágenes peguen
        palabras_guion = [p for p in guion.split() if len(p) > 5]
        for i in range(6): 
            key = random.choice(palabras_guion) if palabras_guion else user_input
            status.write(f"🎞️ Buscando clip {i+1} sobre: {key}...")
            url = f"https://api.pexels.com/videos/search?query={key}&per_page=1&orientation=portrait"
            res = requests.get(url, headers={"Authorization": pexels_key.strip()}, timeout=10).json()
            
            if res.get('videos'):
                v_url = res['videos'][0]['video_files'][0]['link']
                with open(f"clip_{i}.mp4", 'wb') as f: f.write(requests.get(v_url).content)
                # Zoom pan y escalado
                subprocess.run(f'ffmpeg -y -i "clip_{i}.mp4" -vf "scale=1280:-1,zoompan=z=\'min(zoom+0.001,1.3)\':d=125:x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):s=480x854,fps=25" -an -c:v libx264 -preset superfast -t {dur/6 + 0.5} "p_{i}.mp4"', shell=True)
                processed_clips.append(f"p_{i}.mp4")
                os.remove(f"clip_{i}.mp4")

        # UNIÓN Y SUBS
        if processed_clips:
            with open("lista.txt", "w") as f:
                for p in processed_clips: f.write(f"file '{p}'\n")
            subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)

            status.write("✨ Montando subtítulos dinámicos...")
            palabras = guion.split()
            segs = [" ".join(palabras[i:i+2]) for i in range(0, len(palabras), 2)]
            dur_seg = dur / len(segs)
            
            filter_c = ""
            for i, s in enumerate(segs):
                start, end = i * dur_seg, (i + 1) * dur_seg
                filter_c += f"drawtext=text='{s}':fontcolor={color_sub}:fontsize=36:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:borderw=4:bordercolor=black:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{start},{end})',"
            
            v_final = f"output/v_{int(time.time())}.mp4"
            cmd = f'ffmpeg -y -i base.mp4 -i temp_a.mp3 -vf "{filter_c.rstrip(",")}" -c:v libx264 -preset ultrafast -b:v 1200k -shortest "{v_final}"'
            subprocess.run(cmd, shell=True)
            
            if os.path.exists(v_final):
                st.video(v_final)
                st.success(f"🔥 ¡Vídeo de {int(dur)}s completado!")
