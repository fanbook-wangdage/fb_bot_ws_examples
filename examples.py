import requests#http请求
import json#json数据处理
import traceback#错误捕获
import time#延时
import websocket#ws接口链接
import base64#请求体编码
import threading
from pygments import highlight#高亮
from pygments.lexers import JsonLexer#高亮
from pygments.formatters import TerminalFormatter#高亮
from colorama import init, Fore, Back, Style#高亮

lingpai='01a5edd683329aa483f5e3652d5f3dec53b8c01f98d20700ae4023c4ef59703abd892f16c7fd2ea9a1701293ada379d1'#bot的token
bot_id='463988665363562782'#bot的id
websocket_url='wss://gateway-bot.fanbook.mobi/websocket'#websocket主机
requests_url='https://a1.fanbook.mobi/api/bot/'#fb bot api主机
post_headers={'Content-Type':'application/json'}#post请求头

init(autoreset=True)    #  初始化，并且设置颜色设置自动恢复
def addmsg(msg, color="white"):#终端彩色提示信息
    if color == "white":#默认
        print(msg)
    elif color == "red":#错误文本
        print("\033[31m" + msg + "\033[39m")
    elif color == "yellow":#警告文本
        print("\033[33m" + msg + "\033[39m")
    elif color == "green":#成功文本
        print("\033[32m" + msg + "\033[39m")
    elif color == "aqua":#绿底提示文本
        print("\033[36m" + msg + "\033[39m")

def colorprint(smg2,pcolor):#拓展的终端颜色（需要装colorama）
    if pcolor=='red':#红字
      print(Fore.RED + smg2)
    elif pcolor=='bandg':#蓝字
      print(Back.GREEN + smg2)
    elif pcolor=='d':
      print(Style.DIM + smg2)
    # 如果未设置autoreset=True，需要使用如下代码重置终端颜色为初始设置
    #print(Fore.RESET + Back.RESET + Style.RESET_ALL)  autoreset=True
    
def colorize_json(smg2,pcolor=''):#格式化并高亮json字符串
    json_data=smg2
    try:
        parsed_json = json.loads(json_data)  # 解析JSON数据
        formatted_json = json.dumps(parsed_json, indent=4)  # 格式化JSON数据

        # 使用Pygments库进行语法高亮
        colored_json = highlight(formatted_json, JsonLexer(), TerminalFormatter())

        print(colored_json)
    except json.JSONDecodeError as e:#如果解析失败，则直接输出原始字符串
        print(json_data)

false=False
def on_message(ws, message):#当收到消息
    # 处理接收到的消息
    addmsg('收到消息',color='green')
    colorize_json(message)#格式化并高亮显示json字符串
    message=json.loads(message)#将json字符串转换为python对象
    #以下代码可以自行修改
    if message["action"] =="push":#如果是推送消息（忽略心跳消息）
        if message["data"]["author"]["bot"] == false:#如果不是机器人发送的消息（忽略机器人消息）
            content = json.loads(message["data"]["content"])#获取消息内容
            if "${@!"+bot_id+"}" in content['text']:#获取消息内容里面的纯文本内容，并判断有没有@该机器人（如果不是纯文本或者是其他消息会报错，不触发请查看bot id是否填写正确）
                print(content['text'])#输出全部消息
                print(content['text'][23:])#输出去掉@以后的消息
                # 在这里添加你希望执行的操作
                
def on_error(ws, error):
    # 处理错误
    addmsg("发生错误:"+str(error),color='red')
def on_close(ws):
    # 连接关闭时的操作
    addmsg("连接已关闭",color='red')
def on_open(ws):
    # 连接建立时的操作
    addmsg("连接已建立",color='green')
    # 发送心跳包
    def send_ping():
        print('发送：{"type":"ping"}')
        ws.send('{"type":"ping"}')
    send_ping()  # 发送第一个心跳包
    # 定时发送心跳包
# 替换成用户输入的BOT令牌
lingpai = lingpai
url = requests_url+f"{lingpai}/getMe"
# 发送HTTP请求获取基本信息
response = requests.get(url)
data = response.json()
def send_data_thread():
    while True:
        # 在这里编写需要发送的数据
        time.sleep(25)
        ws.send('{"type":"ping"}')
        addmsg('发送心跳包：{"type":"ping"}',color='green')
if response.ok and data.get("ok"):
    user_token = data["result"]["user_token"]#获取user token以建立连接
    device_id = "your_device_id"
    version_number = "1.6.60"
    #拼接base64字符串
    super_str = base64.b64encode(json.dumps({
        "platform": "bot",
        "version": version_number,
        "channel": "office",
        "device_id": device_id,
        "build_number": "1"
    }).encode('utf-8')).decode('utf-8')
    ws_url = websocket_url+f"?id={user_token}&dId={device_id}&v={version_number}&x-super-properties={super_str}"#准备url
    threading.Thread(target=send_data_thread, daemon=True).start()#启动定时发送心跳包的线程
    # 建立WebSocket连接
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(ws_url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
else:
    addmsg("无法获取BOT基本信息，请检查令牌是否正确。",color='red')
