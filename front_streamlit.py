import streamlit as st
import game
import time



RULE_MSG = '''海龟汤是一种文字推理游戏，在这个游戏中，你会发现自己像是在一片迷雾中探索，寻找那些隐藏在表面下的真相。这个游戏的规则其实非常简单，但却充满了乐趣和挑战。

首先，出题者会提出一个看似简单却又难以理解的事件，这就是我们的“汤面”。然后，参与猜题的玩家可以提出任何问题，试图缩小范围并找出事件背后真正的原因。但是，出题者只能用“是”，“不是”，“是也不是”，或者“不重要”来回答。

听起来很简单，对吧？但别小看这个游戏，它可是会考验你的脑洞和发散思维的。你需要善用发问，而不是冥思苦想¹。这个游戏本质上是一个回合式的答复游戏，而并不是需要冥思苦想的猜谜游戏。通过一系列的问答，你需要根据出题人的回答组织信息，获取线索，还原事件过程¹。问题个数不受限制，这个过程就是考验脑洞的时刻！

所以，如果你觉得自己是个脑洞大开的人，或者你想挑战一下自己的推理能力，那就快来试试海龟汤吧！你会发现，每一次成功解开一个谜团，都会带给你无比的成就感和乐趣。'''



st.set_page_config(page_title='文心海龟汤',page_icon='🐢',layout='wide',initial_sidebar_state='auto')

def hint_state_to_sent() -> None:
    st.session_state['hint_state'] = 'sent'

def token_state_to_checking() -> None:
    '''
    set token state to checking
    '''
    st.session_state['token'] = 'checking'

def game_state_to_start() -> None:
    '''
    set game state to start
    '''
    st.session_state['game_state'] = 'start'

def question_state_to_sent():
    '''
    go one step
    '''
    if st.session_state.get('question_input') != None:
        st.session_state['question_state'] = 'sent'

def reset_game() -> None:
    '''
    reset game, clear game state and game object
    '''
    st.session_state['game_state'] = None
    st.session_state['game_object'] = None
    st.session_state['question_state'] = None
    st.session_state['question_input'] = None



def display_token_message() -> None:
    '''
    display token message   \n
    if token is checking, check token, if token is invalid, display warning \n 
    if token is None, display info
    '''
    token_state = st.session_state.get('token')
    if token_state =='checking':
        with st.spinner('正在验证Access Token...'):
            token_is_valid = game.check_api_token(st.session_state.get('token_input'))
        if not token_is_valid:
            st.warning('您的Access toke不正确。如果你不知道如何获得Access Token 可以[点击这里](https://aistudio.baidu.com/index/accessToken)')
            st.session_state['token'] = 'Wrong'
        else:
            st.session_state['token'] = 'Valid'
    elif token_state == None:
        st.info('在开始游戏前，您需要在左侧的侧边栏中输入您的Access Token，如果您不知道如何获得Access Token 可以[点击这里](https://aistudio.baidu.com/index/accessToken)')

def clear_start_game() -> bool:
    ''' 
    check if start game button should be enabled     \n  
    if game has started (game state is start), return False \n
    if game object exists (is not None) and game has started (status is not None), return False  \n
    else if token is valid, return True, if token is invalid, return False
    '''
    if st.session_state.get('game_state') == 'start':
        return False
    if (Game := st.session_state.get('game_object')) is not None:
        if Game.status is not None:
            return False
    else:
        if st.session_state.get('token') == 'Valid':
            return True
        else:
            return False

def start_game() -> None:
    '''
    initialize game object and start games
    '''
    if st.session_state.get('game_state') == 'start':
        with st.spinner('正在生成故事...'):
            Game = game.game()
            Game.start_game(st.session_state.get('story_style'))
            st.session_state['game_object'] = Game
            st.session_state['game_state'] = 'started'
            
def create_new_sys_msg() -> None:
    '''
    display new message from game \n 
    if game is lost, display lose message \n
    if game is win, display win message \n
    else, display normal message
    '''
    message_placeholder = st.empty()
    with st.spinner('文心思考中...'):
        st.session_state.get('game_object').step(st.session_state.get('question_input'))
    res = st.session_state.get('game_object').get_dialogue_pure_text()[-1][1]
    if res.startswith('很遗憾，你没有提问'):
        res = st.session_state.get('game_object').get_dialogue_pure_text()[-3][1]
    elif res.startswith('恭喜你，你赢了'):
        res = st.session_state.get('game_object').get_dialogue_pure_text()[-2][1]
    full_res = ''
    for char in res:
        full_res += char + ""
        time.sleep(0.05)
        message_placeholder.markdown(full_res + "▌")
    message_placeholder.markdown(full_res)

def set_model_para() -> None:
    if st.session_state.get('game_object')!= None:
        st.session_state['game_object'].set_parameters(top_p=st.session_state['top_p'],temperature=st.session_state['temp'])

def display_toast()-> None:
    if st.session_state.get('question_state') == None:
        rounds = st.session_state.get('game_object').rounds
        if rounds== 7 :
            st.info('你还有7次提问机会 \n 可以点击上方按钮获得更多线索')
        # st.session_state['hint_1'] ='sent'
        if 2<= rounds <= 3:
            st.warning('你还有{}次提问机会'.format(rounds))
        elif rounds == 1:
            st.error('你只有1次提问机会')



with st.sidebar:
    
    st.write('# 这是什么？🐢')
    st.write('这是一个基于文心一言的海龟汤推理游戏。')
    with st.expander('''点击展开规则介绍'''):
        st.write(RULE_MSG)
        
    st.write('## 设置Access token')
    access_token = st.text_input('请输入您的Access Token',placeholder='Access token',on_change=token_state_to_checking,key='token_input')
    
    st.write('## 设置模型参数')
    st.write('这两个参数用于控制模型的输出采样策略和多样性，一般调整一个即可。具体可参见[这里](https://aistudio.baidu.com/projectdetail/6779597)')
    top_p_slide = st.slider('top_p',min_value=0.0,max_value=1.0,step=0.01,value=0.8,key='top_p',on_change=set_model_para)
    temp_slide = st.slider('temperature',min_value=0.01,max_value=1.0,step=0.01,value=0.95,key='temp',on_change=set_model_para)

        
    
st.title('【Hackathon 5th】海龟汤——逆向推理文字游戏🐢')

display_token_message()

style_choose = st.multiselect('选择故事风格',['悬疑','恐怖','搞笑','爱情','现实','离谱','超自然','科幻','历史','友情'],default='悬疑',max_selections=3,help='最多选择三个故事风格',label_visibility='visible',placeholder='请选择故事风格，最多选择三个',key='story_style')



col1,col2,col3,col4,_ = st.columns([1,1,1,1,1])

with col1:
    
    start = st.button(label='开始游戏',use_container_width= True, on_click=game_state_to_start,disabled=not(clear_start_game()))
    
if st.session_state.get('game_state') in ['start','started']:
    with col2:
        reset = st.button(label='重置游戏',type='primary',use_container_width= True,on_click=reset_game)

if st.session_state.get('game_state') in ['started'] and 0 <  st.session_state.get('game_object').rounds <= 7:
    with col3:
        hint = st.button(label='给点提示',use_container_width= True,on_click=hint_state_to_sent)
if st.session_state.get('hint_state') == 'sent':
    with col4:
        with st.spinner('寻找线索中...'):
            st.session_state.get('game_object').ask_for_hint()
    st.session_state['hint_state'] = None

        
        
start_game()
    
if st.session_state.get('game_state') == 'started': 
    #st.write('#### 剩余回合数：{}'.format(st.session_state.get('game_object').rounds))
    
    for messages in st.session_state['game_object'].get_dialogue_pure_text():
        if messages[0]:
            with st.chat_message('user'):
                st.markdown(messages[0])
        if messages[1]:
            with st.chat_message('assistant',avatar='🐢'):
                st.markdown(messages[1])

    display_toast()
    question_input= st.chat_input("输入问题，按回车发送",on_submit=question_state_to_sent,key='question_input',disabled=st.session_state.get('game_object').status in ['win','lose'] or st.session_state.get('question_state') == 'sent')

    if st.session_state.get('question_input') :
        with st.chat_message("user"):
            st.markdown(st.session_state.get('question_input'))
        
        
        with st.chat_message("assistant",avatar='🐢'):
            create_new_sys_msg()
        st.session_state['question_state'] = None
        
        st.rerun()
        
        
    
    if st.session_state.get('game_object').status == 'win':
        st.balloons()

    elif st.session_state.get('game_object').status == 'lose':
        st.snow()



