from concurrent.futures import thread
from multiprocessing import context
from threading import Thread
from django.shortcuts import render, HttpResponse
from yahoo_fin.stock_info import  *
import time
import queue
from asgiref.sync import sync_to_async
# Create your views here.
@sync_to_async
def stockSelector(request):
    stock_setector= tickers_nifty50()
    context={'stock_setector':stock_setector}
    return render(request,'mainapp/stockselector.html', context)
@sync_to_async
def checkAuthenticated(request):
    if not request.user.is_authenticated:
        return False
    return True
async def stocktracker(request):
    is_logined = await checkAuthenticated(request)
    if not is_logined:
        return HttpResponse('Login First')
    #print(request)
    stockselector=request.GET.getlist('stockselector')
    #print(stockselector,request,len(stockselector))
    data={}
    #stockselector=['BAJAJFINSV.NS']
    available_stocks=tickers_nifty50()
    for i in stockselector:
        if i in available_stocks:
            pass
        else:
            return HttpResponse('ERROR')
    n_threads=len(stockselector)
    que=queue.Queue()
    thread_list=[]
    start=time.time()
    for i in range(n_threads):
        thread=Thread(target= lambda q, arg1: q.put({stockselector[i]: get_quote_table(arg1)}), args =(que, stockselector[i]))
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
    context={'data':data,'room_name':'track'}
    return render(request,'mainapp/stocktracker.html',context)
