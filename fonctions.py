from datetime import date, timedelta, datetime
from binance.client import Client
import json
import matplotlib.pyplot as plt
import process_ma_solo
import pandas as pd

def get_client(KEYS):
    return Client(KEYS[0], KEYS[1])

def get_account_infos_from_API(rates, KEYS):
    client = get_client(KEYS)
    account_infos = client.get_account()
    balances = (account_infos["balances"])
    for i in balances:
        if float(i["free"]) or float(i["locked"]):
            print('\nasset:', i["asset"], "\nfree:", i["free"], "soit",round(float(i["free"])*rates[-1]["value"], 3), "€ \nlocked:", i["locked"], "soit",round(float(i["locked"])*rates[-1]["value"], 3), "€\n")
 
def create_base_rates_file(params, client):
    
    rates = list()
    data = Client.get_klines(self=client,symbol=params["ASSET"], interval=Client.KLINE_INTERVAL_5MINUTE, limit=1000)
    for i in data:
        rates.append({"date": datetime(1970,1,1,0,0,0) + timedelta(milliseconds=i[0]), "value": float(i[1])})
    """
    filename = params["ASSET"] + "_" + params["INTERVALS"] + ".json"
    f = open(filename, "w")
    f.write(json.dumps(rates))
    f.close()
    """
    return rates


def create_base_rates_file_and_get_client(params):
    client = get_client(params["KEYS"])
    rates = create_base_rates_file(params, client)
    return rates, client

def load_rates_from_file(params):
    filename = params["ASSET"] + "_" + params["INTERVALS"] +".json"
    f = open(filename, "r")
    rates = json.loads(f.read())
    for i in rates:
        d_h = i["date"].split(" ")
        d = d_h[0].split("-")
        h = d_h[1].split(":")
        date_object = datetime(int(d[0]), int(d[1]), int(d[2]), int(h[0]), int(h[1]), int(h[2]))
        i["date"] = date_object
    return rates 

def get_current_rate(params, last_rate_date):
    client = get_client(params["KEYS"])
    #last_rate_date_str = datetime.strftime(last_rate_date)
    new_rate =  client.get_historical_klines(params["ASSET"], Client.KLINE_INTERVAL_5MINUTE, "2 day ago UTC")
    return new_rate

def compute_moving_average_of_rates_data(rates, days_interval):
    s = 0
    averages = list()
    for i in range(len(rates)):
        rate = rates[i]
        s += rate["value"]
        if i >= days_interval:
            s -= rates[i-days_interval]["value"]
            a = s / days_interval
        else:
            a = s / (i+1)
        averages.append({"date": rate["date"], "value": a})
    
    return averages

def compute_buy_and_sell_points_from_ma(short_ma, long_ma, threshold_percent):
    #[("date_str", buy_mode)] buy_mode = True (achat) / False (vente)
    buy_mode = True
    points = list()
    for i in range(len(short_ma)):
        #print(long_ma[i]["date"])
        date_str = short_ma[i]["date"]
        sma_value = short_ma[i]["value"]
        lma_value = long_ma[i]["value"]
        #print("zzzzzzzzzzzzzz",lma_value, type(lma_value),type(threshold_percent),threshold_percent)
        mult = threshold_percent*lma_value/100
        if buy_mode: #on cherche à acheter
            if sma_value > lma_value+mult:
                points.append((date_str, buy_mode))
                buy_mode = False
        else: # on cherche à vandre
            if sma_value < lma_value-mult:
                points.append((date_str, buy_mode))
                buy_mode = True
    return points

def get_rate_value_for_date_str(rates, date_str):
    for i in rates:
        
        if i["date"] == date_str:
            
            return i["value"]
    return None

def compute_buy_and_sell_gains(initial_wallet, rates, buy_and_sell_points, assets,afficher=True):
    current_wallet = initial_wallet
    last_wallet = 0
    shares = 0
    if buy_and_sell_points:
        if buy_and_sell_points[-1][-1]:
            buy_and_sell_points = buy_and_sell_points[:-1]
        for point in buy_and_sell_points:
            rate_value = get_rate_value_for_date_str(rates, point[0])
            if point[1]: # achat
                if afficher: print("Le", point[0]+timedelta(hours=1), ", j'achete pour", round(current_wallet),"$, à",str(rate_value)," en", assets.split("/")[0])
                
                shares = current_wallet / float(rate_value)
                last_wallet = current_wallet
                current_wallet = 0
            else:
                current_wallet = shares * rate_value

                if afficher: print("Le", point[0]+timedelta(hours=1), "je vend les ",assets.split("/")[0]," à",str(rate_value)," et je recupère", round(current_wallet),"$")
                if current_wallet > last_wallet:
                    percent = (current_wallet-last_wallet)*100/last_wallet
                    if afficher: print("Sois un gains de",round(percent, 2),"%\n")
                else:
                    percent = (last_wallet-current_wallet)*100/last_wallet
                    if afficher: print("Soit une perte de", round(percent, 2), "%\n")
                
                shares = 0
    return current_wallet


def compute_buy_and_sell_gains_from_test(initial_wallet, rates, buy_and_sell_points, assets,afficher=True):
    current_wallet = initial_wallet
    last_wallet = 0
    shares = 0
    if buy_and_sell_points:
        if buy_and_sell_points[-1][-1]:
            buy_and_sell_points = buy_and_sell_points[:-1]
        for point in buy_and_sell_points:
            rate_value = get_rate_value_for_date_str(rates, point[0])
            """
            d_h = point[0].split("T")
            d = d_h[0].split("-")
            h = d_h[1].split(":")
            date_object = datetime(int(d[0]), int(d[1]), int(d[2]), int(h[0]), int(h[1]), int(h[2]))
            """
            if point[1]: # achat
                if afficher: print("Le", point[0]+timedelta(hours=1), ", j'achete pour", round(current_wallet),"$, à",str(rate_value)," en", assets.split("/")[0])
                
                shares = current_wallet / float(rate_value)
                last_wallet = current_wallet
                current_wallet = 0
            else:
                current_wallet = shares * rate_value

                if afficher: print("Le", point[0]+timedelta(hours=1), "je vend les ",assets.split("/")[0]," à",str(rate_value)," et je recupère", round(current_wallet),"$")
                if current_wallet > last_wallet:
                    percent = (current_wallet-last_wallet)*100/last_wallet
                    if afficher: print("Sois un gains de",round(percent, 2),"%\n")
                else:
                    percent = (last_wallet-current_wallet)*100/last_wallet
                    if afficher: print("Soit une perte de", round(percent, 2), "%\n")
                
                shares = 0
    return current_wallet

def test_multple_averages(rates,ASSETS,MA_INTETVALS,initial_wallet,ma_list,TOLERANCE):
    # test des moyennes
    final_wallet_for_intervals = list()  # 0: petite interval, 1: grand interval, 2: wallet
    nb=int()
    for k in TOLERANCE:
        for i in range(len(MA_INTETVALS)):
            for j in range(i+1, len(MA_INTETVALS)):
                nb+=1
                p = compute_buy_and_sell_points_from_ma(ma_list[i][0], ma_list[j][0], k)
                if p:
                    final_wallet = compute_buy_and_sell_gains(initial_wallet, rates, p, ASSETS, test=False)
                final_wallet_for_intervals.append(((str(k)+"%"),MA_INTETVALS[i], MA_INTETVALS[j], round(final_wallet, 2)))
            
    final_wallet_for_intervals.sort(key=lambda x: x[3])
    for final in final_wallet_for_intervals:
        print(final)
    print(nb)

def show_graphique_solo(ASSETS,rates, ma_solo, TOLERANCE_solo, buy_and_sell_points):
    
    rates_dates = [i["date"] for i in rates]
    rates_values = [i["value"] for i in rates]
    plt.ylabel(ASSETS)
    plt.plot(rates_dates, rates_values)
  
    plt.plot(rates_dates, [i["value"] for i in ma_solo])
    plt.grid()
    for i in process_ma_solo.compute_buy_and_sell_points_whith_solo_ma(rates, ma_solo, TOLERANCE_solo):
        print(i[0],i[1],i)
        plt.axvline(i[0])
    #[plt.axvline(i[0], color="y" if i[1] else "r") for i in buy_and_sell_points]

    plt.legend()
    plt.show()

def show_graphique(ASSETS,rates, ma_list, TOLERANCE_solo, buy_and_sell_points):
    
    rates_dates = [i["date"] for i in rates]
    rates_values = [i["value"] for i in rates]
    plt.ylabel(ASSETS)
    plt.plot(rates_dates, rates_values)
    """
    ma = []
    for i in ma_list[:-2]:
        for j in i:
            
            m_d = []
            m_v = []
            
            for k in j:
                print(k["date"])
                m_d.append(k["date"])
                m_v.append(k["value"])
            ma.append([m_d,m_v])
    """
    
    [plt.plot(i["date"],i["value"]) for i in ma_list[0]]
    [plt.plot(i["date"],i["value"]) for i in ma_list[1]]
    plt.grid()
    for i in buy_and_sell_points:
        
        plt.axvline(i[0], color= ("g" if i[1] else "r"))
    #[plt.axvline(i[0], color="y" if i[1] else "r") for i in buy_and_sell_points]

    plt.legend()
    plt.show()


def copy_to_file(params, rates):
    f = open(params["ASSET"]+"_"+params["INTERVALS"]+".json", "w")
    r = rates.copy()
    for i in r:
        d =datetime.strftime(i["date"], "%Y-%m-%dT%H:%M:%S")
        i["date"] = d
    f.write(json.dumps(rates))
    f.close()


def BUY(params):
        client = Client(params["KEYS"][0],params["KEYS"][1])
        account_infos = client.get_account()
        balances = (account_infos["balances"])
        for i in balances:
            if i["asset"] == params["BASE_COIN"]:
                sold_coin = i["free"]
            if i["asset"] == params["CHANGE_MONNAIE"]:
                sold_change = i["free"]
        print("sold_coin:", sold_coin, params["BASE_COIN"])
        print("sold_change:",sold_change, params["CHANGE_MONNAIE"])
        order = client.order_market_buy(symbol=params["ASSET"],quantity= int((int(float(sold_change)) * 0.97)/float(client.get_symbol_ticker(symbol=params["ASSET"])["price"])))
        price_of_buy = float(client.get_symbol_ticker(symbol=params["ASSET"])["price"])
        print("sold_coin:", sold_coin, params["BASE_COIN"])
        print("sold_change:", sold_change, params["CHANGE_MONNAIE"])
        print("BUY at", price_of_buy, "à",datetime.now())
        f = open(params["ASSET"] + "_" + params["INTERVALS"] +"_order_list"+ ".json", "a")
        order_ref = "\n\nBUY at "+ str(price_of_buy)+ " at "+str(datetime.now())
        f.write(order_ref)
        
        f.close()
        return price_of_buy
        

def SELL(params, price_of_buy):
    client = Client(params["KEYS"][0],params["KEYS"][1])
    account_infos = client.get_account()
    balances = (account_infos["balances"])
    for i in balances:
        if i["asset"] == params["BASE_COIN"]:
            sold_coin = i["free"]
        if i["asset"] == params["CHANGE_MONNAIE"]:
            sold_change = i["free"]
    print("sold_coin:", sold_coin, params["BASE_COIN"])
    print("sold_change:", sold_change, params["CHANGE_MONNAIE"])
    order = client.order_market_sell(symbol=params["ASSET"],quantity=int(float(sold_coin)))
    price_of_sell = float(client.get_symbol_ticker(symbol=params["ASSET"])["price"])
    print("sold_coin:", sold_coin, params["BASE_COIN"])
    print("sold_change:", sold_change, params["CHANGE_MONNAIE"])
    print("SELL at", price_of_sell, "à", datetime.now())
    f = open(params["ASSET"] + "_" + params["INTERVALS"] +"_order_list"+ ".json", "a")
    order_ref = "  ==>  SELL at "+ str(price_of_sell)+ " at "+ str(datetime.now())
    order_diff = "\n"+("+" if (price_of_sell - price_of_buy)*100/price_of_buy>0 else "") +str((price_of_sell - price_of_buy)*100/price_of_buy)
    f.write(order_ref)
    f.write(order_diff)
    f.close()
    return price_of_sell





def test_multiple_average(ASSETS,rates, TOLERANCE_test, MA_INTETVALS_test,initial_wallet):
        
    
    ma_list = [(compute_moving_average_of_rates_data(rates, i), i) for i in MA_INTETVALS_test]
    nb = 0
    final_wallet_for_intervals = list()  # 0: petite interval, 1: grand interval, 2: wallet
    for k in TOLERANCE_test:
        for i in range(len(MA_INTETVALS_test)):
            for j in range(i+1, len(MA_INTETVALS_test)):
                nb += 1
                p = compute_buy_and_sell_points_from_ma(ma_list[i][0], ma_list[j][0], k)
                if p:
                    final_wallet = compute_buy_and_sell_gains_from_test(initial_wallet, rates, p, ASSETS, afficher=False)
                final_wallet_for_intervals.append(((str(k)+"%"),MA_INTETVALS_test[i], MA_INTETVALS_test[j], round(final_wallet, 2)))
            
    final_wallet_for_intervals.sort(key=lambda x: x[3])
    return final_wallet_for_intervals[-1]

def final_print(params,rates,final_wallet,initial_wallet,new_rate_value,last_rate_value,buy_and_sell_points,price_of_order,first_rate_value,first_rate_date,price_of_sell,price_of_buy,last_side,nb_tours,nb_tour_buy,last_side_in_buy):
    print("nombre de rates: ", len(rates),"\n")
    percent_since_initial_wallet = (final_wallet-initial_wallet)*100/initial_wallet
    print("date de debut de l'analyse:", str(params["START_DATE"]).split(".")[0], "\ndate de fin de l'analyse:", str(params["STOP_DATE"]).split(".")[0],"\nportefeuille de debut de l'analyse:",initial_wallet, "\nportefeuille de fin de l'analyse:",round(final_wallet, 3)," ==> ",("+" if percent_since_initial_wallet>0 else "")+str(round(percent_since_initial_wallet, 3)), "%")
    print("\nnombre de trades:",len(buy_and_sell_points)/2,"soit",len(buy_and_sell_points)/(len(rates)/(24*12/24)),"ordres/heures")

    copy_to_file(params, rates)
    
    print()
    percent = (new_rate_value - last_rate_value) * 100 / last_rate_value
    print("+" if percent > 0 else "", round(percent, 3), "%", "since the last rate  --- ", last_rate_value," ==> ", new_rate_value,"" ,params["CHANGE_MONNAIE"])
    last_order_value = float(price_of_order)
    percent_from_order = (new_rate_value - price_of_buy)*100/price_of_buy
    if buy_and_sell_points:
        print("+" if percent_from_order > 0 else "",round(percent_from_order, 3),"%", "since the last order  ==> ","BUY" if not last_side else "SELL" ,"--", price_of_buy, params["CHANGE_MONNAIE"],"-- "+str(buy_and_sell_points[-1][0] + timedelta(hours=1))," ==> ", (str(nb_tour_buy)+" interval(s) since"),("BUY" if last_side_in_buy else "SELL"), "points = ",buy_and_sell_points[-1][1])
    percent_from_firt_rate = (new_rate_value - first_rate_value)*100/first_rate_value
    print("+" if percent_from_firt_rate > 0 else "",round(percent_from_firt_rate, 3),"%", "since the",first_rate_date+timedelta(hours=1)," ==> ",first_rate_value, params["CHANGE_MONNAIE"],"\n")
    last_trade_percent = (price_of_sell-price_of_buy)*100/price_of_buy
    print("last trade:", "+" if last_trade_percent > 0 else "",round(last_trade_percent, 3),"%  --- ", price_of_buy," ==> ", price_of_sell,params["ASSET"])
    #print((TOLERANCE,"%", MA_INTETVALS) if double_ma_result > solo_ma_result else (str(TOLERANCE_solo)+"% "+str(ma_interval_solo)))
    
    print("\nNombres de tours:",nb_tours)
    print(str(datetime.now()).split(".")[0])

def compute_points(rates, short_ma, long_ma, TOLERANCE=0.1):
    buy_mode = True
    points = list()
    price_of_buy = float()
    list_of_price = list()
    max_buy_rate = float()
    for i in range(len(short_ma)):
        date_str = short_ma[i]["date"]
        sma_value = short_ma[i]["value"]
        lma_value = long_ma[i]["value"]
        mult = TOLERANCE*lma_value/100

        if buy_mode:
            if sma_value > lma_value+mult:
                points.append((date_str, buy_mode))
                buy_mode = False
                price_of_buy = rates[i]["value"]
                

        else: # on cherche à vendre
            if sma_value < lma_value-mult:
                points.append((date_str, buy_mode))
                buy_mode = True

            

    return points


def get_moving_average_exponentiel(rates, alp):
    arr = [i["value"] for i in rates]
    
    # Convert array of integers to pandas series
    numbers_series = pd.Series(arr)
    
    # Get the moving averages of series
    # of observations till the current time
    moving_averages = numbers_series.ewm(alpha=alp, adjust=False).mean()
    
    # Convert pandas series back to list
    moving_averages_list = moving_averages.tolist()
    ema = list()
    for i in moving_averages_list:
        ema.append({"value": i})
    if len(rates) == len(moving_averages_list):
        
        for i in range(len(rates)):
            ema[i]["date"] = rates[i]["date"]

    return ema

def decale_ema(long_ma, rates):
    l = long_ma[:-6]
    l.insert(0, {"date": long_ma[-1]["date"], "value": long_ma[-1]["value"]})
    l.insert(0, {"date": long_ma[-2]["date"], "value": long_ma[-2]["value"]})
    l.insert(0, {"date": long_ma[-3]["date"], "value": long_ma[-3]["value"]})
    l.insert(0, {"date": long_ma[-4]["date"], "value": long_ma[-4]["value"]})
    l.insert(0, {"date": long_ma[-5]["date"], "value": long_ma[-5]["value"]})
    l.insert(0, {"date": long_ma[-6]["date"], "value": long_ma[-6]["value"]})
    for i in range(len(rates)):
        l[i]["date"]=rates[i]["date"]
    return l