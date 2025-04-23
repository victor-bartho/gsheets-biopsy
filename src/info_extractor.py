import re
from datetime import datetime


class BiopsyInfoExtractor:
    __pattern_models = {
        'model_1': {'patient_name': r"Cliente:\s*(.*?)(?=\s*\()",
            'order_number': r"Pedido:\s*(.*?)(?=\s*Coleta)",
            'biopsy_material': r"BIÓPSIA.*?Material:\s*(.*?)(?=\s*MACROSCOPIA)",
            'birth_date': r'Dt\. Nasc:\s*(\d{2}/\d{2}/\d{2,4})(?=\s*RG:)',
            'biopsy_date': r'Origem.:.*?Coleta:\s*(\d{2}/\d{2}/\d{2,4})(?=.*?BIÓPSIA)',
            'chart_number': r'Cliente:.*?\((.*?)\)(?=\s*NPF:)',
            'block_id': r'(?:CRM\s?-\s?\d{5,6})[^\S\r\n]*\n?(?:.*\n){0,2}?([A-Za-z]?:?\s?-?\s?\d{2,5}[-/]\d{2,4})', 
            'block_quantity': r'(?<=MACROSCOPIA).*?\b(\d{1,3})\s*(?:BT|B|BS)\b.*?(?=MICROSCOPIA)',
            'collection_origin': r'Origem.:\s*(.*?)(?=\s*Pedido)',
            'conclusion_text': r'(?i)conclus[aã]o[:]?\s*(.*?)(?=\b(?:DR|DRA)\.?\s)'} #include raw text into a column for
                    #quicker user consultation. Since they manually fill a column based on this text, it is quicker
                    #to read on the spreadsheet than to open the pdf file to read this piece of text
    }
    def __init__(self, content_string, selected_pattern_dictionary: dict[str, str]): #instantiate with classmethod from_model() in order to get a dictionary
        self.__content_string = content_string
        self.__patterns = selected_pattern_dictionary
        self.__biopsy_material = None
        self.__patient_name = None
        self.__patient_initials = None
        self.__order_number = None
        self.__birth_date = None
        self.__biopsy_date = None
        self.__age_at_biopsy = None
        self.__chart_number = None
        self.__block_id = None
        self.__block_quantity = None
        self.__collection_origin = None
        self.__conclusion_text = None


    @classmethod
    def from_model(cls, content_string, model):
        if model in cls.__pattern_models:
            return cls(content_string, cls.__pattern_models[model])
        else:
            raise ValueError(f'unknown model: {model}')

    def validate_biopsy(self): #if cannot find the two most basic info, not valid biopsy
        if self.get_order_number() != 'not found' and self.get_patient_name() != 'not found':
            return True
        else:
            return False

    def inform_no_matches(self, info: str):
        order_number = self.get_order_number()
        patient_name = self.get_patient_name()
        print(f'Informação não encontrada para {info} na biópsia de número de pedido {order_number} para o paciente '
            f'{patient_name}')

    def extract_patient_name(self) -> str:
        content_string = self.get_content_string()
        pattern_section = self.get_pattern('patient_name')
        patient_name = re.search(pattern_section, content_string, re.DOTALL)
        
        if patient_name:
               return str(patient_name.group(1)).upper()
        else:
            return 'not found'
            

    def extract_order_number(self) -> int:
        content_string = self.get_content_string()
        pattern_section = self.get_pattern('order_number')
        order_number = re.search(pattern_section, content_string, re.DOTALL)

        if order_number:
            return int(order_number.group(1))
        else:
            return'not found'
            

    def extract_biopsy_material(self):
        content_string = self.get_content_string()
        pattern_section = self.get_pattern('biopsy_material')
        biopsy_material = re.search(pattern_section, content_string, re.DOTALL)
        if biopsy_material:
            raw_material = biopsy_material.group(1)
            #Handle output. In case there is more than one material, organize them into a list.
            comma_separated_material = re.sub(r'\s*(?:\s+e\s+|\+|\/)\s*', ',', raw_material, flags=re.IGNORECASE)
            material_list = comma_separated_material.upper().split(',')
            organized_materials = ', '.join(material_list)
            return organized_materials
        else:
            self.inform_no_matches('MATERIAL DA BIÓPSIA')
            return 'not found'


    def extract_birth_date(self) -> str:
        content_string = self.get_content_string()
        pattern_section = self.get_pattern('birth_date')
        birth_date = re.search(pattern_section, content_string, re.DOTALL)
        if birth_date:
            return birth_date.group(1)
        else:
            self.inform_no_matches('DATA DE NASCIMENTO')
            return 'not found'

    def extract_biopsy_date(self) -> str:
        content_string = self.get_content_string()
        pattern_section = self.get_pattern('biopsy_date')
        biopsy_date = re.search(pattern_section, content_string, re.DOTALL)
        if biopsy_date:
            return biopsy_date.group(1)
        else:
            self.inform_no_matches('DATA DA BIÓPSIA')
            return 'not found'

    def calculate_age_at_biopsy(self):
        birth_date_as_datetime = self.get_birth_date(return_as_datetime=True)
        biopsy_date_as_datetime = self.get_biopsy_date(return_as_datetime=True)
        if birth_date_as_datetime != 'not found' and biopsy_date_as_datetime != 'not found':
            age_at_biopsy_as_timedelta = biopsy_date_as_datetime - birth_date_as_datetime
            age_at_biopsy_years = int(age_at_biopsy_as_timedelta.days / 365)
            return age_at_biopsy_years
        print('Não foi possível encontrar DATA DE NASCIMENTO e/ou DATA DA BIÓPSIA, logo, não é possível calcular IDADE ' 
            'DO PACIENTE NO DIA DA BIÓPSIA.')
        return 'not found'

    def extract_chart_number(self):
        content_string = self.get_content_string()
        pattern_section = self.get_pattern('chart_number')
        chart_number = re.search(pattern_section, content_string, re.DOTALL)
        if chart_number:
            return chart_number.group(1)
        else:
            self.inform_no_matches('NÚMERO DE PRONTUÁRIO')
            return 'not_found'

    def extract_block_id(self):
        content_string = self.get_content_string()
        pattern = self.get_pattern('block_id')
        block_id = re.search(pattern, content_string, re.DOTALL)
        if block_id:
            return block_id.group(1)
        else:
            self.inform_no_matches('ID BLOCO')
            return 'not found'

    def extract_block_quantity(self) -> str:
        pattern = self.get_pattern('block_quantity')
        content_string = self.get_content_string()
        block_quantity = re.search(pattern, content_string, re.DOTALL)
        if block_quantity:
            return block_quantity.group(1)
        else:
            self.inform_no_matches('QUANTIDADE DE BLOCOS')
            return 'not found'

    def extract_patient_initials(self):
        patient_name = self.get_patient_name()
        if patient_name != 'not found':
            names = patient_name.split()
            initials = []
            for name in names:
                initials.append(name[0].capitalize() + '.')
            return ''.join(initials)
        print('Como não foi encontrado o NOME DO PACIENTE, não é possível informar INICIAIS DO PACIENTE.')
        return 'not found'

    def extract_collection_origin(self):
        content_string = self.get_content_string()
        pattern_section = self.get_pattern('collection_origin')
        collection_origin = re.search(pattern_section, content_string, re.DOTALL)
        if collection_origin:
            return collection_origin.group(1)
        else:
            self.inform_no_matches('ORIGEM DA COLETA')
            return 'not found'


    def extract_conclusion_text(self) -> str:
        content_string = self.get_content_string()
        pattern_section = self.get_pattern('conclusion_text')
        conclusion_text = re.search(pattern_section, content_string, re.DOTALL)
        
        if conclusion_text:
               return str(conclusion_text.group(1))
        else:
            return 'not found'

    def organize_information_into_sheets_api_input_format(self): #returns a list with cell value in order

        # for the list, if information not included in the pdf, it means that biopsy pdf archive does not provide that
        # information, however, the spreadsheet that will receive the information appending has that column, which will
        # be filled manually after automated append

        organized_values = {
            'Identificação': self.get_patient_initials(),
            'Sexo': '', #information about patient is not included in biopsy pdf
            'Prontuário': self.get_chart_number(),
            'Data de Nascimento': self.get_birth_date(),
            'Idade Biopsia': self.get_age_at_biopsy(),
            'Pedido': self.get_order_number(),
            'ID Bloco': self.get_block_id(),
            'Quantidade de Blocos': self.get_block_quantity(),
            'Data da Biopsia': self.get_biopsy_date(),
            'Origem da Coleta': self.get_collection_origin(),
            'Paciente Proviniente de': '', #information about patient address or city is not included in biopsy pdf, however, spreadsheet has this column, which will be filled manually after
            'Material': self.get_biopsy_material(),
            'HD Pedido': '', #information not included in biopsy pdf, however, spreadsheet has this column, which will be filled manually after
            'Conclusão Automatizada': self.get_conclusion_text(),
            'HD Laudo': '',
            'Nota': '',  #to be implemented
            'Neoplasia': '',
            'Cirrose': '',
            'Revisão': '',
            'Transplante': ''
        }

        return [value for value in organized_values.values()]

    def get_content_string(self):
        return self.__content_string

    def get_biopsy_material(self):
        if self.__biopsy_material is None:
            material = self.extract_biopsy_material()
            self.set_biopsy_material(material)
        return self.__biopsy_material

    def set_biopsy_material(self, material):
        self.__biopsy_material = material

    def get_patient_name(self):
        if self.__patient_name is None:
            name = self.extract_patient_name()
            self.set_patient_name(name)
        return self.__patient_name

    def set_patient_name(self, name):
        self.__patient_name = name

    def get_patient_initials(self):
        if self.__patient_initials is None:
            initials = self.extract_patient_initials()
            self.set_patient_initials(initials)
        return self.__patient_initials

    def set_patient_initials(self, initials):
        self.__patient_initials = initials

    def get_order_number(self):
        if self.__order_number is None:
            number = self.extract_order_number()
            self.set_order_number(number)
        return self.__order_number

    def set_order_number(self, number):
        self.__order_number = number

    def get_birth_date(self, return_as_datetime = False):
        if self.__birth_date is None:
            date = self.extract_birth_date()
            self.set_birth_date(date)

        #TODO: improve verifications to solve warning revolving datetime processing and calculations
        if return_as_datetime and self.__birth_date != 'not found':
            return datetime.strptime(self.__birth_date, "%d/%m/%Y")

        return self.__birth_date

    def set_birth_date(self, date: str):
        self.__birth_date = date

    def get_biopsy_date(self, return_as_datetime = False):
        if self.__biopsy_date is None:
            date = self.extract_biopsy_date()
            self.set_biopsy_date(date)
        #TODO: improve verifications to solve warning revolving datetime processing and calculations
        if return_as_datetime and self.__biopsy_date != 'not found':
            return datetime.strptime(self.__biopsy_date, "%d/%m/%Y")
        return self.__biopsy_date

    def set_biopsy_date(self, date: str):
        self.__biopsy_date = date

    def get_age_at_biopsy(self):
        if self.__age_at_biopsy is None:
            self.set_age_at_biopsy(self.calculate_age_at_biopsy())
        return self.__age_at_biopsy

    def set_age_at_biopsy(self, age_in_years):
        self.__age_at_biopsy = age_in_years

    def get_chart_number(self):
        if self.__chart_number is None:
            self.set_chart_number(self.extract_chart_number())
        return self.__chart_number

    def set_chart_number(self, chart_number):
        self.__chart_number = chart_number

    def get_pattern(self, pattern_key):
        if pattern_key in self.__patterns:
            return self.__patterns[pattern_key]
        else:
            raise ValueError(f'Pattern {pattern_key} not defined. Check spelling or try adding it to the list of patterns')

    def get_patterns_dictionary(self):
        return self.__patterns

    def add_pattern(self, pattern_key, pattern):
        try:
            re.compile(pattern)
            if not pattern_key in self.get_patterns_dictionary():
                self.__patterns[pattern_key] = pattern
            else:
                raise ValueError('Pattern key already exists')
        except re.error as e:
            raise ValueError(f'Invalid regex pattern: {e}')

    def remove_pattern(self, pattern_key):
        if pattern_key in self.get_patterns_dictionary():
            self.__patterns.pop(pattern_key)
        else:
            raise ValueError('Pattern Key does not exist')

    def update_pattern(self, pattern_key, new_pattern):
        if pattern_key in self.get_pattern(pattern_key):
            self.__patterns[pattern_key] = new_pattern
        else:
            raise ValueError('Pattern Key does not exist')

    def get_block_id(self):
        if self.__block_id is None:
            block_id = self.extract_block_id()
            self.set_block_id(block_id)
        return self.__block_id

    def set_block_id(self, value):
        self.__block_id = value

    def get_block_quantity(self):
        if self.__block_quantity is None:
            block_quantity = self.extract_block_quantity()
            self.set_block_quantity(block_quantity)
        return self.__block_quantity

    def set_block_quantity(self, value):
        self.__block_quantity = value

    def get_collection_origin(self):
        if self.__collection_origin is None:
            collection_origin = self.extract_collection_origin()
            self.set_collection_origin(collection_origin)
        return self.__collection_origin

    def set_collection_origin(self, value):
        self.__collection_origin = value

    def set_conclusion_text(self, value):
        self.__conclusion_text = value

    def get_conclusion_text(self):
        if self.__conclusion_text is None:
            conclusion_text = self.extract_conclusion_text()
            self.set_conclusion_text(conclusion_text)
        return self.__conclusion_text
