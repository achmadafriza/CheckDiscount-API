from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core import validators, serializers
from django.urls import reverse
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import json
from random import choice, random
import datetime
from ipware import get_client_ip
import hashlib

from .models import APILog, CheckDiscountLog, TransactionTier
from .forms import addAPILog, addCheckDiscountLog

def encryptString(s):
    return hashlib.sha256(s.encode()).hexdigest()

@csrf_exempt
def checkDiscount(request):
    timeRequest = datetime.datetime.now()
    requestdata = json.loads(request.body.decode('utf-8'))
    if request.method == 'POST':
        if request.POST.get('customerid') and request.POST.get('ammount') and request.POST.get('time'):
            try:
                time = datetime.datetime.strptime(request.POST.get('time'), '%d/%m/%Y %H:%M:%S::%f')
            except ValueError:
                log = {
                    "status": '409',
                    "statusDetails": "Incorrect DateTime Format, %d/%m/%Y %H:%M:%S::%f"
                }
                timeResponse = datetime.datetime.now()
                log.update(logAPI(request, log, timeRequest, timeResponse))
                return JsonResponse(log, status=409)
            
            cIDEncrypt = encryptString(request.POST.get('customerid'))
            ammount = request.POST.get('ammount')

            # Check for Existing Transaction
            try:
                discount = CheckDiscountLog.objects.get(customerID=cIDEncrypt, transactionAmmount=ammount, transactionDateTime=time)
                obj = serializers.serialize('json', [discount, ])
                
                log = {
                    "status": '200',
                    "statusDetails": "Transaction already has discount.",
                }
                timeResponse = datetime.datetime.now()
                log.update(logAPI(request, log, timeRequest, timeResponse, discount))
                return JsonResponse({**log, 'response': obj}, status=409)
            except CheckDiscountLog.DoesNotExist:
                pass

            validTiers = TransactionTier.objects.filter(maximumTransaction__gte=ammount, minimumTransaction__lte=ammount)
            try:
                tier = choice(validTiers)
            except IndexError:
                log = {
                    "status": '200',
                    "statusDetails": f"There's no valid tier for {ammount}"
                }
                timeResponse = datetime.datetime.now()
                log.update(logAPI(request, log, timeRequest, timeResponse))
                return JsonResponse(log, status=200)

            if random() <= tier.probability/100:
                # True
                data = {
                    'customerID': cIDEncrypt,
                    'discounted': True,
                    'tier': tier,
                    'transactionAmmount': request.POST.get('ammount'),
                    'discountedAmmount': request.POST.get('ammount') * tier.discount / 100,
                    'transactionDateTime': time
                }
                
                formCheckDiscountLog = addCheckDiscountLog(data)
                if formCheckDiscountLog.is_valid():
                    response = formCheckDiscountLog.save()
                else:
                    log = {
                    "status": '409',
                    "statusDetails": "Error on Saving Check Discount."
                    }
                    timeResponse = datetime.datetime.now()
                    log.update(logAPI(request, log, timeRequest, timeResponse, response))
                    return JsonResponse(log, status=409)
                
                log = {
                    "status": '200',
                    "statusDetails": "Valid for Discount, OK."
                }
                timeResponse = datetime.datetime.now()
                log.update(logAPI(request, log, timeRequest, timeResponse, response))
                return JsonResponse(log, status=200)
        else:
            log = {
                    "status": '409',
                    "statusDetails": "Wrong Format",
                    "customerid": request.POST.get('customerid'),
                    "ammount": request.POST.get('ammount'),
                    "time": request.POST.get('time')
            }
            timeResponse = datetime.datetime.now()
            log.update(logAPI(request, log, timeRequest, timeResponse))
            return JsonResponse(log, status=409)
    else:
        log = {
                    "status": '405',
                    "statusDetails": "Wrong Access"
        }
        timeResponse = datetime.datetime.now()
        log.update(logAPI(request, log, timeRequest, timeResponse))
        return JsonResponse(log, status=405)

def logAPI(request, context, timeRequest, timeResponse, response=None):
    ip, isRoutable = get_client_ip(request)
    data = {
        'ip': ip,
        'response': response,
        'timeRequest': timeRequest,
        'timeResponse': timeResponse,
        'elapsedTime': timeResponse-timeRequest,
        **context
    }

    formlogAPI = addAPILog(data) 
    if formlogAPI.is_valid():
        formlogAPI.save()
        return {'logAdded': True}
    else:
        return {'logAdded': False}