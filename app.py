import streamlit as st
import os, time, random, subprocess, requests, math, re
import urllib.parse

st.set_page_config(page_title="Fénix Viral PRO", layout="centered")
st.markdown("<style>.stApp {background: #0d1117; color: white;}</style>", unsafe_allow_html=True)

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

# --- MOTOR COMBINATORIO ULTRA-EXPANDIDO (El Gran Almacén de Dayron) ---
def generar_guion_procedural(tema):
    tema = tema.upper()
    
    ganchos = [
        "PRESTA MUCHA ATENCION PORQUE LO QUE TE VOY A CONTAR SOBRE",
        "EL GOBIERNO HA INTENTADO BORRAR ESTA INFORMACION SOBRE",
        "HAY UN SECRETO MUY OSCURO QUE NADIE TE QUIERE CONTAR SOBRE",
        "DURANTE DECADAS NOS HAN MENTIDO DESCARADAMENTE SOBRE",
        "SIEMPRE PENSASTE QUE LO SABIAS TODO SOBRE",
        "UN HACKER ACABA DE FILTRAR LA VERDAD OCULTA SOBRE",
        "LA ELITE MUNDIAL ESTA ATERRADA DE QUE SEPAS ESTO SOBRE",
        "ESTO ES LO QUE NO QUIEREN QUE VEAS CUANDO BUSCAS",
        "HEMOS ENCONTRADO PRUEBAS PERTURBADORAS RELACIONADAS CON",
        "LOS ARCHIVOS DESCLASIFICADOS REVELAN ALGO INCREIBLE SOBRE",
        "NADIE SE ATREVE A DECIR LA VERDAD DETRAS DE",
        "DENTRO DE MUY POCO TODO EL MUNDO HABLARA DE",
        "HAY UNA CONEXION PROHIBIDA QUE UNE A LA ELITE CON",
        "ESTE ES EL MOTIVO POR EL QUE SIEMPRE TE OCULTARON",
        "DENTRO DE ESTE ARCHIVO SECRETO ENCONTRAMOS DATOS DE"
    ]
    
    problemas = [
        "PERO LA REALIDAD ES MUCHO MAS ATERRADORA DE LO QUE IMAGINAS",
        "Y RESULTA QUE TODO FUE UN EXPERIMENTO SOCIAL A GRAN ESCALA",
        "QUE CAMBIA POR COMPLETO LAS REGLAS DEL JUEGO",
        "Y ESTO DEMUESTRA QUE VIVIMOS EN UNA COMPLETA MENTIRA",
        "PORQUE DESCUBRIERON QUE ALGUIEN LO MANIPULABA DESDE LAS SOMBRAS",
        "QUE REVELA UNA FALLA CRITICA EN NUESTRO SISTEMA ACTUAL",
        "PERO HOY LOS DOCUMENTOS DESCLASIFICADOS MUESTRAN LO CONTRARIO",
        "Y ES QUE NUNCA NOS CONTARON LA PARTE MAS IMPORTANTE",
        "LO CUAL SIGNIFICA QUE EL PELIGRO ES MUCHO MAYOR DE LO PENSADO",
        "PORQUE DETRAS DE TODO ESTO HAY UNA ESTRATEGIA DE CONTROL",
        "QUE PODRIA HACER QUE TODO LO QUE CONOCES SE DERRUMBE",
        "Y ES QUE LA VERDAD FUE ENTERRADA BAJO CAPAS DE ENGAÑO",
        "LO QUE REVELA UN PATRON QUE SE REPITE UNA Y OTRA VEZ",
        "Y NADIE SE HABIA DADO CUENTA DE ESTE DETALLE HASTA AHORA",
        "PORQUE LA LOGICA QUE NOS ENSEÑARON NO FUNCIONA CON"
    ]
    
    desarrollos = [
        "UN GRUPO DE INVESTIGADORES INDEPENDIENTES ENCONTRO PRUEBAS IRREFUTABLES",
        "UN EX EMPLEADO ROMPIO SU CONTRATO DE SILENCIO PARA MOSTRAR LOS DATOS",
        "LAS PIEZAS EMPEZARON A ENCAJAR CUANDO ANALIZARON LOS PATRONES",
        "ENCONTRARON DOCUMENTOS EN LA DEEP WEB QUE EXPLICAN EL METODO EXACTO",
        "LOS EXPERTOS NOTARON ALGO EXTRAÑO Y DECIDIERON INVESTIGAR A FONDO",
        "ALGUIEN DEJO PISTAS OCULTAS ANTES DE DESAPARECER MISTERIOSAMENTE",
        "LA CLAVE SE ESCONDIA EN UNA TECNOLOGIA QUE CREIAMOS PERDIDA",
        "ANALIZANDO LOS DATOS FILTRADOS DESCUBRIERON ALGO QUE NO ESPERABAN",
        "HAY UNA SERIE DE COINCIDENCIAS QUE NO PUEDEN SER SOLO AZAR",
        "LAS GRABACIONES SECRETAS CONFIRMAN QUE ESTO LLEVA AÑOS PASANDO",
        "UN SOPLO DESDE DENTRO DE LA ORGANIZACION LO REVELO TODO",
        "LAS PRUEBAS DE LABORATORIO DIERON UN RESULTADO INESPERADO",
        "MAPAS ANTIGUOS Y DATOS MODERNOS COINCIDEN EN EL MISMO PUNTO",
        "EL RASTRO DEL DINERO LLEVA DIRECTAMENTE A LA RAIZ DEL ASUNTO",
        "TODO COMENZO CON UN PEQUEÑO ERROR QUE EXPUSO EL PLAN MAESTRO"
    ]
    
    giros = [
        "LO MAS LOCO ES QUE ESTABA DISEÑADO PARA CONTROLARNOS SIN DARNOS CUENTA",
        "AL FINAL DESCUBRIERON QUE TODO SE TRATABA DE DINERO Y PODER ABSOLUTO",
        "LA LOGICA DETRAS DE ESTO ES QUE QUERIAN MANTENERNOS DISTRAIDOS",
        "EL VERDADERO MOTIVO ERA EVITAR QUE EL RESTO PUDIERA EVOLUCIONAR",
        "RESULTA QUE FUE CREADO CON UN PROPOSITO TOTALMENTE DISTINTO AL OFICIAL",
        "DESCUBRIERON QUE LAS GRANDES CORPORACIONES LO SABIAN DESDE EL PRINCIPIO",
        "TODO SE REDUCE A UNA ESTRATEGIA MATEMATICA PERFECTA QUE FALLO",
        "LO PEOR ES QUE ESTO ESTA PASANDO AHORA MISMO MIENTRAS VES ESTO",
        "LA INTENCION OCULTA ERA CREAR UNA DEPENDENCIA TOTAL DEL SISTEMA",
        "RESULTA QUE LA SOLUCION SIEMPRE ESTUVO A NUESTRO ALCANCE PERO OCULTA",
        "CADA DETALLE HABIA SIDO CALCULADO PARA GENERAR EL MAXIMO BENEFICIO",
        "ESTO DEMUESTRA QUE LA REALIDAD SUPERA A CUALQUIER FICCION",
        "EL IMPACTO QUE ESTO TIENE EN NUESTRO FUTURO ES INCALCULABLE",
        "LA CONEXION ENTRE ESTOS EVENTOS ES LO QUE MAS MIEDO LES DA",
        "AL FINAL TODO ENCAJA COMO UN ROMPECABEZAS MACABRO"
    ]
    
    finales = [
        "AHORA QUE SABES ESTA VERDAD TIENES LA VENTAJA SOBRE LOS DEMAS",
        "EL MISTERIO HA SIDO RESUELTO Y YA NO PUEDEN SEGUIR ENGAÑANDONOS",
        "LA HISTORIA OFICIAL QUEDA DESTRUIDA PARA SIEMPRE SIGUENOS PARA MAS",
        "YA CONOCES EL SECRETO APLICALO Y TU FORMA DE VER EL MUNDO CAMBIARA",
        "AHORA TIENES EL PODER EN TUS MANOS LA VERDAD SALIO A LA LUZ",
        "ESTE DESCUBRIMIENTO CIERRA EL CIRCULO Y LO CAMBIA TODO DE POR VIDA",
        "DESPIERTA PORQUE EL ENGAÑO HA TERMINADO ESTAMOS LISTOS PARA AVANZAR",
        "COMPARTE ESTO ANTES DE QUE SEA ELIMINADO DE LA RED",
        "LA VERDAD NOS HARA LIBRES PERO PRIMERO NOS VA A SORPRENDER",
        "NO TE QUEDES CON LA DUDA E INVESTIGA POR TI MISMO",
        "ESTE ES SOLO EL PRINCIPIO DE UNA NUEVA ERA DE CONOCIMIENTO",
        "SÍGUENOS SI QUIERES DESCUBRIR QUE MAS NOS ESTAN OCULTANDO",
        "EL MUNDO YA NO ES EL MISMO DESPUES DE ESTA REVELACION",
        "PREPARATE PORQUE NADA VOLVERA A SER COMO ANTES",
        "RECUERDA QUE LA INFORMACION ES TU MEJOR ARMA EN ESTE JUEGO"
    ]
    
    guion_final = f"{random.choice(ganchos)} {tema} {random.choice(problemas)} {random.choice(desarrollos)} {random.choice(giros)} {random.choice(finales)}"
    return guion_final


def obtener_guion_pro(orden_usuario):
    tema_mostrar, limpias = limpiar_orden(orden_usuario)
    keys = [p for p in limpias[:3]] + [f"{p} cinematic" for p in limpias[:2]]
    if not keys: keys = ["cinematic", "epic", "viral"]

    guion_fallback = generar_guion_procedural(tema_mostrar)

    semilla = random.randint(100000, 9999999)
    prompt_maestro = f"Crea un guion viral UNICO Y ORIGINAL. TEMA: '{orden_usuario}'. ENFOQUE: Una historia fascinante con gancho desarrollo y final cerrado. REGLAS: SOLO TEXTO. TODO EN MAYUSCULAS. CERO PUNTOS. CERO COMAS. CERO TILDES. MINIMO 120 PALABRAS."

    try:
        url_1 = "https://sentence.fineshopdesign.com/api/ai"
        res_1 = requests.get(url_1, params={"prompt": prompt_maestro, "seed": semilla}, timeout=12)
        if res_1.status_code == 200:
            guion = res_1.json().get("reply", "")
            if es_texto_valido(guion):
                gl = limpiar_texto_ia(guion)
                if len(gl) > 60: return gl, keys, tema_mostrar
    except: pass

    try:
        prompt_codificado = urllib.parse.quote(prompt_maestro)
        url_2 = f"https://text.pollinations.ai/{prompt_codificado}?seed={semilla}"
        res_2 = requests.get(url_2, timeout=12)
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

st.title("🦅 Fénix Studio: Gran Almacén")

with st.sidebar:
    st.header("Motor Profesional")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.selectbox("🎨 Color Subtítulos", ["yellow", "white", "cyan"])

if orden := st.chat_input("Pide tu idea (Con el motor de 750,000 variantes):"):
    with st.status("🎬 Ensamblando desde el Almacén y procesando...", expanded=True) as status:
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.mp3 t.vtt music.mp3 final.mp4 temp_a.mp3 lista.txt subs_filter.txt outro.mp4", shell=True)
        
        guion, palabras_claves, tema_mostrar = obtener_guion_pro(orden)
        status.write(f"✍️ Guion listo: {guion[:60]}...")
        
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
                                c_end = current_time + duracion_chunk
                                drawtext_filters.append(f"drawtext=text='{chunk}':fontcolor={color_sub}:fontsize=40:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:borderw=5:bordercolor=black:shadowcolor=black:shadowx=3:shadowy=3:x=(w-tw)/2:y=(h-th)/2:enable='between(t,{current_time},{c_end})'")
                                current_time = c_end
            with open("subs_filter.txt", "w", encoding='utf-8') as f:
                f.write(",\n".join(drawtext_filters))
        except: pass

        clip_duration = 3.5 
        num_clips = math.ceil(dur_audio / clip_duration) 
        processed_clips = []
        
        status.write(f"🎞️ Buscando vídeos para: {tema_mostrar}...")
        v_urls = []
        for k in palabras_claves:
            url = f"https://api.pexels.com/videos/search?query={k}&per_page=10&orientation=portrait"
            try:
                res = requests.get(url, headers={"Authorization": pexels_key.strip()}, timeout=10).json()
                for v in res.get('videos', []):
                    v_urls.append(v['video_files'][0]['link'])
            except: pass
        
        random.shuffle(v_urls)
        last_valid_clip = None
        for i in range(num_clips): 
            try:
                v_url = v_urls[i % len(v_urls)] if v_urls else None
                if v_url:
                    with open(f"clip_{i}.mp4", 'wb') as f: f.write(requests.get(v_url, timeout=10).content)
                    subprocess.run(f'ffmpeg -y -i "clip_{i}.mp4" -vf "scale=1280:-1,zoompan=z=\'min(zoom+0.0015,1.4)\':d=125:x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):s=480x854,fps=25" -an -c:v libx264 -preset superfast -t {clip_duration} "p_{i}.mp4"', shell=True)
                    last_valid_clip = f"p_{i}.mp4"
                else: raise Exception("Error")
            except:
                if last_valid_clip: subprocess.run(f"cp {last_valid_clip} p_{i}.mp4", shell=True)
                else: subprocess.run(f'ffmpeg -y -f lavfi -i color=c=black:s=480x854:d={clip_duration}:r=25 -c:v libx264 -preset superfast p_{i}.mp4', shell=True)
            processed_clips.append(f"p_{i}.mp4")

        subprocess.run('ffmpeg -y -f lavfi -i color=c=black:s=480x854:d=3:r=25 -vf "drawtext=text=\'FENIX STUDIO 🦅\':fontcolor=white:fontsize=45:x=(w-tw)/2:y=(h-th)/2" -c:v libx264 -preset ultrafast outro.mp4', shell=True)
        with open("lista.txt", "w") as f:
            for p in processed_clips: f.write(f"file '{p}'\n")
            f.write("file 'outro.mp4'\n")
        subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)

        status.write("✨ Exportando Máster Viral...")
        v_final = f"output/v_{int(time.time())}.mp4"
        cmd = f'ffmpeg -y -i base.mp4 -i temp_a.mp3 -filter_complex_script subs_filter.txt -c:v libx264 -preset ultrafast -b:v 1500k -shortest "{v_final}"'
        subprocess.run(cmd, shell=True)
        
        if os.path.exists(v_final):
            st.video(v_final)
            st.balloons()
