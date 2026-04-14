import face_recognition
import io

def get_face_embedding(image_bytes):
    image = face_recognition.load_image_file(io.BytesIO(image_bytes))

    # Detección de rostro
    face_locations = face_recognition.face_locations(image)
    if not face_locations:
        return None, 0, 0

    # Generación del embedding
    encodings = face_recognition.face_encodings(image, face_locations)
    return encodings[0]
