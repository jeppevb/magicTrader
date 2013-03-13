from django.http import HttpResponse, HttpResponseNotFound
from django.template import RequestContext, loader
import base64,urllib,hmac,hashlib
import json as JSON
from models import Trader, BinderCard, WishListCard, Card

from django.views.decorators.csrf import csrf_exempt                                          

@csrf_exempt
def traderDispatcher(request, method = None):
    if request.method == 'GET':
        return HttpResponse(u'<script type="text/javascript">window.top.location.href = "https://www.facebook.com/dialog/oauth?client_id=213751205416235&redirect_uri=https://apps.facebook.com/magictrade";</script>')            
    elif request.method == 'POST':
        signature = base64.urlsafe_b64decode((request.POST['signed_request'].partition('.')[0] + '==').encode("utf-8"))
        rawdata = request.POST['signed_request'].partition('.')[2]
        jsondata = JSON.loads(base64.urlsafe_b64decode((rawdata + '==').encode("utf-8")))
        if 'user_id' not in jsondata:
            return HttpResponse(u'<script type="text/javascript">window.top.location.href = "https://www.facebook.com/dialog/oauth?client_id=213751205416235&redirect_uri=https://apps.facebook.com/magictrade";</script>')
        if jsondata['algorithm'].upper() != 'HMAC-SHA256':
            return HttpResponseNotFound('Unknown algorithm. Expected HMAC-SHA256')
        else:
            expectedSignature = hmac.new('cbf6e8d1d36a7a252dfd425c1610a868',rawdata,hashlib.sha256).digest()
            if signature != expectedSignature:
                return HttpResponseNotFound('Wrong')
        return traderIndex(request, jsondata['user_id'])
    
def traderIndex(request, userid):
    template = loader.get_template('trader/index.html')
    if Trader.objects.filter(fbuserid=userid).count() < 1:
        t = Trader(fbuserid=userid)
        t.save()
    trader = Trader.objects.get(fbuserid=userid)
    rq = RequestContext(request, {'trader':t.id})
    return HttpResponse(template.render(rq))
    
def traderGet(request, userid, entity):
    if entity == 'binder':
        return HttpResponse(JSON.dumps(BinderCard.objects.filter(binder__trader__fbuserid = userid)))
    elif entity == 'wishlist':
        return HttpResponse(JSON.dumps(WishListCard.objects.filter(wishlist__trader__fbuserid = userid)))
    