from PyPDF2 import PdfReader
from os import path

class PDFReaderModule:
    def __init__(self, file_path):
        self._file_path = file_path
        self._text_content = ''

    def get_file_path(self):
        return self._file_path

    def set_file_path(self, file_path):
        if path.exists(file_path):
            self._file_path = file_path
        else:
            raise FileNotFoundError('File path not found.')

    def get_text_content(self):
        return self._text_content

    def set_text_content(self, text_content_string: str):
        self._text_content = text_content_string

    def save_content_into_string(self) -> str:
        text_content = ''
        reader = PdfReader(self.get_file_path())
        for page in reader.pages:
            if text_content == '':
                text_content = page.extract_text()
            else:
                text_content = text_content + "\n" + page.extract_text()
        return text_content

    def generate_txt_tile_with_content(self, chosen_path, file_name='teste_exportação_conteúdo_laudo.txt'):
        text_content = self.save_content_into_string()
        with open(chosen_path + file_name, "w") as file:
            file.write(text_content)



