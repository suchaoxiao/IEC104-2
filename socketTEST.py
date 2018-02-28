#!/usr/bin/python
# -*- coding: UTF-8 -*-
import threading
import time
'''
def func(arg):
    while True:
        print 'I am func',arg
        time.sleep(arg)

t1 = threading.Thread(target = func,args =(1,))
t2 = threading.Thread(target = func,args =(2,))
t3 = threading.Thread(target = func,args =(3,))

t1.setDaemon(True)
t1.start()


t2.start()
t3.start()
print 'end'
'''
print range(1,5)