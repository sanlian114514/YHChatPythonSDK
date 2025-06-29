'''
Date: 2023-03-11 08:57:22
LastEditTime: 2025-06-29 13:41 by sanlian114514

Copyright (c) 2023 by S-i-l-v-e-t, All Rights Reserved. 
'''
import sys
sys.path.append('..')

from YHlib import setToken,onMessage
setToken("XXXXXXXX")

@onMessage
def onMsgRecv(ctx):
    # 打印收到的消息文本
    print(ctx["msg"])

if __name__ == "__main__":
    runBot()
