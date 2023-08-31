import customtkinter
from PIL import Image, ImageTk
import os
import subprocess


customtkinter.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

app = customtkinter.CTk()
app.geometry("400x500")
app.title("Reconnaissance faciale.py")



def button_callback():
    print("Button click", combobox_1.get())


def slider_callback(value):
    progressbar_1.set(value)

def add_person():
    try:
        process = subprocess.Popen(['python', 'photobooth_test3_customtkinter3.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    except Exception as e:
        print("Error:", e)

def surveillance():
    try:
        process = subprocess.Popen(['python', 'face_recog2_high_refresh_with_gallery_update.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    except Exception as e:
        print("Error:", e)



frame_1 = customtkinter.CTkFrame(master=app)
frame_1.pack(pady=20, padx=60, fill="both", expand=True)

label_1 = customtkinter.CTkLabel(master=frame_1, justify=customtkinter.LEFT, text="Bienvenue", font=customtkinter.CTkFont(size=20, weight="bold"))
label_1.pack(pady=10, padx=10)
label_2 = customtkinter.CTkLabel(master=frame_1, justify=customtkinter.LEFT, text="sur", font=customtkinter.CTkFont(size=20, weight="bold"))
label_2.pack(pady=10, padx=10)
label_3 = customtkinter.CTkLabel(master=frame_1, justify=customtkinter.LEFT, text="SHIELD RECONNAISSANCE", font=customtkinter.CTkFont(size=20, weight="bold"))
label_3.pack(pady=10, padx=10)

IMAGE_WIDTH = 130
IMAGE_HEIGHT = 130
IMAGE_PATH = 'shield.png'


your_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(IMAGE_PATH)), size=(IMAGE_WIDTH , IMAGE_HEIGHT))
label = customtkinter.CTkLabel(master=app, image=your_image, text='')
label.pack(pady=10, padx=10)



button_1 = customtkinter.CTkButton(master=frame_1,text="Ajouter une personne", command=add_person, width=240,height=64,border_width=0,corner_radius=8)
button_1.pack(pady=10, padx=10)

button_2 = customtkinter.CTkButton(master=frame_1, text="Surveillance", command=surveillance, width=240,height=64,border_width=0,corner_radius=8)
button_2.pack(pady=10, padx=10)

textbox = customtkinter.CTkTextbox(frame_1, width=250)
textbox.pack(pady=10, padx=10)
textbox.insert("0.0", "Bienvenue!\n\n" + "Bienvenue sur Shield reconnaissance, vous pouvez ajouter une personne à la base de données en cliquant sur le premier bouton et suivant les instructions. Cette étape n'est necessaire qu'une fois par personne. Vous pouvez avoir acces au flux camera de surveillance en cliquant sur le second bouton. Vous pourrez acceder aux logs des personnées detectées et au sens de déplacement. Vous pourre aussi acceder aux captures d'écran prises a chaque detection.")




app.mainloop()
