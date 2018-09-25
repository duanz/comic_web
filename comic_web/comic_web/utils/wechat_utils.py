# -*- coding: utf-8 -*-

import time
import json
import random
import string
import urllib
import hashlib
import requests
import logging
import base64
from Crypto.Cipher import AES
import xml.etree.ElementTree as ETree

from comic_web.utils import time_lib
from django.conf import settings

from member.models import WeixinAuth


wx_app_id = settings.WX_CONF.get('AppID')  # 微信平台appid
wx_app_secret = settings.WX_CONF.get('AppSecret')
wx_miniapp_id = settings.WX_CONF.get('MiniAppID')  # 微信平台appid
wx_miniapp_secret = settings.WX_CONF.get('MiniAppSecret')
wx_mch_id = settings.WX_CONF.get('MchID')  # 微信支付商户号
wx_mch_key = settings.WX_CONF.get('MchKey')  # 微信支付密匙
wx_notify_url = settings.WX_CONF.get('NotifyUrl')
wx_app_host = settings.WX_CONF.get('AppHost')
wx_redirect_url = settings.WX_CONF.get('RedirectUrl')


def parse_xml(web_data):
    if len(web_data) == 0:
        return
    xml_data = ETree.fromstring(web_data)
    msg_type = xml_data.find('MsgType').text
    if msg_type == 'text':
        return ReceiveTextMsg(xml_data)
    elif msg_type == 'image':
        return ReceiveImageMsg(xml_data)


def get_code_url(state):
    """获取code的url"""
    dict = {'redirect_uri': wx_redirect_url}
    redirect_uri = urllib.urlencode(dict)
    author_get_code_url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&%s&response_type=code&scope=snsapi_bases&state=%s#wechat_redirect' % (wx_app_id, redirect_uri, state)
    # print '【微信网页授权】获取网页授权的code的url>>>>' + author_get_code_url
    return author_get_code_url


def get_auth_access_token(code):
    """通过code换取网页授权access_token"""
    url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code' % (wx_app_id, wx_app_secret, code)
    r = requests.get(url)
    # print '【微信网页授权】通过code换取网页授权access_token的Response[' + str(r.status_code) + ']'
    if r.status_code == 200:
        res = r.text
        # print '【微信网页授权】通过code换取网页授权access_token>>>>' , res
        json_res = json.loads(res)
        if 'access_token' in json_res.keys():
            return json_res
        elif 'errcode' in json_res.keys():
            errcode = json_res['errcode']
            logging.warning('get_auth_access_token error code: {0}'.format(errcode))


def get_open_auth_access_token(code):
    """通过code换取第三方网页授权access_token"""
    url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code' % (
        wx_app_id, wx_app_secret, code)
    r = requests.get(url)
    # print '【微信网页授权】通过code换取网页授权access_token的Response[' + str(r.status_code) + ']'
    if r.status_code == 200:
        res = r.text
        # print '【微信网页授权】通过code换取网页授权access_token>>>>' , res
        json_res = json.loads(res)
        if 'access_token' in json_res.keys():
            return json_res
        elif 'errcode' in json_res.keys():
            errcode = json_res['errcode']
            logging.warning('get_open_auth_access_token error code: {0}'.format(errcode))


def mini_app_get_openid_by_code(code):
    '''微信小程序通过code获取用户openid'''
    url = "https://api.weixin.qq.com/sns/jscode2session?appid={0}&secret={1}&js_code={2}&grant_type=authorization_code"
    new_url = url.format(wx_miniapp_id, wx_miniapp_secret, code)
    logging.warning('mini_app_get_openid_by_code url: {0}'.format(new_url))
    res = requests.get(new_url).json()
    logging.warning('mini_app_get_openid_by_code result: {0}'.format(res))
    return res


# 发送模版消息
def sen_template_msg(template_msg):
    access_token = get_access_token() if get_access_token() else ""
    result = requests.post(
        'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=' + access_token,
        json.dumps(template_msg, encoding='utf-8'))

    return result


def create_qr_code(scene_data, access_token, expire_seconds=2592000, action_name="QR_SCENE"):
    """创建二维码ticket"""
    url = "https://api.weixin.qq.com/cgi-bin/qrcode/create?access_token={}".format(access_token)
    data = {
        "expire_seconds": expire_seconds,
        "action_name": action_name,
        "action_info": {"scene": scene_data}
    }
    res = requests.post(url, data, timeout=5).json()
    return res


def miniapp_create_qr_code(scene_data, access_token, page="page/component/index/index"):
    """创建小程序二维码"""
    url = "https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token={}".format(access_token)
    data = {
        "scene": scene_data
        # "page": page
    }
    headers = {"Content-Type": "application/json"}
    res = requests.post(url, json.dumps(data), headers=headers, timeout=5)
    if 'json' in res.headers.get("content-type"):
        logging.warning(res.json())
    return res


class ReceiveMsg(object):
    def __init__(self, xmlData):
        self.ToUserName = xmlData.find('ToUserName').text
        self.FromUserName = xmlData.find('FromUserName').text
        self.CreateTime = xmlData.find('CreateTime').text
        self.MsgType = xmlData.find('MsgType').text
        self.MsgId = xmlData.find('MsgId').text


class ReceiveTextMsg(ReceiveMsg):
    def __init__(self, xmlData):
        ReceiveMsg.__init__(self, xmlData)
        self.Content = xmlData.find('Content').text.encode('utf-8')


class ReceiveImageMsg(ReceiveMsg):
    def __init__(self, xmlData):
        ReceiveMsg.__init__(self, xmlData)
        self.PicUrl = xmlData.find('PicUrl0').text
        self.MediaId = xmlData.find('mediaId').text


# ==========发送消息=========


class ReplyMsg(object):
    def __init__(self):
        pass

    def send(self):
        return "success"


class ReplyTextMsg(ReplyMsg):
    def __init__(self, toUserName, fromUserName, content):
        self.__dict = dict()
        self.__dict['ToUserName'] = toUserName
        self.__dict['FromUserName'] = fromUserName
        self.__dict['CreateTime'] = int(time.time())
        self.__dict['Content'] = content

    def send(self):
        XmlForm = """
        <xml>
        <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
        <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
        <CreateTime>{CreateTime}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{Content}]]></Content>
        </xml>
        """
        send_msg = XmlForm.format(**self.__dict)
        return send_msg


class ReplyImageMsg(ReplyMsg):
    def __init__(self, toUserName, fromUserName, mediaId):
        self.__dict = dict()
        self.__dict['ToUserName'] = toUserName
        self.__dict['FromUserName'] = fromUserName
        self.__dict['CreateTime'] = int(time.time())
        self.__dict['MediaId'] = mediaId

    def send(self):
        XmlForm = """
        <xml>
        <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
        <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
        <CreateTime>{CreateTime}</CreateTime>
        <MsgType><![CDATA[image]]></MsgType>
        <Image>
        <MediaId><![CDATA[{MediaId}]]></MediaId>
        </Image>
        </xml>
        """
        return XmlForm.format(**self.__dict)


def set_access_token():
    url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={0}&secret={1}".format(wx_miniapp_id, wx_miniapp_secret)
    res = requests.get(url, timeout=5).json()
    logging.warning(res)

    WeixinAuth.set_access_token(res)

    return res.get('access_token')


def get_access_token():
    weixin_obj = WeixinAuth.get_access_token()

    if weixin_obj:
        return weixin_obj.access_token
    else:
        access_token = set_access_token()
        return access_token


def set_js_ticket():
    url = "'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token={}&type=jsapi".format(get_access_token())
    res = requests.get(url, timeout=5).json()
    WeixinAuth.set_js_ticket(res)

    return res.get('ticket')


def get_js_ticket():
    weixin_obj = WeixinAuth.get_js_ticket()
    if weixin_obj:
        return weixin_obj.ticket
    else:
        js_ticket = set_js_ticket()
        return js_ticket


def get_jsjdk_config_data(url):
    url = wx_app_host + url
    js_ticket = get_js_ticket()
    timestamp = int(time.time())

    ret = {'nonceStr': create_nonce_str(), 'jsapi_ticket': js_ticket, 'timestamp': timestamp, 'url': url}

    string = '&'.join(['%s=%s' % (key.lower(), ret[key]) for key in sorted(ret)])
    ret['signature'] = hashlib.sha1(string).hexdigest()
    ret['appId'] = wx_app_id
    return ret


# 设置微信菜单
def set_menu(body):
    access_token = get_access_token() if get_access_token() else ""
    result = requests.post(
        'https://api.weixin.qq.com/cgi-bin/menu/create?access_token=' + access_token,
        json.dumps(body, ensure_ascii=False, encoding='utf-8'))
    return result


def create_nonce_str():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))


# ##############微信支付相关############
class WxPayError(Exception):
    def __init__(self, msg):
        super(WxPayError, self).__init__(msg)


class WxPay(object):
    def __init__(self, wx_app_id, wx_miniapp_id, wx_mch_id, wx_mch_key, wx_notify_url):
        self.opener = urllib.request.build_opener(urllib.request.HTTPSHandler())
        self.WX_APP_ID = wx_app_id
        self.WX_MINI_APP_ID = wx_miniapp_id
        self.WX_MCH_ID = wx_mch_id
        self.WX_MCH_KEY = wx_mch_key
        self.WX_NOTIFY_URL = wx_notify_url

    @staticmethod
    def user_ip_address():
        return None

    @staticmethod
    def nonce_str(length=32):
        char = string.ascii_letters + string.digits
        return "".join(random.choice(char) for _ in range(length))

    @staticmethod
    def to_utf8(raw):
        return raw.encode("utf-8") if isinstance(raw, str) else raw

    @staticmethod
    def to_dict(content):
        raw = {}
        root = ETree.fromstring(content)
        for child in root:
            raw[child.tag] = child.text
        return raw

    @staticmethod
    def random_num(length):
        digit_list = list(string.digits)
        random.shuffle(digit_list)
        return ''.join(digit_list[:length])

    def sign(self, raw):
        """
        生成签名
        参考微信签名生成算法
        https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=4_3
        """
        raw = [(k, str(raw[k]) if isinstance(raw[k], (int, float)) else raw[k]) for k in sorted(raw.keys())]
        s = "&".join("=".join(kv) for kv in raw if kv[1])
        s += "&key={0}".format(self.WX_MCH_KEY)
        logging.warning('weixin sign string is: {}'.format(s))
        return hashlib.md5(s.encode('utf-8')).hexdigest().upper()

    def check(self, raw):
        """
        验证签名是否正确
        """
        sign = raw.pop("sign")
        return sign == self.sign(raw)

    def to_xml(self, raw):
        s = ""
        for k, v in raw.items():
            s += "<{0}>{1}</{0}>".format(k, v, k)
        xml_data = "<xml>{0}</xml>".format(s)
        xml_data = self.to_utf8(xml_data)
        logging.warning('xml data is : {}'.format(xml_data))
        return xml_data

    def fetch(self, url, data):
        headers = {"charset": 'UTF-8'}
        resp = requests.post(url, self.to_xml(data), headers=headers)
        re_info = resp.content
        try:
            return self.to_dict(re_info)
        except ETree.ParseError:
            return re_info

    def fetch_with_ssl(self, url, data, api_client_cert_path, api_client_key_path):
        req = requests.post(url, data=self.to_xml(data),
                            cert=(api_client_cert_path, api_client_key_path))
        return self.to_dict(req.content)

    def reply(self, msg, ok=True):
        code = "SUCCESS" if ok else "FAIL"
        return self.to_xml(dict(return_code=code, return_msg=msg))

    def unified_order(self, **data):
        """
        统一下单
        详细规则参考 https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=9_1
        :param data: out_trade_no, body, total_fee, trade_type, use_type
            out_trade_no: 商户订单号
            body: 商品描述
            total_fee: 标价金额, 整数, 单位 分
            trade_type: 交易类型
            user_ip: 在flask框架下可以自动填写, 非flask框架需传入spbill_create_ip
            use_type: 使用方式，默认公众号使用， 等于miniapp时小程序使用
        :return: 统一下单生成结果
        """
        url = "https://api.mch.weixin.qq.com/pay/unifiedorder"

        # 必填参数
        if "out_trade_no" not in data:
            raise WxPayError(u"缺少统一支付接口必填参数out_trade_no")
        if "body" not in data:
            raise WxPayError(u"缺少统一支付接口必填参数body")
        if "total_fee" not in data:
            raise WxPayError(u"缺少统一支付接口必填参数total_fee")
        if "trade_type" not in data:
            raise WxPayError(u"缺少统一支付接口必填参数trade_type")
        # 关联参数
        if data["trade_type"] == "JSAPI" and "openid" not in data:
            raise WxPayError(u"trade_type为JSAPI时，openid为必填参数")
        if data["trade_type"] == "NATIVE" and "product_id" not in data:
            raise WxPayError(u"trade_type为NATIVE时，product_id为必填参数")
        user_ip = self.user_ip_address()
        if not user_ip and "spbill_create_ip" not in data:
            raise WxPayError(u"当前未使用flask框架，缺少统一支付接口必填参数spbill_create_ip")
        user_ip = data['spbill_create_ip']

        if data.get('use_type') == 'miniapp':
            data.setdefault('appid', self.WX_MINI_APP_ID)
        else:
            data.setdefault("appid", self.WX_APP_ID)
        data.pop('use_type')
        data.setdefault("mch_id", self.WX_MCH_ID)
        data.setdefault("notify_url", data['notify_url'] if 'notify_url' in data else self.WX_NOTIFY_URL)
        data.setdefault("nonce_str", self.nonce_str())
        data.setdefault("spbill_create_ip", user_ip)

        sign_data = self.sign(data)

        logging.warning('sign data is : {0}'.format(sign_data))
        data.setdefault("sign", sign_data)
        raw = self.fetch(url, data)

        logging.warning('weixin unified_order response is: {0}'.format(raw))

        if raw["return_code"] == "FAIL":
            raise WxPayError(raw["return_msg"])
        err_msg = raw.get("err_code_des")
        if err_msg:
            logging.error('weixin unified_order error: {0}'.format(err_msg))
            raise WxPayError(err_msg)
        return raw

    def js_pay_api(self, **kwargs):
        """
        生成给JavaScript调用的数据
        详细规则参考 https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=7_7&index=6
        :param kwargs: openid, body, total_fee
            openid: 用户openid
            body: 商品名称
            total_fee: 标价金额, 整数, 单位 分
            out_trade_no: 商户订单号, 若未传入则自动生成
            use_type: 使用方式，默认公众号使用， 等于miniapp时小程序使用
        :return: 生成微信JS接口支付所需的信息
        """
        kwargs.setdefault("trade_type", "JSAPI")
        if "out_trade_no" not in kwargs:
            kwargs.setdefault("out_trade_no", self.nonce_str())
        if "use_type" not in kwargs:
            kwargs.setdefault("use_type", 'app')
        raw = self.unified_order(**kwargs)
        package = "prepay_id={0}".format(raw["prepay_id"])
        timestamp = str(int(time.time()))
        nonce_str = self.nonce_str()
        appid = self.WX_MINI_APP_ID if kwargs.get('use_type') == 'miniapp' else self.WX_APP_ID
        raw = dict(appId=appid, timeStamp=timestamp,
                   nonceStr=nonce_str, package=package, signType="MD5")
        sign = self.sign(raw)
        return dict(package=package, appId=appid, signType="MD5",
                    timeStamp=timestamp, nonceStr=nonce_str, paySign=sign)

    def order_query(self, **data):
        """
        订单查询
        详细规则参考 https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=9_2
        :param data: out_trade_no, transaction_id至少填一个
            out_trade_no: 商户订单号
            transaction_id: 微信订单号
        :return: 订单查询结果
        """
        url = "https://api.mch.weixin.qq.com/pay/orderquery"

        if "out_trade_no" not in data and "transaction_id" not in data:
            raise WxPayError(u"订单查询接口中，out_trade_no、transaction_id至少填一个")
        data.setdefault("appid", self.WX_APP_ID)
        data.setdefault("mch_id", self.WX_MCH_ID)
        data.setdefault("nonce_str", self.nonce_str())
        data.setdefault("sign", self.sign(data))

        raw = self.fetch(url, data)
        if raw["return_code"] == "FAIL":
            raise WxPayError(raw["return_msg"])
        return raw

    def close_order(self, out_trade_no):
        """
        关闭订单
        详细规则参考 https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=9_3
        :param out_trade_no: 商户订单号
        :return: 申请关闭订单结果
        """
        url = "https://api.mch.weixin.qq.com/pay/closeorder"
        data = {
            'out_trade_no': out_trade_no,
            'appid': self.WX_APP_ID,
            'mch_id': self.WX_MCH_ID,
            'nonce_str': self.nonce_str(),
        }
        data["sign"] = self.sign(data)
        raw = self.fetch(url, data)
        if raw["return_code"] == "FAIL":
            raise WxPayError(raw["return_msg"])
        return raw

    def refund(self, api_cert_path, api_key_path, **data):
        """
        申请退款
        详细规则参考 https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=9_4
        :param api_cert_path: 微信支付商户证书路径，此证书(apiclient_cert.pem)需要先到微信支付商户平台获取，下载后保存至服务器
        :param api_key_path: 微信支付商户证书路径，此证书(apiclient_key.pem)需要先到微信支付商户平台获取，下载后保存至服务器
        :param data: out_trade_no、transaction_id至少填一个, out_refund_no, total_fee, refund_fee
            out_trade_no: 商户订单号
            transaction_id: 微信订单号
            out_refund_no: 商户退款单号（若未传入则自动生成）
            total_fee: 订单金额
            refund_fee: 退款金额
        :return: 退款申请返回结果
        """
        url = "https://api.mch.weixin.qq.com/secapi/pay/refund"
        if "out_trade_no" not in data and "transaction_id" not in data:
            raise WxPayError(u"订单查询接口中，out_trade_no、transaction_id至少填一个")
        if "total_fee" not in data:
            raise WxPayError(u"退款申请接口中，缺少必填参数total_fee")
        if "refund_fee" not in data:
            raise WxPayError(u"退款申请接口中，缺少必填参数refund_fee")
        if "out_refund_no" not in data:
            data.setdefault("out_refund_no", self.nonce_str())

        data.setdefault("appid", self.WX_APP_ID)
        data.setdefault("mch_id", self.WX_MCH_ID)
        data.setdefault("op_user_id", self.WX_MCH_ID)
        data.setdefault("nonce_str", self.nonce_str())
        sign_data = self.sign(data)
        logging.warning('sign data is :  ', sign_data)
        data.setdefault("sign", sign_data)

        raw = self.fetch_with_ssl(url, data, api_cert_path, api_key_path)
        if raw["return_code"] == "FAIL":
            raise WxPayError(raw["return_msg"])
        return raw

    def refund_query(self, **data):
        """
        查询退款
        提交退款申请后，通过调用该接口查询退款状态。退款有一定延时，
        用零钱支付的退款20分钟内到账，银行卡支付的退款3个工作日后重新查询退款状态。
        详细规则参考 https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=9_5
        :param data: out_refund_no、out_trade_no、transaction_id、refund_id四个参数必填一个
            out_refund_no: 商户退款单号
            out_trade_no: 商户订单号
            transaction_id: 微信订单号
            refund_id: 微信退款单号
        :return: 退款查询结果
        """
        url = "https://api.mch.weixin.qq.com/pay/refundquery"
        if "out_refund_no" not in data and "out_trade_no" not in data \
                and "transaction_id" not in data and "refund_id" not in data:
            raise WxPayError(u"退款查询接口中，out_refund_no、out_trade_no、transaction_id、refund_id四个参数必填一个")

        data.setdefault("appid", self.WX_APP_ID)
        data.setdefault("mch_id", self.WX_MCH_ID)
        data.setdefault("nonce_str", self.nonce_str())
        data.setdefault("sign", self.sign(data))

        raw = self.fetch(url, data)
        if raw["return_code"] == "FAIL":
            raise WxPayError(raw["return_msg"])
        return raw

    def download_bill(self, bill_date, bill_type=None):
        """
        下载对账单
        详细规则参考 https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=9_6
        :param bill_date: 对账单日期
        :param bill_type: 账单类型(ALL-当日所有订单信息，[默认]SUCCESS-当日成功支付的订单, REFUND-当日退款订单)
        :return: 数据流形式账单
        """
        url = "https://api.mch.weixin.qq.com/pay/downloadbill"
        data = {
            'bill_date': bill_date,
            'bill_type': bill_type if bill_type else 'SUCCESS',
            'appid': self.WX_APP_ID,
            'mch_id': self.WX_MCH_ID,
            'nonce_str': self.nonce_str()
        }
        data['sign'] = self.sign(data)
        raw = self.fetch(url, data)
        return raw

    def send_red_pack(self, api_cert_path, api_key_path, **data):
        """
        发给用户微信红包
        详细规则参考 https://pay.weixin.qq.com/wiki/doc/api/tools/cash_coupon.php?chapter=13_4&index=3
        :param api_cert_path: 微信支付商户证书路径，此证书(apiclient_cert.pem)需要先到微信支付商户平台获取，下载后保存至服务器
        :param api_key_path: 微信支付商户证书路径，此证书(apiclient_key.pem)需要先到微信支付商户平台获取，下载后保存至服务器
        :param data: send_name, re_openid, total_amount, wishing, client_ip, act_name, remark
            send_name: 商户名称 例如: 天虹百货
            re_openid: 用户openid
            total_amount: 付款金额
            wishing: 红包祝福语 例如: 感谢您参加猜灯谜活动，祝您元宵节快乐！
            client_ip: 调用接口的机器Ip地址, 注：此地址为服务器地址
            act_name: 活动名称 例如: 猜灯谜抢红包活动
            remark: 备注 例如: 猜越多得越多，快来抢！
        :return: 红包发放结果
        """
        url = "https://api.mch.weixin.qq.com/mmpaymkttransfers/sendredpack"
        if "send_name" not in data:
            raise WxPayError(u"向用户发送红包接口中，缺少必填参数send_name")
        if "re_openid" not in data:
            raise WxPayError(u"向用户发送红包接口中，缺少必填参数re_openid")
        if "total_amount" not in data:
            raise WxPayError(u"向用户发送红包接口中，缺少必填参数total_amount")
        if "wishing" not in data:
            raise WxPayError(u"向用户发送红包接口中，缺少必填参数wishing")
        if "client_ip" not in data:
            raise WxPayError(u"向用户发送红包接口中，缺少必填参数client_ip")
        if "act_name" not in data:
            raise WxPayError(u"向用户发送红包接口中，缺少必填参数act_name")
        if "remark" not in data:
            raise WxPayError(u"向用户发送红包接口中，缺少必填参数remark")

        data.setdefault("wxappid", self.WX_APP_ID)
        data.setdefault("mch_id", self.WX_MCH_ID)
        data.setdefault("nonce_str", self.nonce_str())
        data.setdefault("mch_billno", u'{0}{1}{2}'.format(
            self.WX_MCH_ID, time_lib.today_str('%Y%m%d'), self.random_num(10)
        ))
        data.setdefault("total_num", 1)
        data.setdefault("scene_id", 'PRODUCT_4')
        data.setdefault("sign", self.sign(data))

        raw = self.fetch_with_ssl(url, data, api_cert_path, api_key_path)
        if raw["return_code"] == "FAIL":
            raise WxPayError(raw["return_msg"])
        return raw

    def enterprise_payment(self, **data):
        """
        使用企业对个人付款功能
        详细规则参考 https://pay.weixin.qq.com/wiki/doc/api/tools/mch_pay.php?chapter=14_2
        :param api_cert_path: 微信支付商户证书路径，此证书(apiclient_cert.pem)需要先到微信支付商户平台获取，下载后保存至服务器
        :param api_key_path: 微信支付商户证书路径，此证书(apiclient_key.pem)需要先到微信支付商户平台获取，下载后保存至服务器
        :param data: openid, check_name, re_user_name, amount, desc, spbill_create_ip
            openid: 用户openid
            check_name: 是否校验用户姓名
            re_user_name: 如果 check_name 为True，则填写，否则不带此参数
            amount: 金额: 企业付款金额，单位为分
            desc: 企业付款描述信息
            spbill_create_ip: 调用接口的机器Ip地址, 注：此地址为服务器地址
        :return: 企业转账结果
        """
        url = "https://api.mch.weixin.qq.com/mmpaymkttransfers/promotion/transfers"
        if "openid" not in data:
            raise WxPayError(u"企业付款申请接口中，缺少必填参数openid")
        if "check_name" not in data:
            raise WxPayError(u"企业付款申请接口中，缺少必填参数check_name")
        if data['check_name'] and "re_user_name" not in data:
            raise WxPayError(u"企业付款申请接口中，缺少必填参数re_user_name")
        if "amount" not in data:
            raise WxPayError(u"企业付款申请接口中，缺少必填参数amount")
        if "desc" not in data:
            raise WxPayError(u"企业付款申请接口中，缺少必填参数desc")
        if "spbill_create_ip" not in data:
            raise WxPayError(u"企业付款申请接口中，缺少必填参数spbill_create_ip")

        data.setdefault("mch_appid", self.WX_APP_ID)
        data.setdefault("mchid", self.WX_MCH_ID)
        data.setdefault("nonce_str", self.nonce_str())

        if 'partner_trade_no' not in data:
            data.setdefault("partner_trade_no", u'{0}{1}{2}'.format(
                self.WX_MCH_ID, time_lib.today_str('%Y%m%d'), self.random_num(10)
            ))
        data['check_name'] = 'FORCE_CHECK' if data['check_name'] else 'NO_CHECK'
        data.setdefault("sign", self.sign(data))

        raw = self.fetch_with_ssl(url, data, api_cert_path="", api_key_path="")
        if raw["return_code"] == "FAIL":
            raise WxPayError(raw["return_msg"])
        return raw

    def swiping_card_payment(self, **data):
        """
        提交刷卡支付
        详细规则参考 https://pay.weixin.qq.com/wiki/doc/api/micropay.php?chapter=9_10&index=1
        :param data: body, out_trade_no, total_fee, auth_code, (可选参数 device_info, detail, goods_tag, limit_pay)
            body: 商品描述
            *out_trade_no: 商户订单号
            total_fee: 标价金额, 整数, 单位 分
            auth_code: 微信支付二维码扫描结果
            *device_info: 终端设备号(商户自定义，如门店编号)
            user_ip 在flask框架下可以自动填写, 非flask框架需传入spbill_create_ip
        :return: 统一下单生成结果
        """
        url = "https://api.mch.weixin.qq.com/pay/micropay"

        # 必填参数
        if "body" not in data:
            raise WxPayError(u"缺少刷卡支付接口必填参数body")
        if "total_fee" not in data:
            raise WxPayError(u"缺少刷卡支付接口必填参数total_fee")
        if "out_trade_no" not in data:
            data.setdefault("out_trade_no", self.nonce_str())

        user_ip = self.user_ip_address()
        if not user_ip and "spbill_create_ip" not in data:
            raise WxPayError(u"当前未使用flask框架，缺少刷卡支付接口必填参数spbill_create_ip")

        data.setdefault("appid", self.WX_APP_ID)
        data.setdefault("mch_id", self.WX_MCH_ID)
        data.setdefault("nonce_str", self.nonce_str())
        data.setdefault("spbill_create_ip", user_ip)
        data.setdefault("sign", self.sign(data))

        raw = self.fetch(url, data)
        if raw["return_code"] == "FAIL":
            raise WxPayError(raw["return_msg"])
        err_msg = raw.get("err_code_des")
        if err_msg:
            raise WxPayError(err_msg)
        return raw


wx_pay = WxPay(
    wx_app_id=wx_app_id,  # 微信平台appid
    wx_miniapp_id=wx_miniapp_id,  # 微信平台appid
    wx_mch_id=wx_mch_id,  # 微信支付商户号
    wx_mch_key=wx_mch_key,   # 微信支付密匙
    wx_notify_url=wx_notify_url
)


# encryptedData解密
class WXBizDataCrypt:
    def __init__(self, sessionKey, encryptedData, iv):
        self.appId = wx_miniapp_id
        self.sessionKey = sessionKey
        self.encryptedData = encryptedData
        self.iv = iv

    def decrypt(self):
        # base64 decode
        sessionKey = base64.b64decode(self.sessionKey)
        encryptedData = base64.b64decode(self.encryptedData)
        iv = base64.b64decode(self.iv)

        cipher = AES.new(sessionKey, AES.MODE_CBC, iv)

        decrypted = json.loads(self._unpad(cipher.decrypt(encryptedData)))

        if decrypted['watermark']['appid'] != self.appId:
            raise Exception('Invalid Buffer')

        return decrypted

    def _unpad(self, s):
        return s[:-ord(s[len(s)-1:])]
