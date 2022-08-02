import json
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs

from mainapp.views import stockSelector
from asgiref.sync import sync_to_async,async_to_sync
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from .models import StockDetails

class stockConsumer(AsyncWebsocketConsumer):
    @sync_to_async
    def addCeleryBeat(self, stockselector):
        task= PeriodicTask.objects.filter(name='every-15-seconds')
        if len(task)>0:
            task=task.first()
            args=json.loads(task.args)
            args=args[0]
            for stock in stockselector:
                if stock not in args:
                    args.append(stock)
            task.args=json.dumps([args])
            task.save()
        else:
            schedule,created=IntervalSchedule.objects.get_or_create(every=15, period=IntervalSchedule.SECONDS)
            task=PeriodicTask.objects.create(interval=schedule, name='every-15-seconds',task='mainapp.tasks.update_stock',args=json.dumps([stockselector]))
        print(stockselector,json.dumps([stockselector]))

    @sync_to_async
    def addtostockdetail(self, stockselector):
        user=self.scope['user']
        for i in stockselector:
            stock, created= StockDetails.objects.get_or_create(stock=i)
            stock.user.add(user)



    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'stock_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        #Parse QueryString
        query_params= parse_qs(self.scope['query_string'].decode())
        print(query_params)
        stockselector =query_params['stockselector']
        print(stockselector)

        # add to celery beat
        await self.addCeleryBeat(stockselector)

        # add user to stock detail
        await self.addtostockdetail(stockselector)

        await self.accept()
    @sync_to_async
    def helper_func(self):
        user =self.scope['user']
        stocks =StockDetails.objects.filter(user__id=user.id)
        task=PeriodicTask.objects.get(name='every-15-seconds')
        args=json.loads(task.args)
        args=args[0]
        for i in stocks:
            print(i.stock,args,"celery is stupid")
            i.user.remove(user)
            if i.user.count()==0:
                args.remove(i.stock)
                i.delete()
        if args==None:
            args=[]
        if len(args)==0:
            task.delete()
        else:
            task.args=json.dumps([args])
            task.save()

        
    async def disconnect(self, close_code):
        await self.helper_func()
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'stockUpdate',
                'message': message
            }
        )
    @sync_to_async
    def selectUserStocks(self):
        user=self.scope['user']
        user_stocks= user.stockdetails_set.values_list('stock', flat = True)
        return list(user_stocks)


    # Receive message from room group
    async def stockUpdate(self, event):
        message = event['message'].copy()
        user_stocks = await self.selectUserStocks()
        keys=message.keys()
        for key in list(keys):
            if key not in user_stocks:
                del message[key]
        # Send message to WebSocket
        await self.send(text_data=json.dumps(message))