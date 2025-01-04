from service_manager import ServiceManager


class SheetsManipulator:
    def __init__(self, service_manager_instance: ServiceManager, spreadsheet_id):
        self.__service_manager = service_manager_instance
        self.__spreadsheet_id = spreadsheet_id
        self.__spreadsheet_properties = {}
        self.__spreadsheet_properties_with_format = {}


    def check_service_operation(self, service_name: str)-> bool: # will only check service operation after i at least tried to start a service. Thus, instance as parameter
        instance = self.get_service_manager()
        match service_name:
            case 'all':
                return (instance.service_started('drive', 'v3') and
                        instance.service_started('sheets', 'v4'))
            case 'drive':
                return instance.service_started('drive', 'v3')
            case 'sheets':
                return instance.service_started('sheets', 'v4')

    def append_new_row(self, spreadsheet_id, cells_range, values, value_input_option='USER_ENTERED'):
        if self.check_service_operation('sheets'):
            try:
                service_instance = self.get_service_manager().get_service('sheets', 'v4')
                request = service_instance.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=cells_range, valueInputOption=value_input_option, body={'values':values})
                request.execute()
                #response = request.execute()
                #print(response)
            except Exception as e:
                raise Exception(f'Algo deu errado, a informação NÃO foi inserida na planilha: {e}') from e
        else:
            raise Exception(f'O serviço de sheets não está ativo.')

    def get_spreadsheet_properties(self, spreadsheet_id): #returns the whole list with all sheets properties
        if not self.__spreadsheet_properties:
            if self.check_service_operation('sheets'):
              service_instance = self.get_service_manager().get_service('sheets', 'v4')
              try:
                request = service_instance.spreadsheets().get(spreadsheetId=spreadsheet_id)
                response = request.execute()
                self.__spreadsheet_properties = response
              except Exception as e:
                raise Exception(f'Algo deu errado na aquisição de propriedades da planilha: {e}') from e
            else:
                raise Exception(f'O serviço de sheets não está ativo.')

        return self.__spreadsheet_properties

    def get_spreadsheet_properties_with_formating(self, spreadsheet_id):
        if not self.__spreadsheet_properties_with_format:
            if self.check_service_operation('sheets'):
                service_instance = self.get_service_manager().get_service('sheets', 'v4')
                try:
                    request = service_instance.spreadsheets().get(spreadsheetId=spreadsheet_id, includeGridData=True)
                    response = request.execute()
                    self.__spreadsheet_properties_with_format = response
                except Exception as e:
                    raise Exception(f'Algo deu errado na aquisição de propriedades de formatação da planilha: {e}') from e
            else:
                raise Exception('O serviço de sheets não está ativo.')


        return self.__spreadsheet_properties_with_format


    def insert_blank_line_at_bottom(self, sheet_name, number_of_newlines: int):
        body = {
            "requests": [
                {
                    "appendDimension": {
                        "sheetId": self.get_sheet_id_by_sheet_name(sheet_name),
                        "dimension": "ROWS",
                        "length": number_of_newlines
                    }
                }]
        }
        if self.check_service_operation('sheets'):

            service_instance = self.get_service_manager().get_service('sheets', 'v4')
            try:
                spreadsheet_id = self.get_spreadsheet_id()
                request = service_instance.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body)
                response = request.execute()
                print(f'Linha em branco inserida com sucesso. \n {response}')
            except Exception as e:
                raise Exception(f'Algo deu errado ao inserir uma linha em branco na planilha: {e}') from e
        else:
            print('O serviço de sheets não está ativo')
            raise Exception(f'O serviço de sheets não está ativo.')

    def get_sheet_id_by_sheet_name(self, sheet_name):
        spreadsheet_id = self.get_spreadsheet_id()
        sheet_properties = self.get_spreadsheet_properties(spreadsheet_id)
        for sheets in sheet_properties['sheets']:
            if sheets['properties']['title'] == sheet_name:
                return sheets['properties']['sheetId']
        raise Exception(f'A página de nome {sheet_name} não foi encontrada na planilha.')

    def get_sheet_data(self, sheet_name): #returns a list with the data fragment from resources dictionary. Result format is [{'rowData'[{'values':...}]}]
        sheet_data = []
        spreadsheet_id = self.get_spreadsheet_id()
        spreadsheet_properties_with_gridinfo = self.get_spreadsheet_properties_with_formating(spreadsheet_id)
        for sheet in spreadsheet_properties_with_gridinfo['sheets']:
            sheet_title = sheet['properties']['title']
            if sheet_title == sheet_name:
                sheet_data = sheet['data']
        if not sheet_data:
            raise Exception(f'A página de nome {sheet_name} não foi encontrada na planilha.')

        return sheet_data

    def count_sheet_rows(self, sheet_name):
        row_count = 0
        data_content = self.get_sheet_data(sheet_name)
        for item in data_content[0]['rowData']:
            if any('userEnteredValue' in value for value in item['values']):
                row_count += 1
        return row_count

    def copy_format_from_last_row_to_newly_inserted_row(self, sheet_name):
        sheet_id = self.get_sheet_id_by_sheet_name(sheet_name)
        last_row = self.count_sheet_rows(sheet_name)
        body = {
            "requests": [
                {
                    "copyPaste": {
                        "source": {
                            "sheetId": sheet_id,
                            "startRowIndex": last_row - 2,
                            "endRowIndex": last_row - 1,
                            "startColumnIndex": 0,
                            "endColumnIndex": None
                        },
                        "destination": {
                            "sheetId": sheet_id,
                            "startRowIndex": last_row - 1,
                            "endRowIndex": last_row
                        },
                        "pasteType": "PASTE_FORMAT"
                    }
                }
            ]
        }

        spreadsheet_id = self.get_spreadsheet_id()
        service_instance = self.get_service_manager().get_service('sheets', 'v4')
        if service_instance:
            try:
                request =service_instance.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body)
                response = request.execute()
                print(f'Nova linha de formatação inserida com sucesso. \n {response}')
            except Exception as e:
                print('Algo deu errado, ao inserir uma linha de formatação na planilha.')
                raise Exception(f'Algo deu errado, ao inserir uma linha de formatação na planilha. Detalhes do erro:\n {e}')
        else:
            raise Exception(f'O serviço de sheets não está ativo.')


    def copy_table_banding_to_new_row(self, sheet_name):
        new_endrow_index = self.count_sheet_rows(sheet_name)
        #call function to get bandedRange to be modified
        banded_range, banded_sheet_id, banded_range_id = self.get_table_banded_ranges_info(sheet_name)
        banded_range['sheetId'] = banded_sheet_id
        banded_range['endRowIndex'] = new_endrow_index + 1
        if banded_sheet_id == self.get_sheet_id_by_sheet_name(sheet_name):
            body = {
              "requests": [
                {
                  "updateBanding": {
                    "bandedRange": {
                      "bandedRangeId": banded_range_id,
                      "range": banded_range
                    },
                    "fields": "range"
                  }
                }
              ]
            }
            spreadsheet_id = self.get_spreadsheet_id()
            service = self.get_service_manager().get_service('sheets', 'v4')
            service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
        else:
            raise Exception(f'O bandedSheetId é diferente do sheetId de {sheet_name}')


    def get_table_banded_ranges_info(self, sheet_name):
        banding_info = None
        banded_range = None
        banded_range_id = None
        banded_sheet_id = None
        sheet_id = self.get_sheet_id_by_sheet_name(sheet_name)
        properties = self.get_spreadsheet_properties(sheet_id)
        for sheet in properties['sheets']:
            if sheet['properties']['sheetId'] == sheet_id:
                banding_info = sheet['bandedRanges']
                banded_range_id = banding_info[0]['bandedRangeId']
                banded_range = banding_info[0]['range']
                banded_sheet_id = banding_info[0]['range']['sheetId']
        if not banding_info:
            raise Exception(f'Não foi encontrado banded range para a página {sheet_name}')

        return banded_range, banded_sheet_id, banded_range_id

    def get_spreadsheet_id(self):
        return self.__spreadsheet_id

    def set_spreadsheet_id(self, id_value):
        self.__spreadsheet_id = id_value

    def get_service_manager(self) -> ServiceManager:
        return self.__service_manager