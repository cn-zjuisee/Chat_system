import socket
import threading
import queue
import json  # json.dumps(some)打包   json.loads(some)解包
import time
import os
import os.path
import requests


def call_robot(url, apikey, msg):
    data = {
        "reqType": 0,
        "perception": {
            "inputText": {  # inputText文本信息
                "text": msg
            },
            # 用户输入图片url
            "inputImage": {  # 图片信息，后跟参数信息为url地址，string类型
                "url": "https://cn.bing.com/images/"
            },
            # 用户输入音频地址信息
            "inputMedia": {  # 音频信息，后跟参数信息为url地址，string类型
                "url": "https://www.1ting.com/"
            },
            # 客户端属性信息
            "selfInfo": {  # location 为selfInfo的参数信息，
                "location": {  # 地理位置信息
                    "city": "杭州",  # 所在城市，不允许为空
                    "province": "浙江省",  # 所在省份，允许为空
                    "street": "灵隐街道"  # 所在街道，允许为空
                }
            },
        },
        "userInfo": {  # userInfo用户参数，不允许为空
            "apiKey": "ee19328107fa41e987a42a064a68d0da",  # 你注册的apikey,机器人标识,32位
            "userId": "Brandon"  # 随便填，用户的唯一标识，长度小于等于32位
        }
    }
    headers = {'content-type': 'application/json'}  # 必须是json
    r = requests.post(url, headers=headers, data=json.dumps(data))
    return r.json()


def chatServer():
    IP = ''
    PORT = 50007

    que = queue.Queue()  # 用于存放客户端发送的信息的队列
    users = []  # 用于存放在线用户的信息  [conn, user, addr]
    lock = threading.Lock()  # 创建锁, 防止多个线程写入数据的顺序打乱

    # 用于接收所有客户端发送信息的函数
    def tcp_connect(conn, addr):
        # 连接后将用户信息添加到users列表
        user = conn.recv(1024)  # 接收用户名
        user = user.decode()
        if user == 'no':
            user = addr[0] + ':' + str(addr[1])
        users.append((conn, user, addr))
        print('新连接:', addr, ':', user, end='')  # 打印用户名
        d = onlines()  # 有新连接则刷新客户端的在线用户显示
        recv(addr, d)
        try:
            while True:
                data = conn.recv(1024)
                data = data.decode()
                recv(addr, data)  # 保存信息到队列
            conn.close()
        except:
            print(user + ' 断开连接')
            delUsers(conn, addr)  # 将断开用户移出users
            conn.close()

    # 判断断开用户在users中是第几位并移出列表, 刷新客户端的在线用户显示
    def delUsers(conn, addr):
        a = 0
        for i in users:
            if i[0] == conn:
                users.pop(a)
                print('剩余在线用户: ', end='')  # 打印剩余在线用户(conn)
                d = onlines()
                recv(addr, d)
                print(d)
                break
            a += 1

    # 将接收到的信息(ip,端口以及发送的信息)存入que队列
    def recv(addr, data):
        lock.acquire()
        try:
            que.put((addr, data))
        finally:
            lock.release()

    # 将队列que中的消息发送给所有连接到的用户
    def sendData():
        while True:
            if not que.empty():
                data = ''
                reply_text = ''
                message = que.get()  # 取出队列第一个元素
                if isinstance(message[1], str):  # 如果data是str则返回Ture
                    for i in range(len(users)):
                        #user[i][1]是用户名, users[i][2]是addr, 将message[0]改为用户名
                        for j in range(len(users)):
                            if message[0] == users[j][2]:                            
                                print('this: message is from user[{}]'.format(j))
                                if '@Robot' in message[1] and reply_text == '':
                                    
                                    msg = message[1].split(':;')[0]
                                    reply = call_robot(url,apikey,msg)
                                    reply_text = reply['results'][0]['values']['text']
                                    data = ' ' + users[j][1] + '：' + message[1] + ':;' + 'Robot：' + '@' + users[j][1] + ',' + reply_text
                                    break
                                elif '@Robot' in message[1] and (not reply_text == ''):
                                    data = ' ' + users[j][1] + '：' + message[1] + ':;' + 'Robot：' + '@' + users[j][1] + ',' + reply_text
                                else:
                                    data = ' ' + users[j][1] + '：' + message[1]
                                    break      
                        users[i][0].send(data.encode())
                data = data.split(':;')[0]
                if isinstance(message[1], list):  # 同上
                    # 如果是list则打包后直接发送  
                    data = json.dumps(message[1])
                    for i in range(len(users)):
                        users[i][0].send(data.encode())
                

    # 将在线用户存入online列表并返回
    def onlines():
        online = []
        for i in range(len(users)):
            online.append(users[i][1])
        return online
                    
    s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    s.bind( (IP, PORT) )
    s.listen(5)
    print('tcp server is running...')
    q = threading.Thread(target=sendData)
    q.start()
    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=tcp_connect, args=(conn, addr))
        t.start()
    s.close()

################################################################
def fileServer():
    first = r'.\resources'
    os.chdir(first)  # 把first设为当前工作路径
    IP = ''
    PORT = 50008
    s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    s.bind( (IP, PORT) )
    s.listen(3)

    def tcp_connect(conn, addr):
        print('Connected by: ', addr)
        
        while True:
            data = conn.recv(1024)
            data = data.decode()
            if data == 'quit':
                print('Disconnected from {0}'.format(addr))
                break
            order = data.split()[0]  # 获取动作
            recv_func(order, data)
                
        conn.close()

    # 传输当前目录列表
    def sendList():
        listdir = os.listdir(os.getcwd())
        listdir = json.dumps(listdir)
        conn.sendall(listdir.encode())

    # 发送文件函数
    def sendFile(message):
        name = message.split()[1]  #获取第二个参数(文件名)
        fileName = r'./' + name
        with open(fileName, 'rb') as f:    
            while True:
                a = f.read(1024)
                if not a:
                    break
                conn.send(a)
        time.sleep(0.1)  # 延时确保文件发送完整
        conn.send('EOF'.encode())

    # 保存上传的文件到当前工作目录
    def recvFile(message):
        name = message.split()[1] #获取文件名
        fileName = r'./' + name
        with open(fileName, 'wb') as f:
            while True:
                data = conn.recv(1024)
                if data == 'EOF'.encode():
                    break
                f.write(data)

    # 切换工作目录
    def cd(message):
        message = message.split()[1]  # 截取目录名
        # 如果是新连接或者下载上传文件后的发送则 不切换 只将当前工作目录发送过去
        if message != 'same':
            f = r'./' + message
            os.chdir(f)
        path = ''
        path = os.getcwd().split('\\')  # 当前工作目录 
        for i in range(len(path)):
            if path[i] == 'resources':
                break
        pat = ''
        for j in range(i, len(path)):
            pat = pat + path[j] + ' '
        pat = '\\'.join(pat.split())
        # 如果切换目录超出范围则退回切换前目录
        if not 'resources' in path:
            f = r'./resources'
            os.chdir(f)
            pat = 'resources'
        conn.send(pat.encode())

    # 判断输入的命令并执行对应的函数
    def recv_func(order, message):
        if order == 'get':
            return sendFile(message)
        elif order == 'put':
            return recvFile(message)
        elif order == 'dir':
            return sendList()
        elif order == 'cd':
            return cd(message)

    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=tcp_connect, args=(conn, addr))
        t.start()
    s.close()


apikey = 'ee19328107fa41e987a42a064a68d0da'
url = 'http://openapi.tuling123.com/openapi/api/v2'

#############################################################################


def pictureServer():
    IP = ''
    PORT = 50009    # 再开一个端口运行此图片缓存服务器
    s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    s.bind( (IP, PORT) )
    s.listen(5)

    def tcp_connect(conn, addr):
        while True:
            data = conn.recv(1024)
            data = data.decode()
            print('Received message from {0}: {1}'.format(addr, data))
            if data == 'quit':
                break
            order = data.split()[0]  # 获取动作
            recv_func(order, data)
        conn.close()
        print('---')
    folder = './服务端图片缓存/'    # 图片的保存文件夹
    # 发送文件函数
    def sendFile(message):
        print(message)
        name = message.split()[1]  #获取第二个参数(文件名)
        fileName = folder + name   # 将文件夹和图片名连接起来
        with open(fileName, 'rb') as f:
            while True:
                a = f.read(1024)
                if not a:
                    break
                conn.send(a)
        time.sleep(0.1)  # 延时确保文件发送完整
        conn.send('EOF'.encode())
        print('文件发送完成!')

    # 保存上传的文件到当前工作目录
    def recvFile(message):
        print(message)
        name = message.split()[1] #获取文件名
        fileName = folder + name   # 将文件夹和图片名连接起来
        print('开始保存!')
        with open(fileName, 'wb') as f:
            while True:
                data = conn.recv(1024)
                if data == 'EOF'.encode():
                    print('保存成功!')
                    break
                f.write(data)

    # 判断输入的命令并执行对应的函数
    def recv_func(order, message):
        if order == 'get':
            return sendFile(message)
        elif order == 'put':
            return recvFile(message)

    print('开始运行...')
    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=tcp_connect, args=(conn, addr))
        t.start()
    s.close()

####################################################################################


serv1 = threading.Thread(target=chatServer)
serv1.start()
serv2 = threading.Thread(target=fileServer)
serv2.start()
serv3 = threading.Thread(target=pictureServer)
serv3.start()