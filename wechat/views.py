# -*- coding:utf-8 -*-
import hashlib
from django.http import HttpResponse
from rest_framework.parsers import XMLParser
from rest_framework.views import APIView
from util.log_helper import gikoo_logger
from util.const import WECHAT
from wechat.message_util import MessageProcessor, answerMessageProcessor
logger = gikoo_logger()

#XMLParser supports only 'application/xml'
class TextXMLParser(XMLParser):
    media_type = 'text/xml'

'''公众号服务器入口 '''
class WechatLinkIn(APIView):
    allow_anonymous = True
    # parser_classes = (TextXMLParser,)#WSGIRequest
    token = WECHAT.TOKEN

    def get(self, request, *args, **kwargs):
        print 'WechatLinkIn get request: ', request.GET
        signature = request.GET.get('signature')
        timestamp = request.GET.get('timestamp')
        nonce = request.GET.get('nonce')
        echostr = request.GET.get('echostr')
        tmpList = [self.token, timestamp, nonce]
        tmpList.sort()
        tmpStr = "%s%s%s" % tuple(tmpList)
        hashstr = hashlib.sha1(tmpStr).hexdigest()
        if hashstr == signature:
            return HttpResponse(echostr)
        else:
            return HttpResponse('fail')

    def post(self, request, *args, **kwargs):
        print 'WechatLinkIn post request: ', request.DATA
        try:
            msg = request.DATA
            #正常处理
            resp = answerMessageProcessor.process_message(msg)
            return HttpResponse(resp)
        except Exception,e:
            print e
            return HttpResponse('fail')