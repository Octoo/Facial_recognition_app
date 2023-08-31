import cv2
import os
import numpy as np
from PIL import Image, ImageDraw, ImageTk
import face_recognition
from bounding_box_direction import get_bounding_box_direction
from log import logging_function
from knn_classifier import train
import pickle
import customtkinter as ctk
import tkinter as tk
from tkinter.filedialog import askopenfile
from tkinter import filedialog as fd
import time
from datetime import datetime

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'JPG'}

previous_directions = {}  # Dictionary to store the previous direction for each person
my_text = None



def predict(X_frame, knn_clf=None, model_path=None, distance_threshold=0.5):

    if knn_clf is None and model_path is None:
        raise Exception("Must supply knn classifier either through knn_clf or model_path")

    # Load a trained KNN model (if one was passed in)
    if knn_clf is None:
        with open(model_path, 'rb') as f:
            knn_clf = pickle.load(f)

    X_face_locations = face_recognition.face_locations(X_frame)

    # If no faces are found in the image, return an empty result.
    if len(X_face_locations) == 0:
        return []

    # Find encodings for faces in the test image
    faces_encodings = face_recognition.face_encodings(X_frame, known_face_locations=X_face_locations)

    # Use the KNN model to find the best matches for the test face
    closest_distances = knn_clf.kneighbors(faces_encodings, n_neighbors=1)
    are_matches = [closest_distances[0][i][0] <= distance_threshold for i in range(len(X_face_locations))]

    # Predict classes and remove classifications that aren't within the threshold
    return [(pred, loc) if rec else ("unknown", loc) for pred, loc, rec in zip(knn_clf.predict(faces_encodings), X_face_locations, are_matches)]

def show_prediction_labels_on_image(frame, predictions):
    pil_image= Image.fromarray(frame)
    draw =ImageDraw.Draw(pil_image)

    for name, (top, right, bottom, left) in predictions:
        # enlarge the predictions for the full-sized image.
        top *= 2
        right *= 2
        bottom *= 2
        left *= 2

        # Draw a box around the face using the Pillow module
        draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 255))

        # There's a bug in Pillow where it blows up with non-UTF-8 text
        # when using the default bitmap font
        #raise issues in the log because each name detected is preceded by a "b"
        name = name.encode("UTF-8")
        name_decoded= name.decode()

        # Draw a label with a name below the face
        text_width, text_height = draw.textsize(name)
        draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(0, 0, 255), outline=(0, 0, 255))
        draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 255))
        
        #Print the time and hour at which the screenshot is taken
        
        timestr = time.strftime("%d %m %Y-%H %M %S")


        # Calculate the direction of the bounding box
        box_center = ((left + right) // 2, (top + bottom) // 2)
        direction = get_bounding_box_direction(frame.shape, box_center, name)
        if direction != previous_directions.get(name):
            print(f"Direction for {name}: {direction}")
            previous_directions[name] = direction
            logging_function(top, right, bottom, left, name_decoded, direction)  # Call the logging function with relevant information

            # Take a screenshot and save it in a folder
            folder_name = "screenshots"
            
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)
            filename = os.path.join(folder_name, f"{name_decoded}_{direction}_{timestr}.jpg")
            cv2.imwrite(filename, frame)

        draw.text((left + 6, bottom + 5), f"Direction: {direction}", fill=(255, 255, 255, 255))

    del draw
    opencvimage = np.array(pil_image)
    return opencvimage

def show_frame():
    global process_this_frame, cap, previous_predictions
    
    ret, frame = cap.read()
    if ret:
        img = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        
        #si la frame est une prediction frame (toutes les 15 sec) alors
        #previous_prediction est update avec la nouvelle prediction
        if process_this_frame % 10 == 0:
            predictions = predict(img, model_path="trained_knn_model.clf")
            #
            previous_predictions = predictions  # Store predictions for use in non-prediction frames
        #Sinon, previous_prediction est utilisée pour dessiner les bounding box et le label
        #de cette façon le label et bb sont toujours visibles sur la cam
        else:
            predictions = previous_predictions

        frame_with_labels = show_prediction_labels_on_image(frame, predictions)
        rgb_frame = cv2.cvtColor(frame_with_labels, cv2.COLOR_BGR2RGB)
        imgtk = ImageTk.PhotoImage(image=Image.fromarray(rgb_frame))
        lmain.imgtk = imgtk
        lmain.configure(image=imgtk)

        process_this_frame += 1

    lmain.after(10, show_frame)  # Schedule the next frame update

def open_log():
    global my_text  # Use the global variable

    if my_text is not None:
        with open("std.txt", 'r') as text_file:
            # Get the current content of the text box
            current_content = my_text.get("1.0", tk.END)

            # Read new logs from the file
            new_logs = text_file.read().replace(current_content, "")
            
            # If there are new logs, append them to the text box
            if new_logs:
                my_text.insert(tk.END, new_logs)
                my_text.see(tk.END)  # Scroll to the end of the text box

        # Schedule the function to run again after 1 second
        my_text.after(1000, open_log)


def open_folder_logs():

    os.startfile(r"C:\Users\lbtvi\Documents\Stage\IA\Face_recognition_final\std.txt")
    #filename = fd.askopenfilename()

def open_folder():
    
    #folder = fd.askdirectory(title = "Select Folder to open")  
    # using the startfile() of the os module to open the selected folder  
    os.startfile(r"C:\Users\lbtvi\Documents\Stage\IA\Face_recognition_final\screenshots")
    

def show_picture_gallery():
    global mainWindow, canvas, frame  # Use the global variables

    # Create the canvas and frame for the picture gallery
    canvas = ctk.CTkCanvas(mainWindow, width=140)
    canvas.grid(row=1, column=1, sticky='news')

    # Create a scrollbar and associate it with the canvas
    scrollbar = tk.Scrollbar(mainWindow, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.grid(row=1, column=2, sticky="ns")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Create a frame to hold the images on the canvas
    frame = ctk.CTkFrame(canvas)
    canvas.create_window((0, 0), window=frame, anchor=tk.NW)

    # Function to update canvas scrolling region
    def configure_canvas(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.configure(bg="black")

    # Bind the function to allow scrolling outside the region on the canvas
    frame.bind("<Configure>", configure_canvas)

    for (root_, dirs, files) in os.walk("screenshots"):
        if files:
            for file_ in files:
                path = os.path.join("screenshots", file_)
                image_ = Image.open(path)
                n_image = image_.resize((250, 250))
                photo = ImageTk.PhotoImage(n_image)
                picture_name=os.path.splitext(file_)[0]
                img_label = tk.Label(frame, image=photo, text =picture_name, compound='bottom')
                img_label.photo = photo
                img_label.pack()

                #extract name of the picture displayed
                #picture_name=os.path.split(file_)[0]
                # Create a label to display the picture name under the image
                name_label = tk.Label(frame, text=picture_name)
                #name_label.pack()


def main():
    global mainWindow, lmain, cap, process_this_frame, my_text  # Use the global variable


    mainWindow = ctk.CTk()
    mainWindow.columnconfigure(0, weight=1)  
    mainWindow.columnconfigure(1, weight=1) # Set weight to row and 
    mainWindow.rowconfigure(0, weight=1)
    mainWindow.rowconfigure(1, weight=1)
    mainWindow.rowconfigure(2, weight=1)

    show_gallery_button = ctk.CTkButton(master=mainWindow, text="Rafraichir flux images", command=show_picture_gallery,corner_radius=8)
    show_gallery_button.grid(row=3, column=1,pady=10, padx=10, sticky="s")

    button_folder=ctk.CTkButton(master=mainWindow, text="Ouvrir Dossier images", command=open_folder, corner_radius=8)
    button_folder.grid(row=4, column=1,pady=10, padx=10, sticky="s")

    #Scroll images right side
    #Right side of the mainwindow
    canvas =ctk.CTkCanvas(mainWindow, width=140)
    canvas.grid(row=1, column=1, sticky='news')

    # Create a scrollbar and associate it with the canvas
    scrollbar = tk.Scrollbar(mainWindow, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.grid(row=1, column=2, sticky="ns")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Create a frame to hold the images on the canvas
    frame = ctk.CTkFrame(canvas)
    canvas.create_window((0, 0), window=frame, anchor=tk.NW)

    # Function to update canvas scrolling region
    def configure_canvas(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.configure(bg="black")

    #on bind la fonction qui permet de scroll en dehors de la region sur le canvas
    frame.bind("<Configure>", configure_canvas)

    for (root_, dirs, files) in os.walk("screenshots"):
        if files:
            for file_ in files:
                path = os.path.join("screenshots", file_)
                image_ = Image.open(path)
                n_image = image_.resize((100, 100))
                photo = ImageTk.PhotoImage(n_image)
                img_label = tk.Label(frame, image=photo)
                img_label.photo = photo
                img_label.pack()
        

    #left side of the mainwindow            
    canvas2=ctk.CTkCanvas(mainWindow)
    canvas2.grid(row=1, column=0, sticky="news")
    
    
    logo_label = ctk.CTkLabel(master=mainWindow, text="Shield Surveillance", font=ctk.CTkFont(size=20, weight="bold"))
    logo_label.grid(row=0, column=0, padx=20, pady=(20, 10), columnspan=2)

    lmain = tk.Label(master=canvas2, justify=tk.CENTER)
    lmain.grid(row=1, column=0, padx=10, pady=10, columnspan=2)

    my_text = ctk.CTkTextbox(mainWindow, width=240, height=240, border_width=0,corner_radius=8)
    my_text.grid(row=2, column=0,columnspan=2, pady=10, padx=10)

    button_text = ctk.CTkButton(master=mainWindow, text="Afficher les logs", command=open_log, corner_radius=8)
    button_text.grid(row=3, column=0, columnspan=2, pady=10, padx=10)

    button_text_2 = ctk.CTkButton(master=mainWindow, text="Ouvrir le fichier texte logs", command=open_folder_logs, corner_radius=8)
    button_text_2.grid(row=4, column=0,columnspan=2,pady=10, padx=10)
    
    #Permet de rafraichir le flux de screenshots au demarrage de la fenetre
    show_picture_gallery()


    cap = cv2.VideoCapture(0)
    process_this_frame = 0

    show_frame()  # Start the frame update loop
    mainWindow.mainloop()


if __name__ == "__main__":
    main()
