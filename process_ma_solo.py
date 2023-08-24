from datetime import timedelta



def compute_buy_and_sell_points_whith_solo_ma(rates, ma_solo, tolerance):
    buy_mode = True
    buy_and_sell_points_solo = []
    for i in range(len(ma_solo)):
        if ma_solo[i]["value"]  < rates[i]["value"] and buy_mode:
            buy_and_sell_points_solo.append((rates[i]["date"], True))
            buy_mode = False
        elif ma_solo[i]["value"] -(ma_solo[i]["value"] * tolerance / 100) > rates[i]["value"] and not buy_mode:
            buy_and_sell_points_solo.append((rates[i]["date"], False))
            buy_mode = True
    return buy_and_sell_points_solo

def get_rate_value_for_date_str(rates, date_str):
    for i in rates:
        if i["date"] == date_str:
            return i["value"]
    return None

def compute_buy_and_sell_gains(initial_wallet, rates, buy_and_sell_points, assets,test=True):
    buy_and_sell_copy = buy_and_sell_points.copy()
    current_wallet = initial_wallet
    last_wallet = 0
    shares = 0
    if buy_and_sell_copy:
        if buy_and_sell_copy[-1][-1]:
            buy_and_sell_copy = buy_and_sell_copy[:-1]
        for point in buy_and_sell_copy:
            rate_value = get_rate_value_for_date_str(rates, point[0])
            if point[1]: # achat
                if test: print("Le", point[0]+timedelta(hours=1), ", j'achete pour", round(current_wallet),"$ à",str(rate_value)," en", assets.split("/")[0])
                shares = current_wallet / rate_value
                last_wallet = current_wallet
                current_wallet = 0
            else:
                current_wallet = shares * rate_value

                if test: print("Le", point[0]+timedelta(hours=1), "je vend les ",assets.split("/")[0]," à",str(rate_value)," et je recupère", round(current_wallet),"€")
                if current_wallet > last_wallet:
                    percent = (current_wallet-last_wallet)*100/last_wallet
                    if test: print("Sois un gains de",round(percent, 2),"%\n")
                else:
                    percent = (last_wallet-current_wallet)*100/last_wallet
                    if test: print("Soit une perte de", round(percent, 2), "%\n")
                
                shares = 0
    return current_wallet

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