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
    __use_default_sheet: tk.BooleanVar 
    __spreadsheet_id: str = '1wDG00ttRcT57VVPVppvAxwNvImeSJ_XVi-f5dJDmnsE'
    __custom_spreadsheet_entry: tk.Entry

    def __init__(self, pdf_btn_action, credential_btn_action, start_btn_action):
        self.create_main_window("Projeto Banco de Dados - v1.0")
        self.create_base_layout()
        first_row_label = self.__selected_pdf_dir_string
        self.create_first_row("Selecionar pasta de PDFs", first_row_label, pdf_btn_action)
        second_row_label = self.__selected_credential_file_string
        self.create_second_row("Selecionar arquivo de credencial", second_row_label, credential_btn_action)
        self.create_start_btn("Iniciar", start_btn_action)
        self.__use_default_sheet = tk.BooleanVar(value=True)
        self.create_third_row_with_checkbox_and_entry()

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

    def get_spreadsheet_id(self) -> str:
        return self.__spreadsheet_id

    def set_spreadsheet_id(self, id:str):
        self.__spreadsheet_id = id

    def get_custom_spreadsheet_entry(self) -> tk.Entry:
        return self.__custom_spreadsheet_entry

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

    def create_base_layout(self):
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
        self.__start_button = tk.Button(main_window, text=btn_text, command=btn_action)
        self.__start_button.grid(row=5, column=0, columnspan=2, pady=15)
        
    def update_pdf_dir_label(self, label_text:str):
        self.__pdf_dir_label.config(text=label_text)

    def update_credential_file_label(self, label_text:str):
        self.__credential_file_label.config(text=label_text)

    def create_third_row_with_checkbox_and_entry(self):
        main_window = self.get_main_window()

        #checkbox that is linked to self.__use_default_spreadsheet, used to capture interaction with the widget
        checkbox = tk.Checkbutton(
        main_window,
        text="Usar planilha padrão",
        variable = self.__use_default_sheet,
        command=self.toggle_custom_sheet_entry_visibility)
        checkbox.grid(row=3, column=1, sticky="w")

        #text entry, that is invisible if checkbox is checked. If don`t want to use standard spreadsheet, Entry becomes visible
        self.__custom_spreadsheet_entry = tk.Entry(main_window, width=45)
        self.__custom_spreadsheet_entry.grid(row=4, column=1, columnspan=3, padx=10, pady=5)
        self.__custom_spreadsheet_entry.insert(0, self.get_spreadsheet_id())
        self.__custom_spreadsheet_entry.bind("<FocusOut>", self.capture_typed_spreadsheet_id)
        self.__custom_spreadsheet_entry.grid_remove()


    def capture_typed_spreadsheet_id(self, event):
        typed_text = self.get_custom_spreadsheet_entry().get()
        self.set_spreadsheet_id(typed_text.strip())

    def capture_typed_spreadsheet_id_manual(self):
        typed_text = self.get_custom_spreadsheet_entry().get()
        self.set_spreadsheet_id(typed_text.strip())

    def toggle_custom_sheet_entry_visibility(self):
        custom_sheet_entry = self.get_custom_spreadsheet_entry()
        if self.__use_default_sheet.get():
            custom_sheet_entry.grid_remove()
            self.set_spreadsheet_id('1wDG00ttRcT57VVPVppvAxwNvImeSJ_XVi-f5dJDmnsE')
        else:
            custom_sheet_entry.delete(0, tk.END)
            custom_sheet_entry.insert(0, self.get_spreadsheet_id())
            custom_sheet_entry.grid()
