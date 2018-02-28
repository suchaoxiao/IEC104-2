#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Created on: 2018.02

@author: wqf

Email: 

Version: v1.0

Description:
对fep服务器进行端口Telnet方法的读取数据
Help:
'''
import telnetlib
import time

def read_yx(arg1,location):
#遥信读取
    Host = ['IP','10.255.2.15','10.255.2.21','10.255.2.27','10.255.2.33']
    port =['port',5010,5020,5030,5040]
    while True:
        try:
            tn = telnetlib.Telnet(Host[location], port[location], timeout=3)
        except Exception as e:
            #print e
            time.sleep(5)                                       #重连时间
        else:
            while True:
                try:
                    for i in range(290):                       #根据是否在配置内进行读取
                        if arg1.has_key(str(i)) and arg1[str(i)][2] == str(location):  
                            tn.write('printsrcwords 0'+str(location)+' '+arg1[str(i)][0]+' 1\n')
                            tn.read_until('\n')
                            tn.read_until('\n')
                            message = tn.read_until('\n')                
                            tn.read_until('\n')
                            tn.read_until('\n')
                            yx_tmp1 = message[-6:-2]
                            yx_tmp2 = bin(int(yx_tmp1,16))[2:]
                            yx_tmp3 =yx_tmp2.zfill(16)[15-int(arg1[str(i)][1]):16-int(arg1[str(i)][1])]
                            #如果不同则赋值，变化TAG打1                
                            if arg1[str(i)][3] <> int(yx_tmp3):
                                arg1[str(i)][3] = int(yx_tmp3)
                                arg1[str(i)][4] = 1
                    time.sleep(1)                               #轮训间隔设置
                    print str(location)+'line read Yx completed'
                except Exception as f:
                    print f
                    break     
                
def read_yc(arg1,location):
#遥测读取
    Host = ['IP','10.255.2.15','10.255.2.21','10.255.2.27','10.255.2.33']
    port =['port',5010,5020,5030,5040]
    while True:
        try:
            tn = telnetlib.Telnet(Host[location], port[location], timeout=3)
        except Exception as e:
            #print e
            time.sleep(5)                                        #重连时间
        else:
            while True:
                try:
                    for i in range(16385,16995):                #根据是否在配置内进行读取
                        if arg1.has_key(str(i)) and arg1[str(i)][1] == str(location):  
                            tn.write('printsrcwords 0'+str(location)+' '+arg1[str(i)][0]+' 1\n')
                            tn.read_until('\n')
                            tn.read_until('\n')
                            message = tn.read_until('\n')
                            tn.read_until('\n')
                            tn.read_until('\n') 
                            yc_tmp1 = message[-6:-2] 
                            #如果不同则赋值，变化TAG打1                   
                            if arg1[str(i)][2] <> yc_tmp1:
                                arg1[str(i)][2] = yc_tmp1
                                arg1[str(i)][3] = 1
                    time.sleep(5)                                #轮训间隔设置
                    print str(location)+'line read Yc completed'
                except Exception as f:
                    print f
                    break