from django.db import models


class Set(models.Model):
    name = models.CharField(max_length=255, unique=True)
    shortname = models.CharField(max_length=3, unique=True)
    def __unicode__(self):
        return name
    
class Card(models.Model):
    name = models.CharField(max_length=255, unique=True)
    sets = models.ManyToManyField('Set', through='CardSet', related_name='cards')
    def __unicode__(self):
        return self.name

class CardSet(models.Model):
    card = models.ForeignKey(Card)
    set = models.ForeignKey(Set)

class CardSetImage(models.Model):
    cardid = models.CharField(max_length=64)
    cardset = models.ForeignKey(CardSet, related_name='cardsetimages')
        
class Community(models.Model):
    name = models.CharField(max_length=255, unique=True)
    
class Trader(models.Model):
    communities = models.ManyToManyField('Community', related_name='traders')
    fbuserid = models.CharField(max_length=100)
    bindercards = models.ManyToManyField('Card', through='BinderCard', related_name='bindertraders')
    wishlistcards = models.ManyToManyField('Card', through='WishListCard', related_name='wishlisttraders') 
    
class BinderCard(models.Model):
    trader = models.ForeignKey(Trader)
    card = models.ForeignKey(Card)
    amount = models.IntegerField()
    isFoil = models.BooleanField()
    preferedset = models.ForeignKey(Set)
    preferedimage = models.ForeignKey(CardSetImage)
    comment = models.TextField()
    
class WishListCard(models.Model):
    trader = models.ForeignKey(Trader)
    card = models.ForeignKey(Card)
    amount = models.IntegerField()
    isFoil = models.BooleanField()
    preferedset = models.ForeignKey(Set)
    preferedimage = models.ForeignKey(CardSetImage)
    comment = models.TextField()

