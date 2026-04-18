import cv2
import time
import requests

# Configuración
URL_API = "https://app-periferico.duckdns.org/auth/login"
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
cap = cv2.VideoCapture(0)

# Variables de estado
rostro_detectado_inicio = None
segundos_espera = 3
margen = 40
ya_enviado = False
resultados_auth = [] 

print("--- Sistema de Autenticación Visual iniciado ---")

while True:
    ret, frame = cap.read()
    if not ret: break

    alto_img, ancho_img = frame.shape[:2]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(40, 40))

    num_rostros = len(faces)

    if num_rostros > 0:
        if not ya_enviado:
            if rostro_detectado_inicio is None:
                rostro_detectado_inicio = time.time()
                print(f"\n[INFO] Rostro detectado. Iniciando cuenta regresiva de {segundos_espera}s...")
            
            tiempo_transcurrido = time.time() - rostro_detectado_inicio
            segundos_restantes = int(segundos_espera - tiempo_transcurrido)

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
                cv2.putText(frame, f"Identificando: {max(0, segundos_restantes)}s", (x, y-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

            if tiempo_transcurrido >= segundos_espera:
                print(f"[HTTP] Enviando {num_rostros} rostro(s) a la API...")
                resultados_auth = [] 
                
                for i, (x, y, w, h) in enumerate(faces):
                    y1, y2 = max(0, y - margen), min(alto_img, y + h + margen)
                    x1, x2 = max(0, x - margen), min(ancho_img, x + w + margen)
                    rostro_recortado = frame[y1:y2, x1:x2]

                    _, buffer = cv2.imencode('.jpg', rostro_recortado)
                    files = {'file': (f'rostro_{i}.jpg', buffer.tobytes(), 'image/jpeg')}

                    try:
                        print(f"  -> Procesando rostro {i+1}/{num_rostros}...")
                        response = requests.post(URL_API, files=files, timeout=7)
                        
                        # LOG DE RESPUESTA
                        print(f"  <- Servidor respondió (Status: {response.status_code})")
                        
                        if response.status_code == 200:
                            res_json = response.json()
                            print(f"     Datos: {res_json}") # Ver el JSON completo en consola
                            
                            nombre = res_json.get('name', 'Desconocido') if res_json.get('status') == 'Authenticated' else "No Autorizado"
                            resultados_auth.append(nombre)
                        else:
                            print(f"     Error: Código de estado no esperado.")
                            resultados_auth.append("Error Servidor")
                            
                    except requests.exceptions.Timeout:
                        print(f"  [!] Error: Tiempo de espera agotado (Timeout)")
                        resultados_auth.append("Timeout")
                    except Exception as e:
                        print(f"  [!] Error de red/sistema: {e}")
                        resultados_auth.append("Error Red")

                ya_enviado = True
                print("[INFO] Procesamiento finalizado. Mostrando resultados en pantalla.\n")
        else:
            for i, (x, y, w, h) in enumerate(faces):
                info_texto = resultados_auth[i] if i < len(resultados_auth) else "Procesando..."
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, info_texto, (x, y-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    else:
        if rostro_detectado_inicio is not None:
            print("[INFO] Rostro perdido. Reseteando estado.")
        rostro_detectado_inicio = None
        ya_enviado = False
        resultados_auth = []

    cv2.imshow('Login Biometrico Dinamico', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("[SISTEMA] Cerrando aplicación...")
        break

cap.release()
cv2.destroyAllWindows()