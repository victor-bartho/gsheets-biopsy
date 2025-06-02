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
import threading


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


#defining button click actions
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
        threading.Thread(target=execute_script, daemon=True).start()
        #execute_script()

def execute_script():
    directory_path = gui.get_selected_pdf_dir_string()
    credentials_path = gui.get_selected_credential_file_string()
    credentials_path_dir = os.path.dirname(credentials_path)
    token_path = os.path.join(credentials_path_dir, 'my_token.json')
    spreadsheet_id = gui.get_spreadsheet_id()
    sheet_name = gui.get_sheet_name()
    cells_range = sheet_name

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
    

    log.info('Extração Informação Laudos - Versão 1.2 \n')
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

    #Iterate through a directory and append data for each biopsy file
    for file_name in os.listdir(directory_path):
        old_file_path = os.path.join(directory_path, file_name)
        #if it is a pdf, then start loop. if it is not, ignore, since it may be a logging report or folder
        if os.path.isfile(old_file_path) and old_file_path.split('.')[-1].lower() == 'pdf':
            #Read PDF----------------------------------------------------------------
            pdf_reader_module = PDFReaderModule(old_file_path)
            text_content = pdf_reader_module.save_content_into_string()

            #Extract information fom PDF----------------------------------------------
            info_extractor = BiopsyInfoExtractor.from_model(text_content, 'model_1', gui.append_string_text_box)
            if info_extractor.validate_biopsy():
                print_and_log('INFO',f'-Lendo arquivo: {file_name}', log)
                values_to_be_appended = info_extractor.organize_information_into_sheets_api_input_format()
                biopsy_order_number = info_extractor.get_order_number() #used for document identification

                try:
                    #Insert data into sheet--------------------------------------------------
                    sheets_manipulator = SheetsManipulator(service_manager, spreadsheet_id)
                    sheets_manipulator.copy_table_banding_to_new_row(sheet_name)
                    sheets_manipulator.append_new_row(spreadsheet_id, cells_range, [values_to_be_appended])
                    print_and_log('INFO',f'Informações do arquivo {file_name} (pedido: {biopsy_order_number}) '
                                    f'incluídas na planilha com sucesso', log)

                except Exception as e:
                    gui.append_string_text_box(f'Erro ao inserir informações do arquivo na planilha de Google Sheets. '
                    f'O arquivo {file_name} deverá ser inserido manualmente. \n Detalhes do erro:\n {e}')
                    traceback_register = traceback.format_exc()
                    log.error(f'Erro ao inserir informações do arquivo {file_name} na planilha de Google Sheets. Detalhes do '
                        f'erro:\n {e} \n\n Traceback para consulta:\n{traceback_register}\n\n')
                    add_file_to_review_list(review_list_path, file_name, 'Realizar inserção manual de dados na planilha')
                    continue


                try:
                    #Finish renaming file in directory---------------------------------------
                    new_file_path = os.path.join(directory_path, str(biopsy_order_number) + '.pdf')
                    new_file_path = os.path.normpath(new_file_path)
                    #check if file_name already exists. In case it does, rename with a sequence letter
                    if os.path.exists(new_file_path):
                        n = 2
                        alternative_file_path = os.path.join(directory_path, f'{biopsy_order_number}_{n}.pdf')
                        while os.path.exists(alternative_file_path):
                            n+=1
                            alternative_file_path = os.path.join(directory_path, f'{biopsy_order_number}_{n}.pdf')
                        gui.append_string_text_box(f'biópsia de pedido nº {biopsy_order_number} foi lida repetidamente')
                        new_file_path = alternative_file_path
                    os.rename(old_file_path, new_file_path)
                    log.info(f'Arquivo {file_name} (pedido: {biopsy_order_number}) renomeado com sucesso')
                    log.info(f'OK: arquivo {file_name} (pedido: {biopsy_order_number}).\n')
                except Exception as e:
                    gui.append_string_text_box(f'Erro ao renomear o arquivo na pasta {directory_path}. O arquivo {file_name} deverá'
                        f'ser renomeado manualmente. \n Detalhes do erro:\n{e}')
                    traceback_register = traceback.format_exc()
                    log.error(
                        f'Erro ao renomear o arquivo {file_name} na pasta. Detalhes do '
                        f'erro:\n {e} \n\n Traceback para consulta:\n{traceback_register}\n\n')
                    add_file_to_review_list(review_list_path, file_name, 'Iserção ok. Renomear arquivo manualmente')
                    continue
            else:
                gui.append_string_text_box(f'Documento {file_name} não é uma biópsia válida, e, portanto, será pulado.'
                    f'\n Faça verificação manual')

    gui.append_string_text_box(cowsay.get_output_string('cow', 'Fim do script!'))

        
def main():
    global gui
    gui = Visuals(pdf_btn_action, credential_btn_action, start_btn_action)
    gui.start_main_loop()

if __name__ == "__main__":
    main()
