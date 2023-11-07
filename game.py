import erniebot
with open ('token','r',encoding='utf-8') as f:
    d = f.readlines()
erniebot.api_type = eval(d[0])
erniebot.access_token =  eval(d[1])
init_message = '''
现在，让我们来玩一个情景推理游戏，叫做海龟汤，你来充当游戏的主持人，我是玩家。
海龟汤的规则是这样的：你提出一个难以理解的事件，玩家可以提出任何问题以试图缩小范围并找出事件背后真正的原因，但出题者仅能以“是”、“不是”或“没有关系（与事件无关）”来回答问题。  
以下是一个例子：
谜面：有个女孩独自在家，陪伴她的只有爱犬，半夜她听到了滴水声，地于是把手放到了床边，让爱犬舔了她的手，第二天，狗死了。请问发生什么事？
玩家问主持人：有人进来把狗杀死了？主持人答：是的
玩家问主持人：并不是狗舔了她的手，对吗？主持人答：对，不是她的狗
玩家问主持人：陌生人是小偷吗？主持人答：是的
玩家问主持人：是这个陌生人舔了她的手吗？主持人答：是的
谜底：有一个小偷潜入她的家中，把狗杀死吊在天花板上.滴水声是狗在滴血，舔女孩手的也不是她的狗，而是那个人  
现在，请你作为主持人构思故事。这个故事可以包含悬疑、推理、惊悚、恐怖等元素，但总体上要符合现实生活的逻辑。把这个故事转换成一个表面上令人费解的情景作为谜面。让我来问你问题猜测谜底。
如果你完全理解了规则并且已经想好了谜题，请扮演主持人，对我说：开始游戏，然后把谜面告诉我，接下来让我来问你问题猜测谜底，暂时不要把谜底告诉我。
注意：你要扮演主持人的角色。你不需要生成问题。你需要生成谜面，让我扮演玩家的角色来提问
'''


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
        self.dialogue_pure_text = [['开始游戏',None]]
        self.rounds = 10
        
        
        
    def send_message(self,msg:str) -> dict:
        '''
        send message to erniebot
        msg: message to send, str
        return: sent message and response from erniebot, two dicts, {'role': 'user', 'content': str},{'role': 'assistant', 'content': str}
        '''
        new_msg = {'role': 'user', 'content': msg}
        self.dialogues.append(new_msg)
        response = erniebot.ChatCompletion.create(
            model='ernie-bot',
            messages=self.dialogues)
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
        _,is_end = self.send_message('玩家是否猜到了故事的真相？仅以“是”或“不是”回答，不要给出其他信息。你的回答应该是“是”或“不是”或者“无法判断”')
        print(_,is_end)
        return is_end
    
    def check_bad_story(self,story:str) -> bool:
        '''
        check if story is bad, if bad, return True
        '''
        if '玩家问主持人' in story:
            return True
        else:
            return False
        
        
        
    def start_game(self) -> list:
        '''
        start game, send init_message to erniebot, set status to 'in_process', set first dialouge_pure_text to '开始游戏' to hide initial prompt
        return: dialogue_pure_text
        '''
        
        self.status = 'in_process'
        init_msg = init_message
        _,init_response = self.send_message(init_msg)
        while self.check_bad_story(init_response['content']):
            self.dialogues = []
            _,init_response = self.send_message(init_msg)
        self.add_to_dialogue(init_response)
        self.dialogue_pure_text[0][0] = '开始游戏'
        return self.dialogue_pure_text  
        
    def step(self,msg:str) :
        '''
        go one step in game, send message(user question) to erniebot, ask if game is end, if end, set status to 'end' 
        return dialogue_pure_text
        '''
        question,response = self.send_message(msg)
        self.add_to_dialogue(question)
        self.add_to_dialogue(response)
        
        self.rounds -= 1
        
        is_end = self.ask_if_end()['content']
        
        
        
        if is_end == 'True':
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
            question,response = self.send_message('我猜不出故事的真相，我认输，请你告诉我故事的真相。')
            #self.add_to_dialogue(question)
            self.add_to_dialogue(response)
            self.dialogue_pure_text.append([None,'很遗憾，你没有提问机会了，可以按下重置按钮，然后重新开始游戏'])
            
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
    