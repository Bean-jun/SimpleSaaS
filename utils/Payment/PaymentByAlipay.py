import os
from alipay import AliPay
from django.conf import settings


# 证书文件配置
ALIPAY_PUBLIC_KEY_FILE = os.path.join(settings.BASE_DIR, 'utils/Payment/Cryptography/ALIPAY_PUBLIC_KEY.txt')
APP_PRIVATE_KEY_FILE = os.path.join(settings.BASE_DIR, 'utils/Payment/Cryptography/APP_PRIVATE_KEY.txt')
ALIPAY_PUBLIC_KEY = open(ALIPAY_PUBLIC_KEY_FILE, 'r', encoding='utf-8').read()
APP_PRIVATE_KEY = open(APP_PRIVATE_KEY_FILE, 'r', encoding='utf-8').read()


class AliPayment():
    """
    支付宝支付接口
    """
    def __init__(self,
                 appid,
                 sign_type='RSA2',
                 app_notify_url=None,
                 app_private_key_string=None,
                 alipay_public_key_string=None,
                 debug=True):
        '''
        接口初始化
        :param appid: 用户账号ID
        :param sign_type: 签名方式
        :param app_notify_url: 回调url, 异步通知
        :param app_private_key_string: 应用私钥
        :param alipay_public_key_string: 支付宝公钥
        :param debug: 调试模式，Ture表示沙箱模式，False表示生产环境模式
        '''
        self.appid = appid
        self.debug = debug
        self.sign_type = sign_type
        self.app_notify_url = app_notify_url

        # 证书处理
        if app_private_key_string is None:
            # 应用私钥
            self.app_private_key_string = APP_PRIVATE_KEY

        if alipay_public_key_string is None:
            # 支付宝公钥
            self.alipay_public_key_string = ALIPAY_PUBLIC_KEY

    def _alipay(self):
        alipay = AliPay(
            appid=self.appid,
            app_notify_url=self.app_notify_url,  # 默认回调url, 异步通知, 需要使用公网IP
            app_private_key_string=self.app_private_key_string,
            alipay_public_key_string=self.alipay_public_key_string,
            sign_type=self.sign_type,  # RSA2
            debug=self.debug  # 默认False
        )
        return alipay

    def get_pay(self, out_trade_no, total_amount, subject, return_url=None, notify_url=None):
        '''
        获取交易链接
        :param out_trade_no: 订单ID
        :param total_amount: 订单费用
        :param subject: 订单主题
        :param return_url: 可选, 同步通知订单状态 get请求
        :param notify_url: 可选, 异步通知订单状态 post请求
        :return: 订单链接
        '''
        alipay = self._alipay()
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=out_trade_no,  # 订单id
            total_amount=str(total_amount),  # 支付总金额
            subject='订单交易%s' % subject,
            return_url=return_url,  # 可选, 同步通知订单状态
            notify_url=notify_url  # 可选, 异步通知订单状态
        )
        if self.debug is True:
            return 'https://openapi.alipaydev.com/gateway.do?' + order_string
        else:
            return 'https://openapi.alipay.com/gateway.do?' + order_string

    def get_res(self, params, signature):
        '''
        订单结果获取
        :param signature: 支付宝sign
        :param params: 支付宝返回数据
        :return: 返回订单结果状态码及接口数据
        '''
        alipay = self._alipay()

        # 校验数据内容, True表明为支付宝回传数据
        status = alipay.verify(params, signature)

        return status
