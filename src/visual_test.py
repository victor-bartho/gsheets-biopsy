from visual_interface import Visuals

def first_button_action():
    file_path = my_visual.select_file("Selecione um arquivo")
    my_visual.update_pdf_dir_label(file_path)

def second_button_action():
    my_visual.update_credential_file_label("CR7")

def start_button_action():
    my_visual.capture_typed_spreadsheet_id_manual()
    my_visual.show_dialog_message(my_visual.get_spreadsheet_id() ,"error")

my_visual = Visuals(first_button_action, second_button_action, start_button_action)
my_visual.start_main_loop()
