from tabnanny import verbose
from django.db import models
from django.contrib.auth.models import User 

# Create your models here.
class StockDetails(models.Model):
    stock=models.CharField(max_length=225,unique=True)
    user=models.ManyToManyField(User)
    
    class Meta:
        verbose_name='Stock Details'
        verbose_name_plural='Stock Details'
