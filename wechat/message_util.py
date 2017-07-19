# -*- coding:utf-8 -*-
from util.const import BASEFILE_PATH, CLEANFILE_PATH, RAWFILE_PATH
from answeringlite_util.util import query_question
FORMAT_TEXT_RESPONSE = '<xml> <ToUserName>%s</ToUserName>\
        <FromUserName>%s</FromUserName>\
        <CreateTime>%s</CreateTime><MsgType>text</MsgType>\
        <Content>%s</Content></xml>'

class MessageProcessor(object):
    processor = {}

    @staticmethod
    def add_processor(p, id):
        MessageProcessor.processor[id] = p
        return

    @staticmethod
    def process_message(msg):
        try:
            p = MessageProcessor.processor[msg['ToUserName']]
            return p.process_message(msg)
        except Exception,e:
            return None

class AnswerMessageProcessor(object):

    def process_message(self, msg):
        # openid = msg['FromUserName']
        openid = ""
        default_content = FORMAT_TEXT_RESPONSE % (openid, msg['ToUserName'], msg['CreateTime'], u"谢谢关注")
        if msg['MsgType'] == 'event':
            if msg['Event'] == 'query':
                return self.get_query_answer(msg) or default_content
        return default_content

    def get_query_answer(self, msg):
        query_str = msg.get('question',None)
        if not query_str:
            return None
        else:
            #TODO
            #这里需要区分是哪个公司那个文件，现在先使用小米的参数进行
            FilePath = BASEFILE_PATH
            return query_question(FilePath, query_str)


