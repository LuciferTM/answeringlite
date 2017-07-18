# -*- coding:utf-8 -*-
from django.conf.urls import patterns, url
from wechat.views import WechatLinkIn

urlpatterns = patterns('wechat.views',
        url("^link-in/$", WechatLinkIn.as_view()),
)