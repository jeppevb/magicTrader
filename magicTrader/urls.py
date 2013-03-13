from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from traders import views
from cards import views

urlpatterns = patterns('',
    url(r'^dispatch/$', 'traders.views.traderDispatcher', name='traderDispatcher'),
    url(r'^binder/(.+)[/$]', 'traders.views.updatebinder', name='binder update'),
    url(r'^gathercard/(.+?)[/$]', 'cards.views.gatherCard', name='gather card'),
    url(r'^card/(.+)[/$]', 'cards.views.getCard', name='get card'),
    url(r'^cards/(.*?)[/$]', 'cards.views.cardList', name='list cards'),
    url(r'^fiximages[/$]', 'cards.views.fixImages', name='fix cards and sets'),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    
)
if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))