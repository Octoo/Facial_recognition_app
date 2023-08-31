import time
import numpy as np
import cv2
import os
import tkinter as tk
from PIL import Image, ImageTk
import threading
import customtkinter as ctk
import subprocess
import knn_classifier


ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

cap = cv2.VideoCapture(0)
global button_path
global progressbar_1


def detect_face(img):
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    face_cascade2 = cv2.CascadeClassifier('haarcascade_profileface.xml')

    # Detect frontal faces
    faces = face_cascade.detectMultiScale(img, 1.2, 5)

    for (x, y, w, h) in faces:
        img = cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

    # Detect profile faces
    faces2 = face_cascade2.detectMultiScale(img, 1.2, 5)

    for (x, y, w, h) in faces2:
        img = cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

    return img, faces, faces2


def take_pic():
    global count

    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    face_cascade2 = cv2.CascadeClassifier('haarcascade_profileface.xml')

    def take_picture_thread():
        count = 0
        while count < 40:  # Stop after taking 40 pictures
            ret, frame = cap.read()

            # Make a copy of the frame to keep the original color feed
            color_frame = frame.copy()

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect and draw bounding boxes for both frontal and profile faces
            annotated_img, frontal_faces, profile_faces = detect_face(gray)

            if len(frontal_faces) == 0 and len(profile_faces) == 0:
                label1.configure(text="Can't identify your face. Please get closer and make sure there is a red rectangular around your face.")
                return False

            # Save frontal faces
            for (x, y, w, h) in frontal_faces:
                crop_img = gray[y:y+h, x:x+w]
                count += 1
                cv2.imwrite(newpath + "/User_" + str(id_input) + '_frontal.' + str(count) + ".jpg", crop_img)
                print(f"Frontal Face {count} saved.")

            # Save profile faces
            for (x, y, w, h) in profile_faces:
                crop_img = gray[y:y+h, x:x+w]
                count += 1
                #save the original image
                cv2.imwrite(newpath + "/User_" + str(id_input) + '_profile.' + str(count) + ".jpg", crop_img)
                print(f"Profile Face {count} saved.")

                # We Flip the image horizontally because the haarcascade
                #only recognize one side of the profile
                flipped_img = cv2.flip(crop_img, 1)

                # Save the flipped profile image
                cv2.imwrite(newpath + "/User_" + str(id_input) + '_profile_flipped.' + str(count) + ".jpg", flipped_img)
                print(f"Flipped Profile Face {count} saved.")
                
            # Show the color frame from the webcam feed
            rgb = cv2.cvtColor(color_frame, cv2.COLOR_BGR2RGB)
            prevImg = Image.fromarray(rgb)
            # GUI library (Tkinter) requires images to be in the PhotoImage format to display them on the GUI
            imgtk = ImageTk.PhotoImage(image=prevImg)
            lmain.imgtk = imgtk
            lmain.configure(image=imgtk)

            # Update the GUI
            mainWindow.update()

        # After taking pictures, release the camera and stop capturing
        cap.release()
        cv2.destroyAllWindows()
        
    # Create a new thread for picture-taking to avoid GUI freezing
    pic_thread = threading.Thread(target=take_picture_thread)
    pic_thread.start()



def show_frame():
    ret, frame = cap.read()

    if not ret or frame is None:  # Check if the frame is empty
        lmain.after(10, show_frame)
        return

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    detect_face(rgb)

    prevImg = Image.fromarray(rgb)
    imgtk = ImageTk.PhotoImage(image=prevImg)  # Use ImageTk.PhotoImage from PIL
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)

    lmain.after(10, show_frame)


def create_path():
    global newpath, id_input, label1, button

    if not os.path.exists('train_dir/'):
        os.makedirs('train_dir/')

    button_path.grid_forget()
    label1 = ctk.CTkLabel(master=mainWindow, text="Positionnez vous en face puis tournez vers votre droite doucement")
    button = ctk.CTkButton(mainWindow, text="Prendre les photos", command=take_pic)
    label1.grid(row=1, column=0, columnspan=2)
    button.grid(row=2, column=0, columnspan=2)
    id_input = id_path.get()  # input
    newpath = r'train_dir/' + id_input  # face_data/input
    if not os.path.exists(newpath):
        os.makedirs(newpath)



def reset_program():
    global mainWindow, cap

    # Release the camera if it was initialized before
    if 'cap' in globals():
        cap.release()

    # Destroy the main window
    mainWindow.destroy()

    # Restart the application
    main()

def initialize_camera():
    global cap
    cap = cv2.VideoCapture(0)

def call_classification():
    
    #Permet de faire du threading pour executer la classification
    # dans un process différent et ne pas bloquer la fenetre actuelle
    #tkinter
    global progressbar_1
    progressbar_1.start()
    t = threading.Thread(target=call_knn_script)
    t.start()

def call_knn_script():
    t = threading.Thread(target=run_knn_script)
    t.start()

def run_knn_script():
    try:
        process = subprocess.Popen(['python', 'knn_classifier.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        while True:
            output_line = process.stdout.readline()
            if not output_line:
                break

            print("Output:", output_line.strip())
            if "Training complete!" in output_line:
                progressbar_1.stop()
                trigger_label_update()

        return_code = process.wait()

        if return_code != 0:
            print("Error: knn_classifier.py returned non-zero exit code:", return_code)
    except Exception as e:
        print("Error:", e)


def monitor_command_output(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

    while True:
        output_line = process.stdout.readline()
        if not output_line:
            break

        # Process the output line
        print("Output:", output_line.strip())
        
        # Check if the desired string appears in the output
        if "Training complete!" in output_line:
            trigger_label_update()

    return_code = process.wait()
    return return_code

def trigger_label_update():
    label.configure(text="Entrainement terminé!")



progressbar_1 = None
def main():
    global mainWindow, id_path, lmain, button_path, reset_button,label, progressbar_1

    mainWindow = ctk.CTk()
    mainWindow.geometry(f"{1100}x{580}")
    mainWindow.resizable(False,False)
    mainWindow.bind('<Escape>', lambda e: mainWindow.quit())

    mainWindow.grid_rowconfigure(0, weight=1)
    mainWindow.grid_rowconfigure(1, weight=0)
    mainWindow.grid_rowconfigure(2, weight=0)
    mainWindow.grid_columnconfigure(0, weight=1)
    mainWindow.grid_columnconfigure(1,weight=0)
    mainWindow.grid_columnconfigure(2,weight=0)

    id_path = ctk.StringVar()


    lmain = tk.Label(master=mainWindow, justify=ctk.CENTER)
    lmain.grid(row=0, column=0, padx=10, pady=10, columnspan=2)  # Use ctk.CTkLabel instead of ctk.Label


    entry = ctk.CTkEntry(mainWindow, textvariable=id_path)
    entry.grid(row=1, column=0, columnspan=2)
    
    button_path = ctk.CTkButton(mainWindow, text="Ajouter la personne", command=create_path,corner_radius=8)
    button_path.grid(row=2, column=0, columnspan=2, pady=10)

    reset_button = ctk.CTkButton(mainWindow, text="Valider", command=reset_program, corner_radius=8)
    reset_button.grid(row=3, column=0, columnspan=2, pady=10)

    button = ctk.CTkButton(mainWindow, text="Ajouter la la base de données", command=call_classification, corner_radius=8)
    button.grid(row=1, column=1, columnspan=2, pady=10, padx=10)


    label = ctk.CTkLabel(mainWindow, text="Patientez", font=ctk.CTkFont(size=15, weight="bold"))
    label.grid(row=3, column=1, columnspan=1, pady=10, padx=10)

    slider_progressbar_frame = ctk.CTkFrame(mainWindow, fg_color="transparent")
    slider_progressbar_frame.grid(row=2, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")


    progressbar_1 = ctk.CTkProgressBar(slider_progressbar_frame)
    progressbar_1.grid(row=1, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")


    
    show_frame()
    initialize_camera()  # Reinitialize the camera after the reset
    mainWindow.mainloop()


# Start the application
main()
