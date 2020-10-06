from django import forms
from .models import APILog, CheckDiscountLog, TransactionTier

class addAPILog(forms.ModelForm):
    class Meta:
        model = APILog
        fields = '__all__'

class addCheckDiscountLog(forms.ModelForm):
    class Meta:
        model = CheckDiscountLog
        fields = '__all__'