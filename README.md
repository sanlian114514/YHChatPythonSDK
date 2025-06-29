# YHChatPythonSDK  
# 原作者:@S-i-l-v-e-t (大抵是不维护了)
## 原SDK的魔改版

此 SDK 适用于 Python3.7 及以上版本。  
使用此 SDK 可以构建您的云湖机器人，能让您以非常便捷的方式和云湖服务进行交互。
修复/优化/添加:
- 仅留下了多线程版本
- 添加日志支持
- 修复了“关注和取关消息时报错”的bug
- 移除了runBot的token参数
- 添加了看板设置/取消功能
- 添加了撤回消息/消息列表功能
- 添加了机器人设置事件接收器
- 优化部分过时和繁杂代码
- ...

## 依赖:
`pip install bottle requests`  

## 使用方法：
**在一切开始之前，请*确保*你的订阅链接设置为`http://ip:port/sub`**  
**以及确保开启需使用的*事件订阅*开关**

## 消息接收装饰器:
要令一个函数进行消息接收，请引用本SDK并使用`@onMessage`装饰器  
要令一个函数进行非云湖请求接收，请引用本SDK并使用`@onOtherMessage`装饰器  
要接收指令消息，请使用`@onCommand(cmd='指令名')`装饰器  
要接收按钮响应，请使用`@onButtonPressed(cmd='按钮值')`装饰器  
要接收机器人设置消息，请使用`@onSetting`装饰器  
要接收关注消息，请使用`@onFollowed`装饰器  
要接收取关消息，请使用`@onUnfollowed`装饰器  
要接收入群消息，请使用`@onJoin`装饰器  
要接收退群消息，请使用`@onLeave`装饰器  
例子:
~~~Python
from YHlib import onMessage,runBot
setToken("xxxxxxxxxx")
@onMessage
def onRecvMsg(ctx):
    print(ctx)
runBot(7888)
~~~

## 功能函数:
### 要发送消息，请使用`sendMsg()`函数
#### sendMsg参数:
recvId :String 接收者id  
recvType :String 接收者类型,取值:"group";"user"
contentType :String 消息类型,取值:"text";"image";"markdown";"file";"html"
content :String 消息正文，注意：这只在text、markdown和HTML类型下有效
Key :String image\video\file类型时的上传密钥,详情见[官方文档](https://www.yhchat.com/document/400-410)
buttons :List 按钮，使用方法见[官方文档](https://www.yhchat.com/document/400-410) 
*附注:按钮只需单层列表*  
*汇报按钮的value值需要写在对应函数装饰器中*  
例子:
~~~Python
from YHlib import setToken,sendMsg
setToken("xxxxxx")
sendMsg("653505810","group","text","HelloWorld")
~~~
### 要编辑已发送消息，请使用`editMsg`函数  
#### editMsg参数:  
msgId :String 要编辑的消息id  
其余参数同sendMsg  
例子:  
~~~Python
from YHlib import setToken,editMsg
setToken(token="xxx")
editMsg(msgId='xxxxx',"653505810","group","text","HaveANiceDay")
~~~
