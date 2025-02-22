import torch
import torchvision.transforms as T
import cv2
import numpy as np
import matplotlib.pyplot as plt
 
# Cargar modelo DeepLabV3
model = torch.hub.load("pytorch/vision:v0.10.0", "deeplabv3_resnet101", weights="DEFAULT")
model.eval()
 
# Clases de ropa en COCO y su nueva asignación personalizada
custom_classes = {
    5: 1,  # Camisa/Sudadera -> Nueva clase 1
    6: 2,  # Pantalón -> Nueva clase 2
    7: 3,  # Vestido -> Nueva clase 3
    11: 4, # Zapatos -> Nueva clase 4
    15: 5, # Bufanda -> Nueva clase 5
    17: 1  # Chaqueta -> Se agrupa con Camisa/Sudadera (clase 1)
}
 
# Definir colores personalizados para cada nueva clase
color_map = {
    1: (255, 0, 0),   # Rojo para Camisa/Sudadera/Chaqueta
    2: (0, 255, 0),   # Verde para Pantalón
    3: (0, 0, 255),   # Azul para Vestido
    4: (255, 255, 0), # Amarillo para Zapatos
    5: (255, 0, 255)  # Morado para Bufanda
}
 
# Transformación de imagen
transform = T.Compose([
    T.ToPILImage(),
    T.Resize(520),
    T.ToTensor(),
    T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])
 
# Cargar imagen
image_path = "/Users/claudiamahia/Desktop/Hack_udc/modelo.jpg"
image = cv2.imread(image_path)
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
 
# Convertir imagen
input_tensor = transform(image).unsqueeze(0)
 
# Pasar por el modelo
with torch.no_grad():
    output = model(input_tensor)["out"][0]
 
# Obtener la segmentación
output_predictions = output.argmax(0).byte().cpu().numpy()
 
# Crear una máscara con nuevas clases asignadas
mask = np.zeros_like(output_predictions)
 
for old_class, new_class in custom_classes.items():
    mask[output_predictions == old_class] = new_class
 
# Redimensionar máscara al tamaño original de la imagen
mask = cv2.resize(mask, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_NEAREST)
 
# Aplicar operaciones morfológicas para limpiar la máscara
kernel = np.ones((5, 5), np.uint8)  # Ajusta el tamaño según sea necesario
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)  # Elimina pequeños puntos
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel) # Cierra pequeños huecos
 
 
# Crear imagen en color basada en la segmentación
segmented_image = np.zeros_like(image)
 
for class_id, color in color_map.items():
    segmented_image[mask == class_id] = color
 
# Superponer con la imagen original
final_result = cv2.addWeighted(image, 0.8, segmented_image, 0.3, 0)
 
# Mostrar imágenes
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.imshow(image)
plt.title("Imagen Original")
 
plt.subplot(1, 2, 2)
plt.imshow(final_result)
plt.title("Ropa Segmentada (Optimizada)")
plt.show()