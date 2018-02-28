#!/usr/bin/env python
# coding:utf-8
'''
Created on: 2018.02

@author: wqf

Email: 

Version: v1.0

Description:通过读取配置文件来生成两个字典，存储遥信，遥测数据及地址
#130,179为虚拟点暂时不做,其他测试完了
Help:
'''
import os

#配置文件目录
yx_path = './py_yxconf.csv'
yc_path = './py_ycconf.csv'
class Storage(object):
    def __init__(self):
        #遥信初始化读取值 转发地址:[地址,点位,线路,值，变化tag]
        self.yx = {}
        init_addr = file_control('r', yx_path)
        for i in init_addr:
            self.yx[i[0]] =[i[1],i[2],i[3],0,0]
        #遥测初始化读取值 转发地址:[地址,线路,值，变化tag]
        self.yc ={}
        init_addr = file_control('r', yc_path)
        for i in init_addr:
            self.yc[i[0]] =[i[1],i[2],'0000',0]
  
    def updateyx(self,arg,val):
        self.yx[arg][3] = val

    def updateyc(self,arg,val):
        self.yc[arg][2] = val
    
    def show_storage(self):
        print '遥信:读取完成'#,self.yx
        print '遥测:读取完成'#,self.yc

def file_control(arg,file_path):
    #判断是否存在文件，存在则读取,以前写的函数
    if os.path.exists(file_path):
        account_file = open(file_path, arg)
        MESSAGE =[]
        for i in account_file.readlines():
            MESSAGE.append(i.strip().split(','))
    else:
        print('Error: Account file "account.db" is not exit, please check!')
        exit(1)
    if 'r'  in arg:
        account_file.close()
        return MESSAGE 
    else:
        return account_file

