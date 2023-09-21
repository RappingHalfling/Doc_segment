#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 16 20:47:50 2023

@author: rappinghalfling

Построение графиков обучения 
"""
import matplotlib.pyplot as plt
import json
plt.rcParams['figure.dpi'] = 100

data = [json.loads(line) for line in open('logs/metrics20k.json', 'r')]

x = list(range(len(data)))
loss_box_reg = [x.get('loss_box_reg') for x in data]
loss_cls = [x.get('loss_cls') for x in data]
loss_rpn_cls =[x.get('loss_rpn_cls') for x in data]
loss_rpn_loc =[x.get('loss_rpn_loc') for x in data]
total_loss = [x.get('total_loss') for x in data]

plt.xlabel('Итерации в соотношении 20:1')
plt.ylabel('Значения функции потерь')
plt.plot(x, loss_box_reg, label = 'loss_box_reg')
plt.plot(x, loss_cls, label = 'loss_cls')
plt.plot(x, loss_rpn_cls, label = 'loss_rpn_cls')
plt.plot(x, loss_rpn_loc, label = 'loss_rpn_loc')
plt.plot(x, total_loss, label = 'total_loss')
plt.title('Оценка loss')
plt.legend(loc='upper right')
plt.show()

       