
###########################################
##                                       ##
##              BINANCE 2.2              ##
##                                       ##
###########################################


from binance.client import Client

import config, fonctions, process_ma_solo
from datetime import date, timedelta, datetime
from time import sleep


BASE_COIN = "MATIC"
CHANGE_MONNAIE = "USDT"
ASSET = BASE_COIN + CHANGE_MONNAIE
START_DATE = datetime.today() - timedelta(minutes=60*1000)  #  date(2022, 11, 18)
STOP_DATE = datetime.today() #date(2022, 10, 8)
INTERVALS = "1HOUR" #"1DAY"
KEYS = (config.API_KEY,config.SECRET_KEY)

params ={
    "BASE_COIN": BASE_COIN,
    "CHANGE_MONNAIE": CHANGE_MONNAIE,
    "ASSET": ASSET,
    "START_DATE": START_DATE,
    "STOP_DATE": STOP_DATE,
    "INTERVALS": INTERVALS,
    "KEYS": KEYS
}
MA_INTETVALS = [136*2,2*198]
TOLERANCE = 0.05

MA_INTETVALS_test = [i for i in range(2, 13)]
TOLERANCE_test = [i/100 for i in range(1, 50)]
TOLERANCE_test.append(0)


ma_interval_solo = 3
TOLERANCE_solo_test = 0
ma_interval_solo_test = [i for i in range(3, 13)]
TOLERANCE_solo_test = [i/100 for i in range(1, 50)]
TOLERANCE_solo_test.append(0)
TOLERANCE_solo = 0


minute_since_for_test = 0

initial_wallet = 50

double_ma_or_single_ma = False # False 
double_exponetiel_or_solo_exp = False
double_ma_result = 0
solo_ma_result = 0

def compute_must_average_solo(rates):
    reglage = list()
    for i in ma_interval_solo_test:
        ma = process_ma_solo.compute_moving_average_of_rates_data(rates, i)
        for j in TOLERANCE_solo_test:
            b_s_p = process_ma_solo.compute_buy_and_sell_points_whith_solo_ma(rates, ma, j)
            finl_wall = process_ma_solo.compute_buy_and_sell_gains(initial_wallet, rates, b_s_p, ASSET,test=False)
            reglage.append((i, j, finl_wall ))
    reglage.sort(key=lambda x: x[2])
    return reglage[-1]


last_side = input("\n\n     What is the last side?\n\n   1 pour prêt à acheter (True), 0 pour prêt à la vente (False) ")
if last_side == "1":
    last_side=True
    last_side_in_buy = False
elif last_side == "0":
    last_side=False
    last_side_in_buy = True
nb_tours = 0

check = False
while not check:
    try:
        rates, client = fonctions.create_base_rates_file_and_get_client(params) 
        if client:
            check = True
    except:
        print("Re-tentative")

last_rate_date_object = rates[-1]["date"]
last_rate_value = rates[-1]["value"]
price_of_order = last_rate_value
first_rate_value = float(rates[-1]["value"])
first_rate_date = rates[-1]["date"]

rates_for_test = rates[minute_since_for_test:]

list_of_rate_buy = [0]
max_buy_rate = max(list_of_rate_buy)
nb_tour_buy = -1

price_of_buy = rates[0]["value"]
price_of_sell = last_rate_value



while True:

    print("\nSTART\n")

    

    if last_rate_date_object > datetime.now()-timedelta(hours=1):
        nb_tours += 1
        nb_tour_buy += 1
        print("Waiting for time...")
        while last_rate_date_object >= datetime.now()-timedelta(hours=1):
            sleep(1)


    check = False
    while not check:
        try:
            rates = fonctions.create_base_rates_file(params, client) 
            if client:
                check = True
        except:
            print("Re-tentative")

    

    if double_ma_or_single_ma:
        ma_list = [(fonctions.compute_moving_average_of_rates_data(rates, i), i) for i in MA_INTETVALS]
        buy_and_sell_points = fonctions.compute_buy_and_sell_points_from_ma(ma_list[0][0], ma_list[1][0], TOLERANCE)
        

    else:
        
        if double_exponetiel_or_solo_exp:
            short_ma = fonctions.get_moving_average_exponentiel(rates,.1827)
            long_ma = fonctions.get_moving_average_exponentiel(rates,.0366)
            long_ma = fonctions.decale_ema(long_ma, rates)
            buy_and_sell_points = fonctions.compute_points(rates, short_ma, long_ma,TOLERANCE)
        else:
            ma = fonctions.get_moving_average_exponentiel(rates,.135)
            buy_and_sell_points = process_ma_solo.compute_buy_and_sell_points_whith_solo_ma(rates,ma,TOLERANCE)
        
        
    last_rate_date_object = rates[-1]["date"] + timedelta(seconds=60*60)
    last_rate_value = float(rates[-2]["value"])
    new_rate_value = float(rates[-1]["value"])
   
    if buy_and_sell_points:
        
        if last_rate_date_object > datetime.now()-timedelta(hours=1):

            if buy_and_sell_points[-1][1] and last_side == False:

                if last_side_in_buy :
                    pass
                    #list_of_rate_buy.append(rates[-1]["value"])
                    #max_buy_rate = max(list_of_rate_buy)


            else:
                if buy_and_sell_points[-1][1] and last_side==True and rates[-1]["value"] > ( rates[-2]["value"]+rates[-3]["value"]+rates[-4]["value"]+rates[-5]["value"]+rates[-6]["value"]+rates[-7]["value"]+rates[-8]["value"]+rates[-9]["value"])/8:
                    price_of_buy = fonctions.BUY(params)
                    last_side = False
                    last_side_in_buy = True
                    nb_tour_buy = 0
                    print("marqueur: A1")

            if not buy_and_sell_points[-1][1] and last_side==False and last_side_in_buy==True:
                price_of_sell = fonctions.SELL(params, price_of_buy)
                last_side = True
                last_side_in_buy = False
                nb_tour_buy = 0
                list_of_rate_buy = [0]
                print("marqueur: V4")

            

    else:
        if last_rate_date_object > datetime.now()-timedelta(hours=1):
            if last_side==False:
                
                price_of_sell = fonctions.SELL(params)
                last_side = True
                print("marqueur: V5")

    
    START_DATE = datetime.today() - timedelta(hours=1000)  #  date(2022, 11, 18)
    STOP_DATE = datetime.today()


    if double_ma_or_single_ma:
        final_wallet = fonctions.compute_buy_and_sell_gains(initial_wallet, rates, buy_and_sell_points, ASSET, afficher=False)
    else:
        final_wallet = fonctions.compute_buy_and_sell_gains(initial_wallet,rates,buy_and_sell_points,ASSET,False)

    fonctions.final_print(params,rates,final_wallet,initial_wallet,new_rate_value,last_rate_value,buy_and_sell_points,price_of_order,first_rate_value,first_rate_date,price_of_sell,price_of_buy,last_side,nb_tours,nb_tour_buy,last_side_in_buy)
    
    

    """
    buy_and_sell_p = list()
    
    for i in buy_and_sell_points:
        buy_and_sell_p.append((datetime.strftime(i[0], "%Y-%m-%d %H:%M:%S"), i[1]))
    ma_l = []
    for i in ma_list[:-2]:
        for j in i[0]:
            m = []
            for k in j:
                print("zzzzzzzzzz")
                m.append({k["date": datetime.strftime(k["date"], "%Y-%m-%d %H:%M:%S")]})
            ma_l.append(m)
    r = rates.copy()
    rates_str = []
    for i in r:
        d = i["date"].split("T")
        dd = " ".join(d)
        i["date"] = dd
    print(len(ma_l), "rrr")

    fonctions.show_graphique(ASSET,r, ma_l, TOLERANCE_solo,buy_and_sell_p)
    """