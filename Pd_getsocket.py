#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Created on: 2018.02

@author: wqf

Email: 

Version: v1.0

Description:

Help:
'''
import socket
import threading
import time
import Queue
import IECLIB.Storage
import telnetinfo

'''
*******************************
工具类函数
*******************************
'''
def address_cal(arg):
#用于数字转换为6位信息体地址
    tmp = hex(arg)[2:].zfill(6)
    listout =[tmp[i:i+2] for i in xrange(0, len(tmp), 2)]
    return listout

def apci_sequence(arg1,arg2):
#apci收发序号+1用    
    if int(arg1+arg2,16) == 65279:
        return '0000'
    tmp = hex(int(arg2+arg1,16)+2)[2:]
    tmp1 =tmp.zfill(4)
    output = tmp1[2:]+tmp1[0:2]
    return output

def message_process(arg):
#字符串按字节hex化
    s = arg.encode('hex')
    n = 2
    hex_message = [s[i:i+n] for i in xrange(0, len(s), n)]
    return hex_message

def hexstr_toSendstr(a):
#HEX字符串按2字节翻译成send用的
    return ''.join([chr(int(b, 16)) for b in [a[i:i+2] for i in range(0, len(a), 2)]])

'''
*******************************
IEC104问答模块
*******************************
'''
def active(arg,sto):
#进行数据接收并对接受数据反馈
    global rec_sq
    global send_sq
    print 'active is running'
    while True:
        rec_message = arg.recv(1024)
        if len(rec_message) ==0: break
        rec_list =message_process(rec_message)
        rec_hex = ''.join(rec_list)
        print 'REC:',rec_hex
        if rec_hex == '680443000000':
        #链路测试帧
            arg.send(hexstr_toSendstr('680483000000'))
            print 'send:',hexstr_toSendstr('680483000000')
        elif rec_hex == '680413000000':
        #结束帧
            arg.send(hexstr_toSendstr('680423000000'))
            print 'send:',hexstr_toSendstr('680423000000')
            arg.close()
        elif rec_list[1] > '04' and rec_list[6] == '64':
        #总召唤帧
            rec_sq =rec_list[2]+rec_list[3] 
            send_all(arg,sto)
        

def send_all(arg,sto):
#总召唤*********************************
    global rec_sq
    global send_sq
    #总召唤确认帧
    arg.send(hexstr_toSendstr('680E'+send_sq+apci_sequence(rec_sq[:2],rec_sq[2:])+'64010700010000000000'))
    send_sq = apci_sequence(send_sq[:2],send_sq[2:])
    #分组发送遥信
    sumyxpart(1, 128,'01ff14000100010000', arg, sto)
    sumyxpart(128, 255,'01ff14000100800000', arg, sto)
    sumyxpart(255, 290,'01ad14000100ff0000', arg, sto)
    #分组发送遥测
    for i in range(16385,16995,80):
        stryc = '09d014000100'+hex(i)[-2:]+hex(i)[2:4]
        sumycpart(i, i+80,stryc , arg, sto)
    sumycpart(16945, 16995,'09b214000100', arg, sto)
    #总召唤结束
    arg.send(hexstr_toSendstr('680E'+send_sq+apci_sequence(rec_sq[:2],rec_sq[2:])+'64010A00010000000014'))
    send_sq = apci_sequence(send_sq[:2],send_sq[2:])

def sumycpart(i1,i2,str1,arg,sto):              #遥测传输组合
    global rec_sq
    global send_sq
    sumyc =[]
    sumyc.append(send_sq)
    sumyc.append(apci_sequence(rec_sq[:2],rec_sq[2:]))
    sumyc.append(str1)
    for i in range(i1,i2):
        if sto.yc.has_key(str(i)):
            sumyc.append(sto.yc[str(i)][2][2:])
            sumyc.append(sto.yc[str(i)][2][:2])
            sumyc.append('00')           #低位在前高位在后
            continue
        sumyc.append('000000')
    sendlen =hex(len(''.join(sumyc))/2)[2:].zfill(2)
    arg.send(hexstr_toSendstr('68'+sendlen+''.join(sumyc)))
    send_sq = apci_sequence(send_sq[:2],send_sq[2:])
    
def sumyxpart(i1,i2,str1,arg,sto):              #遥信传输组合
    global rec_sq
    global send_sq
    sumyx =[]
    sumyx.append(send_sq)
    sumyx.append(apci_sequence(rec_sq[:2],rec_sq[2:]))
    sumyx.append(str1)
    for i in range(i1,i2):
        if sto.yx.has_key(str(i)):
            sumyx.append(str(sto.yx[str(i)][3]).zfill(2))
            continue
        sumyx.append('00')
    sendlen =hex(len(''.join(sumyx))/2)[2:].zfill(2)
    arg.send(hexstr_toSendstr('68'+sendlen+''.join(sumyx)))
    send_sq = apci_sequence(send_sq[:2],send_sq[2:])

'''
*******************************
被动上送函数
*******************************
'''    
def passive(arg,sto):
#主动上送变位数据,
    global rec_sq
    global send_sq
    print 'passive is running'
    time.sleep(5)                 #在等待总召唤完成后开始主动上传
    while True:
        for i in range(290):      #轮训遥信寻找变位的遥信塞入队列等待上送
            if sto.yx.has_key(str(i)) and sto.yx[str(i)][4] == 1:
                addryx = address_cal(i)
                Output_YX.put(addryx[2]+addryx[1]+addryx[0]+str(sto.yx[str(i)][3]).zfill(2)) 
                sto.yx[str(i)][4] = 0
        for j in range(16385,16995):  #轮训遥测寻找变位的遥信塞入队列等待上送
            if sto.yc.has_key(str(j)) and sto.yc[str(j)][3] == 1:
                addryc = address_cal(j)
                Output_YC.put(addryc[2]+addryc[1]+addryc[0]+sto.yc[str(j)][2][2:]+sto.yc[str(j)][2][:2])
                sto.yc[str(j)][3] = 0
        try:
            while Output_YX.empty() == False: #发送遥信队列直到清空
                YXsend = '680e'+send_sq+rec_sq+'010103000100'+Output_YX.get()
                arg.send(hexstr_toSendstr(YXsend))
                send_sq = apci_sequence(send_sq[:2],send_sq[2:])
                print 'send:',hexstr_toSendstr(YXsend)
            while  Output_YC.empty() == False:#发送遥测队列直到清空
                YCsend = '6810'+send_sq+rec_sq+'090103000100'+Output_YC.get()+'00'
                arg.send(hexstr_toSendstr(YCsend))
                send_sq = apci_sequence(send_sq[:2],send_sq[2:])
            time.sleep(2)
        except Exception as e:
            print e
        else:
            continue
            
'''
*******************************
2个模块 读取和服务端
*******************************
'''
def read_fep(sto):
    #读取各个服务器数据
    ttlist =[]
    tt1_yx = threading.Thread(target = telnetinfo.read_yx,args =(sto.yx,1,))
    tt1_yx.setName('thread1_yx')
    tt1_yc= threading.Thread(target = telnetinfo.read_yc,args =(sto.yc,1,))
    tt1_yc.setName('thread1_yc')
    tt2_yx = threading.Thread(target = telnetinfo.read_yx,args =(sto.yx,2,))
    tt2_yx.setName('thread2_yx')
    tt2_yc = threading.Thread(target = telnetinfo.read_yc,args =(sto.yc,2,))
    tt2_yc.setName('thread2_yc')
    tt3_yx = threading.Thread(target = telnetinfo.read_yx,args =(sto.yx,3,))
    tt3_yx.setName('thread3_yx')
    tt3_yc = threading.Thread(target = telnetinfo.read_yc,args =(sto.yc,3,))
    tt3_yc.setName('thread3_yc')
    tt4_yx = threading.Thread(target = telnetinfo.read_yx,args =(sto.yx,4,))
    tt4_yx.setName('thread4_yx')
    tt4_yc = threading.Thread(target = telnetinfo.read_yc,args =(sto.yc,4,))
    tt4_yc.setName('thread4_yc')
    ttlist.append(tt1_yx)
    ttlist.append(tt1_yc)
    ttlist.append(tt2_yx)
    ttlist.append(tt2_yc)
    ttlist.append(tt3_yx)
    ttlist.append(tt3_yc)
    ttlist.append(tt4_yx)
    ttlist.append(tt4_yc)
    for t in ttlist:
        t.setDaemon(True)  # 设置为守护线程
        t.start()
    for t in ttlist:
        t.join()
        
    
def pd_server(sto):
    #打开服务
    s = socket.socket()         # 创建 socket 对象
    host = socket.gethostname() # 获取本地主机名
    port = 2404                # 设置端口
    s.bind((host, port))        # 绑定端口
    s.listen(5)                 # 等待客户端连接
    print '监听已打开 等待中..........'
    while True:
        c, addr = s.accept()     # 建立客户端连接。
        print 'getaddr:', addr
        while True:
        #判断启动帧    
            start_str = ''.join(message_process(c.recv(1024)))
            if start_str =='680407000000':
                c.send(hexstr_toSendstr('68040B000000'))
                break
        thread_list = []
        t2 = threading.Thread(target = passive,args =(c,sto,))
        t1 = threading.Thread(target = active,args =(c,sto,))
        thread_list.append(t1)
        thread_list.append(t2)
        for t in thread_list:
            t.setDaemon(True)  # 设置为守护线程
            t.start()
    for t in thread_list:
        t.join()
 
if __name__ == '__main__':
    #初始化配置文件
    Output_YX = Queue.Queue()
    Output_YC = Queue.Queue()
    send_sq = '0000'
    rec_sq = '0000'
    sto = IECLIB.Storage.Storage()
    sto.show_storage()
    print '初始数据地址加载完成'
    process_list =[]
    p1 = threading.Thread(target = pd_server,args =(sto,))
    #打开sever服务提供轮训
    p2 = threading.Thread(target = read_fep,args =(sto,))
    #开始读取各个fep数据
    process_list.append(p1)
    process_list.append(p2)
    for p in process_list:
        p.setDaemon(True)  # 设置为守护线程
        p.start()
    for p in process_list:
        p.join()


