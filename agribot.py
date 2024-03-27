import streamlit as st
import time
from transformers import pipeline
import os
import replicate

# Import transformer to convert english to hindi
hindi = pipeline("translation", model="Helsinki-NLP/opus-mt-en-hi")

st.set_page_config(page_title='AgriBot 🤖', initial_sidebar_state="expanded", layout='wide')

st.subheader('AgriBot 🤖',divider = 'rainbow')

replicate_api = ''

with st.sidebar:
    version = st.selectbox('Please select version',options = ['Guest','Login'],index = None)
    language = st.selectbox('Select Language',options = ['English','Hindi'],index = None)
    if version == 'Guest':
        replicate_api = 'r8_eDEuNQayWEIms6SKmhqc3BH9WxEfX574HZp9p'
    elif version == 'Login':
        replicate_api = st.sidebar.text_input("Enter Your Api Key",type = 'password')
        if not (replicate_api.startswith('r8_') and len(replicate_api)==40) and len(replicate_api)!=0:
            st.warning('Please check your api key!', icon='⚠️')
        elif len(replicate_api)!=0:
            st.success('Logged in successfully', icon='👉')
    os.environ['REPLICATE_API_TOKEN'] = replicate_api
    st.write("If you want change version, then please launch the app again")

convo = st.container(height = 380,border=True)

if version and language:
    with convo:
            # A method to store the conversation for context
            if "messages" not in st.session_state:
                st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
    
            # Display chat messages from history on app rerun
            for message in st.session_state.messages:
                if language == 'English':
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
                elif language == 'Hindi':
                    if message['role'] == 'user':
                        with st.chat_message(message["role"]):
                            st.markdown(message["content"])
                    elif message['role'] == 'assistant':
                        with st.chat_message(message["role"]):
                            translated = hindi(message["content"])
                            st.markdown(translated[0]['translation_text'])
            
            #Function to Clear Chats
            def clear_chats():
                st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
            clear = st.sidebar.button("Clear Chat",on_click=clear_chats)

            #Function to Change Api Key
            def change_api_key(api_key):
                os.environ['REPLICATE_API_TOKEN'] = api_key
                clear_chats()

            #Function to Generate Response
            def generate_response(user_prompt, context):

                if len(context)>2:

                    pre_prompt = "<<SYS>>\n" + """
                            You are a helpful assistant who is an expert in agriculture. 
                            You do not respond as 'User' or pretend to be 'User'. 
                            You only respond once as 'Assistant' to the prompt.
                            You must consider the context when generating a response
                            You should provide valuable information and assistance to farmers regarding various aspects of agriculture such as crop management, pest control, weather forecasting, market prices, and general farming queries, including basic queries and recommendations
                            You should provide precise response.
                            """ + "\n<<SYS>>\n\n"

                    output = replicate.run('a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5', # LLM model
                                        input={"prompt": f"[INST]{pre_prompt} {user_prompt}\n Context: {context}[/INST]", # Prompts
                                        "temperature":0.5}) 
                    
                else:

                    pre_prompt = "<<SYS>>\n" + """
                            You are a helpful assistant who is an expert in agriculture. 
                            You do not respond as 'User' or pretend to be 'User'. 
                            You only respond once as 'Assistant' to the prompt.
                            You should provide valuable information and assistance to farmers regarding various aspects of agriculture such as crop management, pest control, weather forecasting, market prices, and general farming queries, including basic queries and recommendations
                            You should provide precise response.
                            """ + "\n<<SYS>>\n\n"

                    output = replicate.run('a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5', # LLM model
                                        input={"prompt": f"[INST]{pre_prompt} {user_prompt}[/INST]", # Prompts
                                        "temperature":0.5}) 
                
                response = ""
                for item in output:
                    response += item

                return response

    user_prompt = st.chat_input("Type your message here...")

    with convo:
        if user_prompt:

                #Display User Message
                with st.chat_message("user"):
                    st.markdown(user_prompt)
                
                #Store the User Message for Context
                st.session_state.messages.append({"role": "user", "content": user_prompt})

                #Display the Response
                with st.chat_message("assistant"):
                    with st.spinner("Generating Response..."):
                        response = generate_response(user_prompt,st.session_state.messages)
                        placeholder = st.empty()
                        if language == 'English':
                            placeholder.markdown(response)
                        else:
                            translated = hindi(response)
                            placeholder.markdown(translated[0]['translation_text'])
                            
                #Store the Response for Context
                st.session_state.messages.append({"role":'assistant',"content":response})