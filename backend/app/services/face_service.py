import face_recognition
import io

class FaceDetectionError(Exception):
    def __init__(self, message):
        self.message = message

def get_face_embedding(image_bytes):
    try:
        image = face_recognition.load_image_file(io.BytesIO(image_bytes))
        face_locations = face_recognition.face_locations(image)
        
        if not face_locations:
            raise FaceDetectionError("No se detectó ningún rostro.")
            
        if len(face_locations) > 1:
            raise FaceDetectionError("Se detectó más de un rostro.")
            
        encodings = face_recognition.face_encodings(image, known_face_locations=face_locations)
        
        return encodings[0] if encodings else None
    except FaceDetectionError as e:
        # Re-lanzamos nuestra excepción personalizada
        raise e
    except Exception as e:
        return None