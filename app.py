# imports
import gradio as gr
import time
from vertexai.preview.language_models import TextGenerationModel
from vertexai.preview.language_models import ChatModel
from vertexai.preview.language_models import InputOutputTextPair

# Initialize PaLM Chatbot
def llm_chatbot(foundational_model, context_for_model):
    chat_model = ChatModel.from_pretrained(foundational_model)
    chat = chat_model.start_chat(context=context_for_model)
    return chat
# Define model and context
llm_chatbot = llm_chatbot('chat-bison@001', 'Your name is Ace. You are a friendly and helpful personal assistant that provides factual answers.')

# Build App
with gr.Blocks(theme=gr.themes.Default(text_size='lg')) as demo:
    with gr.Row():
        # Introduction
        gr.Markdown(
        '''
        # Mirage - Ace
        ## Your personal AI assistant, ready to ace any task
        Powered by PaLM 2, a large language model from Google AI.
        <br>
        Start chatting with your helpful assistant below!
        '''
        )
        gr.Image(value='Mirage Logo.png', height=200, width=200, show_label=False)

    # UI User input
    msg = gr.Textbox(lines=3,
        label='Your Message',
        info='"Shift"+"Enter" to send, "Enter" for new line.')
    # UI Send message button
    send_message = gr.Button('Send Message', size='lg')
    # UI Chatbot and chat history
    chatbot = gr.Chatbot().style(height=500, show_label=False)
    # UI Sliders to tune model params
    temperature = gr.Slider(0, 1, value=0.2, step=0.1,
        label='Temperature', 
        info='Lower temperatures are good for prompts that require a more deterministic and less open-ended or creative response, while higher temperatures can lead to more diverse or creative results. '
        ) 
    max_output_tokens = gr.Slider(128, 1024, value=128, step=128,
        label='Max Output Tokens',
        info='Maximum number of tokens that can be generated in the response.'
        )
    top_p = gr.Slider(0, 1, value=0.9, step=0.1,
        label='Top P',
        info='Specify a lower value for less random responses and a higher value for more random responses.'
        )
    top_k = gr.Slider(1, 40, value=30, step=1,
        label='Top K',
        info='Enter a lower value for less random responses and a higher value for more random responses.'
        )
    speed = gr.Slider(0.005, 0.05, value=0.0025, step=0.005, 
        label='Speed',
        info='Enter a lower value for slower streaming of responses and a higher value for faster streaming of resposnes.'
        )
    # UI reset and clear button
    clear_chat = gr.Button('Clear and Reset', size='sm')
    # Session state
    state = gr.State()

    # Function to call user message and chat history
    def user(user_message, history):
        return "", history + [[user_message, None]]

    # Function to call model and chat history
    def bot(history, temperature, max_output_tokens, top_p, top_k, speed):
        # Store param arguments as dictionary 
        llm_parameters = {
        'temperature': temperature,
        'max_output_tokens': max_output_tokens, 
        'top_p': top_p,
        'top_k': top_k,
        }
        # Get last user message
        user_message = history[-1][0]
        # Invoke model
        bot_message = llm_chatbot.send_message(user_message, **llm_parameters).text
        # Set last message in chat history as blank to prepare for response
        history[-1][1] = ""
        # Stream model response
        for character in bot_message:
            history[-1][1] += character
            # Adjust the speed of stream
            time.sleep(speed)
            yield history

    # User message activates a chain of functions
    msg.submit(fn=user, inputs=[msg, chatbot], outputs=[msg, chatbot], queue=False).then(
        fn=bot, inputs=[chatbot, temperature, max_output_tokens, top_p, top_k, speed], outputs=chatbot
        )
    send_message.click(fn=user, inputs=[msg, chatbot], outputs=[msg, chatbot], queue=False).then(
        fn=bot, inputs=[chatbot, temperature, max_output_tokens, top_p, top_k, speed], outputs=chatbot
        )
    
    # Reset chatbot on click of 'clear_chat' button
    clear_chat.click(lambda: None, None, chatbot, queue=False)

# Launch app
demo.queue()
demo.launch(server_name="0.0.0.0", server_port=7860)