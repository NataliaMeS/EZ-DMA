import tkinter as tk
from tkinter import messagebox
#import requests
from selenium import webdriver
import time
import pyautogui
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os
import boto3
#import io
from collections import Counter
from threading import Thread

class Empatico:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Empathic Zoom")
        
        self.etiqueta_link = tk.Label(ventana, text="Ingrese enlace:")
        self.etiqueta_link.pack(pady=10)
        
        self.entrada_link = tk.Entry(ventana, width=50)
        self.entrada_link.pack(pady=10)
        
        self.etiqueta_participantes = tk.Label(ventana, text="Participantes aburridos para alerta (por defecto 2):")
        self.etiqueta_participantes.pack(pady=10)
        
        self.entrada_participantes = tk.Entry(ventana, width=10)
        self.entrada_participantes.insert(0, "2")  # Valor por defecto
        self.entrada_participantes.pack(pady=10)
        
        self.boton_iniciar = tk.Button(ventana, text="Iniciar Zoom", command=self.iniciar_zoom)
        self.boton_iniciar.pack(pady=10)
        
        self.etiqueta_resultado = tk.Label(ventana, text="", font=("Helvetica", 14))
        self.etiqueta_resultado.pack(padx=20, pady=20)
        
        self.etiqueta_aburrimiento = tk.Label(ventana, text="Nivel de aburrimiento: 0", font=("Helvetica", 14), fg="red")
        self.etiqueta_aburrimiento.pack(padx=20, pady=20)
        
        self.contador_aburrimiento = 0

    def iniciar_zoom(self):
        enlace = self.entrada_link.get()
        
        if not enlace:
            messagebox.showerror("Error", "El enlace no puede estar vacío")
            return
        
        try:
            self.umbral_aburrimiento = int(self.entrada_participantes.get())
        except ValueError:
            messagebox.showerror("Error", "Ingrese un número válido para los participantes aburridos.")
            return
        
        self.hilo = Thread(target=self.procesar_enlace, args=(enlace,))
        self.hilo.start()

    def procesar_enlace(self, enlace):
        opciones = webdriver.ChromeOptions()
        opciones.add_argument("--disable-notifications")
        
        navegador = webdriver.Chrome(options=opciones)
        navegador.get(enlace)
        time.sleep(5)

        pyautogui.press('esc')

        try:
            boton_iniciar_reunion = WebDriverWait(navegador, 20).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "mbTuDeF1"))
            )
            boton_iniciar_reunion.click()
        except Exception as e:
            print(f"No se pudo hacer clic en el botón 'Iniciar reunión': {e}")

        pyautogui.press('esc')
        time.sleep(2)

        try:
            enlace_unirse = WebDriverWait(navegador, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Únase desde su navegador')]"))
            )
            enlace_unirse.click()
        except Exception as e:
            print(f"No se pudo hacer clic en el enlace 'Únase desde su navegador': {e}")

        time.sleep(3)

        try:
            iframe = WebDriverWait(navegador, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "iframe"))
            )
            navegador.switch_to.frame(iframe)
        except Exception as e:
            print(f"No se pudo cambiar al iframe: {e}")

        try:
            campo_nombre = WebDriverWait(navegador, 20).until(
                EC.presence_of_element_located((By.ID, "input-for-name"))
            )
            campo_nombre.send_keys("Empático")
        except Exception as e:
            print(f"No se pudo encontrar el campo de texto usando ID: {e}")
    
        try:
            boton_entrar = WebDriverWait(navegador, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Entrar')]"))
            )
            boton_entrar.click()
        except Exception as e:
            print(f"No se pudo hacer clic en el botón 'Entrar': {e}")

        pyautogui.press('esc')
        time.sleep(10)
        try:
            boton_audio = WebDriverWait(navegador, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Entrar al audio por computadora')]"))
            )
            boton_audio.click()
        except Exception as e:
            print(f"No se pudo hacer clic en el botón 'Entrar al audio por computadora': {e}")

        cliente_rekognition = boto3.client('rekognition')
        directorio_capturas = 'Capturas'
        os.makedirs(directorio_capturas, exist_ok=True)
        self.analizar_emociones(navegador, cliente_rekognition, directorio_capturas)

    def analizar_emociones(self, navegador, cliente_rekognition, directorio_capturas):
        def capturar_y_analizar_imagen():
            captura = navegador.get_screenshot_as_png()
            respuesta = cliente_rekognition.detect_faces(
                Image={'Bytes': captura},
                Attributes=['ALL']
            )

            detalles_caras = respuesta['FaceDetails']
            contador_emociones = Counter()

            for detalle_cara in detalles_caras:
                emociones = detalle_cara['Emotions']
                if emociones:
                    emocion_maxima = max(emociones, key=lambda x: x['Confidence'])
                    contador_emociones[emocion_maxima['Type']] += 1

            return contador_emociones

        try:
            while True:
                resumen_emociones = capturar_y_analizar_imagen()

                texto_resultado = "\n".join([f"{emocion}: {conteo}" for emocion, conteo in resumen_emociones.items()])
                self.etiqueta_resultado.config(text=f"Resumen de emociones:\n{texto_resultado}")

                # Elegimos estas dos emociones a veces igual calm no esta clara que tipo de emoción es.
                if resumen_emociones.get('NEUTRAL', 0) + resumen_emociones.get('DISGUST', 0) >= self.umbral_aburrimiento:
                    self.contador_aburrimiento += 1
                else:
                    self.contador_aburrimiento = max(0, self.contador_aburrimiento - 1)

                self.etiqueta_aburrimiento.config(text=f"Nivel de aburrimiento: {self.contador_aburrimiento}")

                if self.contador_aburrimiento > 3:
                    messagebox.showinfo("Alerta", "Parece que la audiencia se esta aburriendo.")
                    self.contador_aburrimiento = 0
                    self.etiqueta_aburrimiento.config(text=f"Nivel de aburrimiento: {self.contador_aburrimiento}")

                time.sleep(10)

        except KeyboardInterrupt:
            print("Captura de imágenes detenida.")
            navegador.quit()

if __name__ == "__main__":
    ventana = tk.Tk()
    app = Empatico(ventana)
    ventana.mainloop()
