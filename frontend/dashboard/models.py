from django.db import models


class Trade(models.Model):
    trade_datetime = models.DateTimeField('trade datetime')
    symbol = models.CharField(max_length=7)
    size = models.IntegerField(default=0)
    closed_pnl = models.FloatField(default=0.00000000)
    exchange_fee = models.FloatField(default=0.00000000)
    funding_fee = models.FloatField(default=0.00000000)
    realised_pnl = models.FloatField(default=0.00000000)

    def __str__(self):
        return self.trade_datetime


class Order(models.Model):
    order_datetime = models.DateTimeField('order datetime')
    order_id = models.CharField(max_length=40)
    cl_ord_id = models.CharField(max_length=40)
    symbol = models.CharField(max_length=7)
    side = models.CharField(max_length=4)
    order_type = models.CharField(max_length=20)
    price_ep = models.IntegerField('scaled order price')
    order_qty = models.IntegerField('order quantity')

    def __str__(self):
        return self.order_datetime
