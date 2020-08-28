from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class APILog(models.Model):
    ip = models.GenericIPAddressField()
    response = models.ForeignKey("api.CheckDiscountLog", blank=True, null=True, on_delete=models.PROTECT)
    timeRequest = models.DateTimeField()
    timeResponse = models.DateTimeField()
    elapsedTime = models.DurationField()
    status = models.CharField(max_length=3)
    statusDetails = models.TextField()

class CheckDiscountLog(models.Model):
    customerID = models.CharField(max_length=256)
    discounted = models.BooleanField()
    tier = models.ForeignKey("api.TransactionTier", on_delete=models.PROTECT)
    transactionAmmount = models.PositiveIntegerField()
    discountedAmmount = models.PositiveIntegerField()
    transactionDateTime = models.DateTimeField()

class TransactionTier(models.Model):
    minimumTransaction = models.PositiveIntegerField()
    maximumTransaction = models.PositiveIntegerField()
    probability = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    discount = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])