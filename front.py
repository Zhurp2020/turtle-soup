import gradio as gr
import game

Game = game.game()


def clear_input():
    return ''
def push_to_chatbot(msg,history):
    history.append([msg,'...'])
    return history
def disable_element(element):
    return {e:type(e)(interactive=False) for e in element}
def check_remain_rounds(elements):
    if Game.rounds == 0:
        return disable_element(elements)
    else:
        return enable_element(elements)
def enable_element(element):
    return {e:type(e)(interactive=True) for e in element}

with gr.Blocks() as demo:
    title = gr.Markdown('# 海龟汤')
    
    description = gr.Markdown('''海龟汤的规则是这样的：出题人提出一个难以理解的事件，玩家可以提出任何问题以试图缩小范围并找出事件背后真正的原因，但出题者仅能以“是”、“不是”或“没有关系（与事件无关）”来回答问题。   
    如果你不知道如何获得API Token 可以[点击这里](https://aistudio.baidu.com/index/accessToken)''')

    
    with gr.Row():
        token_input = gr.Textbox(placeholder='输入你的API Token，按回车确认',scale=4)
        
        api_btn = gr.Button('确认',variant='primary',scale=1,size='sm')
        
        token_input.submit(disable_element,inputs={token_input,api_btn},outputs=[token_input,api_btn]).then(Game.set_api_token,inputs=token_input).then(enable_element,inputs={token_input,api_btn},outputs=[token_input,api_btn])
        
        api_btn.click(disable_element,inputs={token_input,api_btn},outputs=[token_input,api_btn]).then(Game.set_api_token,inputs=token_input).then(enable_element,inputs={token_input,api_btn},outputs=[token_input,api_btn])

    

    with gr.Row():
        top_p_slide = gr.Slider(minimum=0,maximum=1,step=0.01,value=0.8,label='top_p')
        temp_slide = gr.Slider(minimum=0.01,maximum=1,step=0.01,value=0.95,label='temperature')

        
        top_p_slide.change(Game.set_parameters,inputs=[top_p_slide,temp_slide])
        temp_slide.change(Game.set_parameters,inputs=[top_p_slide,temp_slide])
    
    chatbot = gr.Chatbot()
    
    with gr.Row():
        msg_input = gr.Textbox(placeholder='输入你的问题，按回车发送',scale=4)
        
        send_btn = gr.Button('发送',variant='primary',scale=1,size='sm')
    
    with gr.Row():
        style_choose = gr.Dropdown(choices=['悬疑','恐怖','搞笑','爱情','现实','离谱','超自然','科幻','历史','友情'],value='悬疑',multiselect=True, max_choices=3,label='选择故事风格',allow_custom_value=True)
        
        start = gr.Button('开始游戏')
        start.click(disable_element,inputs={start,style_choose},outputs=[start,style_choose]).then(Game.start_game,inputs =style_choose ,outputs=chatbot,show_progress='full')
        
        clear = gr.ClearButton([msg_input, chatbot],value='重置游戏',variant='stop')
        clear.click(Game.reset_game).then(enable_element,inputs={start,style_choose},outputs=[start,style_choose])
        
        
        rounds = gr.Label('剩余回合数：10')
    
        
    send_btn.click(disable_element,inputs={send_btn,msg_input},outputs=[send_btn,msg_input]).then(push_to_chatbot,inputs=[msg_input,chatbot],outputs=chatbot,queue=False).then(Game.step, inputs=msg_input, outputs=chatbot,show_progress='full').then(clear_input,outputs=msg_input).then(check_remain_rounds,inputs={send_btn,msg_input},outputs=[send_btn,msg_input]).then(Game.get_rounds,outputs=rounds)
    

    msg_input.submit(disable_element,inputs={send_btn,msg_input},outputs=[send_btn,msg_input]).then(push_to_chatbot,inputs=[msg_input,chatbot],outputs=chatbot).then(Game.step, inputs=msg_input, outputs=chatbot,show_progress='full').then(clear_input,outputs=msg_input).then(check_remain_rounds,inputs={send_btn,msg_input},outputs=[send_btn,msg_input]).then(Game.get_rounds,outputs=rounds)
        
    

demo.launch()
