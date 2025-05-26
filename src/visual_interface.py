import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox


class Visuals:

    __main_window: tk.Tk 
    __welcome_message: str = "Bem-vindo à exportação de informações de laudos. Tenha seu arquivo de credencial e PDFs separados."
    __initial_selected_pdf_dir_string: str = "Nenhuma pasta de PDFs selecionada"
    __selected_pdf_dir_string: str
    __initial_selected_credential_file_string: str = "Nenhum arquivo de credencial selecionado"
    __selected_credential_file_string:str
    __pdf_dir_label: tk.Label
    __credential_file_label: tk.Label
    __use_default_sheet: tk.BooleanVar 
    __default_spreadsheet_id: str = '1wDG00ttRcT57VVPVppvAxwNvImeSJ_XVi-f5dJDmnsE'
    __spreadsheet_id: str 
    __custom_spreadsheet_entry: tk.Entry
    __text_box: tk.Text
    __btn_select_pdf_dir: tk.Button
    __btn_select_credential_file: tk.Button
    __checkbox_use_default_spreadsheet: tk.Checkbutton
    __btn_start: tk.Button
    __sheet_name_entry: tk.Entry
    __sheet_name:str

    def __init__(self, pdf_btn_action, credential_btn_action, start_btn_action):
        self.__spreadsheet_id = self.__default_spreadsheet_id
        self.__selected_pdf_dir_string = self.__initial_selected_pdf_dir_string
        self.__selected_credential_file_string = self.__initial_selected_credential_file_string
        self.create_main_window("Projeto Banco de Dados - v1.1")
        self.create_base_layout()
        first_row_label = self.__selected_pdf_dir_string
        self.create_first_row("Selecionar pasta de PDFs", first_row_label, pdf_btn_action)
        second_row_label = self.__selected_credential_file_string
        self.create_second_row("Selecionar arquivo de credencial", second_row_label, credential_btn_action)
        self.create_sheet_name_row()
        self.create_start_btn("Iniciar", start_btn_action)
        self.__use_default_sheet = tk.BooleanVar(value=True)
        self.create_third_row_with_checkbox_and_entry()
        self.create_text_box()

    def create_main_window(self, title: str):
        self.__main_window = tk.Tk()
        self.__main_window.title(title)
        self.__main_window.geometry("850x300")
        #for i in range(3):
        #    self.__main_window.columnconfigure(i, weight=1)
        self.__main_window.columnconfigure(0, weight=1)
        self.__main_window.columnconfigure(1, weight=1)
        self.__main_window.columnconfigure(2, weight=1)
        self.__main_window.columnconfigure(3, weight=1)
        self.__main_window.rowconfigure(0, weight=1)
        self.__main_window.rowconfigure(1, weight=1)
        self.__main_window.rowconfigure(2, weight=1)
        self.__main_window.rowconfigure(3, weight=1)
        self.__main_window.rowconfigure(4, weight=1)
        self.__main_window.rowconfigure(5, weight=1)
        self.__main_window.rowconfigure(6, weight=1)

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

    def get_default_spreadsheet_id(self) -> str:
        return self.__default_spreadsheet_id

    def get_text_box(self) -> tk.Text:
        return self.__text_box

    def get_btn_select_pdf_dir(self) -> tk.Button:
        return self.__btn_select_pdf_dir

    def get_btn_select_credential_file(self) -> tk.Button:
        return self.__btn_select_credential_file

    def get_checkbox_use_default_spreadsheet(self) -> tk.Checkbutton:
        return self.__checkbox_use_default_spreadsheet

    def get_initial_selected_pdf_dir_string(self) -> str:
        return self.__initial_selected_pdf_dir_string

    def get_initial_selected_credential_file_string(self) -> str:
        return self.__initial_selected_credential_file_string

    def get_btn_start(self) -> tk.Button:
        return self.__btn_start

    def get_sheet_name_entry(self) -> tk.Entry:
        return self.__sheet_name_entry

    def get_sheet_name(self) -> str:
        return self.__sheet_name

    def set_sheet_name(self, sheet_name:str):
        self.__sheet_name = sheet_name

    def start_main_loop(self):
        self.__main_window.mainloop()

    def select_file(self, user_message) -> str:
        file_path = filedialog.askopenfilename(title=user_message)
        return file_path

    def select_dir(self, user_message) -> str:
        dir_path = filedialog.askdirectory(title=user_message)
        return dir_path

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
        title = tk.Label(main_window, text=welcome_text, font=("Arial", 13)) 
        title.grid(row=0, column=1, columnspan=2, pady=10)

    def create_first_row(self, btn_text: str, label_text:str, btn_action):
        #set first role, containing btn to select pdf directory and selected_directory name
        main_window = self.get_main_window()
        self.__btn_select_pdf_dir = tk.Button(main_window, text=btn_text, command=btn_action)
        self.__btn_select_pdf_dir.grid(row=1, column=1, padx=10, pady=5, sticky="e")
        self.__pdf_dir_label = tk.Label(main_window, text=label_text, wraplength=500, anchor="w", justify="left")
        self.__pdf_dir_label.grid(row=1, column=2, padx=10, pady=5, sticky="w")

    def create_second_row(self, btn_text: str, label_text:str, btn_action):
        #set first role, containing btn to select pdf directory and selected_directory name
        main_window = self.get_main_window()
        self.__btn_select_credential_file = tk.Button(main_window, text=btn_text, command=btn_action)
        self.__btn_select_credential_file.grid(row=2, column=1, padx=10, pady=5, sticky="e")
        self.__credential_file_label= tk.Label(main_window, text=label_text, wraplength=500, anchor="w", justify="left")
        self.__credential_file_label.grid(row=2, column=2, padx=10, pady=5, sticky="w")

    def create_start_btn(self, btn_text, btn_action):
        #start button on the bottom, centralized under 2 rows of buttons
        main_window = self.get_main_window()
        self.__btn_start = tk.Button(main_window, text=btn_text, command=btn_action)
        self.__btn_start.grid(row=5, column=1, columnspan=2, pady=15)
        
    def update_pdf_dir_label(self, label_text:str):
        self.set_selected_pdf_dir_string(label_text)
        self.__pdf_dir_label.config(text=label_text)

    def update_credential_file_label(self, label_text:str):
        self.set_selected_credential_file_string(label_text)
        self.__credential_file_label.config(text=label_text)

    def create_third_row_with_checkbox_and_entry(self):
        main_window = self.get_main_window()

        #checkbox that is linked to self.__use_default_spreadsheet, used to capture interaction with the widget
        self.__checkbox_use_default_spreadsheet = tk.Checkbutton(
        main_window,
        text="Usar planilha padrão",
        variable = self.__use_default_sheet,
        command=self.toggle_custom_sheet_entry_visibility)
        self.__checkbox_use_default_spreadsheet.grid(row=3, column=1, sticky="e")

        #text entry, that is invisible if checkbox is checked. If don`t want to use standard spreadsheet, Entry becomes visible
        self.__custom_spreadsheet_entry = tk.Entry(main_window, width=45)
        self.__custom_spreadsheet_entry.grid(row=3, column=2, columnspan=3, padx=10, pady=5, sticky="w")
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
            self.set_spreadsheet_id(self.get_default_spreadsheet_id())
            custom_sheet_entry.delete(0, tk.END)
            custom_sheet_entry.insert(0, self.get_default_spreadsheet_id())
            custom_sheet_entry.grid_remove()
        else:
            custom_sheet_entry.delete(0, tk.END)
            custom_sheet_entry.insert(0, self.get_spreadsheet_id())
            custom_sheet_entry.grid()

    def create_text_box(self):
        main_window = self.get_main_window()

        scrollbar = tk.Scrollbar(main_window)
        self.__text_box = tk.Text(main_window, wrap="word", height=20,  width=50,yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.__text_box.yview)
        self.__text_box.grid(row=6, column=1, columnspan=2, padx=10, pady=10, sticky="we")
        self.__text_box.config(state="disabled")
        self.__text_box.grid_remove()

    def append_string_text_box(self, text:str):
        text_box = self.get_text_box()
        text_box.config(state="normal")
        text_box.insert(tk.END, text + "\n")
        text_box.config(state="disabled")

    def toggle_text_box_visibility(self):
        main_window = self.get_main_window()
        text_box = self.get_text_box()

        if text_box.winfo_ismapped(): #if it is visible at the grid
            text_box.grid_remove()
            main_window.geometry("850x300")
        else:
            main_window.geometry("850x600")
            text_box.grid(row=6, column=1, columnspan=2, padx=10, pady=10, sticky="we")
        
        main_window.update()

    def reset_pdf_dir_selection(self):
        initial_pdf_selection_string = self.get_initial_selected_pdf_dir_string()
        self.set_selected_pdf_dir_string(initial_pdf_selection_string)
        self.update_pdf_dir_label(initial_pdf_selection_string)

    def reset_credential_file_selection(self):
        initial_credential_file_string = self.get_initial_selected_credential_file_string()
        self.set_selected_credential_file_string(initial_credential_file_string)
        self.update_credential_file_label(initial_credential_file_string)

    def create_sheet_name_row(self):
        main_window = self.get_main_window()
        sheet_name_label = tk.Label(main_window, text="Digite o nome da aba da planiha:")
        sheet_name_label.grid(row=4, column=1, sticky="e", padx=10, pady=5)

        self.__sheet_name_entry = tk.Entry(main_window, width=30)
        self.__sheet_name_entry.grid(row=4, column=2, sticky="w", padx=10, pady=5)
        self.__sheet_name_entry.bind("<FocusOut>", self.capture_typed_sheet_name)

    def capture_typed_sheet_name(self, event):
        typed_text = self.get_sheet_name_entry().get()
        self.set_sheet_name(typed_text.strip())

    def capture_typed_sheet_name_manual(self):
        typed_text = self.get_sheet_name_entry().get()
        self.set_sheet_name(typed_text.strip())

    def make_all_widgets_unclickable(self):
        #textbox does not participate, since it is supposed to always be unclickable
        btn_select_pdf_dir = self.get_btn_select_pdf_dir()
        btn_select_credential_file = self.get_btn_select_credential_file()
        checkbox_use_default_spreadsheet = self.get_checkbox_use_default_spreadsheet()
        btn_start = self.get_btn_start()
        entry_sheet_name = self.get_sheet_name_entry()
        spreadsheet_id_entry = self.get_custom_spreadsheet_entry()

        btn_select_pdf_dir.configure(state="disabled")
        btn_select_credential_file.configure(state="disabled")
        checkbox_use_default_spreadsheet.configure(state="disabled")
        btn_start.configure(state="disabled")
        entry_sheet_name.configure(state="disabled")
        spreadsheet_id_entry.configure(state="disabled")

    def make_all_widgets_clickable(self):
        #textbox does not participate, since it is supposed to always be unclickable
        btn_select_pdf_dir = self.get_btn_select_pdf_dir()
        btn_select_credential_file = self.get_btn_select_credential_file()
        checkbox_use_default_spreadsheet = self.get_checkbox_use_default_spreadsheet()
        btn_start = self.get_btn_start()
        entry_sheet_name = self.get_sheet_name_entry()
        spreadsheet_id_entry = self.get_custom_spreadsheet_entry()

        btn_select_pdf_dir.configure(state="normal")
        btn_select_credential_file.configure(state="normal")
        checkbox_use_default_spreadsheet.configure(state="normal")
        btn_start.configure(state="normal")
        entry_sheet_name.configure(state="normal")
        spreadsheet_id_entry.configure(state="normal")

