import erniebot

init_message = '''
现在，让我们来玩一个情景推理游戏。你将扮演【主持人】，而我将扮演【玩家】。

游戏规则如下：【主持人】提出一个难以理解的情景作为谜面，而【玩家】可以通过提问来尝试缩小范围并找出事件背后的真正原因。【主持人】可以用“是”、“不是”或“没有关系（与事件无关）”来回答，并给出简短的解释。

以下是一个例子：
谜面：有个女孩独自在家，陪伴她的只有爱犬，半夜她听到了滴水声，地于是把手放到了床边，让爱犬舔了她的手，第二天，狗死了。请问发生什么事？
【玩家】问【主持人】：有人进来把狗杀死了？【主持人】答：是的
【玩家】问【主持人】：并不是狗舔了她的手，对吗？【主持人】答：对，不是她的狗
【玩家】问【主持人】：陌生人是小偷吗？【主持人】答：是的
【玩家】问【主持人】：是这个陌生人舔了她的手吗？【主持人】答：是的
【主持人】解答谜题：有一个小偷潜入她的家中，把狗杀死吊在天花板上。滴水声是狗在滴血，舔女孩手的也不是她的狗，而是那个人。

现在，作为【主持人】，请你构思一个故事作为谜面。这个故事可以包含以下元素：{}，但总体上要符合现实生活的逻辑。将这个故事转换成一个表面上令人费解的情景作为谜面。然后，对我说：“开始游戏”，并告诉我谜面。接下来，我将通过提问来猜测谜底。请不要提前告诉我谜底，我希望进行多轮对话，直到我猜出谜底。在玩家认输之后，请你告诉我谜底。

请确保你完全理解了规则，并且已经准备好了谜题。现在，你可以扮演【主持人】，对我说：“开始游戏”并告诉我谜面。

注意：你要扮演主持人的角色。你不需要生成问题。你需要生成谜面，让我扮演玩家的角色来提问。玩家的提问应该是一个一般疑问句。如果玩家的提问不是一个一般疑问句（不能用是否回答），那么请你说“无效问题”
'''

def check_api_token(token:str) -> bool:
    '''
    check if api token is valid
    token: api token, str
    return: is_valid, bool
    '''
    erniebot.api_type = 'aistudio'
    erniebot.access_token = token
    try:
        erniebot.ChatCompletion.create(
            model='ernie-bot-4',
            messages=[{'role': 'user', 'content': '你好'}])
        return True
    except:
        return False


class game(object):
    
    def __init__(self) -> None:
        ''' 
        status: current status of game, one of None, 'in_process', 'end', 'win'
        dialogues: list of dicts, full message history with erniebot [{'role': 'user', 'content': str},{'role': 'assistant', 'content': str},...]
        dialogue_pure_text: list of lists, message history that is displayed to player [[str(user),str(bot)],...]
        rounds: number of remaining rounds in game, int
        '''
        self.status = None
        self.dialogues = []
        self.dialogue_pure_text = [['开始游戏，一共有十次提问机会',None]]
        self.rounds = 10
        self.top_p = 0.8
        self.temperature = 0.95
        
        
        
    def set_api_token(self,token:str) -> None:
        '''
        set api token for erniebot
        token: api token, str
        '''
        erniebot.api_type = 'aistudio'
        erniebot.access_token = token
    
    def set_story_style(self,style:str) -> None:
        self.init_message = init_message.format(style)
        
        
    
    def set_parameters(self,top_p:float,temperature:float) -> None:
        '''
        set parameters for erniebot
        top_p: 以使生成的token从概率和恰好达到或超过top_p的token集合中采样得到。float in [0,1], default = 0.8
        temperature: 控制采样的随机性, float in (0,1.0], default = 0.95,to
        '''
        self.top_p = top_p
        self.temperature = temperature
        
        
        
    def send_message(self,msg:str,system_msg:str ='') -> dict:
        '''
        send message to erniebot
        msg: message to send, str
        system_msg: system message to send, str, default is empty
        return: sent message and response from erniebot, two dicts, {'role': 'user', 'content': str},{'role': 'assistant', 'content': str}
        '''
        new_msg = {'role': 'user', 'content': msg}
        self.dialogues.append(new_msg)
        response = erniebot.ChatCompletion.create(
            model='ernie-bot-4',
            messages=self.dialogues,
            system = system_msg,
            top_p=self.top_p,temperature=self.temperature)
        result_msg = {'role': 'assistant', 'content': response.result}
        self.dialogues.append(result_msg)
        return new_msg, result_msg
    
    def add_to_dialogue(self,msg:dict) -> None:
        '''
        add message to dialogue_pure_text
        msg: message to add, dict, {'role': 'user'/'assistant', 'content': str}
        '''
        if msg['role'] == 'user':
            self.dialogue_pure_text.append([msg['content'],None])
        elif msg['role'] == 'assistant':
            self.dialogue_pure_text[-1][1] = msg['content']
        
        
    def ask_if_end(self) -> bool:
        '''
        ask erniebot if game has ended
        return: is_end, bool
        '''
        _,is_end = self.send_message('玩家是否猜到了故事的真相？仅以“是”或“不是”回答，不要给出其他信息。你的回答应该是“是”或“不是”或者“无法判断”',system_msg='你是游戏的主持人。对于这个问题，你应该回答“是”或“不是”或者“无法判断”')
        #print(_,is_end)
        return is_end
    
    def check_bad_story(self,story:str) -> bool:
        '''
        check if story is bad, if bad, return True
        '''
        if '玩家问主持人' in story or '【玩家】问【主持人】' in story or '谜底是' in story:
            return True
        else:
            return False
        
        
        
    def start_game(self,style:str|list) -> list:
        '''
        start game, send init_message to erniebot, set status to 'in_process', set first dialouge_pure_text to '开始游戏' to hide initial prompt
        style: style of story, str
        return: dialogue_pure_text
        '''
        
        self.status = 'in_process'
        if style == None:
            style = '悬疑'
        if type(style) == list:
            style = '、'.join(style)
        self.set_story_style(style)
        init_msg = self.init_message
        _,init_response = self.send_message(init_msg,'你需要扮演游戏的主持人，告诉玩家谜面。')
        while self.check_bad_story(init_response['content']):
            self.dialogues = []
            _,init_response = self.send_message(init_msg)
        self.add_to_dialogue(init_response)
        self.dialogue_pure_text[0][0] = '开始游戏，你一共有10次提问机会！'
        return self.dialogue_pure_text  
        
    def step(self,msg:str) :
        '''
        go one step in game, send message(user question) to erniebot, ask if game is end, if end, set status to 'end' 
        return dialogue_pure_text
        '''
        question,response = self.send_message(msg,system_msg='如果玩家问的问题不是一个一般疑问句，请说“无效问题”')
        self.add_to_dialogue(question)
        self.add_to_dialogue(response)
        
        self.rounds -= 1
        
        is_end = self.ask_if_end()['content']
        
        if is_end[0] == '是':
            self.status = 'win'
            self.end_game()
        elif self.rounds == 0:
            self.status = 'lose'
            self.end_game()

        return self.dialogue_pure_text     
        
    def end_game(self):
        if self.status =='win':
            self.dialogue_pure_text.append([None,'恭喜你，你赢了，可以按下重置按钮，然后重新开始游戏'])
        elif self.status == 'lose':
            question,response = self.send_message('我猜不出故事的真相，我认输并放弃猜测，请你告诉我故事的真相。','玩家已经认输，作为主持人请你说出谜底')
            #self.add_to_dialogue(question)
            self.dialogue_pure_text.append([None,response['content']])
            self.dialogue_pure_text.append([None,'很遗憾，你没有提问机会了，可以按下重置按钮，然后重新开始游戏'])
            
    def ask_for_hint(self):
        '''
        ask for hint, send message to erniebot, return dialogue_pure_text
        '''
        question,response = self.send_message('我想要一个提示','玩家想要一个提示，作为主持人请你给出一个提示')
        self.add_to_dialogue(question)
        self.add_to_dialogue(response)
        return self.dialogue_pure_text
            
    def reset_game(self):
        '''
        reset game, set status to None, clear dialogues, clear dialogue_pure_text, set rounds to 10
        '''
        self.status = None
        self.dialogues = []
        self.dialogue_pure_text = [['开始游戏',None]]
        self.rounds = 10
    
    
    
    def get_dialogue_pure_text(self) -> list:
        '''
        return dialogue_pure_text
        '''
        return self.dialogue_pure_text
        
    def get_status(self) -> str:
        '''
        return current status of game
        '''
        return self.status
    
    def get_rounds(self) -> int:
        '''
        return remaining rounds
        '''
        return '剩余回合数：{}'.format(self.rounds)
    
    def get_full_dialogue(self) -> list:
        return self.dialogues
    