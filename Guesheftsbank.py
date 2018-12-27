#MVP Stage1 - 3-6-3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
from datetime import datetime
from bs4 import BeautifulSoup

capital = 100000
liabilities = 0
placcount = 0
loanaccount = 0

days = 20
id = 0 #Пусть клиентский айди начинается с 1
accounts = pd.DataFrame(columns = ['AccType', 'ClientId', 'BeginDate', 'EndDate', 'BeginQ', 'EndQ', 'Status'])
#день
for i in range(days):   #номер дня это i+1
    randnumloans = random.choice(range(40))
    randnumdeposits = random.choice(range(40))
    for n in range(randnumloans):
        accType = 'L'
        clientId = id + 1
        beginDate = i + 1 #это чтобы дня О не было
        endDate = i + 6
        beginQ = 1000
        endQ = beginQ * 1.06
        status = 'Active'
        newcostomer = [accType, clientId, beginDate, endDate, beginQ, endQ, status]
        accounts.loc[id] = newcostomer
        id += 1
        loanaccount += 1000
    for n in range(randnumdeposits):
        accType = 'D'
        clientId = id + 1
        beginDate = i + 1
        endDate = i + 6
        beginQ = 1000
        endQ = beginQ * 1.03
        status = 'Active'
        newcostomer = [accType, clientId, beginDate, endDate, beginQ, endQ, status]
        accounts.loc[id] = newcostomer
        id += 1
        liabilities += 1000
#вечер
    for n in range(len(accounts)):
        if accounts.loc[n, 'EndDate'] == i+1 and accounts.loc[n, 'Status'] == 'Active':
            accounts.loc[n, 'Status'] = 'Closed'
            if accounts.loc[n, 'AccType'] == 'D':
                liabilities -= 1000
                placcount -= 30
            else:
                loanaccount -= 1000
                placcount += 60


print("Assets: ", capital + placcount + liabilities)
print("    including cash: ", capital + placcount + liabilities - loanaccount)
print("    including loans: ", loanaccount)
print("Capital: ", capital)
print("Retained Earnings: ", placcount)
print("Liabilities: ", liabilities)
"""Переменные:
Заявка - Id, score - объединяются в датафрейм - генерируются во фрейме1, состоящем из 100 заявок, каждый день этот фрейм обнуляется, данные переписываются во фрейм2
Score сравнивается с бенчмарком (30) - в MVP отказаться!!! 
Число одобренных заявок в день * 1000, ну т.е. кредиты по 1000
Случайное число депозитов в день * 1000, ну т.е. депозиты по 1000
Счета: A, L, K, PnL - обновляются каждый день
Если счета баланса уходят в минус - дефолт
Итерация датафрейма по счетам
Внутри дня разделение на: открытие - активность - закрытие
Каждый новый счёт оформлять в виде словаря - на втором этапе. На первом в виде листа
Оформить графон и настроить инпуты
