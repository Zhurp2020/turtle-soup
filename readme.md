# turtle soup
## known issues
+ 模型抽风(Resolved with rule matching at alpha 1.1)
+ 判断游戏结束(Partly resolved)
### Roadmap
+ fix bugs
+ 美化页面
+ 增加功能：玩家可以选择故事的风格
+ 优化玩家体验
## Update log
### V1.1 
+ 增加了显示剩余轮数的功能（untested!）,10轮未答出判输
+ 增加了判断游戏是否结束的功能（untested!）
+ 通过规则，让模型重新生成失败的故事
+ 完善后端接口和注释
### V1.2 
+ 修复了重置游戏后会报错的bug
+ 当没有剩余提问之后，现在游戏可以正常结束并且告诉玩家真相了。