from django.conf import settings
from django.contrib.auth import get_user_model
from celery import shared_task
from django.core.mail import send_mail
from stockapp import settings
from django.utils import timezone
from datetime import timedelta
from yahoo_fin.stock_info import  *
import time
import queue
from threading import Thread
from channels.layers import get_channel_layer
import asyncio
import simplejson as json
@shared_task(bind=True)
def update_stock(self, stockselector):
    data={}
    #stockselector=['BAJAJFINSV.NS']
    print(stockselector)
    available_stocks=tickers_nifty50()
    for i in stockselector:
        if i in available_stocks:
            pass
        else:
            stockselector.remove(i)
    n_threads=len(stockselector)
    que=queue.Queue()
    thread_list=[]
    start=time.time()
    for i in range(n_threads):
        thread=Thread(target= lambda q, arg1: q.put({stockselector[i]: json.loads(json.dumps(get_quote_table(arg1), ignore_nan=True))}), args =(que, stockselector[i]))
        thread_list.append(thread)
        thread_list[i].start()
    for thread in thread_list:
        thread.join()
    while not que.empty():
        result=que.get()
        data.update(result)
    #for i in stockselector:
    #    details=get_quote_table(i)
    #    data.update({i:details})
    end=time.time()
    timetaken=end-start
    print(timetaken)
    print(data)
    # send data to group
    channel_layer= get_channel_layer()
    loop = asyncio.new_event_loop()

    asyncio.set_event_loop(loop)
    loop.run_until_complete(channel_layer.group_send('stock_track', {
        'type': 'stockUpdate',
        'message':data,
    }))

    return 'Done'
    