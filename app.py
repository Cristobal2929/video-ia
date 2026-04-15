import streamlit as st
import os, time, random, subprocess, requests, math, re
import urllib.parse

st.set_page_config(page_title="Fénix Viral PRO", layout="centered")
st.markdown("<style>.stApp {background: #0d1117; color: white;}</style>", unsafe_allow_html=True)

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0B0F19 0%, #1A2235 100%); color: #F8FAFC; }
    .pro-title { font-size: 38px; font-weight: 900; background: -webkit-linear-gradient(45deg, #00C6FF, #0072FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 5px; letter-spacing: -1px; }
    .pro-subtitle { text-align: center; color: #94A3B8; font-size: 15px; margin-bottom: 30px; font-weight: 400; }
    .stTextInput>div>div>input { background-color: #0F172A; color: white; border: 1px solid #334155; border-radius: 8px; }
    .stSelectbox>div>div>div { background-color: #0F172A; color: white; border: 1px solid #334155; border-radius: 8px; }
    hr { border-color: #334155; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="pro-title">FÉNIX AI STUDIO v3.1</div>', unsafe_allow_html=True)
st.markdown('<div class="pro-subtitle">Generador de Contenido Viral • Lógica Perfecta HD</div>', unsafe_allow_html=True)

def es_texto_valido(texto):
    t_lower = texto.lower()
    basura_html = ["doctype", "<html", "502 bad gateway", "cloudflare", "html class", "error code", "div class"]
    for b in basura_html:
        if b in t_lower: return False
    return True

def limpiar_texto_ia(texto):
    basura_ia = ["USER REQUEST", "START UP", "WRITE A", "ALL CAPS", "NO PERIODS", "SAYS ZERO", "REASONING CONTENT"]
    texto_limpio = texto.upper()
    for b in basura_ia: texto_limpio = texto_limpio.replace(b, "")
    texto_limpio = re.sub(r'[^\w\s]', '', texto_limpio).replace('\n', ' ').strip()
    return re.sub(' +', ' ', texto_limpio)

def limpiar_orden(orden):
    basura = ["hazme", "haz", "arme", "asme", "dame", "dime", "un", "una", "el", "la", "los", "las", "video", "vídeo", "videos", "quiero", "sobre", "de", "del", "historia", "que", "hable", "como", "mejor", "para", "sin", "con", "en", "año"]
    palabras = orden.lower().split()
    limpias = [p for p in palabras if p not in basura and len(p) > 3]
    return " ".join(limpias) if limpias else orden, limpias

# --- MOTOR COMBINATORIO CON FLUIDEZ GRAMATICAL LÓGICA ---
def generar_guion_procedural(tema):
    tema = tema.upper()
    
    # 1. GANCHO DIRECTO AL TEMA
    ganchos = [
        "PRESTA MUCHA ATENCION PORQUE NADIE TE ESTA CONTANDO LA VERDAD SOBRE",
        "HAY UN MISTERIO MUY OSCURO QUE LA ELITE INTENTA OCULTAR SOBRE",
        "ESTO ES LO QUE NO QUIEREN QUE DESCUBRAS CUANDO INVESTIGAS SOBRE",
        "DURANTE DECADAS NOS HAN ESTADO MINTIENDO DESCARADAMENTE SOBRE",
        "SIEMPRE HAS CREIDO QUE LO SABIAS TODO SOBRE",
        "EL GOBIERNO HA GASTADO MILLONES EN OCULTAR ESTE SECRETO SOBRE",
        "HAY UNA ESTRATEGIA PROHIBIDA QUE MUY POCOS CONOCEN SOBRE"
    ]
    
    # 2. EL PUENTE LÓGICO (Explica por qué estábamos engañados)
    creencias = [
        "SIEMPRE NOS HAN HECHO CREER QUE ES ALGO COMPLETAMENTE INOFENSIVO Y NORMAL",
        "LA MAYORIA DE LA GENTE PIENSA QUE FUNCIONA DE FORMA TRANSPARENTE Y SEGURA",
        "NOS VENDIERON LA IDEA DE QUE ERA PARA NUESTRO BENEFICIO EXCLUSIVO",
        "Y CASI TODO EL MUNDO HA CAIDO EN LA TRAMPA SIN HACER MAS PREGUNTAS",
        "A SIMPLE VISTA PARECE ALGO COTIDIANO A LO QUE NO HAY QUE PRESTAR ATENCION",
        "NOS EDUCARON PARA PENSAR QUE ESTO NO TENIA NINGUNA IMPORTANCIA REAL",
        "LA HISTORIA OFICIAL SIEMPRE HA DICHO QUE NO HABIA NADA EXTRAÑO AQUI"
    ]
    
    # 3. EL SUCESO DETONANTE (Alguien descubre la verdad)
    descubrimientos = [
        "PERO HACE POCO UNOS INVESTIGADORES INDEPENDIENTES FILTRARON PRUEBAS REALES",
        "SIN EMBARGO UN HACKER LOGRO ENTRAR A LOS SERVIDORES PRIVADOS Y VIO LOS DATOS",
        "HASTA QUE UN DOCUMENTO CLASIFICADO SALIO A LA LUZ POR COMPLETO ACCIDENTE",
        "PERO RECIENTEMENTE ALGUIEN DE ADENTRO ROMPIO EL SILENCIO PARA AVISARNOS",
        "AUNQUE TODO CAMBIO CUANDO UN CIENTIFICO ANALIZO LOS VERDADEROS PATRONES",
        "HASTA QUE UN GRUPO DE EXPERTOS SE DIO CUENTA DE UN PEQUEÑO ERROR MATEMATICO",
        "PERO UN ARCHIVO OLVIDADO EN LA DEEP WEB DEMOSTRO QUE ESTABAMOS CIEGOS"
    ]
    
    # 4. EL GIRO Y LA VERDAD CRUDA
    giros = [
        "Y SE DIERON CUENTA DE QUE EL VERDADERO PROPOSITO ERA MANIPULAR NUESTRAS DECISIONES",
        "REVELANDO QUE TODO ES UN NEGOCIO MULTIMILLONARIO PARA MANTENERNOS ESTANCADOS",
        "Y DESCUBRIERON QUE ESTA TECNOLOGIA ES MUCHO MAS AVANZADA DE LO QUE PARECE",
        "DEMOSTRANDO QUE TODO HABIA SIDO CALCULADO AL MILIMETRO PARA TENERNOS BAJO CONTROL",
        "LA CONCLUSION FUE QUE ALGUIEN DESDE LAS SOMBRAS LO ESTA USANDO A SU FAVOR",
        "Y LO PEOR DE TODO ES QUE ESTE SISTEMA LLEVA ACTIVO MUCHISIMO MAS TIEMPO DEL QUE CREIAMOS",
        "CONFIRMANDO QUE LA REGLA PRINCIPAL FUE CREADA JUSTAMENTE PARA QUE FRACASARAMOS"
    ]
    
    # 5. EL FINAL PERFECTO
    finales = [
        "AHORA QUE SABES ESTO TIENES LA VENTAJA DEFINITIVA SOBRE EL SISTEMA SIGUENOS PARA MAS SECRETOS",
        "EL ENGAÑO HA TERMINADO Y LA HISTORIA OFICIAL QUEDA DESTRUIDA SIGUENOS PARA MAS SECRETOS",
        "ESTE DESCUBRIMIENTO LO CAMBIA TODO Y NO HAY VUELTA ATRAS SIGUENOS PARA MAS SECRETOS",
        "YA CONOCES LA VERDAD OCULTA APLICALA Y NADIE PODRA DETENERTE SIGUENOS PARA MAS SECRETOS",
        "LA ILUSION SE HA ROTO AHORA TIENES EL PODER EN TUS MANOS SIGUENOS PARA MAS SECRETOS",
        "EL MUNDO YA NO VOLVERA A SER IGUAL DESPUES DE ESTO DESPIERTA Y SIGUENOS PARA MAS SECRETOS",
        "TIENES LA CLAVE PARA ENTENDERLO TODO NO TE DEJES MANIPULAR SIGUENOS PARA MAS SECRETOS"
    ]
    
    return f"{random.choice(ganchos)} {tema} {random.choice(creencias)} {random.choice(descubrimientos)} {random.choice(giros)} {random.choice(finales)}"

def obtener_guion_pro(orden_usuario):
    tema_mostrar, limpias = limpiar_orden(orden_usuario)
    keys = [p for p in limpias[:3]] + [f"{p} cinematic" for p in limpias[:2]]
    if not keys: keys = ["cinematic", "epic", "viral"]

    guion_fallback = generar_guion_procedural(tema_mostrar)
    semilla = random.randint(100000, 9999999)
    prompt_maestro = f"Crea un guion viral UNICO. TEMA: '{orden_usuario}'. ESTRUCTURA: 1. Gancho explosivo. 2. Desarrollo misterioso con datos reales. 3. FINAL: Concluye la historia y añade EXACTAMENTE la frase 'SIGUENOS PARA MAS SECRETOS'. REGLAS: TODO EN MAYUSCULAS. CERO PUNTOS. CERO COMAS. CERO TILDES. MINIMO 120 PALABRAS."

    try:
        res_1 = requests.get("https://sentence.fineshopdesign.com/api/ai", params={"prompt": prompt_maestro, "seed": semilla}, timeout=12)
        if res_1.status_code == 200 and es_texto_valido(res_1.json().get("reply", "")):
            gl = limpiar_texto_ia(res_1.json().get("reply", ""))
            if len(gl) > 60: return gl, keys, tema_mostrar
    except: pass

    try:
        res_2 = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote(prompt_maestro)}?seed={semilla}", timeout=12)
        if res_2.status_code == 200 and es_texto_valido(res_2.text):
            gl = limpiar_texto_ia(res_2.text)
            if len(gl) > 60: return gl, keys, tema_mostrar
    except: pass
            
    return guion_fallback, keys, tema_mostrar

def time_to_sec(t_str):
    t_str = t_str.strip().split(' ')[0].replace(',', '.')
    partes = t_str.split(':')
    if len(partes) == 3: return float(partes[0])*3600 + float(partes[1])*60 + float(partes[2])
    elif len(partes) == 2: return float(partes[0])*60 + float(partes[1])
    else: return float(partes[0])

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2111/2111432.png", width=50)
    st.header("⚙️ Panel de Agencia")
    pexels_key = st.text_input("🔑 Pexels API Key:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.selectbox("🎨 Estilo Subtítulos", ["yellow", "white", "cyan", "#00FF00"])
    st.markdown("---")
    st.caption("Fénix System | Licencia Comercial Activa ✅")

if orden := st.chat_input("Introduzca el tema del vídeo a generar..."):
    with st.status("🚀 Iniciando Motor de Producción HD...", expanded=True) as status:
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.mp3 t.vtt music.mp3 final.mp4 temp_a.mp3 lista.txt subs_filter.txt outro.mp4", shell=True)
        
        guion, palabras_claves, tema_mostrar = obtener_guion_pro(orden)
        status.write(f"✓ Guion lógico y de alta retención generado.")
        
        subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --rate=-10% --text "{guion}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
        dur_audio_str = subprocess.check_output("ffprobe -i t.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True).decode('utf-8').strip()
        if not dur_audio_str: dur_audio_str = "40.0"
        dur_audio = float(dur_audio_str)

        subprocess.run(f'ffmpeg -y -f lavfi -i "sine=frequency=70:duration={dur_audio+2}" -f lavfi -i "anoisesrc=d={dur_audio+2}:c=pink:a=0.03" -filter_complex "[0:a]volume=0.5[t];[1:a]volume=0.1[n];[t][n]amix=inputs=2:duration=first" music.mp3', shell=True)
        subprocess.run(f'ffmpeg -y -i t.mp3 -i music.mp3 -filter_complex "[0:a]volume=3.0[v];[1:a]volume=0.2[m];[v][m]amix=inputs=2:duration=first" temp_a.mp3', shell=True)

        drawtext_filters = []
        try:
            with open('t.vtt', 'r', encoding='utf-8') as f:
                lines = f.readlines()
            for i in range(len(lines)):
                if "-->" in lines[i]:
                    tiempos = lines[i].strip().split(" --> ")
                    start = time_to_sec(tiempos[0])
                    end = time_to_sec(tiempos[1])
                    if i + 1 < len(lines):
                        texto = lines[i+1].strip()
                        if texto:
                            palabras = texto.split()
                            chunks = [" ".join(palabras[j:j+2]) for j in range(0, len(palabras), 2)]
                            total_letras = sum(len(c) for c in chunks)
                            current_time = start
                            for chunk in chunks:
                                duracion_chunk = (len(chunk) / total_letras) * (end - start) if total_letras > 0 else (end - start)
                                drawtext_filters.append(f"drawtext=text='{chunk}':fontcolor={color_sub}:fontsize=32:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:borderw=3:bordercolor=black:shadowcolor=black:shadowx=2:shadowy=2:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{current_time},{current_time+duracion_chunk})'")
                                current_time += duracion_chunk
            with open("subs_filter.txt", "w", encoding='utf-8') as f:
                f.write(",\n".join(drawtext_filters))
        except: pass

        clip_duration = 3.5 
        num_clips = math.ceil(dur_audio / clip_duration) 
        processed_clips = []
        
        status.write(f"✓ Descargando metraje HD...")
        v_urls = []
        for k in palabras_claves:
            try:
                res = requests.get(f"https://api.pexels.com/videos/search?query={k}&per_page=10&orientation=portrait", headers={"Authorization": pexels_key.strip()}, timeout=10).json()
                for v in res.get('videos', []): v_urls.append(v['video_files'][0]['link'])
            except: pass
        
        random.shuffle(v_urls)
        last_valid_clip = None
        for i in range(num_clips): 
            try:
                v_url = v_urls[i % len(v_urls)] if v_urls else None
                if v_url:
                    with open(f"clip_{i}.mp4", 'wb') as f: f.write(requests.get(v_url, timeout=10).content)
                    subprocess.run(f'ffmpeg -y -i "clip_{i}.mp4" -vf "scale=1280:-1,zoompan=z=\'min(zoom+0.0015,1.4)\':d=125:x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):s=720x1280,fps=30" -an -c:v libx264 -preset veryfast -t {clip_duration} "p_{i}.mp4"', shell=True)
                    last_valid_clip = f"p_{i}.mp4"
                else: raise Exception("Error")
            except:
                if last_valid_clip: subprocess.run(f"cp {last_valid_clip} p_{i}.mp4", shell=True)
                else: subprocess.run(f'ffmpeg -y -f lavfi -i color=c=black:s=720x1280:d={clip_duration}:r=30 -c:v libx264 -preset veryfast p_{i}.mp4', shell=True)
            processed_clips.append(f"p_{i}.mp4")

        subprocess.run('ffmpeg -y -f lavfi -i color=c=black:s=720x1280:d=3:r=30 -vf "drawtext=text=\'FÉNIX STUDIO 🦅\':fontcolor=white:fontsize=55:x=(w-tw)/2:y=(h-th)/2" -c:v libx264 -preset veryfast outro.mp4', shell=True)
        with open("lista.txt", "w") as f:
            for p in processed_clips: f.write(f"file '{p}'\n")
            f.write("file 'outro.mp4'\n")
        subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)

        status.write("✨ Renderizando Exportación Final Comercial...")
        v_final = f"output/v_{int(time.time())}.mp4"
        cmd = f'ffmpeg -y -i base.mp4 -i temp_a.mp3 -filter_complex_script subs_filter.txt -c:v libx264 -preset veryfast -b:v 3000k -shortest "{v_final}"'
        subprocess.run(cmd, shell=True)
        
        if os.path.exists(v_final):
            st.success("✅ Renderizado Completo. Calidad HD.")
            st.video(v_final)
