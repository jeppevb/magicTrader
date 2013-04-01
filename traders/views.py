from django.http import HttpResponse, HttpResponseNotFound
from django.template import RequestContext, loader
import base64,urllib,hmac,hashlib
import json as JSON
from models import Trader, BinderCard, WishListCard, Card, Set, CardSetImage

from django.views.decorators.csrf import csrf_exempt                                          

@csrf_exempt
def traderDispatcher(request):
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
    
def userFromSig(sig):
    signature = base64.urlsafe_b64decode((sig.partition('.')[0] + '==').encode("utf-8"))
    rawdata = sig.partition('.')[2]
    jsondata = JSON.loads(base64.urlsafe_b64decode((rawdata + '==').encode("utf-8")))
    if 'user_id' not in jsondata:
        return None
    else:
        return jsondata['user_id']
        
def update(request, sig, data):
    user = userFromSig(sig)
    if user == None:
        return HttpResponseNotFound()
    else:
        jsondata = JSON.loads(base64.urlsafe_b64decode((data).encode("utf-8")))
        if jsondata['method'] == 'addToBinder':
            _trader = Trader.objects.get(fbuserid=user)
            _card = Card.objects.get(name=jsondata['cardname'])
            _amount = jsondata['amount']
            _isFoil = jsondata['foil']
            if jsondata['careSet']:
                _preferedset = Set.objects.get(name=jsondata['set'])
            else:
                _preferedset = None
            if jsondata['careIllu']:
                _preferedimage = CardSetImage.objects.get(cardid=jsondata['image'])
            else:
                _preferedimage = None
            _comment = jsondata['comment']
            BinderCard.objects.create(trader=_trader, card=_card, amount=_amount, isFoil=_isFoil, preferedset=_preferedset, preferedimage=_preferedimage, comment=_comment)
        elif jsondata['method'] == 'addToWishlist':
            _trader = Trader.objects.get(fbuserid=user)
            _card = Card.objects.get(name=jsondata['cardname'])
            _amount = jsondata['amount']
            _isFoil = jsondata['foil']
            if jsondata['careSet']:
                _preferedset = Set.objects.get(name=jsondata['set'])
            else:
                _preferedset = None
            if jsondata['careIllu']:
                _preferedimage = CardSetImage.objects.get(cardid=jsondata['image'])
            else:
                _preferedimage = None
            _comment = jsondata['comment']
            WishListCard.objects.create(trader=_trader, card=_card, amount=_amount, isFoil=_isFoil, preferedset=_preferedset, preferedimage=_preferedimage, comment=_comment)

def traderIndex(request, userid):
    template = loader.get_template('trader/index.html')
    if Trader.objects.filter(fbuserid=userid).count() < 1:
        t = Trader(fbuserid=userid)
        t.save()
    trader = Trader.objects.get(fbuserid=userid)
    sr = request.POST['signed_request']
    rq = RequestContext(request, {'magicstring':sr})
    return HttpResponse(template.render(rq))
    
def traderGet(request, userid, entity):
    if entity == 'binder':
        return HttpResponse(JSON.dumps(BinderCard.objects.filter(binder__trader__fbuserid = userid)))
    elif entity == 'wishlist':
        return HttpResponse(JSON.dumps(WishListCard.objects.filter(wishlist__trader__fbuserid = userid)))
    