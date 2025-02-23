# ¡¿Cuánto vale tu outfit en Inditex?!

Sube una foto de un outfit y descubre cuánto costaría si lo compraras en Inditex. Utilizando la **API Visual Search de INDITEXTECH**, nuestra aplicación identifica cada prenda en la imagen y encuentra las opciones más similares en las tiendas de Inditex.

---

## 🚀 Instalación y requisitos

### 1. Clona el repositorio:
```bash
git clone https://github.com/tu-repo/outfit-inditex.git
cd outfit-inditex
```

### 2. Crea un entorno virtual y actívalo:
```bash
python -m venv venv
. ./venv/bin/activate      # En macOS/Linux
.\venv\Scripts\activate    # En Windows
```

### 3. Instala las dependencias con *requirements.txt*:
```bash
pip install -r requirements.txt
```

### 4. Configura las credenciales de la API de INDITEXTECH:
Registra una cuenta en INDITEXTECH y obtén una clave de API para la **Visual Search API**. Luego, crea un archivo `.env` y agrega:
```
PUBLIC=tu-id
SECRET=tu-clave
```

Donde `PUBLIC` es el "`client_id`" y `SECRET` es el "`client_secret`" de tu cuenta en `developers.inditex.com`. \
Sigue sus instrucciones para obtener estos valores.

---

## 🔍 Cómo funciona
1. Sube una imagen con un outfit completo.
2. Nuestra aplicación segmenta las prendas individuales utilizando [MediaPipe PoseLandmarker](https://developers.google.com/mediapipe/solutions/vision/pose_landmarker).
3. Cada prenda segmentada se envía a la [API de Búsqueda Visual de InditexTech](https://developers.inditex.com/).
4. Obtenemos las prendas más similares disponibles en tiendas Inditex.
5. Se genera un informe con precios y enlaces de compra.

---

## ✅ Lo que funciona
✔ Identificación de prendas mediante **visión por computadora** con [MediaPipe](https://developers.google.com/mediapipe).
✔ Búsqueda de prendas similares en Inditex con la **API de Visual Search**.
✔ Interfaz sencilla para cargar imágenes y obtener resultados rápidos.

## ⚠ Limitaciones
⚠ La precisión puede variar en condiciones de mala iluminación o poses complejas.
⚠ Algunas prendas pueden no tener equivalentes exactos en Inditex.
⚠ Por limitaciones Inditex, actualmente sólo se recuperan prendas similares en Zara.

---

## ❓ ¿Tienes problemas o dudas?
Abre un **issue** en GitHub o contáctanos en:
- [lua.ricor@udc.es](mailto:lua.ricor@udc.es)
- [p.fernandezf@udc.es](mailto:p.fernandezf@udc.es)
- [c.mvarela@udc.es](mailto:c.mvarela@udc.es)
- [xoel.maestu@udc.es](mailto:xoel.maestu@udc.es)

---

## 🤝 Contribuir
¿Quieres mejorar este proyecto? ¡Toda ayuda es bienvenida!

1. Haz un fork del repositorio.
2. Crea una nueva rama para tu cambio: `git checkout -b feature/nueva-mejora`
3. Haz tus cambios y comprueba que todo funciona.
4. Sube tus cambios: `git commit -m "Mejorando X"`
5. Haz un push: `git push origin feature/nueva-mejora`
6. Abre un **Pull Request**.

---

## 👥 Créditos
Proyecto desarrollado durante **HackUDC2025** por un equipo de estudiantes de **3º curso de Ciencia e Ingeniería de Datos** de la Universidad de A Coruña.

---

## ❌ Intentos de implementación no satisfactorios
- Segmentación de prendas individuales: [Torchvision *deeplabv3_resnet101*](https://pytorch.org/vision/main/models/generated/torchvision.models.segmentation.deeplabv3_resnet101.html) fine tunning con [Fashionpedia](https://fashionpedia.github.io/home/data_license.html).

---

## 💡 Posibles futuras implementaciones
- Implementación de un LLM que interactúe con la usuaria para optimizar la capacidad de respuesta satisfactoria.

---

## 🐝 Licencia
Este proyecto está bajo la licencia [BSD 3-Clause](https://opensource.org/licenses/BSD-3-Clause). ¡Úsalo libremente! 🎉
