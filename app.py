import streamlit as st
from openai import OpenAI
import pandas as pd
from utils import get_context_from_query, custom_prompt, get_response, get_security_trigger_message

df_vector_store = pd.read_pickle('df_vector_store.pkl')

def main_page():
  if "temperature" not in st.session_state:
      st.session_state.temperature = 0.0
  if "model" not in st.session_state:
      st.session_state.model = "gpt-3.5-turbo"
  if "message_history" not in st.session_state:
      st.session_state.message_history = []

  with st.sidebar:
    st.image('logo-arauco.png', use_column_width="always")
    st.header(body="CHAT Q&A :robot_face:")
    st.subheader(body="[Capas de seguridad]")
    st.header(body="")
    st.subheader('Configuración del modelo :level_slider:')

    model_name = st.radio("**Elije un modelo**:", ("GPT-3.5", "GPT-4", "GPT-4o"))
    if model_name == "GPT-3.5":
      st.session_state.model = "gpt-3.5-turbo"
    elif model_name == "GPT-4":
      st.session_state.model = "gpt-4"
    elif model_name == "GPT-4o":
      st.session_state.model = "gpt-4o"
    
    st.session_state.temperature = st.slider("**Nivel de creatividad de respuesta**  \n  [Poco creativo ►►► Muy creativo]",
                                             min_value = 0.0,
                                             max_value = 1.0,
                                             step      = 0.1,
                                             value     = 0.0)
    
  if st.session_state.get('generar_pressed', False):
    for message in st.session_state.message_history:
      with st.chat_message(message["role"]):
        st.markdown(message["content"])

  if prompt := st.chat_input("¿Cuál es tu consulta?"):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        security_message = get_security_trigger_message(prompt)

        if security_message:
            full_response = security_message
        else:
            # Proceed with generating the context and response
            Context_List = get_context_from_query(query=prompt,
                                                  vector_store=df_vector_store,
                                                  n_chunks=5)
            messages = [{"role": "system", "content": f"{custom_prompt.format(source=str(Context_List))}"}] + st.session_state.message_history + [{"role": "user", "content": prompt}]
            
            full_response = get_response(model=st.session_state.model, 
                                        temperature=st.session_state.temperature, 
                                        messages=messages)

        message_placeholder.markdown(full_response)
    st.session_state.message_history.append({"role": "user", "content": prompt})
    st.session_state.message_history.append({"role": "assistant", "content": full_response})
    st.session_state.generar_pressed = True

if __name__ == "__main__":
    main_page()