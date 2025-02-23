import cv2
import logging
import numpy as np
import requests
import mediapipe as mp
from mediapipe.tasks.python import vision
from mediapipe.tasks import python
from mediapipe.framework.formats import landmark_pb2

# Función para descargar el modelo PoseLandmarker
def download_model(model_url="https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/1/pose_landmarker_heavy.task", model_path="pose_landmarker.task"):
    """
    Descarga el modelo PoseLandmarker desde una URL y lo guarda en el disco local.
    
    Args:
    model_url (str): URL desde la cual se descargará el modelo.
    model_path (str): Ruta donde se guardará el modelo descargado.
    
    Returns:
    None
    """
    # Descargar el modelo PoseLandmarker desde la URL proporcionada
    logging.debug(f"Descargando el modelo desde {model_url}...")
    response = requests.get(model_url)
    
    # Guardar el archivo descargado en el disco
    with open(model_path, "wb") as f:
        f.write(response.content)
    logging.debug(f"Modelo descargado y guardado en {model_path}")


# Función para cargar el modelo PoseLandmarker
def load_pose_model(model_path="pose_landmarker.task"):
    """
    Carga el modelo PoseLandmarker usando Mediapipe.
    
    Args:
    model_path (str): Ruta del archivo del modelo descargado.
    
    Returns:
    detector: Instancia del detector PoseLandmarker cargado.
    """
    # Cargar el modelo PoseLandmarker de Mediapipe
    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.PoseLandmarkerOptions(base_options=base_options, output_segmentation_masks=True)
    detector = vision.PoseLandmarker.create_from_options(options)
    logging.debug("Modelo PoseLandmarker cargado exitosamente.")
    return detector


# Función para descargar la imagen desde la URL
def download_image(url):
    """
    Descarga una imagen desde una URL.
    
    Args:
    url (str): URL de la imagen a descargar.
    
    Returns:
    image: Imagen descargada como un arreglo NumPy.
    """
    img_array = np.asarray(bytearray(requests.get(url).content), dtype=np.uint8)
    image = cv2.imdecode(img_array, -1)
    return image


# Función para calcular el factor de escala usando múltiples landmarks
def calculate_scale_factor(landmarks, image, scale_multiplier=1.5):
    """
    Calcula un factor de escala basado en la distancia entre varios puntos clave del cuerpo.
    
    Args:
    landmarks (list): Lista de landmarks de la pose.
    image (numpy.ndarray): Imagen original en la que se detectó la pose.
    scale_multiplier (float): Multiplicador que ajusta la magnitud de la escala.
    
    Returns:
    scale_factor (float): Factor de escala calculado.
    """
    # Calcular la distancia entre varios puntos clave (hombros, caderas, rodillas, tobillos)
    shoulder_distance = np.linalg.norm(np.array([landmarks[14].x, landmarks[14].y]) - np.array([landmarks[15].x, landmarks[15].y]))
    hip_distance = np.linalg.norm(np.array([landmarks[18].x, landmarks[18].y]) - np.array([landmarks[19].x, landmarks[19].y]))
    knee_distance = np.linalg.norm(np.array([landmarks[25].x, landmarks[25].y]) - np.array([landmarks[26].x, landmarks[26].y]))
    ankle_distance = np.linalg.norm(np.array([landmarks[28].x, landmarks[29].y]) - np.array([landmarks[31].x, landmarks[31].y]))

    # Promediar las distancias calculadas
    average_distance = np.mean([shoulder_distance, hip_distance, knee_distance, ankle_distance])

    # Definir una distancia estándar promedio (esto es una aproximación en píxeles)
    standard_average_distance = 200  # Ajustable según el tamaño de la imagen y los objetivos

    # Calcular el factor de escala basado en la distancia promedio y el tamaño de la imagen
    scale_factor = standard_average_distance / (average_distance * image.shape[1])

    # Ajustar el factor de escala usando el multiplicador
    scale_factor *= scale_multiplier

    return scale_factor


# Función para extraer una región ajustada a la escala
def extract_scaled_region(image, landmarks, region_points, scale_factor, margin=80):
    """
    Extrae y ajusta a la escala una región de la imagen basada en puntos clave de los landmarks.
    
    Args:
    image (numpy.ndarray): Imagen original.
    landmarks (list): Lista de landmarks de la pose.
    region_points (list): Lista de índices de puntos clave para definir la región a extraer.
    scale_factor (float): Factor de escala calculado.
    margin (int): Margen adicional para la extracción de la región.
    
    Returns:
    region_resized (numpy.ndarray): Región extraída y redimensionada de la imagen.
    """
    # Obtener las coordenadas de los puntos clave
    x_coords = [int(landmarks[point].x * image.shape[1]) for point in region_points]
    y_coords = [int(landmarks[point].y * image.shape[0]) for point in region_points]

    # Calcular los límites de la región
    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)

    # Ajustar los límites de la región con un margen
    min_x = max(min_x - margin, 0)
    max_x = min(max_x + margin, image.shape[1])
    min_y = max(min_y - margin, 0)
    max_y = min(max_y + margin, image.shape[0])

    # Extraer la región
    region = image[min_y:max_y, min_x:max_x]
    
    # Redimensionar la región a las nuevas dimensiones basadas en el factor de escala
    new_width = int(region.shape[1] * scale_factor)
    new_height = int(region.shape[0] * scale_factor)
    region_resized = cv2.resize(region, (new_width, new_height))

    return region_resized


# Función para procesar la imagen desde una URL y devolver las regiones ajustadas a la escala
def process_image_from_url(image_url, detector, scale_multiplier=1.5):
    """
    Procesa la imagen desde una URL, calcula el factor de escala y extrae regiones ajustadas.
    
    Args:
    image_url (str): URL de la imagen a procesar.
    detector: Instancia de PoseLandmarker.
    scale_multiplier (float): Multiplicador de escala ajustable.
    
    Returns:
    dict: Diccionario con las imágenes extraídas (cabeza, torso, piernas, pies).
    """
    # Descargar la imagen
    image = download_image(image_url)

    # Convertir la imagen para ser compatible con MediaPipe
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)

    # Detectar los landmarks de la pose
    results = detector.detect(mp_image)

    if not results.pose_landmarks:
        logging.debug("No se detectaron landmarks en la imagen.")
        return None

    # Calcular el factor de escala
    scale_factor = calculate_scale_factor(results.pose_landmarks[0], image, scale_multiplier)

    # Definir puntos clave para diferentes regiones del cuerpo
    head_points = [1, 2, 3, 4, 5]   # Puntos correspondientes a la cabeza
    torso_points = [12, 13, 14, 15]  # Puntos correspondientes al torso
    legs_points = [23, 24, 25, 26, 27, 28]  # Puntos correspondientes a las piernas
    feet_points = [28, 29, 30, 31]  # Puntos correspondientes a los pies

    # Extraer las diferentes regiones de la imagen
    head_image = extract_scaled_region(image, results.pose_landmarks[0], head_points, scale_factor)
    torso_image = extract_scaled_region(image, results.pose_landmarks[0], torso_points, scale_factor)
    legs_image = extract_scaled_region(image, results.pose_landmarks[0], legs_points, scale_factor)
    feet_image = extract_scaled_region(image, results.pose_landmarks[0], feet_points, scale_factor)

    # Retornar las imágenes extraídas
    return {
        "head": head_image,
        "torso": torso_image,
        "legs": legs_image,
        "feet": feet_image
    }

# Main para ejecutar el código
if __name__ == "__main__":
    # Descargar y cargar el modelo
    download_model()
    detector = load_pose_model()

    # Ejemplo de uso con una URL
    image_url = "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?q=80&w=1920&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D.jpg"
    result = process_image_from_url(image_url, detector, scale_multiplier=2.0)
    logging.debug(result)
