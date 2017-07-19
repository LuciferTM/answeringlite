# -*- coding:utf-8 -*-
BASEFILE_PATH = "/Users/lucifer/github/answeringlite/answeringlite_util/answeringlite"
RAWFILE_PATH = BASEFILE_PATH
CLEANFILE_PATH = "cleaned"

class CONST:
    class ConstError(TypeError): pass

    def __setattr__(self, name, value):
        if self.__dict__.has_key(name):
            raise self.ConstError, "Can't rebind const(%s)" % name
        self.__dict__[name] = value


class WECHAT(CONST):
    WECHAT_NAME = u'青年派'
    TOKEN = ''
    APP_ID = ''
    APP_SECRET = ''
    APP_MCHID = ''

    BASE_PATH = ''
    API_KEY_PATH = BASE_PATH + ''
    SSL_KEY_PATH = BASE_PATH + ''
    SSL_CERT_PATH = BASE_PATH + ''

    EMPLOYEE_WISHING = u'每天分享就有机会拿最高50元的分享奖金！'
    EMPLOYEE_ACT_NAME = u'随时转发现金你拿'
    EMPLOYEE_REMARK = u'好朋友就要一起工作！第一时间分享招聘信息给TA吧！'


# class WECHAT(CONST):
#     WECHAT_NAME = u'我的库工作'
#     TOKEN = 'gikoomlp122306'
#     APP_ID = 'wx31a24c5111cc84e2'
#     APP_SECRET = '62659dd580506e5f13f76b1e79025ce3'
#     APP_MCHID = '1269893901'
#
#     BASE_PATH = '/home/gikoo/product/iap/GiKoo3/cert/wechat'
#     API_KEY_PATH = BASE_PATH + '/api_key.txt'
#     SSL_KEY_PATH = BASE_PATH + '/apiclient_key.pem'
#     SSL_CERT_PATH = BASE_PATH + '/apiclient_cert.pem'
#
#     EMPLOYEE_WISHING = u'每天分享就有机会拿最高50元的分享奖金！'
#     EMPLOYEE_ACT_NAME = u'随时转发现金你拿'
#     EMPLOYEE_REMARK = u'好朋友就要一起工作！第一时间分享招聘信息给TA吧！'