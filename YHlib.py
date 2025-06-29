from bottle import route, request, run
import logging,traceback
import requests,json,threading,time
onCmdDict = {}
btnEventDict = {}
onMsgList = []
onOtherMsgList = []
onFollowedList = []
onUnfollowedList = []
onJoinList = []
onLeaveList = []
onSettingList = []
rs = requests.Session()
rs.headers["referer"] = "http://myapp.jwznb.com"

formatter = logging.Formatter("[%(asctime)s][%(funcName)s]\n    [%(levelname)s] %(message)s")

logger = logging.getLogger("YHlib")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

file_handler = logging.FileHandler("YHlib.log", encoding="utf-8")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

def debug_log(console=True, file=False):
    logger.handlers.clear()
    if console:
        logger.addHandler(console_handler)
        if file:
            logger.addHandler(file_handler)

def exceptionHook(func):
    def wrapper(*args, **kwds):
        __name__= func.__name__
        try:
            return func(*args, **kwds)
        except Exception as e:
            logger.error(f"出现错误: {traceback.format_exc()}")
    return wrapper

class ThreadCtrl:
    threads = []
    lock = threading.Lock()

    def __init__(self, func=lambda x="NoFunc": print(x), *args, init=False, **kwds):
        if init:
            ThreadCtrl.daemon = threading.Thread(
                target=ThreadCtrl.checker, daemon=True)
            ThreadCtrl.daemon.start()
        else:
            with ThreadCtrl.lock:
                ThreadCtrl.threads.append(self)
                self.func = func
                self.args = args
                self.kwds = kwds
                self.initThread()

    def initThread(self):
        self._thread = threading.Thread(
            target=self.func, args=self.args, kwargs=self.kwds)
        self._thread.start()

    def getstat(self):
        return self._thread.is_alive()

    @staticmethod
    def checker():
        while True:
            time.sleep(1)  # 防止 CPU 100% 占用
            with ThreadCtrl.lock:
                ThreadCtrl.threads = [
                    t for t in ThreadCtrl.threads if t.getstat()]

def setToken(token: str):
    global tok
    tok = token
    logger.info(f"Token: {tok}")

@exceptionHook
def editMsg(msgId: str, recvId: str, recvType: str, contentType: str, content="", Key="", parentId="", buttons=False):
    data = {
        "msgId": msgId,
        "recvId": recvId,
        "recvType": recvType,
        "contentType": contentType,
        "content": {
            "text": content
        },
        "parentId": parentId
    }
    if contentType == 'image':
        data['content'] = {'imageKey': Key}
    elif contentType == 'file':
        data['content'] = {'fileKey': Key}
    elif contentType == 'video':
        data['content'] = {'videoKey': Key}
    if buttons:
        data['content']['buttons'] = [buttons]
    logger.debug(f"请求数据: {str(data)}")
    response = rs.post(
        f"https://chat-go.jwzhd.com/open-apis/v1/bot/edit?token={tok}", json=data).json()
    return response

@exceptionHook
def sendMsg(recvId: str, recvType: str, contentType: str, content="", Key="", parentId="", buttons=False):
    data = {
        "recvId": recvId,
        "recvType": recvType,
        "contentType": contentType,
        "content": {
            "text": content
        },
        "parentId": parentId
    }
    if contentType == 'image':
        data['content'] = {'imageKey': Key}
    elif contentType == 'file':
        data['content'] = {'fileKey': Key}
    elif contentType == 'video':
        data['content'] = {'videoKey': Key}
    if buttons:
        data['content']['buttons'] = [buttons]
    logger.debug(f"请求数据: {str(data)}")
    response = rs.post(
        f"https://chat-go.jwzhd.com/open-apis/v1/bot/send?token={tok}", json=data).json()
    return response["data"]

@exceptionHook
def setBoard(contentType: str, content: str, Global=False, recvId="", recvType="", expireTime=0, memberId=""):
    url = f"https://chat-go.jwzhd.com/open-apis/v1/bot/board-all?token={tok}"
    data = {
        "contentType": contentType,
        "content": content,
        "expireTime": expireTime
    }
    if not Global:
        data["chatId"] = recvId
        data["chatType"] = recvType
        data["memberId"] = memberId
        url = f"https://chat-go.jwzhd.com/open-apis/v1/bot/board?token={tok}"
    logger.debug(f"请求数据: {str(data)}")
    response = rs.post(url, json=data).json()
    return response

@exceptionHook
def dismissBoard(Global=False, recvId="", recvType=""):
    data = ""
    url = f"https://chat-go.jwzhd.com/open-apis/v1/bot/board-all-dismiss?token={tok}"
    if not Global:
        data["chatId"]=recvId,
        data["chatType"]=recvType
        url = f"https://chat-go.jwzhd.com/open-apis/v1/bot/board-dismiss?token={tok}"
    logger.debug(f"请求数据: {str(data)}")
    response = rs.post(url, json=data).json()
    return response

@exceptionHook
def recallMsg(msgId: str, recvId: str, recvType: str):
    data = {
        "msgId": msgId,
        "chatId": recvId,
        "chatType": recvType
    }
    logger.debug(f"请求数据: {str(data)}")
    response = rs.post(
        f"https://chat-go.jwzhd.com/open-apis/v1/bot/recall?token={tok}", json=data).json()
    return response

@exceptionHook
def msgList(recvId: str, recvType: str, messageId="", before=0, after=0):
    url=f"https://chat-go.jwzhd.com/open-apis/v1/bot/messages?token={tok}&chat-id={recvId}&chat-type={recvType}&message-id={messageId}&before={str(before)}&after={str(after)}"
    logger.debug(f"请求url: {url}")
    response = rs.get(url).json()
    return response

@exceptionHook
def geneBaseBox(jsons, cnt=True, set=False, btn=False):
    msgbox = {}
    msgbox["time"] = jsons["header"]["eventTime"]
    if set:
        msgbox['id'] = jsons['event']['groupId']
        msgbox['setjson'] = json.loads(jsons['event']['settingJson'])
        return msgbox
    if btn:
        msgbox["msgId"] = jsons["event"]["msgId"]
        msgbox["sender"] = jsons['event']['userId']
        msgbox["id"] = jsons["event"]["recvId"]
        msgbox["recvType"] = jsons["event"]["recvType"]
        msgbox["value"] = jsons["event"]["value"]
        return msgbox
    try:
        msgbox["type"] = jsons["event"]["chat"]["chatType"]
    except:
        msgbox["type"] = jsons["event"]["chatType"]
    if cnt:
        msgbox["contentType"] = jsons['event']['message']['contentType']
        msgbox["msgId"] = jsons["event"]["message"]["msgId"]
        if msgbox['contentType'] in ('text', 'markdown', "post", "html"):
            msgbox['msg'] = jsons["event"]["message"]["content"]["text"]
        elif msgbox['contentType'] == 'image':
            msgbox['url'] = jsons['event']['message']['content']['imageUrl']
        elif msgbox["contentType"] == "expression":
            msgbox['url'] = "https://chat-img.jwznb.com/" + \
                jsons['event']['message']['content']['imageName']
        elif msgbox['contentType'] == 'file':
            msgbox['fileName'] = jsons['event']['message']['content']['fileName']
            msgbox['url'] = "https://chat-file.jwznb.com/" + \
                jsons['event']['message']['content']['fileUrl']
        elif msgbox['contentType'] == 'form':
            msgbox['form'] = jsons['event']['message']['content']['formJson']
        msgbox['sender'] = jsons["event"]["sender"]["senderId"]
        msgbox['senderInfo'] = {'nickname': jsons['event']['sender']
                                ['senderNickname'], 'level': jsons['event']['sender']['senderUserLevel']}
    if msgbox['type'] == 'group' and cnt:
        msgbox["id"] = jsons["event"]["message"]["chatId"]
    elif msgbox['type'] == 'group':
        msgbox['id'] = jsons['event']['chatId']
        msgbox['nickname'] = jsons['event']['nickname']
        msgbox['avatar'] = jsons['event']['avatarUrl']
        msgbox['sender'] = jsons["event"]["userId"]
    elif cnt:
        msgbox["id"] = jsons["event"]["sender"]["senderId"]
    else:
        msgbox['id'] = jsons['event']['userId']
        msgbox['sender'] = jsons['event']['userId']
        msgbox['nickname'] = jsons['event']['nickname']
        msgbox['avatar'] = jsons['event']['avatarUrl']
    if msgbox['type'] == 'group':
        msgbox['recvType'] = 'group'
    elif msgbox['type'] == 'bot':
        msgbox['recvType'] = 'user'
    return msgbox

@route("/sub", method='POST')
@exceptionHook
def onRecvPost():
    logger.debug(f"""请求详细信息:
    IP:{request.remote_addr}
    UA:{request.get_header("User-Agent", "Unknown")}
    请求体:{request.body.read().decode('utf-8')}
""")
    retVal = None
    jsons = request.json
    if 'header' not in jsons:
        for func in onOtherMsgList:
            retVal = func(ctx=jsons)
            if retVal:
                return retVal
    elif jsons['header']['eventType'] == "message.receive.normal":
        logger.info("收到普通消息")
        for func in onMsgList:
            retVal = func(ctx=geneBaseBox(jsons))
            if retVal:
                return retVal
    elif jsons['header']['eventType'] == 'message.receive.instruction':
        cmd = jsons['event']['message']['commandName']
        logger.info("收到指令消息,指令名: "+cmd)
        if cmd not in onCmdDict:
            cmd=0
        retVal = onCmdDict[cmd](ctx=geneBaseBox(jsons))
        if retVal:
            return retVal
    elif jsons['header']['eventType'] == 'bot.followed':
        logger.info("收到添加机器人事件")
        for func in onFollowedList:
            retVal = func(ctx=geneBaseBox(jsons, False))
            if retVal:
                return retVal
    elif jsons['header']['eventType'] == "bot.unfollowed":
        logger.info("收到移除机器人事件")
        for func in onUnfollowedList:
            retVal = func(ctx=geneBaseBox(jsons, False))
            if retVal:
                return retVal
    elif jsons['header']['eventType'] == "group.join":
        logger.info("收到进群事件")
        for func in onJoinList:
            retVal = func(ctx=geneBaseBox(jsons, False))
            if retVal:
                return retVal
    elif jsons['header']['eventType'] == 'group.leave':
        logger.info("收到退群事件")
        for func in onLeaveList:
            retVal = func(ctx=geneBaseBox(jsons, False))
            if retVal:
                return retVal
    elif jsons['header']['eventType'] == 'bot.setting':
        logger.info("收到机器人设置事件")
        for func in onSettingList:
            retVal = func(ctx=geneBaseBox(jsons, set=True))
            if retVal:
                return retVal
    elif jsons['header']['eventType'] == 'button.report.inline':
        logger.info("收到按钮事件")
        msgbox = geneBaseBox(jsons, False, btn=True)
        try:
            value = json.loads(msgbox['value'])
            if value[0] in btnEventDict:
                retVal = btnEventDict[value[0]](ctx=msgbox)
        except:
            if msgbox['value'] in btnEventDict:
                retVal = btnEventDict[msgbox['value']](ctx=msgbox)
        if retVal:
            return retVal

class onOtherMessage:
    def __init__(self, func):
        logger.debug(f"其他请求处理器: {func.__name__}")
        global onOtherMsgList
        self.func = func
        onOtherMsgList.append(func)

    def __call__(self, *args, **kwds):
        rv = self.func(*args, **kwds)
        return rv

class onSetting:
    def __init__(self, func):
        logger.debug(f"机器人设置处理器: {func.__name__}")
        global onSettingList
        self.func = func
        onSettingList.append(func)

    def __call__(self, *args, **kwds):
        rv = self.func(*args, **kwds)
        return rv

class onLeave:
    def __init__(self, func):
        logger.debug(f"退群处理器: {func.__name__}")
        global onLeaveList
        self.func = func
        onLeaveList.append(func)

    def __call__(self, *args, **kwds):
        rv = self.func(*args, **kwds)
        return rv

class onJoin:
    def __init__(self, func):
        logger.debug(f"进群处理器: {func.__name__}")
        global onJoinList
        self.func = func
        onJoinList.append(func)

    def __call__(self, *args, **kwds):
        rv = self.func(*args, **kwds)
        return rv

class onUnfollowed:
    def __init__(self, func):
        logger.debug(f"移除机器人处理器: {func.__name__}")
        global onUnfollowedList
        self.func = func
        onUnfollowedList.append(func)

    def __call__(self, *args, **kwds):
        rv = self.func(*args, **kwds)
        return rv

class onFollowed:
    def __init__(self, func):
        logger.debug(f"添加机器人处理器: {func.__name__}")
        global onFollowedList
        self.func = func
        onFollowedList.append(func)

    def __call__(self, *args, **kwds):
        rv = self.func(*args, **kwds)
        return rv

class onMessage:
    def __init__(self, func):
        logger.debug(f"正常消息处理器: {func.__name__}")
        global onMsgList
        self.func = func
        onMsgList.append(func)

    def __call__(self, *args, **kwds):
        rv = self.func(*args, **kwds)
        return rv

def onCommand(cmd=0):
    def deco(func):
        logger.debug(f"{func.__name__} 绑定命令: {str(cmd)}")
        global onCmdDict
        if cmd not in onCmdDict:
            onCmdDict[cmd] = func

        def warpper(*args, **kwds):
            try:
                rv = func(*args, **kwds)
                return rv
            except:
                pass
        return warpper
    return deco

def onButtonPressed(value):
    def deco(func):
        logger.debug(f"{func.__name__} 绑定按钮: {value}")
        global btnEventDict
        if value not in btnEventDict:
            btnEventDict[value] = func

        def warpper(*args, **kwds):
            try:
                rv = func(*args, **kwds)
                return rv
            except:
                pass
        return warpper
    return deco

def runBot(port=7888):
    logger.info(f"运行端口: {str(port)}")
    ThreadCtrl(init=True)
    BottleThread = threading.Thread(
        run(host='0.0.0.0', port=port, loader=True, quiet=True))
    BottleThread.start()
    logger.info("已退出")
