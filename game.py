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
'''


class game(object):
    def __init__(self) -> None:
        self.status = None
        self.dialogues = []
        self.dialogue_pure_text = []
        
    def send_message(self,msg:str):
        new_msg = {'role': 'user', 'content': msg}
        self.dialogues.append(new_msg)
        response = erniebot.ChatCompletion.create(
            model='ernie-bot',
            messages=self.dialogues)
        result_msg = {'role': 'assistant', 'content': response.result}
        self.dialogues.append(result_msg)
        msg_pure_text=[msg,result_msg['content']]
        self.dialogue_pure_text.append(msg_pure_text)
        
    def start_game(self):
        self.status = 'in_process'
        init_msg = init_message
        self.send_message(init_msg)
        self.dialogue_pure_text[0][0] = '开始游戏'
        return self.dialogue_pure_text  
    def step(self,msg:str) :
        self.send_message(msg)
        return self.dialogue_pure_text 
    def end_game(self):
        self.dialogues = []
        self.dialogue_pure_text = []
        self.status = None