from deep_translator import GoogleTranslator


# Функция, которая переводит текст
def translate_text(text, language='en'):
    # Переводим текст на английский
    translated = GoogleTranslator(source='auto', target=language).translate(text)
    return translated