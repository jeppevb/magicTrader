from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound
from django.template import Context, loader
import base64, urllib, hmac, hashlib
import json as JSON
import re, os, thread

from traders.models import Card, Set, CardSet, CardSetImage
from django.views.decorators.csrf import csrf_exempt                                          
import urllib2
from django.utils.encoding import iri_to_uri
import xml.etree.ElementTree as ET

def cardList(request, prefix):
    return HttpResponse(JSON.dumps(list(Card.objects.filter(name__icontains=prefix).values_list('name', flat=True))))

def cardList(request, prefix):
    return HttpResponse(JSON.dumps(list(Card.objects.filter(name__icontains=prefix).values_list('name', flat=True))))


#get card and set from gatherer
def gatherCard(request, cardname):
    #search for the name of the card and save the resuktubg htmldok in html
    req = urllib2.urlopen('http://gatherer.wizards.com/Pages/Search/Default.aspx?output=compact&name=+[' + iri_to_uri(cardname) + ']')
    encoding = req.headers['content-type'].split('charset=')[-1]
    html = unicode(req.read(), encoding)
    #check ro see if the result redirected to the list of possible matches
    cardidmatch = re.search('onclick="return CardLinkAction\(event, this, \'SameWindow\'\);" href="\.\./Card/Details\.aspx\?multiverseid=([0-9]+)">(' + cardname + ')</a>', html, re.IGNORECASE)
    if (not(cardidmatch)):
        #if it did not we check to see if the result redirected to the detail page
        detailmatch = re.search('<div id="ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_nameRow" class="row">[^<]*<div class="label">\s*Card Name:</div>[^<]*<div class="value">\s*(' + cardname + ')</div>\s*</div>', html, re.IGNORECASE)
        if (not(detailmatch)):
            #if neither occured the name we searched for does not exist
            return HttpResponseNotFound()
        else:
            #if we are on the detailpage the real name of the card is saved as the search term could have any capitalization 
            realCardName = detailmatch.group(1)
    else:
        #if we were redirected to a list of matches we chose the one with the exact name we searched for and save the html again
        req = urllib2.urlopen('http://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid=' + str(cardidmatch.group(1)))
        realCardName = cardidmatch.group(2)
        encoding = req.headers['content-type'].split('charset=')[-1]
        html = unicode(req.read(), encoding)
    # At this point we know that html holds the correct page
    primaryexp = re.search('ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_currentSetSymbol">\s+(.+?)</div>', html, re.DOTALL).group(1)
    # http://gatherer.wizards.com/Handlers/Image.ashx?type=symbol&set=GTC&size=large&rarity=C
    setregex = re.compile('<img title="(.+?)\s\(.+?set=(...)', re.DOTALL)
    prisetname = setregex.search(primaryexp).group(1)
    prisetshort = setregex.search(primaryexp).group(2)
    cardid = re.search('<img src=.+?multiverseid=([0-9]+)&amp;type=card" id="ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_cardImage"', html, re.DOTALL).group(1)
    #if the card is in only one set this next match will fail and we will only get that one relation and download only the image of the card and the set if necessary
    try:
        otherexp = re.search('ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_otherSetsValue">\s+(.+?)</div>', html, re.DOTALL).group(1)
        pattern = '<a href="Details\.aspx\?multiverseid=([0-9]+)"><img title="(.+?) \(.+?\)" src="\.\./\.\./Handlers/Image\.ashx\?type=symbol&amp;set=(.+?)&amp;size=small&amp'
        imageregexp = re.compile(pattern, re.DOTALL)
        
        for m in imageregexp.finditer(otherexp):
            bindCardSetImage(realCardName, m.group(2), m.group(3), m.group(1))
    except AttributeError as e: 
        bindCardSetImage(realCardName, prisetname, prisetshort, cardid)
    return HttpResponse(JSON.dumps(realCardName))
        
def bindCardSetImage(cardname, setname, setshort, imageid):
    if Card.objects.filter(name=cardname).count() < 1:
        c = Card(name=cardname)
        c.save()
    else:
        c = Card.objects.get(name=cardname)
    if Set.objects.filter(name=setname).count() < 1:
        s = Set(name=setname, shortname=setshort)
        thread.start_new_thread(downloadSet, (s.shortname,))
        s.save()
    else:
        s = Set.objects.get(name=setname)
    if CardSet.objects.filter(card=c, set=s).count() < 1:
        cs = CardSet(card=c, set=s)    
        cs.save()
    else:
        cs = CardSet.objects.get(card=c, set=s)
    if CardSetImage.objects.filter(cardset=cs, cardid=imageid).count() < 1:
        csi = CardSetImage(cardset=cs, cardid=imageid)
        thread.start_new_thread(downloadCard,(imageid,))
        csi.save() 
    
def downloadSet(shortname):
    if not(os.path.exists(settings.MEDIA_ROOT + 'sets/' + shortname + '.jpg')):
        f = urllib2.urlopen('http://gatherer.wizards.com/Handlers/Image.ashx?type=symbol&set=' + shortname + '&size=large&rarity=C')
        data = f.read()
        with open(settings.MEDIA_ROOT + 'sets/' + shortname + '.jpg', "wb") as code:
            code.write(data)

def downloadCard(cardid):
    if not(os.path.exists(settings.MEDIA_ROOT + 'cards/' + cardid + '.jpg')):
        f = urllib2.urlopen('http://gatherer.wizards.com/Handlers/Image.ashx?multiverseid=' + cardid + '&type=card')
        data = f.read()
        with open(settings.MEDIA_ROOT + 'cards/' + cardid + '.jpg', "wb") as code:
            code.write(data)    
