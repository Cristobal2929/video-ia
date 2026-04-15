import streamlit as st
import os, time, random, subprocess, re, requests

st.set_page_config(page_title="Fénix AI Ultra", layout="centered")
st.markdown("<style>.stApp {background: #0d1117; color: white;}</style>", unsafe_allow_html=True)

def obtener_guion_ia(tema):
    try:
        # Prompt en inglés suele dar respuestas más rápidas y cortas
        prompt = f"Write a very short, viral TikTok story (max 35 words) about {tema} that hooks instantly. Use Spanish, ALL CAPS, no dots or commas."
        # Cambiamos a una API de inferencia gratuita más rápida y fiable
        url = f"https://sentence.fineshopdesign.com/api/ai?prompt={prompt}"
        res = requests.get(url, timeout=10).json()
        return res.get("reply", "").upper()
    except:
        return f"SABIAS QUE EL MUNDO DE {tema.upper()} ESCONDE UN SECRETO QUE PODRIA CAMBIAR TU VIDA PARA SIEMPRE PRESTA ATENCION AL FINAL."

st.title("🦅 Fénix AI: Edición Blindada")

with st.sidebar:
    st.header("Ajustes")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.selectbox("🎨 Color Texto", ["yellow", "white", "cyan"])

if user_input := st.chat_input("Dime el tema..."):
    with st.status("🧠 La IA está pensando tu historia...", expanded=True) as status:
        # Limpieza total inicial
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.mp3 music.mp3 final.mp4 temp_v.mp4 temp_a.mp3 lista.txt", shell=True)
        
        guion = obtener_guion_ia(user_input)
        # Limpiamos el guion de comillas que puedan romper el comando edge-tts
        guion = guion.replace('"', '').replace("'", "")
        status.write(f"✍️ Guion generado: {guion[:50]}...")
        
        # 1. AUDIO SEGURO (Generación Interna de Tono Rítmico)
        status.write("🎙️ Generando voz y audio de fondo (modo seguro)...")
        # Generar voz edge-tts
        try:
            subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --text "{guion}" --write-media "t.mp3"', shell=True)
            # Sacar duración exacta
            dur = float(subprocess.check_output("ffprobe -i t.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True))
        except:
            st.error("Error al generar la voz de la IA. Prueba de nuevo.")
            st.stop()
        
        # 2. GENERAR MÚSICA DE FONDO RÍTMICA INTERNAMENTE CON FFMPEG
        # Usamos lavfi para crear un tono bajo y un ruido de fondo que parezca un latido/pulso misterioso
        # -t es la duración exacta del audio de la voz
        tono = 110 # Tono bajo misterioso
        if "terror" in user_input.lower(): tono = 60 # Tono más bajo para terror
        
        # Generamos un sonido de 10s para cubrir el audio (aunque dure menos, shortest lo corta)
        subprocess.run(f'ffmpeg -y -f lavfi -i "sine=frequency={tono}:duration=10:sample_rate=44100" -f lavfi -i "anoisesrc=d=10:c=pink:r=44100:a=0.01" -filter_complex "[0:a]volume=0.8,afade=t=in:st=0:d=1,afade=t=out:st=8:d=2[t];[1:a]volume=0.2[n];[t][n]amix=inputs=2:duration=first" music.mp3', shell=True)
        
        # Mezclamos voz (2.5x) y música generada (0.2x)
        subprocess.run(f'ffmpeg -y -i t.mp3 -i music.mp3 -filter_complex "[0:a]volume=2.5[v];[1:a]volume=0.2[m];[v][m]amix=inputs=2:duration=first" temp_a.mp3', shell=True)

        # 3. VÍDEOS (3 clips con Zoom suave, clip por clip para RAM)
        processed_clips = []
        keys = user_input.split() + ["mystery", "dark", "urban", "nature"]
        for i in range(3): 
            k = random.choice(keys)
            status.write(f"🎞️ Procesando clip {i+1} de 3...")
            url = f"https://api.pexels.com/videos/search?query={k}&per_page=1&orientation=portrait"
            res = requests.get(url, headers={"Authorization": pexels_key.strip()}, timeout=10).json()
            if res.get('videos'):
                v_url = res['videos'][0]['video_files'][0]['link']
                with open(f"clip_{i}.mp4", 'wb') as f: f.write(requests.get(v_url).content)
                
                # Zoom simplificado (scale ligero, preset superfast)
                # Duración de cada clip es un poco más que dur/3 para asegurar el corte más tarde
                subprocess.run(f'ffmpeg -y -i "clip_{i}.mp4" -vf "scale=800:-1,zoompan=z=\'min(zoom+0.001,1.3)\':d=125:x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):s=480x854,fps=25" -an -c:v libx264 -preset superfast -t {(dur/3)+1} "p_{i}.mp4"', shell=True)
                processed_clips.append(f"p_{i}.mp4")
                os.remove(f"clip_{i}.mp4") # Borrar original immediately

        # UNIÓN MUDO
        if processed_clips:
            with open("lista.txt", "w") as f:
                for p in processed_clips: f.write(f"file '{p}'\n")
            subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)

            # 4. MEZCLA FINAL CON SUBTÍTULOS DINÁMICOS (De dos en dos palabras)
            status.write("✨ Escribiendo subtítulos dinámicos de dos palabras...")
            palabras = guion.split()
            segs = [" ".join(palabras[i:i+2]) for i in range(0, len(palabras), 2)]
            dur_seg = dur / len(segs)
            
            # Generamos el filtro compleja de drawtext
            filter_complex = ""
            for i, seg in enumerate(segs):
                start = i * dur_seg
                end = (i + 1) * dur_seg
                # Texto con borde grueso, centrado
                filter_complex += f"drawtext=text='{seg}':fontcolor={color_sub}:fontsize=38:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:borderw=4:bordercolor=black:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{start},{end})',"
            
            v_final = f"output/v_{int(time.time())}.mp4"
            # Comando final: une el vídeo mudo, el audio mezclado y le quema los subtítulos
            cmd = f'ffmpeg -y -i base.mp4 -i temp_a.mp3 -vf "{filter_complex.rstrip(",")}" -c:v libx264 -preset ultrafast -b:v 800k -c:a aac -b:a 128k -shortest "{v_final}"'
            subprocess.run(cmd, shell=True)
            
            if os.path.exists(v_final):
                st.video(v_final)
                st.success("🔥 ¡VÍDEO TERMINADO CON ÉXITO Y CON GARANTÍA DE AUDIO!")
                st.balloons()
            else:
                st.error("Ocurrió un error al generar el archivo final.")
