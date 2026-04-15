import streamlit as st
import os, time, random, subprocess, textwrap, re, urllib.parse
import requests

st.set_page_config(page_title="Fénix Viral PRO | V26", layout="centered")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #09090b 0%, #111827 100%); color: #F8FAFC; }
    .pro-title { font-size: 38px; font-weight: 900; background: -webkit-linear-gradient(45deg, #00FF87, #60EFFF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 5px; }
    .stTextInput>div>div>input { background-color: #1F2937; color: white; border: 1px solid #60EFFF; border-radius: 8px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX AI STUDIO v26.0</div>', unsafe_allow_html=True)
st.markdown('<div class="pro-subtitle" style="text-align:center; color:#94A3B8; margin-bottom: 30px;">Formato Web Universal • Reproducción Garantizada • Cero Archivos Rotos</div>', unsafe_allow_html=True)

def limpiar_orden(orden):
    basura = ["hazme", "haz", "arme", "asme", "dame", "dime", "un", "una", "el", "la", "los", "las", "video", "quiero", "sobre", "de", "del", "que", "hable", "como", "para"]
    orden_limpia = re.sub(r'[^A-Za-zÁÉÍÓÚáéíóúÑñ0-9\s]', '', orden)
    palabras = orden_limpia.lower().split()
    limpias = [p for p in palabras if p not in basura and len(p) > 3]
    return " ".join(limpias) if limpias else orden_limpia

def detectar_nicho(tema):
    t = tema.lower()
    if any(w in t for w in ["miedo", "terror", "fantasma", "paranormal", "horror", "misterio", "oscuro"]): return "TERROR"
    if any(w in t for w in ["dinero", "negocio", "invertir", "rico", "millonario", "cripto", "empresa"]): return "NEGOCIOS"
    if any(w in t for w in ["ciencia", "espacio", "luna", "planeta", "curiosidad"]): return "CIENCIA"
    return "UNIVERSAL"

def generar_base_director(tema, nicho):
    if nicho == "TERROR":
        return [
            {"t": f"El secreto más oscuro sobre {tema} acaba de salir a la luz.", "s": "creepy dark shadows"},
            {"t": "Todos piensan que es un invento, pero la policía encontró algo macabro.", "s": "scary abandoned house"},
            {"t": "Las grabaciones de seguridad mostraron algo que rompe la lógica humana.", "s": "creepy ghost camera"},
            {"t": "El gobierno intentó ocultarlo, pero un informante filtró los vídeos.", "s": "hacker computer dark"},
            {"t": "Si escuchas un ruido extraño hoy, no abras la puerta. Síguenos para más.", "s": "scary monster dark"}
        ]
    elif nicho == "NEGOCIOS":
        return [
            {"t": f"Te están robando el dinero con {tema} y ni siquiera te has dado cuenta.", "s": "money counting wealth"},
            {"t": "Las grandes élites diseñaron un sistema para que fracases desde el principio.", "s": "corporate business building"},
            {"t": "Pero un analista financiero acaba de filtrar el patrón exacto para ganar.", "s": "trading chart screen"},
            {"t": "La clave es buscar donde nadie más mira y adelantarse al resto.", "s": "success luxury rich"},
            {"t": "El sistema está roto, es tu momento de aprovecharlo. Síguenos para más.", "s": "luxury car money"}
        ]
    else: 
        return [
            {"t": f"Te apuesto lo que quieras a que no sabías la verdad sobre {tema}.", "s": "curious mystery cinematic"},
            {"t": "La gran mayoría de la gente vive engañada aceptando la versión oficial.", "s": "crowd of people walking"},
            {"t": "Pero hace poco tiempo se reveló un detalle oculto que lo cambia todo.", "s": "secret documents investigation"},
            {"t": "Si prestas atención a los pequeños detalles, verás la inmensa mentira.", "s": "shocked dramatic face"},
            {"t": "Abre los ojos y no te dejes manipular nunca más. Síguenos para más secretos.", "s": "epic cinematic lighting"}
        ]

with st.sidebar:
    st.header("⚙️ Configuración")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.selectbox("🎨 Color de Letra", ["yellow", "white", "cyan"])

if orden := st.chat_input("Dime el tema (El vídeo ahora sí se reproducirá):"):
    with st.status(f"🚀 Renderizando '{orden}' en formato Universal...", expanded=True) as status:
        subprocess.run("rm -f a_*.mp3 v_*.mp4 s_*.mp4 text_*.txt lista.txt music.mp3 final.mp4 base.mp4", shell=True)
        
        tema_limpio = limpiar_orden(orden)
        nicho = detectar_nicho(orden)
        escenas = generar_base_director(tema_limpio, nicho)
        
        status.write("🧠 Guion generado.")
        clips_finales = []

        for i, esc in enumerate(escenas):
            texto_frase = esc["t"]
            busqueda_pexels = esc["s"]
            status.write(f"🎬 Creando Escena {i+1}/5 (Video + Audio + Texto)...")

            # 1. Audio
            subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --rate=0% --text "{texto_frase}" --write-media "a_{i}.mp3"', shell=True)
            
            try:
                dur_str = subprocess.check_output(f"ffprobe -i a_{i}.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True).decode('utf-8').strip()
                duracion_exacta = float(dur_str)
            except:
                duracion_exacta = 3.5
                
            # 2. Texto
            texto_mayus = re.sub(r'[^A-Z0-9\s.,]', '', texto_frase.upper()).replace('Á','A').replace('É','E').replace('Í','I').replace('Ó','O').replace('Ú','U').replace('Ñ','N')
            texto_envuelto = textwrap.fill(texto_mayus, width=22)
            with open(f"text_{i}.txt", "w", encoding="utf-8") as f:
                f.write(texto_envuelto)

            # 3. Vídeo de Pexels
            v_url = None
            try:
                r = requests.get(f"https://api.pexels.com/videos/search?query={urllib.parse.quote(busqueda_pexels)}&per_page=3&orientation=portrait", headers={"Authorization": pexels_key.strip()}, timeout=5).json()
                if r.get('videos'): v_url = random.choice(r['videos'])['video_files'][0]['link']
            except: pass
            
            try:
                if not v_url: raise Exception()
                with open(f"v_{i}.mp4", 'wb') as f: f.write(requests.get(v_url, timeout=10).content)
            except:
                subprocess.run(f'ffmpeg -y -f lavfi -i color=c=black:s=720x1280:d=1:r=30 -c:v libx264 -preset ultrafast v_{i}.mp4', shell=True)

            # 4. EL RENDERIZADOR UNIVERSAL (format=yuv420p y ar 44100)
            # Esto fuerza a todos los vídeos a tener el mismo color, los mismos píxeles y el mismo tipo de audio
            cmd_mezcla = f"""ffmpeg -y -stream_loop -1 -i v_{i}.mp4 -i a_{i}.mp3 -vf "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,format=yuv420p,drawtext=textfile='text_{i}.txt':fontcolor={color_sub}:fontsize=45:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:box=1:boxcolor=black@0.6:boxborderw=15:borderw=2:bordercolor=black:line_spacing=12:x=(w-tw)/2:y=(h-th)/2,fps=30" -c:v libx264 -preset ultrafast -c:a aac -ar 44100 -ac 2 -t {duracion_exacta} s_{i}.mp4"""
            subprocess.run(cmd_mezcla, shell=True)
            
            clips_finales.append(f"s_{i}.mp4")

        # 5. Ensamblaje Perfecto
        status.write("✨ Uniendo todo en formato Web...")
        with open("lista.txt", "w") as f:
            for c in clips_finales: f.write(f"file '{c}'\n")
            
        subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)
        
        frecuencia = 60 if nicho == "TERROR" else 75
        subprocess.run(f'ffmpeg -y -f lavfi -i "sine=f={frecuencia}:d=120" -filter_complex "[0:a]volume=0.05" music.mp3', shell=True)
        
        v_final = f"output/v_{int(time.time())}.mp4"
        # Usamos copy para el vídeo porque ya están todos en yuv420p, y re-mezclamos el audio final
        subprocess.run(f'ffmpeg -y -i base.mp4 -i music.mp3 -filter_complex "[0:a][1:a]amix=inputs=2:duration=first[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -ar 44100 -ac 2 -shortest "{v_final}"', shell=True)
        
        if os.path.exists(v_final):
            st.success("✅ VÍDEO COMPATIBLE CREADO. ¡Listo para reproducir!")
            st.video(v_final)
            st.balloons()
