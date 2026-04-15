import streamlit as st
import os, time, random, subprocess, re, requests

st.set_page_config(page_title="Fénix Viral Studio", layout="centered")
st.markdown("<style>.stApp {background: #0d1117; color: white;}</style>", unsafe_allow_html=True)

# --- BASE DE DATOS DE HISTORIAS DE ALTO ENGANCHE ---
def obtener_historia_bomba(tema):
    t = tema.lower()
    if "terror" in t or "miedo" in t:
        return {
            "guion": "Hay una grabacion de 1970 que la NASA prohibio. En ella se escucha a un astronauta suplicando que algo deje de golpear la escotilla desde fuera. Lo peor es que estaban en el vacio absoluto.",
            "keys": ["space", "astronaut", "darkness", "scary face"]
        }
    if "coche" in t or "motor" in t:
        return {
            "guion": "Este es el coche que Mercedes no quiere que veas. Tiene un motor que no usa gasolina, sino agua salada. Misteriosamente, el inventor desaparecio dias despues de presentarlo.",
            "keys": ["concept car", "secret engine", "ocean waves", "mysterious man"]
        }
    if "curiosidad" in t or "sabias" in t:
        return {
            "guion": "Si escribes tu nombre en una habitacion a oscuras frente a un espejo a las tres de la mañana, tu cerebro empezara a crear una cara deforme detras de ti. Es un efecto psicologico real.",
            "keys": ["mirror", "dark room", "creepy shadow", "brain"]
        }
    # Genérico pero con gancho
    return {
        "guion": f"Lo que vas a descubrir sobre {tema} es algo que han intentado ocultar durante años. No es una casualidad, es un plan diseñado para que no sepas la verdad.",
        "keys": [tema, "secret", "magnifying glass", "shouting"]
    }

st.title("🦅 Fénix Viral Studio")

with st.sidebar:
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.selectbox("🎨 Color Texto", ["yellow", "white", "cyan"])

if user_input := st.chat_input("Dime el tema (Terror, Coches, Secretos...)"):
    with st.status("🚀 Creando vídeo de alto impacto...", expanded=True) as status:
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.* outro.mp4 final.mp4", shell=True)
        
        info = obtener_historia_bomba(user_input)
        guion = info["guion"]
        keywords = info["keys"]
        v_final = f"output/v_{int(time.time())}.mp4"
        
        # 1. Voz
        status.write("🎙️ Grabando voz con enganche...")
        subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --text "{guion}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
        subprocess.run("ffmpeg -y -i t.vtt t.srt", shell=True)
        
        # 2. Clips Coherentes (Uno por cada parte de la historia)
        for i, key in enumerate(keywords):
            status.write(f"🎞️ Buscando imagen para: {key}...")
            url = f"https://api.pexels.com/videos/search?query={key}&per_page=1&orientation=portrait"
            res = requests.get(url, headers={"Authorization": pexels_key.strip()}).json()
            if res.get('videos'):
                v_url = res['videos'][0]['video_files'][0]['link']
                with open(f"clip_{i}.mp4", 'wb') as f: f.write(requests.get(v_url).content)
                subprocess.run(f'ffmpeg -y -i "clip_{i}.mp4" -vf "scale=480:854:force_original_aspect_ratio=increase,crop=480:854,fps=25" -an -c:v libx264 -preset ultrafast "p_{i}.mp4"', shell=True)
        
        # Sello Final
        subprocess.run('ffmpeg -y -f lavfi -i color=c=black:s=480x854:d=2:r=25 -vf "drawtext=text=\'FENIX STUDIO 🦅\':fontcolor=white:fontsize=40:x=(w-tw)/2:y=(h-th)/2" -c:v libx264 -preset ultrafast outro.mp4', shell=True)
        
        with open("lista.txt", "w") as f:
            for i in range(len(keywords)): f.write(f"file 'p_{i}.mp4'\n")
            f.write("file 'outro.mp4'\n")
        subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)

        # 3. Mezcla Final con Subtítulos Bonitos
        status.write("✨ Montando subtítulos y efectos...")
        # Estilo Impact con borde y sombra (Para que se vean sí o sí)
        estilo = f"Fontname=Impact,FontSize=32,PrimaryColour={f'&H0000FFFF' if color_sub=='yellow' else '&H00FFFFFF'},OutlineColour=&H000000,BorderStyle=1,Outline=3,Shadow=2,Alignment=2,MarginV=400"
        
        cmd = f'ffmpeg -y -i base.mp4 -i t.mp3 -vf "subtitles=t.srt:force_style=\'{estilo}\'" -c:v libx264 -preset ultrafast -c:a aac -map 0:v:0 -map 1:a:0 -shortest "{v_final}"'
        subprocess.run(cmd, shell=True)
        
        if os.path.exists(v_final):
            st.video(v_final)
            st.success("🔥 ¡ESTO ES OTRA LIGA, DAYRON!")
