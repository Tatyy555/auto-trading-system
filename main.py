import pandas as pd
import time
import logging
import sys
import talib
import numpy as np

from coincheck import Coincheck
import settings
from utils.notify import send_message_to_line


logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

if __name__ == "__main__":

    # 何秒毎にデータを取りに行くか。
    interval = 1 
    # 保有JPYの何％を使うか。
    use_percent = 1
    # レートが何％減ったら強制的に売るか。
    stop_limit = 0.95
    # 何個分のでBBBandを計算するか
    n = 20
    # BBBandの標準偏差はどうするか。
    k = 2.4
    # 何個のデータが集まったら半分消すか。
    delete_time = 100

    send_message_to_line('ビットコインの自動売買を開始します...')

    coincheck = Coincheck(access_key=settings.access_key, secret_key=settings.secret_key)
    list = []
   
    while True:
        time.sleep(interval)
               
        try:
            amount = float(coincheck.get_balance() * use_percent)
            positions = coincheck.position

            list.append(coincheck.last)
            df = pd.DataFrame(data=list,columns=['price'])

            up, mid, down = talib.BBANDS(np.asarray(list), n, k, k, 0)
            df['bb_up'] = up
            df['mid'] = mid 
            df['bb_down'] = down 

            logger.info(f'action=check df status=run df={df}')

            i = len(list)-1
            if len(list) >= n:



                if df['bb_up'].iloc[i-1] < df['price'].iloc[i-1] and df['bb_up'].iloc[i] > df['price'].iloc[i]:
                    if 'btc' in positions.keys():
                        params = {
                            'pair': 'btc_jpy',
                            'order_type': 'market_sell',
                            'amount': positions['btc']
                        }
                        r = coincheck.order(params)
                        send_message_to_line(f'売ることができました。{r}')
                        print('exit', r)
                    else:
                        send_message_to_line(f'売りタイミングですが、btcがないので売れません。ask_rate:{coincheck.ask_rate} current_rate:{coincheck.last} 増減幅:{int((coincheck.last/coincheck.ask_rate-1)*100)}%')       
                
                if df['bb_down'].iloc[i-1] > df['price'].iloc[i-1] and df['bb_down'].iloc[i] < df['price'].iloc[i]:
                    if not positions.get('btc'):
                        params = {
                            'pair': 'btc_jpy',
                            'order_type': 'market_buy',
                            'market_buy_amount': amount
                        }
                        r = coincheck.order(params)
                        send_message_to_line(f'買うことができました。{r}')
                        print('exit', r)
                    else:
                        send_message_to_line(f'買いタイミングですが、btcを持っているので買えません。ask_rate:{coincheck.ask_rate} current_rate:{coincheck.last} 増減幅:{int((coincheck.last/coincheck.ask_rate-1)*100)}%') 

            if len(list) >= delete_time:
                send_message_to_line(f'データの個数が{delete_time}に達したので半分削除します。なお、現在のボジションは以下の通りです。{positions}。また、現在の状況は以下の通りです。ask_rate:{coincheck.ask_rate} current_rate:{coincheck.last} 増減幅:{int((coincheck.last/coincheck.ask_rate-1)*100)}%')
                del list[0:int(delete_time/2)]

        except:
           send_message_to_line(f'Connection Errorが発生したため、Coincheckに接続し直します。')
           coincheck = Coincheck(access_key=settings.access_key, secret_key=settings.secret_key)
           continue
        




