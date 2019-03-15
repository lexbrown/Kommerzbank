#Geschaftsbank - Stage4. Draft 03.13.2019

#Основные задачи:
#   Ввести стохастические параметры клиентов - В ПРОЦЕССЕ
#   Внедряю MySQL
#   Сформировать резервы
#   Написать проверку на  кэ

import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
import mysql.connector as cnt
#import statsmodels.api as sm
from sqlalchemy import create_engine
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

db_connector = cnt.connect(host="localhost", user="lexbrown", passwd="******")
bank_cursor = db_connector.cursor()
bank_cursor.execute("CREATE DATABASE IF NOT EXISTS Geshbank")
engine = create_engine('mysql+mysqldb://lexbrown:******@localhost/Geshbank', echo=False)


capital = 100000
liabilities = 0
interestincome = 0
interestcosts = 0
placcount = 0
loanaccount = 0
operationcosts = 0
default_losses = 0

reserve_expenses = 0
reserve_recovery = 0

risk_free_rate = 0.06

daily_outflow = 0
daily_inflow = 0


days =  int(input("Введите количество дней: ")) #перевести на инпуты
max_clients = int(input("Введите максимальное количество клиентов в день: "))
id_loan_closed = 0
id_deposit_closed = 0

loan_accounts = pd.DataFrame(columns = ['AccType', 'ClientId', 'BeginDate', 'EndDate', 'BeginQ', 'EndQ', 'PD', 'LGD', 
                                   'Interest rate','Status', 'Random', 'Default function'])
pd.DataFrame(loan_accounts).to_sql('loan_accounts', con = engine, index = False, if_exists = 'replace')
deposit_accounts = pd.DataFrame(columns = ['AccType', 'ClientId', 'BeginDate', 'EndDate', 'BeginQ', 'EndQ', 'Status'])
pd.DataFrame(deposit_accounts).to_sql('deposit_accounts', con = engine, index = False, if_exists = 'replace')
cash_balance = pd.DataFrame(columns = ['DayNumber', 'Balance', 'Daily outflows', 'Daily inflows'])
cash_balance.to_sql('cash_balance', con = engine, index = False, if_exists = 'replace')
assets_series = pd.DataFrame(columns = ['DayNumber', 'Assets'])
assets_series.to_sql('assets_series', con = engine, index = False, if_exists = 'replace')



"""
open_loan_accounts = pd.DataFrame(columns = ['AccType', 'ClientId', 'BeginDate', 
                                   'EndDate', 'BeginQ', 'EndQ', 'PD', 'LGD', 
                                   'Interest rate','Status', 'Random', 'Default function'])
open_deposit_accounts = pd.DataFrame(columns = ['AccType', 'ClientId', 'BeginDate', 
                                   'EndDate', 'BeginQ', 'EndQ', 'Status'])
closed_loan_accounts = pd.DataFrame(columns = ['AccType', 'ClientId', 'BeginDate', 
                                   'EndDate', 'BeginQ', 'EndQ', 'PD', 'LGD', 
                                   'Interest rate', 'Status', 'Random', 'Default function'])
closed_deposit_accounts = pd.DataFrame(columns = ['AccType', 'ClientId', 'BeginDate', 
                                   'EndDate', 'BeginQ', 'EndQ', 'Status'])
cash_balance = pd.DataFrame(columns = ['DayNumber', 'Balance', 'Daily outflows', 'Daily inflows'])
assets_series = pd.DataFrame(columns = ['DayNumber', 'Assets'])
"""

#cash_balance = pd.Series([0])
id = 0  #len(openaccounts) 

def assets():
    return capital + netincome() + liabilities
def cash():
    return assets() - loanaccount
def placcount():
    return interestincome - interestcosts
def reserves():
    return reserve_expenses - reserve_recovery
def netincome():
    return placcount() - operationcosts - default_losses
'''def interbank_loan():
    accType = 'O/N'
    clientId = id + 1
    beginDate = i + 1
    endDate = i + 2
    beginQ = -2 * cash
    endQ = beginQ * 1.01
    status = 'Active'
    newcustomer = [accType, clientId, beginDate, endDate, beginQ, endQ, status]
    openaccounts.loc[len(openaccounts)] = newcustomer
    global id
    global liabilities
    global daily_inflow
    id += 1
    liabilities += beginQ
    daily_inflow += beginQ'''


#день
for i in range(days):   #номер дня это i+1
    randnumloans = random.choice(range(max_clients)) #чот сильно
    #randnumloans = (10 + 15 * np.sin(i / 5) + i)
    #randnumdeposits = (10 + 15 * np.sin(i / 5) + i) #чот тож, многовато для маленького банка то
    randnumdeposits = random.choice(range(max_clients)) #чот сильно
    #if cash() > assets()/10:
    for n in range(int(randnumloans)):
        accType = 'L'
        clientId = id + 1
        beginDate = i + 1 #это чтобы дня О не было
        endDate = i + 1 + random.choice(range(2, 16)) * 10
        beginQ = random.choice(range(1, 101))*100
        if beginQ > cash():
            continue
        status = 'Active'
        prob_d = random.choice(range(1, 21))/100
        lgd = round(np.random.beta(2, 4), 1) + 0.1
        interest_rate = round((risk_free_rate + prob_d * lgd) /(1 - prob_d), 4)
        endQ = round(beginQ * (1 + interest_rate * (endDate - beginDate) / 252), 2)
        random_default = random.choice(range(1, 101))/100
        default_function = random_default * np.exp(prob_d)
        #newcustomer = [accType, clientId, beginDate, endDate, beginQ, endQ, prob_d, lgd, interest_rate, status, random_default, default_function]
        #open_loan_accounts.loc[len(open_loan_accounts)] = newcustomer
        pd.DataFrame([{'AccType':accType, 'ClientId':clientId, 'BeginDate':beginDate, 'EndDate':endDate, 
                      'BeginQ':beginQ, 'EndQ':endQ, 'PD':prob_d, 'LGD':lgd, 'Interest rate':interest_rate, 'Status':status,
                       'Random':random_default, 'Default function':default_function}]).to_sql('loan_accounts', con = engine, index = False, if_exists = 'append')
        id += 1
        loanaccount += beginQ
        daily_outflow += beginQ
        reserve_expenses += (beginQ * prob_d * lgd)
    for n in range(int(randnumdeposits)):
        accType = 'D'
        clientId = id + 1
        beginDate = i + 1
        endDate = i + 1 + random.choice(range(2, 16)) * 10
        beginQ = random.choice(range(1, 101))*100
        endQ = round(beginQ * (1 + 0.03 * (endDate - beginDate) / 252), 2)
        status = 'Active'
        #newcustomer = [accType, clientId, beginDate, endDate, beginQ, endQ, status]
        #open_deposit_accounts.loc[len(open_deposit_accounts)] = newcustomer
        pd.DataFrame([{'AccType':accType, 'ClientId':clientId, 'BeginDate':beginDate, 'EndDate':endDate, 'BeginQ':beginQ, 'EndQ':endQ, 'Status':status}]).to_sql('deposit_accounts', con = engine, index = False, if_exists = 'append')
        id += 1
        liabilities += beginQ
        daily_inflow += beginQ

'''
#вечер
    for n in range(len(open_loan_accounts)): #вечерняя проверка кредитных счетов
        if open_loan_accounts.loc[n, 'EndDate'] == i+1 and open_loan_accounts.loc[n, 'Status'] == 'Active':
            open_loan_accounts.loc[n, 'Status'] = 'Closed'
            loanaccount -= open_loan_accounts.loc[n, 'BeginQ']
            if open_loan_accounts.loc[n, 'AccType'] != 'O/N - L':
                reserve_recovery += (open_loan_accounts.loc[n, 'BeginQ'] * open_loan_accounts.loc[n, 'LGD'] * open_loan_accounts.loc[n, 'PD'])
                if open_loan_accounts.loc[n, 'Default function'] >= 1: #Если дефолт
                    daily_inflow += (open_loan_accounts.loc[n, 'BeginQ'] * (1 - open_loan_accounts.loc[n, 'LGD']))
                    default_losses += (open_loan_accounts.loc[n, 'BeginQ'] * open_loan_accounts.loc[n, 'LGD'])
                else:
                    interestincome += open_loan_accounts.loc[n, 'BeginQ'] * (open_loan_accounts.loc[n, 'Interest rate'] * (open_loan_accounts.loc[n, 'EndDate'] - open_loan_accounts.loc[n, 'BeginDate']) / 252)
                    daily_inflow += (open_loan_accounts.loc[n, 'BeginQ'] * (1 + (open_loan_accounts.loc[n, 'Interest rate'] * (open_loan_accounts.loc[n, 'EndDate'] - open_loan_accounts.loc[n, 'BeginDate']) / 252)))
            else:
                interestincome += open_loan_accounts.loc[n, 'BeginQ'] * (open_loan_accounts.loc[n, 'Interest rate'] * (open_loan_accounts.loc[n, 'EndDate'] - open_loan_accounts.loc[n, 'BeginDate']) / 252)
                daily_inflow += (open_loan_accounts.loc[n, 'BeginQ'] * (1 + (open_loan_accounts.loc[n, 'Interest rate'] * (open_loan_accounts.loc[n, 'EndDate'] - open_loan_accounts.loc[n, 'BeginDate']) / 252)))
            closed_loan_accounts.loc[id_loan_closed] = open_loan_accounts.loc[n]
            id_loan_closed += 1
    for n in range(len(open_deposit_accounts)): #вечерняя проверка депозитных счетов
        if open_deposit_accounts.loc[n, 'EndDate'] == i+1 and open_deposit_accounts.loc[n, 'Status'] == 'Active':
            open_deposit_accounts.loc[n, 'Status'] = 'Closed'
            if open_deposit_accounts.loc[n, 'AccType'] == 'D':
                liabilities -= open_deposit_accounts.loc[n, 'BeginQ']
                interestcosts += open_deposit_accounts.loc[n, 'BeginQ'] * (0.03 * (open_deposit_accounts.loc[n, 'EndDate'] - open_deposit_accounts.loc[n, 'BeginDate']) / 252)
                daily_outflow += (open_deposit_accounts.loc[n, 'BeginQ'] * (1 + (0.03 * (open_deposit_accounts.loc[n, 'EndDate'] - open_deposit_accounts.loc[n, 'BeginDate']) / 252)))
            else: #open_deposit_accounts.loc[n, 'AccType'] == 'O/N':
                liabilities -= open_deposit_accounts.loc[n, 'BeginQ']
                interestcosts += open_deposit_accounts.loc[n, 'BeginQ'] * (0.01 * (open_deposit_accounts.loc[n, 'EndDate'] - open_deposit_accounts.loc[n, 'BeginDate']) / 252)
                daily_outflow += (open_deposit_accounts.loc[n, 'BeginQ'] * (1 + (0.01 * (open_deposit_accounts.loc[n, 'EndDate'] - open_deposit_accounts.loc[n, 'BeginDate']) / 252)))
            #начать closedaccounts
            closed_deposit_accounts.loc[id_deposit_closed] = open_deposit_accounts.loc[n]
            id_deposit_closed += 1
    operationcosts += 200
    daily_outflow += 200
    
    #вечерние проверки
    if cash() < 0:
        accType = 'O/N - D'
        clientId = id + 1
        beginDate = i + 1
        endDate = i + 2
        beginQ = int(-cash() + assets() * 0.1)
        endQ = beginQ * (1 + risk_free_rate * (endDate - beginDate) / 252)
        status = 'Active'
        newcustomer = [accType, clientId, beginDate, endDate, beginQ, endQ, status]
        open_deposit_accounts.loc[len(open_deposit_accounts)] = newcustomer
        id += 1
        liabilities += beginQ
        daily_inflow += beginQ
    elif cash() < (assets() * 0.05):
        accType = 'O/N - D'
        clientId = id + 1
        beginDate = i + 1
        endDate = i + 2
        beginQ = int(assets() * 0.1)
        endQ = beginQ * (1 + risk_free_rate * (endDate - beginDate) / 252)
        status = 'Active'
        newcustomer = [accType, clientId, beginDate, endDate, beginQ, endQ, status]
        open_deposit_accounts.loc[len(open_deposit_accounts)] = newcustomer
        id += 1
        liabilities += beginQ
        daily_inflow += beginQ
    elif cash() > (assets() * 0.20):
        accType = 'O/N - L'
        clientId = id + 1
        beginDate = i + 1
        endDate = i + 2
        beginQ = int(cash() - assets() * 0.15)
        status = 'Active'
        prob_d = 0
        lgd = 0
        interest_rate = risk_free_rate
        endQ = beginQ * (1 + interest_rate * (endDate - beginDate) / 252)
        random_default = random.choice(range(1, 101))/100
        default_function = random_default * np.exp(prob_d)
        newcustomer = [accType, clientId, beginDate, 
                       endDate, beginQ, endQ, prob_d, lgd, interest_rate, status,
                       random_default, default_function]
        open_loan_accounts.loc[len(open_loan_accounts)] = newcustomer
        id += 1
        loanaccount += beginQ
        daily_outflow += beginQ
    else:
        True
        
        
    #openaccounts = openaccounts.drop(np.where(openaccounts["Status"] == "Closed")[0]) - не работает более чем для 6 дней
    open_loan_accounts = open_loan_accounts[open_loan_accounts.Status != "Closed"] #это ужасно
    open_deposit_accounts = open_deposit_accounts[open_deposit_accounts.Status != "Closed"] #дублирование - вообще ужас
    open_loan_accounts.index = np.arange(len(open_loan_accounts))
    open_deposit_accounts.index = np.arange(len(open_deposit_accounts))
    #operationcosts += 200
    #daily_outflow += 200
    placcount()
    cash_balance.loc[i] = [i+1, cash(), daily_outflow, daily_inflow]
    assets_series.loc[i] = [i+1, assets()]
    daily_outflow = 0
    daily_inflow = 0
    #cash_balance[i] = cash()
    #cash_balance.index = np.arange(days)
    #placcount()
    print("День ", i+1)
#cash_balance.index = cash_balance['DayNumber'] - может и зря закомментил
#assets_series.index = assets_series['DayNumber']


#Reports:

#Graphical Report
graphRep = plt.figure(figsize=(15, 15))
ax1 = graphRep.add_subplot(3, 2, 1)
ax2 = graphRep.add_subplot(3, 2, 2)
ax3 = graphRep.add_subplot(3, 2, 3)
ax4 = graphRep.add_subplot(3, 2, 4)
ax5 = graphRep.add_subplot(3, 2, 5)
ax6 = graphRep.add_subplot(3, 2, 6)
balancesheet = pd.DataFrame([[loanaccount, 0], [cash(), 0], 
                        [0, capital], [0, netincome()-reserves()], [0, reserves()], [0, liabilities]], 
    index = ['Loans', 'Cash', 'Equity', 'RE', 'Reserves', 'Debt'], 
    columns = ['Assets', 'Equity and Debt'])
incomestatement = pd.DataFrame([interestincome, interestcosts, 
                                placcount(), reserves(), placcount() - reserves(),
                                operationcosts, default_losses, netincome()-reserves()], 
    index = ['Interest income', 'Interest costs (-)', 'Net interest income', 'Net reserve expenses(-)',
             'NII after reserves', 'Operating costs (-)', 'Default losses (-)', 'Net income'], 
    columns = ['Accounts'])
#incomestatement.index.name = "P&L accounts"

balancesheet.T.plot(grid = True, rot = 0, ax = ax1, kind = "bar", stacked = True, fontsize = 12)
ax1.set_ylabel("U.S. dollars", fontsize = 15)
ax1.set_title("Balance sheet", fontsize = 25)
ax1.legend(loc= "center right", fontsize = 10)

#ax2.set_ylabel(fontsize = 20)
ax2.set_title("Income statement", fontsize = 25)
#ax2.legend(loc="center left", fontsize = 12)
#incomestatement.T.plot(grid = True, rot = 0, ax = ax2, kind = "bar", fontsize = 12)
ax2.barh(incomestatement.index, incomestatement.Accounts)
ax2.invert_yaxis()
ax2.grid(True)

cash_balance['Balance'].plot(grid = True, ax = ax3, marker = 'D', fontsize = 12, color = 'orange')
#ax3.fill_between(cash_balance['DayNumber'], cash_balance['Balance'], color = 'r')
assets_series['Assets'].plot(grid = True, ax = ax3, marker = 'o', fontsize = 12, color = 'red')
ax3.set_ylabel("U.S. dollars", fontsize = 15)
ax3.set_title("Cash balance", fontsize = 25)
ax3.legend(loc="best", fontsize = 12)

cash_balance['Daily outflows'].plot(grid = True, ax = ax4, marker = 's', fontsize = 12, color = 'g')
cash_balance['Daily inflows'].plot(grid = True, ax = ax4, marker = 'v', fontsize = 12, color = 'b')
ax4.set_title("Daily flows", fontsize = 25)
ax4.legend(loc="best", fontsize = 12)
#ax4.set_xticks(cash_balance['DayNumber'])

unionframe = pd.concat([closed_loan_accounts, open_loan_accounts], axis = 0)
unionframe.index = np.arange(len(unionframe))
ax5.hist(unionframe['LGD'], bins = 11)
ax5.set_title("LGD Distribution", fontsize = 25)

ax6.hist(unionframe['PD'], bins = 21)
ax6.set_title("PD Distribution", fontsize = 25)

plt.subplots_adjust(wspace=0.5)
graphRep.savefig("Report - Stage 4.png")

#Table reports:
print()
print("Банк работал ", days, " дней")
print()
print("Баланс на конец периода:")
print(balancesheet)
print()
print("Total assets: ", assets())
print()
print(incomestatement)
print()
print('Овернайты на рынке межбанковских кредитов брались ', 
      len(closed_deposit_accounts.loc[closed_deposit_accounts.AccType == 'O/N - D']) +
      len(open_deposit_accounts.loc[open_deposit_accounts.AccType == 'O/N - D']),
      ' раз:')
if len(closed_deposit_accounts.loc[closed_deposit_accounts.AccType == 'O/N - D']) != 0:
    print(closed_deposit_accounts.loc[closed_deposit_accounts.AccType == 'O/N - D'])
if len(open_deposit_accounts.loc[open_deposit_accounts.AccType == 'O/N - D']) != 0:
    print(open_deposit_accounts.loc[open_deposit_accounts.AccType == 'O/N - D'])
    
print('Овернайты на рынке межбанковских кредитов давались ', 
      len(closed_loan_accounts.loc[closed_loan_accounts.AccType == 'O/N - L']) +
      len(open_loan_accounts.loc[open_loan_accounts.AccType == 'O/N - L']),
      ' раз:')
if len(closed_loan_accounts.loc[closed_loan_accounts.AccType == 'O/N - L']) != 0:
    print(closed_loan_accounts.loc[closed_loan_accounts.AccType == 'O/N - L'])
if len(open_loan_accounts.loc[open_loan_accounts.AccType == 'O/N - L']) != 0:
    print(open_loan_accounts.loc[open_loan_accounts.AccType == 'O/N - L'])
    
question = input('Сохраняем весь этот ужас? ')
if question == 'y':
    closed_deposit_accounts.to_excel('Stage4-CDA-test.xlsx')
    open_deposit_accounts.to_excel('Stage4-ODA-test.xlsx')
    closed_loan_accounts.to_excel('Stage4-CLA-test.xlsx')
    open_loan_accounts.to_excel('Stage4-OLA-test.xlsx')
    cash_balance.to_excel('Stage4-CB-test.xlsx')
    

#гипотеза: RE коррелирует с кэшем
#Внедрить Statsmodel в 4й версии
#Внедрить этап "Утро" - проверка условий
    
'''
