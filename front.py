import gradio as gr
import game

Game = game.game()

def clear_input():
    return ''
def push_to_chatbot(msg,history):
    return history.append[msg,None]
def disable_element(element):
    return {e:type(e)(interactive=False) for e in element}
def enable_element(element):
    return {e:type(e)(interactive=True) for e in element}

with gr.Blocks() as demo:
    title = gr.Markdown('# 海龟汤')
    
    description = gr.Markdown('海龟汤的规则是这样的：出题人提出一个难以理解的事件，玩家可以提出任何问题以试图缩小范围并找出事件背后真正的原因，但出题者仅能以“是”、“不是”或“没有关系（与事件无关）”来回答问题。')
    
    chatbot = gr.Chatbot()
    
    
    with gr.Row():
        msg_input = gr.Textbox(placeholder='Enter your question, press to enter',scale=4)
        
        send_btn = gr.Button('send',variant='primary',scale=1,size='sm')

        send_btn.click(disable_element,inputs={send_btn,msg_input},outputs=[send_btn,msg_input]).then(push_to_chatbot,inputs=[msg_input,chatbot],outputs=chatbot).then(Game.step, inputs=msg_input, outputs=chatbot,show_progress='full').then(clear_input,outputs=msg_input).then(enable_element,inputs={send_btn,msg_input},outputs=[send_btn,msg_input])
    
        #msg_input.submit(conversation,inputs=msg_input,outputs=chatbot)
        msg_input.submit(disable_element,inputs={send_btn,msg_input},outputs=[send_btn,msg_input]).then(push_to_chatbot,inputs=[msg_input,chatbot],outputs=chatbot).then(Game.step, inputs=msg_input, outputs=chatbot,show_progress='full').then(clear_input,outputs=msg_input).then(enable_element,inputs={send_btn,msg_input},outputs=[send_btn,msg_input])
    
    with gr.Row():
        start = gr.Button('Start')
        start.click(disable_element,inputs={start},outputs=[start]).then(Game.start_game,outputs=chatbot,show_progress='full')
        
        clear = gr.ClearButton([msg_input, chatbot],variant='stop')
        clear.click(Game.end_game).then(enable_element,inputs={start},outputs=[start])
    
    
        

demo.launch()