import streamlit as st
import os, time, random, subprocess, requests, math, re
import urllib.parse

st.set_page_config(page_title="Fénix Viral PRO", layout="centered")
st.markdown("<style>.stApp {background: #0d1117; color: white;}</style>", unsafe_allow_html=True)

def limpiar_texto_ia(texto):
    basura_ia = [
        "USER REQUEST", "START UP", "WRITE A", "ALL CAPS", "NO PERIODS", "SAYS ZERO", 
        "POINTS ZERO", "COMMAS ZERO", "DOESNT FORBID", "PERIODS OR", "OTHER PUNCTUATION",
        "ZERO COMAS", "SO CANNOT", "ZERO PUNTOS", "MEANS NO", "ARE PERIODS", "MAYBE SO",
        "EITHER WOULD", "BE EXTREMELY", "DIFFICULT THEY", "LIKELY MEAN", "PUNCTUATION LIKE",
        "COMMAS AND", "TILDES PROBABLY", "WE HAVE", "TO AVOID", "PERIODS BUT", "ESCRIBIR TODO",
        "EN MAYUSCULAS", "CAPS MUST", "BE AT", "LEAST", "WORDS NO", "TILDES EACH", "SENTENCE WITHOUT",
        "COMMAS OR", "SEEMS IMPOSSIBLE", "BECAUSE IT", "SENTENCE TERMINATION", "BUT PUNCTUATION",
        "MARKS OTHER", "THAN COMMA", "AND PERIOD", "ARE ALLOWED", "USE EXCLAMATION", "POINT QUESTION",
        "MARK MAYBE", "BUT THEY", "WHICH IS", "PERIODS SO", "CANT USE", "PERIODS THEY", "DIDNT FORBID",
        "FORBID EXCLAMATION", "OR QUESTION", "MARKS BUT", "WE CAN", "USE COLON", "WITHOUT COMMAS",
        "NEED TO", "CRAFT PARAGRAPHS", "ENSURE TOTAL", "NUMBER OF", "COMMAS IS", "ZERO SO", "WE",
        "CANNOT USE", "ANY COMMA", "WE CANNOT", "USE COMMAS", "SO WE", "HAVE TO", "AVOID LISTING",
        "WITH COMMAS", "WELL SEPARATE", "WITH OR", "SIEMPRE", "ETC", "ALSO AVOID", "TILDES ACCENT",
        "ACCENT MARKS", "IN SPANISH", "WORDS USE", "ONLY UNACCENTED", "SPANISH UNACCENTED", "LETTERS USE",
        "N INSTEAD", "OF NYE", "THEY SAID", "ZERO TILDES", "BUT ACCENTED", "BE REPLACED", "NYE IS",
        "NOT A", "TILDE BUT", "A DIFFERENT", "LETTER IN", "SPANISH ITS", "OKAY ITS", "A SEPARATE",
        "LETTER HOWEVER", "LIKELY THEY", "CONSIDER IT", "A TILDE", "MIGHT BE", "OKAY BUT", "ITS",
        "SAFER TO", "AVOID NYE", "OR MAYBE", "USE N", "VERSION N", "IS NYE", "NINO CONTAINS", "NYE WE",
        "MIGHT AVOID", "USING IT", "USE WORDS", "WITHOUT ACCENTS", "EG MODO", "USO AVOID", "CEDULA",
        "PROXIMO", "ETC SO", "USE PLAIN", "WORDS WE", "NEED 100", "WORDS ALL", "CAPS WE", "NEED STRUCTURE",
        "1 START", "WITH AN", "EYEOPENING FACT", "2 DEVELOPMENT", "EXPLAINING TO", "FRIEND DETAILS",
        "UNKNOWN 3", "REVEAL SECRET", "AND CLOSE", "LOGICALLY NO", "COMMAS NO", "PERIODS USE", "LINE BREAKS",
        "MAYBE WE", "CAN USE", "EXCLAMATION MARKS", "TO SEPARATE", "SENTENCES ENSURE", "NO PERIOD", "WE MUST",
        "AVOID PUNCTUATION", "THAT INCLUDES", "PERIOD USE", "EXCLAMATION AND", "QUESTION MAYBE", "THEY ASKED",
        "FOR ZERO", "PUNTOS MEANING", "PERIODS SO", "ONLY EXCLAMATION", "WE CAN", "USE QUESTION", "BUT ANY",
        "NUMBER OF", "EXCLAMATION COUNTS", "AS PUNCTUATION", "BUT NOT", "PERIODS IT", "IS ALLOWED", "IT DIDNT",
        "FORBID EXCLAMATION", "BUT ITS", "SAFER THEY", "SAID ZERO", "PUNTOS ZERO", "COMAS ZERO", "TILDES SO",
        "EXCLAMATION AND", "QUESTION ARE", "FINE WELL", "PRODUCE TEXT", "WITH EXCLAMATION", "MARKS ENSURE",
        "EACH SENTENCE", "ENDS WITH", "AN EXCLAMATION", "THAT WILL", "BE OKAY", "BUT WE", "NEED TO", "COUNT",
        "WORDS MINIMUM", "100 WORDS", "ALL CAPS", "LETS WRITE", "AROUND 130", "140 WORDS", "AVOID COMMAS",
        "AVOID TILDES", "AVOID ACCENTS", "LETS CRAFT", "GRACIAS A", "UNA ESTUDIO", "PUBLICADO EN", "2025 DATOS",
        "CUANDO EL", "GRADO DE", "UNA PYME", "DE SERVICIO", "O EL", "SEIS VECES", "MAYOR QUE", "QUE INVIERTE",
        "EUROS EN", "ESTO WE", "NEED WORDS", "WORDS WITHOUT", "ACCENTS EG", "GRACIAS ALL", "RIGHT LETS", "WRITE ENTIRE",
        "PIECE ENSURE", "NO COMMAS", "THAT MEANS", "CAREFUL PUNCTUATION", "NO COMMAS", "NO ACCENT", "MARKS ALSO",
        "NO NYE", "USE N", "BUT N", "IS A", "DISTINCT WORD", "INGRESOS OKAY", "LETS PRODUCE", "WE SHOULD", "WRITE",
        "WITH EXCLAMATION", "AT ENDS", "NO PUNCTUATION", "IN MIDDLE", "THAT USES", "COMMA LETS", "CRAFT GRACIAS",
        "A UN", "ESTUDIO DE", "FONDO EN", "2025 SE", "HALLA QUE", "POR CIENTO", "DE ESTUDIOS", "AGENCIAS DE",
        "INVIERTEN EN", "SERVICIOS SIN", "CAPITULO DIVERSIFICADO", "GANAN MUCHO", "DE LO", "QUE JUEGAN", "CON MILES",
        "DE EUROS", "EN BARRATUDES", "TOTALES NO", "BUT WE", "NEED TO", "ENSURE NO", "COMMAS PUNCTUATION", "NO COMMAS",
        "NO PERCENT", "USE POR", "CIENTO NO", "COMMAS NO", "TO STRUCTURE", "1 OPENING", "STATEMENT 2", "NARRATIVE",
        "STATEMENT 2", "3 REVEAL", "SECRET 4", "CLOSED FINAL", "WE CAN", "SEPARATE PARAGRAPHS", "LETS GENERATE",
        "FINAL ANSWER", "TOOL CALL", "REASONING CONTENT"
    ]
    texto_limpio = texto.upper()
    for b in basura_ia: texto_limpio = texto_limpio.replace(b, "")
    texto_limpio = re.sub(r'[^\w\s]', '', texto_limpio).replace('\n', ' ').strip()
    return re.sub(' +', ' ', texto_limpio)

def limpiar_orden(orden):
    basura = ["hazme", "haz", "arme", "asme", "dame", "dime", "un", "una", "el", "la", "los", "las", "video", "vídeo", "videos", "quiero", "sobre", "de", "del", "historia", "que", "hable", "como", "mejor", "para", "sin", "con", "en", "año"]
    palabras = orden.lower().split()
    limpias = [p for p in palabras if p not in basura and len(p) > 3]
    return " ".join(limpias) if limpias else orden, limpias

def obtener_guion_pro(orden_usuario):
    tema_mostrar, limpias = limpiar_orden(orden_usuario)
    keys = [p for p in limpias[:3]] + [f"{p} cinematic" for p in limpias[:2]]
    if not keys: keys = ["cinematic", "epic", "viral"]

    # LA MAGIA DE LA CREATIVIDAD: Un ángulo distinto cada vez que le pidas algo
    angulos = [
        "como si fuera un secreto revelado en la Deep Web por un hacker",
        "como si fuera un archivo desclasificado de una agencia de inteligencia",
        "como una estrategia secreta que usan los millonarios a puerta cerrada",
        "como un descubrimiento reciente que las grandes empresas intentan ocultar",
        "como una historia increible y poco conocida de hace decadas"
    ]
    angulo_elegido = random.choice(angulos)
    
    prompt_maestro = f"Crea un guion viral UNICO Y ORIGINAL. TEMA: '{orden_usuario}'. ENFOQUE OBLIGATORIO: Cuentame la historia {angulo_elegido}. ESTRUCTURA: 1. Gancho explosivo. 2. Desarrollo con datos muy raros o desconocidos. 3. Final cerrado revelando el secreto. REGLAS: INVENTA UNA HISTORIA NUEVA, NO REPITAS. SOLO TEXTO, NADA DE EXPLICACIONES. TODO EN MAYUSCULAS. CERO PUNTOS. CERO COMAS. CERO TILDES. MINIMO 120 PALABRAS."

    # RULETA DE GUIONES DE EMERGENCIA: Si falla la IA, tienes 4 salvavidas distintos
    fallbacks = [
        f"PRESTA ATENCION PORQUE LO QUE TE VOY A CONTAR SOBRE {tema_mostrar.upper()} FUE BORRADO DE INTERNET HACE HORAS UN HACKER LOGRO EXTRAER LOS DATOS ANTES DE QUE CERRARAN EL SERVIDOR Y DESCUBRIO QUE TODO ERA UNA ESTRATEGIA PARA MANTENERNOS DISTRAIDOS LA VERDADERA CLAVE DETRAS DE ESTO ES UNA TECNICA QUE SOLO EL UNO POR CIENTO CONOCE AHORA QUE SABES ESTO TIENES EL PODER EN TUS MANOS EL MISTERIO ESTA RESUELTO",
        f"DURANTE AÑOS NOS HICIERON CREER UNA MENTIRA SOBRE {tema_mostrar.upper()} PERO HOY VAMOS A DESTAPAR LA VERDAD UN EX EMPLEADO DE UNA GRAN CORPORACION HA DECIDIDO ROMPER SU CONTRATO DE SILENCIO PARA CONTAR QUE ESTE SISTEMA FUE DISEÑADO ORIGINALMENTE PARA CONTROLAR EL MERCADO AL CAMBIAR LAS REGLAS ELLOS SE QUEDABAN CON TODA LA VENTAJA HOY EL SECRETO HA SALIDO A LA LUZ Y EL JUEGO HA CAMBIADO PARA SIEMPRE",
        f"HAY UNA TEORIA OSCURA SOBRE {tema_mostrar.upper()} QUE LA ELITE NO QUIERE QUE ESCUCHES SIEMPRE PENSAMOS QUE FUNCIONABA DE FORMA NORMAL PERO LOS DOCUMENTOS RECIENTEMENTE DESCLASIFICADOS DEMUESTRAN LO CONTRARIO HABIA UN GRUPO DE EXPERTOS TRABAJANDO EN LA SOMBRA PARA ASEGURARSE DE QUE NADIE MAS PUDIERA REPLICAR EL METODO AHORA LAS PIEZAS ENCAJAN Y LA HISTORIA OFICIAL QUEDA DESTRUIDA",
        f"ESTE ES EL SECRETO MEJOR GUARDADO SOBRE {tema_mostrar.upper()} EN TODO EL MUNDO MUCHOS INTENTARON LLEGAR AL FONDO DE ESTO Y FRACASARON PERO LA LOGICA ES MUCHO MAS SIMPLE DE LO QUE PARECE TODO SE BASA EN UNA PEQUEÑA FALLA DEL SISTEMA QUE ALGUIEN DESCUBRIO POR ACCIDENTE Y DECIDIO OCULTAR PARA BENEFICIARSE AL DESCUBRIR ESE FALLO EL MISTERIO DESAPARECE Y LA VERDAD BRILLA CON FUERZA"
    ]
    guion_fallback = random.choice(fallbacks)

    # ANTI-CACHE: Usamos un número enorme al azar para que la IA piense que es una petición 100% nueva
    semilla = random.randint(100000, 9999999)

    try:
        url_1 = "https://sentence.fineshopdesign.com/api/ai"
        res_1 = requests.get(url_1, params={"prompt": prompt_maestro, "seed": semilla}, timeout=15).json()
        guion = limpiar_texto_ia(res_1.get("reply", ""))
        if len(guion) > 50: return guion, keys, tema_mostrar
    except:
        pass

    try:
        prompt_codificado = urllib.parse.quote(prompt_maestro)
        url_2 = f"https://text.pollinations.ai/{prompt_codificado}?seed={semilla}&system=Guionista%20experto"
        res_2 = requests.get(url_2, timeout=20)
        guion = limpiar_texto_ia(res_2.text)
        if len(guion) > 50: return guion, keys, tema_mostrar
    except:
        pass
            
    return limpiar_texto_ia(guion_fallback), keys, tema_mostrar

def time_to_sec(t_str):
    t_str = t_str.strip().split(' ')[0].replace(',', '.')
    partes = t_str.split(':')
    if len(partes) == 3: return float(partes[0])*3600 + float(partes[1])*60 + float(partes[2])
    elif len(partes) == 2: return float(partes[0])*60 + float(partes[1])
    else: return float(partes[0])

st.title("🦅 Fénix Studio: Universos Infinitos")

with st.sidebar:
    st.header("Motor de Renderizado")
    pexels_key = st.text_input("🔑 API Pexels:", value="Ty0uFISh3APEAXIVcrFpSM7ZdwOeRElCuUgoG42EW6WVISRTEfqjm0BZ", type="password")
    color_sub = st.selectbox("🎨 Color Subtítulos", ["yellow", "white", "cyan"])

if orden := st.chat_input("Pídeme lo que sea (Cada vídeo será único):"):
    with st.status("🎬 Pensando una historia 100% nueva...", expanded=True) as status:
        subprocess.run("rm -f p_*.mp4 clip_*.mp4 base.mp4 t.mp3 t.vtt music.mp3 final.mp4 temp_a.mp3 lista.txt subs_filter.txt outro.mp4", shell=True)
        
        guion, palabras_claves, tema_mostrar = obtener_guion_pro(orden)
        status.write(f"✍️ Guion creativo generado para: '{tema_mostrar}'.")
        
        subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --rate=-10% --text "{guion}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
        dur_audio_str = subprocess.check_output("ffprobe -i t.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True).decode('utf-8').strip()
        if not dur_audio_str:
            st.error("Error en audio. Generando respaldo rápido...")
            guion = limpiar_texto_ia(random.choice([
                f"PRESTA ATENCION PORQUE LO QUE TE VOY A CONTAR SOBRE {tema_mostrar.upper()} NO LO VAS A ESCUCHAR EN NINGUN OTRO LADO SIEMPRE NOS HAN DICHO QUE ERA ALGO COMPLETAMENTE NORMAL PERO HACE POCO UNOS INVESTIGADORES DESCUBRIERON ALGO QUE CAMBIA LAS REGLAS DEL JUEGO RESULTA QUE TODO ESTO FUE CREADO CON UNA TECNOLOGIA QUE AUN NO COMPRENDEMOS DEL TODO LOS QUE DESCUBRIERON ESTO INTENTARON AVISARNOS PERO FUERON SILENCIADOS RAPIDAMENTE POR SUERTE UNO DE ELLOS DEJO PRUEBAS OCULTAS Y AHORA EL MISTERIO ESTA RESUELTO YA NO PUEDEN SEGUIR ENGAÑANDONOS LA VERDAD POR FIN SALIO A LA LUZ"
            ]))
            subprocess.run(f'edge-tts --voice es-ES-AlvaroNeural --rate=-10% --text "{guion}" --write-media "t.mp3" --write-subtitles "t.vtt"', shell=True)
            dur_audio_str = subprocess.check_output("ffprobe -i t.mp3 -show_entries format=duration -v quiet -of csv='p=0'", shell=True).decode('utf-8').strip()

        dur_audio = float(dur_audio_str)

        tono = 70
        subprocess.run(f'ffmpeg -y -f lavfi -i "sine=frequency={tono}:duration={dur_audio+2}" -f lavfi -i "anoisesrc=d={dur_audio+2}:c=pink:a=0.03" -filter_complex "[0:a]volume=0.5[t];[1:a]volume=0.1[n];[t][n]amix=inputs=2:duration=first" music.mp3', shell=True)
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
        except:
            pass

        clip_duration = 3.5 
        num_clips = math.ceil(dur_audio / clip_duration) 
        processed_clips = []
        
        status.write(f"🎞️ Buscando vídeos creativos para: {', '.join(palabras_claves[:2])}...")
        v_urls = []
        for k in palabras_claves:
            url = f"https://api.pexels.com/videos/search?query={k}&per_page=10&orientation=portrait"
            try:
                res = requests.get(url, headers={"Authorization": pexels_key.strip()}, timeout=10).json()
                for v in res.get('videos', []):
                    v_urls.append(v['video_files'][0]['link'])
            except:
                pass
        
        random.shuffle(v_urls)
        last_valid_clip = None
        for i in range(num_clips): 
            try:
                v_url = v_urls[i % len(v_urls)] if v_urls else None
                if v_url:
                    with open(f"clip_{i}.mp4", 'wb') as f: f.write(requests.get(v_url, timeout=10).content)
                    subprocess.run(f'ffmpeg -y -i "clip_{i}.mp4" -vf "scale=1280:-1,zoompan=z=\'min(zoom+0.0015,1.4)\':d=125:x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):s=480x854,fps=25" -an -c:v libx264 -preset superfast -t {clip_duration} "p_{i}.mp4"', shell=True)
                    last_valid_clip = f"p_{i}.mp4"
                else:
                    raise Exception("Fallo Pexels")
            except:
                if last_valid_clip: subprocess.run(f"cp {last_valid_clip} p_{i}.mp4", shell=True)
                else: subprocess.run(f'ffmpeg -y -f lavfi -i color=c=black:s=480x854:d={clip_duration}:r=25 -c:v libx264 -preset superfast p_{i}.mp4', shell=True)
            processed_clips.append(f"p_{i}.mp4")

        subprocess.run('ffmpeg -y -f lavfi -i color=c=black:s=480x854:d=3:r=25 -vf "drawtext=text=\'FENIX STUDIO 🦅\':fontcolor=white:fontsize=45:x=(w-tw)/2:y=(h-th)/2" -c:v libx264 -preset ultrafast outro.mp4', shell=True)

        with open("lista.txt", "w") as f:
            for p in processed_clips: f.write(f"file '{p}'\n")
            f.write("file 'outro.mp4'\n")
        subprocess.run('ffmpeg -y -f concat -safe 0 -i lista.txt -c copy base.mp4', shell=True)

        status.write("✨ Quemando master único...")
        v_final = f"output/v_{int(time.time())}.mp4"
        cmd = f'ffmpeg -y -i base.mp4 -i temp_a.mp3 -filter_complex_script subs_filter.txt -c:v libx264 -preset ultrafast -b:v 1500k -shortest "{v_final}"'
        subprocess.run(cmd, shell=True)
        
        if os.path.exists(v_final):
            st.video(v_final)
            st.balloons()
