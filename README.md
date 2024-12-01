# Trabajo Práctico Final. Emphatic Zoom

# Grupo 2 - Santesteban/Sincosky/Fierro

Se genero una app que monitorea en tiempo real el estado emocional de los participantes en reuniones de Zoom, ayudando a los oradores a detectar señales de desinterés y así poder cambiar el rumbo de la presentación. Tiene una interfaz que permite ingresar el enlace de la reunión e indicar el número de participantes "aburridos" necesarios para activar una alerta. Utiliza Selenium para realizar la navegación automática y unirse al Zoom y AWS REKOGNITION para detectar las emociones faciales en las capturas que se realizan en él. Para este caso las emociones a detectar son: neutral, alegría, confusión, sorpresa, calma y disgustado pero se podrían adicionar otras. Además cuanto estas persisten, superando el umbral definido (partipantes "aburridos") emite una alerta, luego de esta los contadores se reinician.

## Workflow.

Librerias necesarias: tkinter-selenium-time-pyautogui-os-boto3-io-collections-threading 

1. Generar las credenciales de AWS REKOGNITION para que se puedan acceder a través de Boto3 (librería de python).

2. Ejecutar por terminal el script EZoom.py

   --> 2.1 Completar el primer label con el link del Zoom. 
   --> 2.2 Completar el segundo label con el número de participantes aburridos para que emita una alerta (Umbral). Por defecto el número de participantes es 2.
   --> 2.3 Hacer click en "Iniciar Zoom" para ingresar a la reunión. Tener en cuenta que una vez que se abra la pantalla de zoom, usted no debe intervenir en la ejecución ya que la app hace la navegación en forma automática.
