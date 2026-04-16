import streamlit as st
import os, time, random, subprocess, textwrap, re, urllib.parse
import requests

st.set_page_config(page_title="Fénix Viral PRO | V32", layout="centered")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #09090b 0%, #111827 100%); color: #F8FAFC; }
    .pro-title { font-size: 40px; font-weight: 900; background: -webkit-linear-gradient(45deg, #FFD700, #00FF00); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 2px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX DUAL ENGINE</div>', unsafe_allow_html=True)
st.markdown('<div class="pro-subtitle" style="text-align:center; color:#94A3B8; margin-bottom: 30px;">Salvavidas de Google Integrado • Cero Caídas de Red</div>', unsafe_allow_html=True)

# 1. ESCUDO DE FUENTE
font_path = "Arial.ttf"
if not os.path.exists(font_path):
    try:
        r_font = requests.get("https://github.com/matomo-org/travis-scripts/raw/master/fonts/Arial.ttf", timeout=5)
        with open(font_path, "wb") as f: f.write(r_font.content)
    except: pass

def limpiar_orden(orden):
    return re.sub(r'[^A-Za-zÁÉÍÓÚáéíóúÑñ0-9\s]', '', orden).strip()

def detectar_nicho(tema):
    t = tema.lower()
    if any(w in t for w in ["miedo", "terror", "fantasma", "paranormal", "horror", "misterio", "oscuro"]): return "TERROR"
    if any(w in t for w in ["dinero", "negocio", "invertir", "rico", "millonario", "cripto", "empresa"]): return "NEGOCIOS"
    return "UNIVERSAL"

def generar_master_guion(tema, nicho):
    tema = tema.upper()
    if nicho == "TERROR":
        return [
            {"t": f"No mires este video de noche si le temes a {tema}.", "s": "creepy dark shadows horror"},
            {"t": "Todo el mundo piensa que es un invento, pero la policia encontro algo macabro.", "s": "scary abandoned house dark"},
            {"t": "Las grabaciones de seguridad mostraron algo que rompe la logica humana.", "s": "creepy ghost surveillance"},
            {"t": "El gobierno intento ocultarlo, pero un informante filtro los videos.", "s": "hacker computer screen dark"},
            {"t": "Si escuchas un ruido extraño hoy, no abras la puerta. Siguenos para mas.", "s": "scary monster dark eyes"}
        ]
    elif nicho == "NEGOCIOS":
        return [
            {"t": f"Te estan robando el dinero con {tema} y ni siquiera te has dado cuenta.", "s": "counting money wealth"},
            {"t": "Las grandes elites diseñaron un sistema para que fracases desde el principio.", "s": "corporate business skyscraper"},
            {"t": "Pero un analista financiero acaba de filtrar el patron exacto para ganar.", "s": "trading chart screen success"},
            {"t": "La clave es buscar donde nadie mas mira y adelantarse al resto.", "s": "rich lifestyle luxury"},
            {"t": "El sistema esta roto, es tu momento de aprovecharlo. Siguenos para mas.", "s": "luxury car money rain"}
        ]
    else: 
        return [
            {"t": f"Te apuesto lo que quieras a que no sabias la verdad sobre {tema}.", "s": "curious mystery cinematic epic"},
            {"t": "La gran mayoria de la gente vive engañada aceptando la version oficial.", "s": "crowd of people walking city"},
            {"t": "Pero hace poco tiempo se revelo un detalle oculto que lo cambia todo.", "s": "secret documents investigation"},
            {"t": "Si prestas atencion a los pequeños detalles, veras la inmensa mentira.", "s": "shocked face dramatic lighting"},
            {"t": "Abre los ojos y no te dejes manipular nunca mas. Siguenos para mas secretos.", "s": "epic cinematic lighting nature"}
        ]

# --- EL SALVAVIDAS DUAL (El antídoto contra los baneos de IP) ---
def generar_voz_segura(texto, archivo_salida):
    texto_limpio = re.sub(r'[^A-Za-zÁÉÍÓÚáéíóúÑñ0-9\s.,]', '', texto)
    
    with open("temp_txt.txt", "w", encoding="utf-8") as f:
        f.write(texto_limpio)

    # PLAN A: Intentamos usar a Microsoft (Álvaro)
    subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --rate=0% -f temp_txt.txt --write-media "{archivo_salida}"', shell=True)
    
    if os.path.exists(archivo_salida) and os.path.getsize(archivo_salida) > 0:
        return "Microsoft"
    
    # PLAN B: Si la IP está baneada en Streamlit, usamos Google directamente
    try:
        url_google = f"https://translate.google.com/translate_tts?ie=UTF-8&q={urllib.parse.quote(texto_limpio)}&tl=es&client=tw-ob"
        res = requests.get(url_google, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if res.status_code == 200:
            with open(archivo_salida, 'wb') as f:
                f.write(res.content)
            return "Google"
    except: pass
    
    return False

with st.sidebar:
    st.header("⚙️ Configuración")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.selectbox("🎨 Color de Letra", ["yellow", "white", "cyan", "#00FF87"])

if orden := st.chat_input("Dime el tema (El Motor Dual garantiza tu vídeo):"):
    with st.status(f"🚀 Forjando vídeo sobre '{orden}'...", expanded=True) as status:
        subprocess.run("rm -f a_*.mp3 v_*.mp4 s_*.mp4 text_*.txt temp_txt.txt lista.txt music.mp3 final.mp4 base.mp4", shell=True)
        
        tema_limpio = limpiar_orden(orden)
        nicho = detectar_nicho(orden)
        escenas = generar_master_guion(tema_limpio, nicho)
        
        status.write("🧠 Lógica y Dirección Visual preparadas.")
        clips_finales = []

        for i, esc in enumerate(escenas):
            texto_frase = esc["t"]
            busqueda_ingles = esc["s"]
            status.write(f"🎬 Procesando Escena {i+1}/5...")

            # 3. VOZ DUAL: Anti-Caídas
            motor = generar_voz_segura(texto_frase, f"a_{i}.mp3")
            
            if not motor:
                st.error(f"❌ Fallo global de servidores en la escena {i+1}. Ni Microsoft ni Google responden.")
                st.stop()
            
            # Cálculo de tiempo exacto
            try:
                dur_str = subprocess.check_output(f"ffprobe -i a_{i}.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True).decode('utf-8').strip()
                duracion = float(dur_str)
            except: duracion = 3.5

            # 4. SUBTÍTULOS ESTILO TIKTOK
            texto_mayus = texto_frase.upper().replace('Á','A').replace('É','E').replace('Í','I').replace('Ó','O').replace('Ú','U').replace('Ñ','N')
            texto_mayus = re.sub(r'[^A-Z0-9\s.,]', '', texto_mayus)
            texto_envuelto = textwrap.fill(texto_mayus, width=22)
            with open(f"text_{i}.txt", "w", encoding="utf-8") as f: f.write(texto_envuelto)

            # 5. PEXELS
            v_url = None
            try:
                r = requests.get(f"https://api.pexels.com/videos/search?query={urllib.parse.quote(busqueda_ingles)}&per_page=5&orientation=portrait", headers={"Authorization": pexels_key.strip()}, timeout=5).json()
                if r.get('videos'): v_url = random.choice(r['videos'])['video_files'][0]['link']
            except: pass
            
            try:
                if not v_url: raise Exception()
                with open(f"v_{i}.mp4", 'wb') as f: f.write(requests.get(v_url, timeout=10).content)
            except:
                subprocess.run(f'ffmpeg -y -f lavfi -i color=c=black:s=720x1280:d=1:r=30 -c:v libx264 -preset ultrafast v_{i}.mp4', shell=True)

            # 6. RENDERIZADOR UNIVERSAL
            font_cmd = f"fontfile='{font_path}':" if os.path.exists(font_path) else ""
            cmd_scene = f"""ffmpeg -y -stream_loop -1 -i v_{i}.mp4 -i a_{i}.mp3 -vf "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,format=yuv420p,drawtext=textfile='text_{i}.txt':fontcolor={color_sub}:fontsize=45:{font_cmd}box=1:boxcolor=black@0.6:boxborderw=15:borderw=2:bordercolor=black:line_spacing=12:x=(w-tw)/2:y=(h-th)/2,fps=30" -c:v libx264 -preset ultrafast -c:a aac -ar 44100 -ac 2 -t {duracion} s_{i}.mp4"""
            subprocess.run(cmd_scene, shell=True)
            
            if os.path.exists(f"s_{i}.mp4"): 
                clips_finales.append(f"s_{i}.mp4")
            else:
                st.error(f"❌ FFmpeg falló en la escena {i+1}.")
                st.stop()

        # 7. UNIÓN Y MÚSICA
        status.write("✨ Fusionando la Obra Maestra...")
        with open("lista.txt", "w") as f:
            for c in clips_finales: f.write(f"file '{c}'\n")
            
        subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c:v copy -c:a aac -ar 44100 -ac 2 base.mp4', shell=True)
        
        if not os.path.exists("base.mp4"):
            st.error("❌ Fallo crítico al unir los clips.")
            st.stop()
            
        v_final = f"output/v_{int(time.time())}.mp4"
        frecuencia = 60 if nicho == "TERROR" else 75
        
        cmd_final = f"""ffmpeg -y -i base.mp4 -f lavfi -i "sine=f={frecuencia}:d=120" -filter_complex "[1:a]volume=0.03[m];[0:a][m]amix=inputs=2:duration=first" -c:v copy -c:a aac -ar 44100 -ac 2 "{v_final}" """
        subprocess.run(cmd_final, shell=True)
        
        if os.path.exists(v_final):
            st.success("✅ VÍDEO DEFINITIVO LISTO. (Baneos de IP superados con éxito).")
            st.video(v_final)
            st.balloons()
        else:
            st.error("❌ Fallo en el último paso de renderizado.")
