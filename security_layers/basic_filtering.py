import os
import re
from typing import List, Union, Callable
# from google.cloud import language_v1

def get_predefined_ban_list() -> List[str]:
    """
    Retrieve a list of predefined banned words from a file.

    This function reads a file named 'security_basic_filtering.txt' located
    in the same directory as the script and returns a list of words, each 
    representing a line from the file.

    Returns:
        List[str]: A list of banned words.
    """
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, 'security_basic_filtering.txt')
    word_list = []
    with open(file_path, 'r') as file:
        word_list = [line.strip() for line in file]
    return word_list

def clean_text(text_input:str) -> str:
    """
    Clean the input text by performing predefined character substitutions.

    This function converts the input text to lowercase and replaces specific
    characters and digits with their corresponding substitutions. The substitutions
    include replacing accented characters with their unaccented equivalents and
    some digits with letters that resemble them.

    Args:
        text_input (str): The text to be cleaned.

    Returns:
        str: The cleaned text with substitutions applied.
    """
    substitutions = {"ü": "u",
                     "é": "e",
                     "á": "a",
                     "í": "i",
                     "ó": "o",
                     "ú": "u",
                     "4": "a",
                     "3": "e",
                     "1": "i",
                     "0": "o",
                     "5": "s",
                     }
    text_input = text_input.lower()

    substitutions = dict((re.escape(k), v) for k, v in substitutions.items()) 
    pattern = re.compile("|".join(substitutions.keys()))
    cleaned = pattern.sub(lambda m: substitutions[re.escape(m.group(0))], text_input)
    return cleaned

def basic_word_occurance(text_input:str,
                         banned_words: List[str],
                         )->bool:
    """
    Check if any banned word is present in the input text using basic string containment.

    This function iterates through the list of banned words and checks if any of them
    are present as substrings in the provided text.

    Args:
        text_input (str): The text to be checked.
        banned_words (List[str]): A list of banned words to check against the text.

    Returns:
        bool: True if any banned word is found in the text, False otherwise.
    """
    return any(word in text_input for word in banned_words)

def regex_word_occurance(text_input:str,
                         banned_words: List[str],
                         )->bool:
    """
    Check if any banned word is present in the input text using regular expressions.

    This function compiles a regular expression pattern that matches any of the banned
    words, ensuring that they are treated as whole words rather than substrings, and
    checks if any match is found in the provided text.

    Args:
        text_input (str): The text to be checked.
        banned_words (List[str]): A list of banned words to check against the text.

    Returns:
        bool: True if any banned word is found in the text, False otherwise.
    """
    regex = re.compile(r's?($|\s+|\.+)|(^|\s+)'.join(re.escape(x) for x in banned_words))
    result = re.search(regex, text_input)
    if result is None:
        return False
    return True

def security_basic_filtering(text_input: str,
                             banned_words: List[str] = None,
                             filter_method:Union[str,Callable[[str,str],bool]] = "REGEX",
                             ):
    """
    Filter the input text for banned words using a specified filtering method.

    This function checks if the input text contains any banned words. It supports
    different filtering methods: "SIMPLE", "REGEX", or a custom filtering function.
    The text is first cleaned by replacing certain characters and converting it to
    lowercase.

    Args:
        text_input (str): The text to be filtered.
        banned_words (List[str], optional): A list of banned words to check against the text.
            If not provided, a predefined list of banned words is used.
        filter_method (Union[str, Callable[[str, List[str]], bool]], optional): The method
            to use for filtering. This can be "SIMPLE" for basic string containment,
            "REGEX" for regular expression matching, or a custom function that takes
            the text and banned words as input and returns a boolean.

    Returns:
        bool: True if any banned word is found in the text, False otherwise.

    Raises:
        NotImplementedError: If an unsupported filter method is provided.

    Example:
        >>> security_basic_filtering("This is a test text", ["test"], "SIMPLE")
        True
    """
    if banned_words is None:
        banned_words = get_predefined_ban_list()

    if not callable(filter_method):
        match filter_method:
            case "SIMPLE":
                filter_method = basic_word_occurance
            case "REGEX":
                filter_method = regex_word_occurance
            case _:
                raise NotImplementedError("Only methods available are SIMPLE, REGEX or custom made")

    text_input = clean_text(text_input)

    return filter_method(text_input,banned_words,)

# def security_category_check(text_input:str):
#     """
#     Clasifica el contenido de un texto y retorna el resultado como una lista de diccionarios.

#     Args:
#       text_input: El texto de contenido a analizar.

#     Returns:
#       Lista de diccionarios que contiene el nombre de categoría y el score de confiabilidad.
#     """
#     client = language_v1.LanguageServiceClient()
    
#     type_ = language_v1.Document.Type.PLAIN_TEXT
#     language = "es"
#     document = {"content": text_input, "type_": type_, "language": language}

#     content_categories_version = (language_v1.ClassificationModelOptions.V2Model.ContentCategoriesVersion.V2)

#     # Make the classification request
#     response = client.classify_text(request={
#         "document": document,
#         "classification_model_options": {
#             "v2_model": {
#                 "content_categories_version": content_categories_version
#             }
#         }
#     })

#     # Create a list of dictionaries
#     category_list = [
#         {"name": category.name, "confidence": category.confidence}
#         for category in response.categories
#     ]

#     return category_list
