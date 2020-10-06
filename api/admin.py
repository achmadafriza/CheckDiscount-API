from django.contrib import admin
from api.models import APILog, CheckDiscountLog, TransactionTier

# Register your models here.
admin.site.register(APILog)
admin.site.register(CheckDiscountLog)
admin.site.register(TransactionTier)