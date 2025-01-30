import os
import traceback
from pdf_reader_module import PDFReaderModule
from info_extractor import BiopsyInfoExtractor
from sheets_manipulation import SheetsManipulator
from service_manager import ServiceManager
from datetime import date
import logging
import cowsay

#Logging methods
def print_and_log(level_name, message, logger=logging):
        print(message)
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

def main():
    print('Projeto Banco de Dados \n')
    #Define necessary files, such as directory that contains PDFs, credentials json path and token json path (which,
    # by default, will be name 'my_token.json' inside the same directory as credentials json)
    standard_config = input('Inserir informações na planilha padrão (S/N)?')
    while not (standard_config.lower() == 's' or standard_config.lower() == 'n'):
        standard_config = input('Insira uma resposta válida para uso de planilha padrão (S/N): ')

    match standard_config.lower():
        case 'n':
            __spreadsheet_id = input('Digite o id da planilha (encontrado na URL): ')
            sheet_name = input('Digite o nome da aba da planilha: ')
            cells_range = input('Digite o range em notação A1: ')
        case 's' | _:
            __spreadsheet_id = '1wDG00ttRcT57VVPVppvAxwNvImeSJ_XVi-f5dJDmnsE' #default spreadsheet id for the project
            sheet_name = input('Digite o nome da aba da planilha: ')
            cells_range = sheet_name  # since we're using only append function, no need to define A1 notation range

    directory_path = input('Digite o caminho da pasta onde estão os PDFS e aperte Enter: ')
    directory_path = os.path.normpath(directory_path)
    while not (os.path.exists(directory_path) and os.path.isdir(directory_path)):
        directory_path = input('Digite um caminho de pasta válido: ')
        directory_path = os.path.normpath(directory_path)

    credentials_path = input('Digite o caminho do arquivo de credenciais do Google: ')
    credentials_path = os.path.normpath(credentials_path)

    while not (os.path.exists(credentials_path) and credentials_path.split('.')[-1].lower() == 'json'):
        credentials_path = input('Digite um caminho de arquivo de credenciais válido: ')
        credentials_path = os.path.normpath(credentials_path)

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

    #Iterate through a directory and append data for each biopsy file
    for file_name in os.listdir(directory_path):
        old_file_path = os.path.join(directory_path, file_name)
        #if it is a pdf, then start loop. if it is not, ignore, since it may be a logging report or folder
        if os.path.isfile(old_file_path) and old_file_path.split('.')[-1].lower() == 'pdf':
            #Read PDF----------------------------------------------------------------
            pdf_reader_module = PDFReaderModule(old_file_path)
            text_content = pdf_reader_module.save_content_into_string()

            #Extract information fom PDF----------------------------------------------
            info_extractor = BiopsyInfoExtractor.from_model(text_content, 'model_1')
            if info_extractor.validate_biopsy():
                print_and_log('INFO',f'Lendo arquivo: {file_name}', log)
                values_to_be_appended = info_extractor.organize_information_into_sheets_api_input_format()
                biopsy_order_number = info_extractor.get_order_number() #usded for document identification
                try:
                    #Insert data into sheet--------------------------------------------------
                    sheets_manipulator = SheetsManipulator(service_manager, __spreadsheet_id)
                    sheets_manipulator.copy_table_banding_to_new_row(sheet_name)
                    sheets_manipulator.append_new_row(__spreadsheet_id, cells_range, [values_to_be_appended])
                    print_and_log('INFO',f'Informações do arquivo {file_name} (pedido: {biopsy_order_number}) '
                                        f'incluídas na planilha com sucesso', log)
                except Exception as e:
                    print(f'Erro ao inserir informações do arquivo na planilha de Google Sheets. '
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
                        print(f'biópsia de pedido nº {biopsy_order_number} foi lida repetidamente')
                        new_file_path = alternative_file_path
                    os.rename(old_file_path, new_file_path)
                    log.info(f'Arquivo {file_name} (pedido: {biopsy_order_number}) renomeado com sucesso')
                    log.info(f'OK: arquivo {file_name} (pedido: {biopsy_order_number}).\n')
                except Exception as e:
                    print(f'Erro ao renomear o arquivo na pasta {directory_path}. O arquivo {file_name} deverá'
                        f'ser renomeado manualmente. \n Detalhes do erro:\n{e}')
                    traceback_register = traceback.format_exc()
                    log.error(
                        f'Erro ao renomear o arquivo {file_name} na pasta. Detalhes do '
                        f'erro:\n {e} \n\n Traceback para consulta:\n{traceback_register}\n\n')
                    add_file_to_review_list(review_list_path, file_name, 'Iserção ok. Renomear arquivo manualmente')
                    continue
            else:
                print(f'Documento {file_name} não é uma biópsia válida, e, portanto, será pulado.'
                    f'\n Faça verificação manual')

    print(cowsay.get_output_string('cow', 'Fim do script!'))

if __name__ == '__main__':
    main()



