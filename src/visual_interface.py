import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox


class Visuals:

    __main_window: tk.Tk 
    __welcome_message: str = "Bem-vindo a exportacao de infos dos laudos. Tenha sua credencial e PDFs separados"
    __selected_pdf_dir_string: str = "Nenhuma pasta de PDFs selecionada"
    __selected_credential_file_string:str = "Nenhum arquivo de credencial selecionado"
    __pdf_dir_label: tk.Label
    __credential_file_label: tk.Label

    def create_main_window(self, title: str):
        self.__main_window = tk.Tk()
        self.__main_window.title(title)
        self.__main_window.geometry("700x300")

    def get_main_window(self) -> tk.Tk | None:
        return self.__main_window

    def get_welcome_message(self) -> str:
        return self.__welcome_message

    def get_selected_pdf_dir_string(self) -> str:
        return self.__selected_pdf_dir_string

    def set_selected_pdf_dir_string(self, dir_name):
        self.__selected_pdf_dir_string = dir_name

    def get_selected_credential_file_string(self) -> str:
        return self.__selected_credential_file_string

    def set_selected_credential_file_string(self, file_name):
        self.__selected_credential_file_string = file_name

    def start_main_loop(self):
        self.__main_window.mainloop()

    def select_file(self, user_message) -> str:
        file_path = filedialog.askopenfilename(title=user_message)
        return file_path

    def show_dialog_message(self, dialog_message: str, message_type: str):
        match message_type:
            case "info": messagebox.showinfo(title="Aviso", message=dialog_message)
            case "warning": messagebox.showwarning(title="Atenção", message=dialog_message)
            case "error": messagebox.showerror(title="Erro", message=dialog_message)

    def print_on_main(self, text):
        main_window = self.get_main_window()
        label = tk.Label(main_window, text=text)
        label.pack(pady=20)

    def create_and_organize_layout(self):
        main_window = self.get_main_window()

        #welcome text, a centralized string on top
        welcome_text = self.get_welcome_message()
        title = tk.Label(main_window, text=welcome_text, font=("Arial", 14)) 
        title.grid(row=0, column=0, columnspan=2, pady=10)

    def create_first_row(self, btn_text: str, label_text:str, btn_action):
        #set first role, containing btn to select pdf directory and selected_directory name
        main_window = self.get_main_window()
        first_row_btn = tk.Button(main_window, text=btn_text, command=btn_action)
        first_row_btn.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.__pdf_dir_label = tk.Label(main_window, text=label_text)
        self.__pdf_dir_label.grid(row=1, column=1, padx=10, pady=5, sticky="w")

    def create_second_row(self, btn_text: str, label_text:str, btn_action):
        #set first role, containing btn to select pdf directory and selected_directory name
        main_window = self.get_main_window()
        second_row_btn = tk.Button(main_window, text=btn_text, command=btn_action)
        second_row_btn.grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.__credential_file_label= tk.Label(main_window, text=label_text)
        self.__credential_file_label.grid(row=2, column=1, padx=10, pady=5, sticky="w")

    def create_start_btn(self, btn_text, btn_action):
        #start button on the bottom, centralized under 2 rows of buttons
        main_window = self.get_main_window()
        start_btn = tk.Button(main_window, text=btn_text, command=btn_action)
        start_btn.grid(row=3, column=0, columnspan=2, pady=15)
        
    def update_pdf_dir_label(self, label_text:str):
        self.__pdf_dir_label.config(text=label_text)

    def update_credential_file_label(self, label_text:str):
        self.__credential_file_label.config(text=label_text)
