import tkinter as tk
import cv2
import numpy as np
import pyautogui
import time
from deepface import DeepFace
from datetime import datetime
import threading
from flask import Flask, jsonify, request
from flask_cors import CORS
from collections import Counter

app = Flask(__name__)
CORS(app)

class Interface:
    def __init__(self, master):
        self.master = master
        self.master.title("Interfaz con botones")

        self.start_button = tk.Button(self.master, text="Iniciar", command=self.start_action)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(self.master, text="Parar", command=self.stop_action)
        self.stop_button.pack(pady=5)

        self.running = False
        self.thread = None
        self.start_time = None
        self.end_time = None

        self.counter_label = tk.Label(self.master, text="Tiempo transcurrido: 0 segundos")
        self.counter_label.pack(pady=5)

        self.entry_label = tk.Label(self.master, text="Nombre del archivo:")
        self.entry_label.pack(pady=5)

        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(self.master, textvariable=self.entry_var)
        self.entry.pack(pady=5)

    def set_output_filename(self, filename):
        self.entry_var.set(filename)

    def start_action(self):
        if not self.running:
            self.running = True
            self.start_time = time.time()
            self.update_counter()  # Iniciar el contador
            print("Acción iniciada")
            self.thread = threading.Thread(target=self.run_code)
            self.thread.start()
        else:
            print("La acción ya está en curso")

    def stop_action(self):
        if self.running:
            self.running = False
            self.end_time = time.time()
            print("Acción detenida")
            if self.thread:
                self.thread.join()  # Esperar a que el hilo termine
            duration = self.end_time - self.start_time
            print(f"Duración del contador: {duration:.2f} segundos")
        else:
            print("La acción no está en curso")

    def update_counter(self):
        if self.running:
            current_time = time.time()
            duration = current_time - self.start_time
            self.counter_label.config(text=f"Tiempo transcurrido: {duration:.2f} segundos")
            self.master.after(1000, self.update_counter)

    def run_code(self):
        output_file = self.entry_var.get() + '.txt' if self.entry_var.get() else 'emotions_log.txt'
        cv2.namedWindow('Emotion Recognition', cv2.WINDOW_NORMAL)
        cv2.moveWindow('Emotion Recognition', -10000, -10000)
        cv2.resizeWindow('Emotion Recognition', 1, 1)

        while self.running:
            try:
                screenshot = pyautogui.screenshot()
                screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            except Exception as e:
                print(f"Error al capturar la pantalla: {e}")
                break  # Salir del bucle en caso de error

            frame_with_emotions, emotions_data = self.detect_emotions(screenshot)
            cv2.imshow('Emotion Recognition', frame_with_emotions)

            # Guardar emociones en el archivo cada 2 segundos
            if time.time() - self.start_time >= 2:
                with open(output_file, 'a', encoding='utf-8') as file:
                    for emotion, timestamp in emotions_data:
                        file.write(f"{emotion}\n")

            # Ajusta el retraso basado en el tiempo transcurrido
            delay = max(1, int((0.1 - (time.time() - self.start_time)) * 1000))
            time.sleep(delay / 1000)

            # Salir del bucle cuando self.running se establezca en False
            if not self.running:
                break

        # Cerrar la ventana de OpenCV
        cv2.destroyAllWindows()

    def detect_emotions(self, frame):
        # Utilizando OpenCV para detectar caras
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        emotions_data = []  # Lista para almacenar las emociones capturadas

        # Utilizando DeepFace para reconocimiento de emociones
        for (x, y, w, h) in faces:
            face = frame[y:y + h, x:x + w]
            emotions_list = DeepFace.analyze(face, actions=['emotion'], enforce_detection=False)

            # Verificar si se detectó alguna cara antes de intentar acceder a las emociones
            if emotions_list and 'emotion' in emotions_list[0]:
                emotion = max(emotions_list[0]['emotion'], key=emotions_list[0]['emotion'].get)

                # Dibujar un rectángulo alrededor de la cara y mostrar la emoción
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.putText(frame, emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

                emotions_data.append((emotion, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        return frame, emotions_data

def create_api(interface):

    @app.route('/api/start_detection', methods=['OPTIONS'])
    def handle_options():
        # Responder con los encabezados CORS necesarios
        response = jsonify({"message": "Preflight request accepted"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        return response

    # Para comenzar el análisis de reconocimiento
    @app.route("/start_detection", methods=["GET"])
    def start_detection():
        interface.start_action()
        return jsonify({"message": "Grabación Iniciada."})

    # Para detener el análisis de reconocimiento
    @app.route("/stop_detection", methods=["GET"])
    def stop_detection():
        interface.stop_action()
        return jsonify({"message": "Grabación Detenida."})

    # Para guardar el análisis de reconocimiento en consola
    @app.route("/view_emotions", methods=["GET"])
    def view_emotions():
        filename = interface.entry_var.get() + '.txt' if interface.entry_var.get() else 'emotions_log.txt'
        with open(filename, 'r', encoding='utf-8') as file:
            emotions_log = file.read()
        print(emotions_log)  # Imprime el registro de emociones en la consola del servidor Flask
        return emotions_log

    # Para cambiar el nombre del archivo de salida
    @app.route('/set_filename', methods=['POST'])
    def set_filename():
        data = request.json
        filename = data.get('filename')
        if filename:
            # Llamar al método para establecer el nombre del archivo en la interfaz tkinter
            interface.set_output_filename(filename)
            return jsonify({'message': 'Nombre agregado correctamente'})
        else:
            return jsonify({'error': 'Error'}), 400

    return app

def main():
    root = tk.Tk()
    app_interface = Interface(root)
    api = create_api(app_interface)
    api_thread = threading.Thread(target=api.run, kwargs={"host": "0.0.0.0", "port": 5001})
    api_thread.start()
    root.mainloop()

if __name__ == "__main__":
    main()

