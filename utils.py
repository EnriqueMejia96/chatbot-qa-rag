import numpy as np
from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_KEY'))

def text_embedding(text=[]):
    embeddings = client.embeddings.create(model="text-embedding-ada-002",
                                          input=text,
                                          encoding_format="float")
    return embeddings.data[0].embedding

def get_dot_product(row):
    return np.dot(row, query_vector)

def cosine_similarity(row):
    denominator1 = np.linalg.norm(row)
    denominator2 = np.linalg.norm(query_vector.ravel())
    dot_prod = np.dot(row, query_vector)
    return dot_prod/(denominator1*denominator2)

def get_context_from_query(query, vector_store, n_chunks = 5):
    global query_vector
    query_vector = np.array(text_embedding(query))
    top_matched = (
        vector_store["Embedding"]
        .apply(cosine_similarity)
        .sort_values(ascending=False)[:n_chunks]
        .index)
    top_matched_df = vector_store[vector_store.index.isin(top_matched)][["Chunks"]]
    return list(top_matched_df['Chunks'])

custom_prompt = """
Eres una Inteligencia Artificial super avanzada que trabaja asistente personal.
Utilice los RESULTADOS DE BÚSQUEDA SEMANTICA para responder las preguntas del usuario. 
Solo debes utilizar la informacion de la BUSQUEDA SEMANTICA si es que hace sentido y tiene relacion con la pregunta del usuario.
Si la respuesta no se encuentra dentro del contexto de la búsqueda semántica, no inventes una respuesta, y responde amablemente que no tienes información para responder.

RESULTADOS DE BÚSQUEDA SEMANTICA:
{source}

Lee cuidadosamente las instrucciones, respira profundo y escribe una respuesta para el usuario!
"""

def get_response(model, temperature, messages):
    completion = client.chat.completions.create(
        model=model,
        temperature = temperature,
        messages= messages
    )
    full_response = completion.choices[0].message.content

    return full_response

from security_layers.basic_filtering import security_basic_filtering
from security_layers.pii_management import security_pii_management
from security_layers.agent_validator import security_agent_validator
def get_security_trigger_message(prompt):
    # Check for security issues and return the corresponding message
    checks = [
        (security_basic_filtering, "Se ha detectado contenido inapropiado en tu consulta, por favor intenta de nuevo."),
        (security_pii_management, "Se ha detectado información personal en tu consulta, por favor intenta de nuevo."),
        (security_agent_validator, "Se ha detectado consulta fuera de contexto, por favor intenta de nuevo.")
    ]
    for check_function, message in checks:
        if check_function(prompt):
            return message
    return None