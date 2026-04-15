import streamlit as st
import os, time, random, subprocess, math, re

st.set_page_config(page_title="Fénix Viral PRO", layout="centered")

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

st.markdown('<div class="pro-title">FÉNIX AI STUDIO v9.0</div>', unsafe_allow_html=True)
st.markdown('<div class="pro-subtitle">Cerebro Omnipotente • Todos los Nichos del Mundo</div>', unsafe_allow_html=True)

def limpiar_orden(orden):
    basura = ["hazme", "haz", "arme", "asme", "dame", "dime", "un", "una", "el", "la", "los", "las", "video", "vídeo", "videos", "quiero", "sobre", "de", "del", "historia", "que", "hable", "como", "mejor", "para", "sin", "con", "en", "año"]
    palabras = orden.lower().split()
    limpias = [p for p in palabras if p not in basura and len(p) > 3]
    return " ".join(limpias) if limpias else orden, limpias

# --- EL MEGA DETECTOR DE NICHOS ---
def detectar_nicho(tema):
    t = tema.lower()
    if any(w in t for w in ["miedo", "terror", "fantasma", "paranormal", "horror", "oscuridad", "demonio", "maldito", "asesino", "leyenda", "creepy"]): return "terror"
    elif any(w in t for w in ["negocio", "dinero", "invertir", "inversion", "empresa", "millonario", "finanzas", "cripto", "emprendedor", "ventas", "marketing", "riqueza", "dolares", "trabajo"]): return "negocios"
    elif any(w in t for w in ["ciencia", "espacio", "universo", "planeta", "tecnologia", "curiosidad", "animales", "naturaleza", "biologia", "descubrimiento"]): return "ciencia"
    elif any(w in t for w in ["motivacion", "psicologia", "mente", "exito", "depresion", "ansiedad", "habitos", "disciplina", "desarrollo"]): return "motivacion"
    elif any(w in t for w in ["salud", "fitness", "ejercicio", "dieta", "gimnasio", "musculo", "entrenamiento", "comida", "nutricion"]): return "salud"
    elif any(w in t for w in ["conspiracion", "gobierno", "secreto", "oculto", "misterio", "alien", "ovni"]): return "misterio"
    else: return "universal" # El Comodín para TODO LO DEMÁS

# --- EL CEREBRO HUMANO UNIVERSAL ---
def generar_guion_humano(tema, nicho):
    tema = tema.upper()
    
    variables = {
        "tema": tema,
        "año": random.choice(["DOS MIL OCHO", "DOS MIL QUINCE", "HACE MUY POCO TIEMPO", "MIL NOVECIENTOS NOVENTA", "EL AÑO PASADO", "HACE UNOS MESES"]),
        "enemigo_negocio": random.choice(["LOS BANCOS", "LA ELITE FINANCIERA", "LAS GRANDES EMPRESAS", "EL SISTEMA TRADICIONAL"]),
        "enemigo_misterio": random.choice(["EL GOBIERNO", "UNA AGENCIA SECRETA", "LAS ALTAS ESFERAS", "LA ELITE"]),
        "porcentaje": random.choice(["NOVENTA Y NUEVE", "NOVENTA Y CINCO", "OCHENTA Y OCHO", "NOVENTA"]),
        "dinero": random.choice(["MILES DE DOLARES", "TODO SU DINERO", "MUCHISIMO CAPITAL", "SUS AHORROS"]),
        "lugar_creepy": random.choice(["UN HOSPITAL ABANDONADO", "MEDIO DEL BOSQUE", "UNA CUEVA CERRADA AL PUBLICO", "UN SOTANO ANTIGUO"]),
        "locura": random.choice(["UNA VERDADERA LOCURA", "ALGO BRUTAL", "ALGO QUE NO TIENE SENTIDO LOGICO", "UNA AUTENTICA BARBARIDAD", "ALGO QUE TE VOLARA LA CABEZA"]),
    }

    if nicho == "negocios":
        plantillas = [
            "SI ESTAS INTENTANDO METERTE EN {tema} DEJA DE HACERLO AHORA MISMO Y ESCUCHA EL {porcentaje} POR CIENTO DE LA GENTE PIERDE {dinero} PORQUE NO ENTIENDEN ESTA TRAMPA EN {año} {enemigo_negocio} CREARON UN SISTEMA PERFECTO PARA QUE TU Y YO FRACASEMOS SU PLAN ERA QUEDARSE CON TODO EL BENEFICIO MIENTRAS NOSOTROS PERDEMOS EL TIEMPO PERO HACE NADA UN ANALISTA FILTRO LA ESTRATEGIA REAL Y ES {locura} LA CLAVE ESTA EN HACER JUSTO LO CONTRARIO DE LO QUE DICEN LAS NOTICIAS CUANDO TODOS ENTRAN EN PANICO TU ATACAS CUANDO TODOS COMPRAN TU TE ALEJAS ESTE SIMPLE CAMBIO MENTAL ROMPE SU ALGORITMO APLICALO HOY Y EMPEZARAS A VER RESULTADOS DE VERDAD SIGUENOS PARA MAS NEGOCIOS"
        ]
    elif nicho == "terror":
        plantillas = [
            "NO MIRES ESTO DE NOCHE SI DE VERDAD LE TIENES MIEDO A {tema} SEGURO PIENSAS QUE ES UN INVENTO DE INTERNET O UN CUENTO PARA ASUSTAR PERO EN {año} LA COSA SE SALIO DE CONTROL LA POLICIA ENCONTRO ALGO HORRIBLE EN {lugar_creepy} LAS GRABACIONES DE SEGURIDAD MOSTRARON ALGO QUE DESAFIA TODA LOGICA EL GOBIERNO CLASIFICO LOS VIDEOS EN SEGUNDOS PERO ALGUIEN LOGRO FILTRARLOS EN LA DEEP WEB ANTES DE DESAPARECER LOS DOCUMENTOS REVELAN QUE TODAS LAS VICTIMAS HICIERON LO MISMO ANTES DE SU FINAL Y LO MAS ATERRADOR DE TODO ESTO NO ES QUE HAYA PASADO SINO QUE ESA COSA SIGUE SUELTA BUSCANDO A GENTE QUE NO PRESTA ATENCION SI ESTA NOCHE ESCUCHAS UN GOLPE NO ABRAS LA PUERTA SIGUENOS PARA MAS TERROR"
        ]
    elif nicho == "ciencia":
        plantillas = [
            "EL {porcentaje} POR CIENTO DE LA GENTE NO TIENE NI IDEA DE ESTA LOCURA SOBRE {tema} SIEMPRE NOS ENSEÑARON QUE ERA ALGO SUPER ABURRIDO O NORMAL PERO UN ESTUDIO DE {año} REVELO UN DATO QUE TE VA A DEJAR SIN PALABRAS RESULTA QUE LOS EXPERTOS HABIAN IGNORADO UN DETALLE DURANTE DECADAS PERO UN CIENTIFICO SE PUSO A INVESTIGAR A FONDO Y ENCONTRO {locura} BASICAMENTE LA CIENCIA MODERNA CONFIRMA QUE CASI TODO LO QUE SABIAMOS ESTABA MAL ESTE SIMPLE HECHO CAMBIA POR COMPLETO NUESTRA FORMA DE ENTENDER EL MUNDO AHORA QUE CONOCES ESTE DATO ERES PARTE DEL UNO POR CIENTO QUE VE LA REALIDAD COMO ES SIGUENOS PARA MAS CURIOSIDADES"
        ]
    elif nicho == "motivacion":
        plantillas = [
            "ESTAS PERDIENDO EL TIEMPO CON {tema} Y TE VOY A EXPLICAR EXACTAMENTE POR QUE TODO EL MUNDO SE OBSESIONA CON HACERLO COMO TE DIJERON EN LA ESCUELA PERO ESO ES UNA TRAMPA GIGANTE LA VERDADERA CLAVE LA DESCUBRIO UN EXPERTO EN PSICOLOGIA HACE NADA Y ES {locura} EL TRUCO ESTA EN CAMBIAR COMPLETAMENTE TU ENFOQUE MENTAL DEJA DE HACER LO QUE HACE LA MASA ABORREGADA Y EMPIEZA A USAR TUS HABITOS A TU FAVOR APLICALO HOY MISMO Y NOTARAS EL CAMBIO EN TU VIDA AL INSTANTE DEJA DE PONER EXCUSAS Y TOMA EL CONTROL DE UNA VEZ SIGUENOS PARA MAS MOTIVACION"
        ]
    elif nicho == "salud":
        plantillas = [
            "TE ESTAN ENGAÑANDO DESCARADAMENTE CON {tema} LA INDUSTRIA GASTA MILLONES PARA QUE CREAS QUE NECESITAS METODOS COMPLICADOS Y CAROS PERO ES PURA BASURA EN {año} SE FILTRO UN ESTUDIO INDEPENDIENTE QUE LO CAMBIO TODO DESCUBRIERON QUE EL {porcentaje} POR CIENTO DE LOS PRODUCTOS COMERCIALES NO SIRVEN PARA NADA EL VERDADERO SECRETO ES TAN SIMPLE QUE DA RABIA Y ES {locura} SOLO TIENES QUE DEJAR DE SEGUIR MODAS TONTAS Y APLICAR LA BIOLOGIA BASICA A TU FAVOR TU CUERPO RESPONDERA EN CUESTION DE DIAS SI DEJAS DE METERLE BASURA EMPIEZA HOY MISMO Y SIENTE LA DIFERENCIA SIGUENOS PARA MAS SALUD"
        ]
    elif nicho == "misterio":
        plantillas = [
            "VAN A BORRAR ESTE VIDEO EN CUALQUIER MOMENTO PORQUE HABLA DE {tema} LLEVAMOS DECADAS PENSANDO QUE ES ALGO TOTALMENTE INOFENSIVO PERO DOCUMENTOS RECIENTES DEMUESTRAN QUE EN {año} {enemigo_misterio} LLEVO A CABO EXPERIMENTOS SUPER SECRETOS CON ESTO SU OBJETIVO REAL ERA METERSE EN NUESTRA MENTE SIN DEJAR RASTRO UN INVESTIGADOR SE DIO CUENTA DE LA TRAMPA Y ESCAPO CON LOS DISCOS DUROS INTENTARON CALLARLO PERO YA ERA TARDE LA INFORMACION ESTA VOLANDO POR LA RED EL ENGAÑO SE HA CAIDO A PEDAZOS Y AHORA TU TAMBIEN LO SABES SIGUENOS PARA MAS MISTERIOS"
        ]
    else: # UNIVERSAL (El comodín maestro para cualquier tema)
        plantillas = [
            "TE APUESTO LO QUE QUIERAS A QUE NO SABIAS ESTO SOBRE {tema} CASI TODO EL MUNDO CREE QUE ES ALGO TOTALMENTE NORMAL Y CORRIENTE PERO HAY UN DETALLE OCULTO QUE MUY POCOS CONOCEN HACE POCO TIEMPO SE HIZO VIRAL UN CASO QUE LO CAMBIA TODO ALGUIEN SE DIO CUENTA DE UN PATRON QUE NADIE MAS HABIA VISTO Y ES {locura} ESTE SIMPLE DETALLE CAMBIA POR COMPLETO LA FORMA EN LA QUE DEBERIAMOS VERLO LA PROXIMA VEZ QUE ESTES FRENTE A ESTO RECUERDA ESTE VIDEO PORQUE YA NO VAS A PODER IGNORARLO NUNCA MAS COMPARTELO CON TUS AMIGOS Y SIGUENOS PARA MAS CURIOSIDADES INCREIBLES",
            
            "EL NOVENTA Y NUEVE POR CIENTO DE LAS PERSONAS HACE MAL ESTO CON {tema} SIEMPRE NOS HEMOS ACOSTUMBRADO A HACERLO DE LA MANERA TRADICIONAL PERO ESTAMOS DESPERDICIANDO SU VERDADERO POTENCIAL UN EXPERTO REVELO HACE POCO EL TRUCO DEFINITIVO Y ES {locura} EN LUGAR DE COMPLICARTE LA VIDA SOLO TIENES QUE HACER UN PEQUEÑO AJUSTE Y EL RESULTADO SE MULTIPLICA AL INSTANTE LOS QUE YA LO ESTAN HACIENDO TIENEN UNA VENTAJA BRUTAL SOBRE EL RESTO NO TE QUEDES ATRAS Y EMPIEZA A APLICARLO HOY MISMO TE PROMETO QUE ME LO VAS A AGRADECER SIGUENOS PARA MAS TRUCOS COMO ESTE"
        ]
    
    return random.choice(plantillas).format(**variables)

def obtener_guion_pro(orden_usuario):
    tema_mostrar, limpias = limpiar_orden(orden_usuario)
    nicho = detectar_nicho(orden_usuario)
    
    if nicho == "terror": sufijo = "creepy dark"
    elif nicho == "negocios": sufijo = "money success"
    elif nicho == "ciencia": sufijo = "science macro"
    elif nicho == "motivacion": sufijo = "success focus"
    elif nicho == "salud": sufijo = "fitness healthy"
    else: sufijo = "cinematic epic"
        
    keys = [p for p in limpias[:3]] + [f"{p} {sufijo}" for p in limpias[:2]]
    if not keys: keys = [sufijo]

    guion = generar_guion_humano(tema_mostrar, nicho)
    return guion, keys, tema_mostrar

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
    st.caption("Fénix System | Cerebro Omnipotente ✅")

if orden := st.chat_input("Dime CUALQUIER tema (Ej: el amor, perros, dieta, planetas...):"):
    with st.status(f"🚀 Iniciando... Analizando nicho para '{orden}'", expanded=True) as status:
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.mp3 t.vtt music.mp3 final.mp4 temp_a.mp3 lista.txt subs_filter.txt outro.mp4", shell=True)
        
        guion, palabras_claves, tema_mostrar = obtener_guion_pro(orden)
        nicho_detectado = detectar_nicho(orden)
        status.write(f"✓ Nicho activado: **{nicho_detectado.upper()}**")
        
        subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --rate=-10% --text "{guion}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
        dur_audio_str = subprocess.check_output("ffprobe -i t.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True).decode('utf-8').strip()
        if not dur_audio_str: dur_audio_str = "40.0"
        dur_audio = float(dur_audio_str)

        # Ajuste de audio según nicho
        tono = 50 if nicho_detectado == "terror" else 75
        ruido = 0.05 if nicho_detectado == "terror" else 0.02
        subprocess.run(f'ffmpeg -y -f lavfi -i "sine=frequency={tono}:duration={dur_audio+2}" -f lavfi -i "anoisesrc=d={dur_audio+2}:c=pink:a={ruido}" -filter_complex "[0:a]volume=0.5[t];[1:a]volume=0.1[n];[t][n]amix=inputs=2:duration=first" music.mp3', shell=True)
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
        
        status.write(f"🎞️ Sincronizando imágenes HD ({nicho_detectado})...")
        palabras_guion = guion.split()
        chunk_size = max(1, len(palabras_guion) // max(1, num_clips))
        stop_words = {"PRESTA", "MUCHA", "ATENCION", "PORQUE", "QUE", "TE", "VOY", "A", "CONTAR", "SOBRE", "EL", "LA", "LOS", "LAS", "UN", "UNA", "UNOS", "UNAS", "CON", "SIN", "PARA", "POR", "DE", "DEL", "Y", "O", "ES", "SON", "HA", "HAN", "SE", "LO", "LE", "NO", "MAS", "ESTO", "ESTA", "ESTAS", "ESTOS", "TODO", "PERO", "SI", "COMO", "CUANDO", "DONDE", "AQUI", "ALLI", "MUY", "TAN", "SU", "SUS", "AL", "NOS", "MI", "MIS", "ENTRE", "HAY", "ESTE", "AUNQUE", "HASTA", "DESDE", "ENTONCES", "TIENES", "SIGUENOS", "AHORA", "ELLOS", "MUNDO", "TIEMPO", "SOLO"}
        
        last_valid_clip = None
        for i in range(num_clips): 
            inicio = int(i * chunk_size)
            fin = int((i + 1) * chunk_size)
            trozo = palabras_guion[inicio:fin]
            
            palabras_utiles = [p for p in trozo if p not in stop_words and len(p) > 4]
            busquedas_a_intentar = []
            
            if nicho_detectado == "terror": sufijo_nicho = "creepy"
            elif nicho_detectado == "negocios": sufijo_nicho = "money"
            elif nicho_detectado == "ciencia": sufijo_nicho = "science"
            elif nicho_detectado == "motivacion": sufijo_nicho = "success"
            elif nicho_detectado == "salud": sufijo_nicho = "fitness"
            else: sufijo_nicho = "cinematic"
            
            if palabras_utiles:
                palabras_utiles.sort(key=len, reverse=True)
                busquedas_a_intentar.append(f"{palabras_utiles[0]} {sufijo_nicho}")
                if len(palabras_utiles) > 1:
                    busquedas_a_intentar.append(f"{palabras_utiles[1]} {sufijo_nicho}")
            
            busquedas_a_intentar.extend(palabras_claves)
            
            v_url = None
            for busqueda in busquedas_a_intentar:
                try:
                    res = requests.get(f"https://api.pexels.com/videos/search?query={busqueda}&per_page=5&orientation=portrait", headers={"Authorization": pexels_key.strip()}, timeout=5).json()
                    videos = res.get('videos', [])
                    if videos:
                        v_url = random.choice(videos)['video_files'][0]['link']
                        status.write(f"  ► Clip {i+1}: '{busqueda}'")
                        break
                except: pass
            
            try:
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

        status.write("✨ Renderizando Master Final HD...")
        v_final = f"output/v_{int(time.time())}.mp4"
        cmd = f'ffmpeg -y -i base.mp4 -i temp_a.mp3 -filter_complex_script subs_filter.txt -c:v libx264 -preset veryfast -b:v 3000k -shortest "{v_final}"'
        subprocess.run(cmd, shell=True)
        
        if os.path.exists(v_final):
            st.success("✅ Video Universal completado.")
            st.video(v_final)
