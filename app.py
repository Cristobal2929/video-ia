import streamlit as st
import os, time, random, subprocess, math, re, urllib.parse
import requests

st.set_page_config(page_title="Fénix Viral PRO", layout="centered")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0B0F19 0%, #1A2235 100%); color: #F8FAFC; }
    .pro-title { font-size: 38px; font-weight: 900; background: -webkit-linear-gradient(45deg, #00C6FF, #0072FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 5px; letter-spacing: -1px; }
    .stTextInput>div>div>input { background-color: #0F172A; color: white; border: 1px solid #334155; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX AI STUDIO v11.0</div>', unsafe_allow_html=True)
st.markdown('<div class="pro-subtitle">Sincronización Total • Imagen por Palabra</div>', unsafe_allow_html=True)

# Diccionario de traducción rápido para que Pexels no se pierda
TRADUCTOR = {
    "AMOR": "love", "ELEFANTE": "elephant", "DINERO": "money", "ESTAFA": "scam",
    "GATO": "cat", "PERRO": "dog", "COCHE": "car", "CIUDAD": "city", "MIEDO": "scary",
    "TRABAJO": "work", "MUNDO": "world", "ESPACIO": "space", "LUNA": "moon",
    "SOL": "sun", "GENTE": "people", "NIÑO": "child", "MUJER": "woman", "HOMBRE": "man",
    "COMIDA": "food", "AGUA": "water", "ORO": "gold", "MUERTE": "death", "VIDA": "life"
}

def traducir(palabra):
    return TRADUCTOR.get(palabra.upper(), palabra.lower())

def limpiar_orden(orden):
    basura = ["hazme", "haz", "arme", "asme", "dame", "dime", "un", "una", "el", "la", "los", "las", "video", "vídeo", "videos", "quiero", "sobre", "de", "del", "historia", "que", "hable", "como", "mejor", "para", "sin", "con", "en", "año"]
    palabras = orden.lower().split()
    limpias = [p for p in palabras if p not in basura and len(p) > 3]
    return " ".join(limpias) if limpias else orden

def detectar_nicho(tema):
    t = tema.lower()
    if any(w in t for w in ["miedo", "terror", "fantasma", "creepy"]): return "terror"
    if any(w in t for w in ["negocio", "dinero", "invertir", "rico"]): return "negocios"
    return "misterio"

def generar_guion(tema, nicho):
    tema = tema.upper()
    if nicho == "negocios":
        return f"EL NOVENTA Y NUEVE POR CIENTO DE LA GENTE PIERDE DINERO CON {tema} PORQUE NO ENTIENDEN ESTA TRAMPA SIEMPRE NOS ENSEÑARON QUE EL DINERO ES DIFICIL DE CONSEGUIR PERO LA REALIDAD ES QUE EL SISTEMA ESTA ROTO UN ANALISTA FILTRO LA FORMULA REAL PARA HACERSE RICO Y ES UNA LOCURA LA CLAVE ESTA EN BUSCAR DONDE NADIE MAS ESTA MIRANDO APLICALO HOY MISMO Y TU VIDA CAMBIARA SIGUENOS PARA MAS NEGOCIOS"
    elif nicho == "terror":
        return f"NO MIRES ESTO DE NOCHE SI LE TEMES A {tema} TODO EL MUNDO PIENSA QUE ES UN INVENTO PERO LA POLICIA ENCONTRO ALGO HORRIBLE EN UN LUGAR ABANDONADO HABIA PRUEBAS DE QUE ALGO MALDITO ESTABA PASANDO LO MAS ATERRADOR ES QUE ESA COSA SIGUE SUELTA BUSCANDO A QUIEN ROMPA LAS REGLAS SI ESCUCHAS UN GOLPE HOY NO ABRAS LA PUERTA SIGUENOS PARA MAS TERROR"
    else:
        return f"TE HAN MENTIDO TODA TU VIDA SOBRE {tema} UNA AGENCIA SECRETA DECIDIO QUE NO ESTABAS LISTO PARA LA VERDAD PERO ALGUIEN DE ADENTRO FILTRO ARCHIVOS QUE LO CAMBIAN TODO RESULTA QUE ESTO ES UN SECRETO BRUTAL Y FUE OCULTADO PARA MANTENER EL CONTROL EL MUNDO YA NO VOLVERA A SER IGUAL SIGUENOS PARA MAS SECRETOS"

def time_to_sec(t_str):
    try:
        t_str = t_str.strip().split(' ')[0].replace(',', '.')
        partes = t_str.split(':')
        if len(partes) == 3: return float(partes[0])*3600 + float(partes[1])*60 + float(partes[2])
        elif len(partes) == 2: return float(partes[0])*60 + float(partes[1])
        else: return float(partes[0])
    except: return 0

with st.sidebar:
    st.header("⚙️ Configuración")
    pexels_key = st.text_input("🔑 Pexels API Key:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.selectbox("🎨 Color Subtítulos", ["yellow", "white", "cyan"])

if orden := st.chat_input("Dime tu idea (Ej: El amor, Elefantes...):"):
    with st.status(f"🚀 Creando vídeo sincronizado...", expanded=True) as status:
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.mp3 t.vtt music.mp3 final.mp4 temp_a.mp3 lista.txt subs_filter.txt", shell=True)
        
        tema_limpio = limpiar_orden(orden)
        nicho = detectar_nicho(orden)
        guion = generar_guion(tema_limpio, nicho)
        
        # 1. Generar Audio y Subtítulos
        subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --rate=-10% --text "{guion}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
        
        # 2. Analizar Sincronización (Palabra -> Tiempo)
        escenas = []
        try:
            with open('t.vtt', 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for i in range(len(lines)):
                    if "-->" in lines[i]:
                        start = time_to_sec(lines[i].split(" --> ")[0])
                        end = time_to_sec(lines[i].split(" --> ")[1])
                        txt = lines[i+1].strip().upper()
                        # Extraer la palabra más importante de la frase para buscar el vídeo
                        palabras = [p for p in txt.split() if len(p) > 3]
                        keyword = palabras[-1] if palabras else tema_limpio
                        escenas.append({"start": start, "end": end, "text": txt, "keyword": keyword})
        except: pass

        # 3. Descargar y Procesar Vídeos por cada Escena
        status.write("🎞️ Sincronizando imágenes con cada palabra...")
        clips_finales = []
        last_clip = None
        
        for i, escena in enumerate(escenas):
            dur_escena = escena["end"] - escena["start"]
            if dur_escena <= 0: continue
            
            search_query = traducir(escena["keyword"])
            v_url = None
            try:
                r = requests.get(f"https://api.pexels.com/videos/search?query={search_query}&per_page=1&orientation=portrait", headers={"Authorization": pexels_key.strip()}, timeout=5).json()
                if r.get('videos'):
                    v_url = r['videos'][0]['video_files'][0]['link']
            except: pass
            
            try:
                if not v_url: raise Exception("No video")
                with open(f"clip_{i}.mp4", 'wb') as f: f.write(requests.get(v_url, timeout=10).content)
                subprocess.run(f'ffmpeg -y -i "clip_{i}.mp4" -vf "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,fps=30" -an -c:v libx264 -preset ultrafast -t {dur_escena + 0.1} "p_{i}.mp4"', shell=True)
                last_clip = f"p_{i}.mp4"
            except:
                if last_clip: subprocess.run(f"cp {last_clip} p_{i}.mp4", shell=True)
                else: subprocess.run(f'ffmpeg -y -f lavfi -i color=c=black:s=720x1280:d={dur_audio}:r=30 -c:v libx264 -preset ultrafast p_{i}.mp4', shell=True)
            
            clips_finales.append(f"p_{i}.mp4")
            status.write(f"  ✓ Palabra '{escena['keyword']}' sincronizada.")

        # 4. Crear Filtro de Subtítulos
        subs_cmd = []
        for i, escena in enumerate(escenas):
            subs_cmd.append(f"drawtext=text='{escena['text']}':fontcolor={color_sub}:fontsize=35:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:borderw=3:bordercolor=black:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{escena['start']},{escena['end']})'")
        with open("subs_filter.txt", "w") as f: f.write(",\n".join(subs_cmd))

        # 5. Montaje Final
        with open("lista.txt", "w") as f:
            for c in clips_finales: f.write(f"file '{c}'\n")
        
        subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)
        # Música de fondo
        subprocess.run(f'ffmpeg -y -f lavfi -i "sine=f=75:d=60" -filter_complex "[0:a]volume=0.1" music.mp3', shell=True)
        subprocess.run(f'ffmpeg -y -i t.mp3 -i music.mp3 -filter_complex "[0:a]volume=3.0[v];[1:a]volume=0.2[m];[v][m]amix=inputs=2:duration=first" temp_a.mp3', shell=True)
        
        v_final = f"output/v_{int(time.time())}.mp4"
        subprocess.run(f'ffmpeg -y -i base.mp4 -i temp_a.mp3 -filter_complex_script subs_filter.txt -c:v libx264 -preset ultrafast -b:v 2500k -shortest "{v_final}"', shell=True)
        
        if os.path.exists(v_final):
            st.video(v_final)
            st.balloons()
