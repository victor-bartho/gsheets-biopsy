import tkinter as tk
from tkinter import filedialog
from visual_interface import Visuals

def first_button_action():
    my_visual.update_pdf_dir_label("texto atualizado")

def second_button_action():
    my_visual.update_credential_file_label("CR7")

def start_button_action():
    my_visual.show_dialog_message("you pressed start button" ,"error")
my_visual = Visuals()
my_visual.create_main_window("Projeto Banco de Dados")

#create layout:
my_visual.create_and_organize_layout()

fst_row_label = my_visual.get_selected_pdf_dir_string()
my_visual.create_first_row("selecionar pasta PDF", fst_row_label, first_button_action)

snd_row_label = my_visual.get_selected_credential_file_string()
my_visual.create_second_row("selecionar arquivo credencial", snd_row_label, second_button_action)

my_visual.create_start_btn("iniciar", start_button_action)


my_visual.start_main_loop()

