import streamlit as st
import os, time, random, subprocess, re, requests

st.set_page_config(page_title="Fénix Viral Master", layout="centered")
st.markdown("<style>.stApp {background: #0d1117; color: white;}</style>", unsafe_allow_html=True)

# --- IA CON ESTRUCTURA VIRAL ---
def obtener_guion_viral(tema):
    try:
        # Prompt optimizado para retención: Gancho -> Historia -> Giro -> CTA
        prompt = f"Escribe un guion viral de 80 palabras sobre {tema}. Estructura: 1. Gancho impactante. 2. Historia increible con datos reales. 3. Final sorprendente. Todo en ESPAÑOL y MAYUSCULAS."
        url = f"https://sentence.fineshopdesign.com/api/ai?prompt={prompt}"
        res = requests.get(url, timeout=15).json()
        guion = res.get("reply", "").upper().replace('"', '').replace("'", "")
        if len(guion) < 100: raise Exception("IA perezosa")
        return guion
    except:
        return f"¿SABIAS QUE EL MUNDO DE {tema.upper()} ESCONDE UN SECRETO QUE HA SIDO GUARDADO POR GENERACIONES? LO QUE ESTAS A PUNTO DE VER NO ES UNA COINCIDENCIA SINO UN PLAN MAESTRO PARA OCULTAR LA VERDAD MAS PERTURBADORA DE NUESTRA ERA. PRESTA MUCHA ATENCION PORQUE ESTO PODRIA CAMBIAR TU FORMA DE VER LA REALIDAD PARA SIEMPRE. SIGUENOS PARA DESCUBRIR LA VERDAD OCULTA."

st.title("🦅 Fénix Studio: Viral Master")

with st.sidebar:
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.selectbox("🎨 Color Subtítulos", ["yellow", "white", "cyan"])

if user_input := st.chat_input("¿Qué tema quieres hacer viral hoy?"):
    with st.status("🎬 Produciendo vídeo de alta retención...", expanded=True) as status:
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.mp3 music.mp3 final.mp4 temp_a.mp3 lista.txt", shell=True)
        
        guion = obtener_guion_viral(user_input)
        status.write("✍️ Guion viral generado.")
        
        # 1. AUDIO (Voz + Música Cinematic)
        subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --text "{guion}" --write-media "t.mp3"', shell=True)
        dur = float(subprocess.check_output("ffprobe -i t.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True))
        
        # Música de ambiente cinemático generada
        subprocess.run(f'ffmpeg -y -f lavfi -i "sine=frequency=70:duration={dur+5}" -f lavfi -i "anoisesrc=d={dur+5}:c=pink:a=0.03" -filter_complex "[0:a]volume=0.6[t];[1:a]volume=0.1[n];[t][n]amix=inputs=2:duration=first" music.mp3', shell=True)
        subprocess.run(f'ffmpeg -y -i t.mp3 -i music.mp3 -filter_complex "[0:a]volume=3.0[v];[1:a]volume=0.4[m];[v][m]amix=inputs=2:duration=first" temp_a.mp3', shell=True)

        # 2. ESCENAS (10 clips rápidos = Máxima Retención)
        processed_clips = []
        palabras_claves = [p for p in guion.split() if len(p) > 6]
        random.shuffle(palabras_claves)
        
        for i in range(10): 
            k = palabras_claves[i % len(palabras_claves)] if palabras_claves else user_input
            status.write(f"🎞️ Editando escena {i+1}...")
            url = f"https://api.pexels.com/videos/search?query={k}&per_page=1&orientation=portrait"
            res = requests.get(url, headers={"Authorization": pexels_key.strip()}, timeout=10).json()
            
            if res.get('videos'):
                v_url = res['videos'][0]['video_files'][0]['link']
                with open(f"clip_{i}.mp4", 'wb') as f: f.write(requests.get(v_url).content)
                # Zoom suave y escalado rápido
                subprocess.run(f'ffmpeg -y -i "clip_{i}.mp4" -vf "scale=1280:-1,zoompan=z=\'min(zoom+0.0012,1.4)\':d=125:x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):s=480x854,fps=25" -an -c:v libx264 -preset superfast -t {dur/10 + 1} "p_{i}.mp4"', shell=True)
                processed_clips.append(f"p_{i}.mp4")
                os.remove(f"clip_{i}.mp4")

        # UNIÓN CON SALIDA ASEGURADA
        if processed_clips:
            with open("lista.txt", "w") as f:
                for p in processed_clips: f.write(f"file '{p}'\n")
            subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)

            # 3. SUBTÍTULOS DINÁMICOS (Una sola palabra para máximo impacto)
            status.write("✨ Quemando subtítulos de alto impacto...")
            palabras = guion.split()
            dur_p = dur / len(palabras)
            
            filter_complex = ""
            for i, p in enumerate(palabras):
                start, end = i * dur_p, (i + 1) * dur_p
                filter_complex += f"drawtext=text='{p}':fontcolor={color_sub}:fontsize=45:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:borderw=5:bordercolor=black:shadowcolor=black:shadowx=2:shadowy=2:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{start},{end})',"
            
            v_final = f"output/v_{int(time.time())}.mp4"
            # Mezcla final: Video base + Audio Mezclado + Subs Dinámicos
            cmd = f'ffmpeg -y -i base.mp4 -i temp_a.mp3 -vf "{filter_complex.rstrip(",")}" -c:v libx264 -preset ultrafast -b:v 1500k -shortest "{v_final}"'
            subprocess.run(cmd, shell=True)
            
            if os.path.exists(v_final):
                st.video(v_final)
                st.success(f"🔥 VÍDEO VIRAL DE {int(dur)} SEGUNDOS LISTO.")
                st.balloons()
