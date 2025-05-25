import os
import traceback
from pdf_reader_module import PDFReaderModule
from info_extractor import BiopsyInfoExtractor
from sheets_manipulation import SheetsManipulator
from service_manager import ServiceManager
from datetime import date
import logging
import cowsay
from visual_interface import Visuals


#Logging methods
def print_and_log(level_name, message, logger=logging):
        gui.append_string_text_box(message)
        match level_name:
            case 'INFO':
                logger.info(message)
            case 'ERROR':
                logger.error(message)

def add_file_to_review_list(review_list_path, review_file_name, message=''):
        with open(review_list_path, 'a') as file:
            if message != '':
                file.write(f'Arquivo: {review_file_name} - {message} \n')
            else:
                file.write(f'Arquivo: {review_file_name}\n')


#defining button click actions and creating visual interface
def pdf_btn_action():
    dir_path = gui.select_dir("Selecione uma pasta")
    if dir_path != "":
        dir_path = os.path.normpath(dir_path)
        if not (os.path.exists(dir_path) and os.path.isdir(dir_path)): 
            gui.show_dialog_message("Selecione uma pasta válida!", "error")
            gui.reset_pdf_dir_selection()
        else:
            gui.update_pdf_dir_label(dir_path)
    else:
        gui.reset_pdf_dir_selection()

def credential_btn_action():
    credential_path = gui.select_file("Selecione o arquivo .JSON de credencial")
    if credential_path != "":
        credential_path = os.path.normpath(credential_path)
        if not (os.path.exists(credential_path) and credential_path.split('.')[-1].lower() == 'json'):
            gui.show_dialog_message("Selecione um arquivo de credencial válido!", "error")
            gui.reset_credential_file_selection()
        else:
            gui.update_credential_file_label(credential_path)
    else:
        gui.reset_credential_file_selection()

def check_filled_fields() -> bool:
    if gui.get_selected_pdf_dir_string() == gui.get_initial_selected_pdf_dir_string():
        gui.show_dialog_message("Pasta de PDFs ainda não foi selecionada! Selecione uma pasta válida antes de continuar.", 
                                "warning")
        return False

    if gui.get_selected_credential_file_string() == gui.get_initial_selected_credential_file_string():
        gui.show_dialog_message("Arquivo de credencial ainda não foi selecionado! Selecione um aquivo de credendial "+
            "válido antes de continuar.", "warning")
        return False

    if gui.get_spreadsheet_id().strip() == "":
        gui.show_dialog_message("Id da planilha não foi preenchido! Preencha antes de continuar!", "warning")
        return False
    
    if gui.get_sheet_name().strip() == "":
        gui.show_dialog_message("O nome da aba da planilha não foi preenchido!  \n Preencha antes de continuar.", "warning")
        return False

    return True


def start_btn_action():
    gui.capture_typed_spreadsheet_id_manual()
    gui.capture_typed_sheet_name_manual()
    if check_filled_fields():
        gui.toggle_text_box_visibility()
        #call function to start script
        gui.make_all_widgets_unclickable()
        execute_script()

def execute_script():
    directory_path = gui.get_selected_pdf_dir_string()
    credentials_path = gui.get_selected_credential_file_string()
    credentials_path_dir = os.path.dirname(credentials_path)
    token_path = os.path.join(credentials_path_dir, 'my_token.json')

    #Logging setup
    today_date = date.today().strftime('%d.%m.%Y')
    log_folder = os.path.join(directory_path, 'Relatório de importação')
    os.makedirs(log_folder, exist_ok=True)
    log_path = os.path.join(log_folder, f'log de importação do dia {today_date}.txt')
    log_format = '--%(name)s - %(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename=log_path, format=log_format, datefmt='%Y-%m-%d %H:%M:%S')
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    logging.getLogger('googleapiclient').setLevel(logging.WARNING)
    logging.getLogger('google.auth').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

    #List of review pending documents setup
    review_list_path = os.path.join(log_folder, 'Lista de Arquivos Pendentes.txt')
    

    print_and_log('INFO', 'Iniciando execução do script:', log)


    try:
        # Authenticate and start service from Google API--------------------------
        service_manager = ServiceManager(credentials_path, token_path)
        service_manager.start_services()

        if service_manager.service_started('sheets', 'v4'):
            log.info('Serviço de sheets ativo e operante \n')
    except Exception as e:
        traceback_register = traceback.format_exc()
        print_and_log('ERROR',f'Erro ao autenticar e iniciar serviço. Detalhes do erro: \n{e}', log)
        log.error(f'Erro ao autenticar e iniciar serviço. Detalhes do erro: \n{e}\n\n Traceback para consulta:\n{traceback_register}\n\n')
        raise ConnectionError

        
def main():
    global gui
    gui = Visuals(pdf_btn_action, credential_btn_action, start_btn_action)
    gui.start_main_loop()

if __name__ == "__main__":
    main()
