import os
import math
from collections import Counter
from google.cloud import vision
from service_manager import ServiceManager

file_path = '/home/bart/my-coding-projects/Google_Sheets_Automation_Script_Biopsies/Resources/biopsy_reports_for_testing/Laudos separados 1/1 - andreza aparecida fernandes.pdf'
file_path_claro = '/home/bart/my-coding-projects/Google_Sheets_Automation_Script_Biopsies/Resources/biopsy_reports_for_testing/Laudos separados 1/1 - anibal goulart (claro).pdf'
file_path_modelo_2 = '/home/bart/my-coding-projects/Google_Sheets_Automation_Script_Biopsies/Resources/biopsy_reports_for_testing/Laudos separados 2/2 - geraldo orlando.pdf'


def detect_text(path):
    
    service_manager = ServiceManager('/home/bart/my-coding-projects/Google_Sheets_Automation_Script_Biopsies/Resources/Projeto_Banco_de_Dados_Prof_Paula_Vidigal/OAuth_Credentials_Projeto_Banco_Dados/client_secret_teste_victor.json', '/home/bart/my-coding-projects/Google_Sheets_Automation_Script_Biopsies/Resources/Projeto_Banco_de_Dados_Prof_Paula_Vidigal/OAuth_Credentials_Projeto_Banco_Dados/my_token.json')
    creds = service_manager.authenticate()
    """Detects text in the file."""
    client = vision.ImageAnnotatorClient(credentials=creds)

    with open(path, 'rb') as image_file:
        content = image_file.read()
    
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations

    text_content = ''
    for text in texts:
        if text_content == '':
            text_content = text.description
        else:
            text_content = text_content + "\n" + text.description
    
    return text_content


text = detect_text(file_path)
for line in text:
    print(line)
