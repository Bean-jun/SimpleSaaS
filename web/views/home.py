import datetime
import json

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django_redis import get_redis_connection

from utils.Payment.PaymentByAlipay import AliPayment
from utils.encrypt import uid
from web.models import PricePolicy, Transaction


def index(request):
    return render(request, 'web/index.html')


def price(request):
    """套餐"""
    policy_list = PricePolicy.objects.filter(category=2)
    return render(request, 'web/price.html', {'policy_list': policy_list})


def payment(request, policy_id):
    """ 支付页面"""
    # 1. 价格策略（套餐）policy_id
    policy_object = PricePolicy.objects.filter(id=policy_id, category=2).first()
    if not policy_object:
        return redirect('web:price')

    # 2. 要购买的数量
    number = request.GET.get('number', '')
    if not number or not number.isdecimal():
        return redirect('web:price')
    number = int(number)
    if number < 1:
        return redirect('web:price')

    # 3. 计算原价
    origin_price = number * policy_object.price

    # 4.之前购买过套餐
    balance = 0
    _object = None
    if request.tracer.price_policy.category == 2:
        # 找到之前订单：总支付费用 、 开始~结束时间、剩余天数 = 抵扣的钱
        # 之前的实际支付价格
        _object = Transaction.objects.filter(user=request.tracer.user, status=2).order_by('-id').first()
        total_timedelta = _object.end_time - _object.start_time
        balance_timedelta = _object.end_time - datetime.datetime.now()
        if total_timedelta.days == balance_timedelta.days:
            # 按照价值进行计算抵扣金额
            balance = _object.price_policy.price * _object.count / total_timedelta.days * (balance_timedelta.days - 1)
        else:
            balance = _object.price_policy.price * _object.count / total_timedelta.days * balance_timedelta.days

    if balance >= origin_price:
        return redirect(reverse('web:price'))

    context = {
        'policy_id': policy_object.id,
        'number': float(number),
        'origin_price': float(origin_price),
        'balance': float(round(balance, 2)),
        'total_price': float(origin_price - round(balance, 2))
    }
    conn = get_redis_connection()
    key = 'payment_{}'.format(request.tracer.user.mobile_phone)
    conn.set(key, json.dumps(context), ex=60 * 30)  # ex（表示超时时间） ps：nx=True,表示redis中已存在key，再次执行时候就不会再设置了。

    context['policy_object'] = policy_object
    context['transaction'] = _object

    return render(request, 'web/payment.html', context)


def pay(request):
    conn = get_redis_connection()
    key = 'payment_{}'.format(request.tracer.user.mobile_phone)
    context_string = conn.get(key)
    if not context_string:
        return redirect('price')
    context = json.loads(context_string.decode('utf-8'))

    # 1. 数据库中生成交易记录（待支付）
    #     等支付成功之后，我们需要把订单的状态更新为已支付、开始&结束时间
    order_id = uid(request.tracer.user.mobile_phone)
    total_price = context['total_price']
    Transaction.objects.create(
        status=1,
        order=order_id,
        user=request.tracer.user,
        price_policy_id=context['policy_id'],
        count=context['number'],
        pay_price=total_price
    )

    # 付款后的回调
    callback_url = 'http://' + settings.WEB_ADDRESS + ':' + settings.WEB_HOST + reverse('web:pay_notify')

    payment = AliPayment(appid=settings.APPID)
    pay_url = payment.get_pay(order_id,
                              total_price,
                              'trace payment',
                              return_url=callback_url,
                              notify_url=callback_url
                              )

    return redirect(pay_url)


def pay_notify(request):
    """ 支付成功之后触发的URL """

    if request.method == 'GET':
        # 只做跳转，判断是否支付成功了，不做订单的状态更新。
        # 支付吧会讲订单号返回：获取订单ID，然后根据订单ID做状态更新 + 认证。
        # 支付宝公钥对支付给我返回的数据request.GET 进行检查，通过则表示这是支付宝返还的接口。
        params = request.GET.dict()
        signature = params.pop("sign")
        payment = AliPayment(appid=settings.APPID)
        try:
            status = payment.get_res(params, signature)
        except Exception as e:
            status = False

        if status:
            '''
            current_datetime = datetime.datetime.now()
            out_trade_no = params['out_trade_no']
            _object = Transaction.objects.filter(order=out_trade_no).first()

            _object.status = 2
            _object.start_time = current_datetime
            _object.end_time = current_datetime + datetime.timedelta(days=365 * _object.count)
            _object.save()
            '''
            return HttpResponse('支付完成')

        return HttpResponse('支付失败')
    else:
        post_params = request.GET.dict()
        signature = post_params.pop("sign")
        payment = AliPayment(appid=settings.APPID)
        try:
            status = payment.get_res(post_params, signature)
        except Exception as e:
            status = False

        if status:
            current_datetime = datetime.datetime.now()
            out_trade_no = post_params['out_trade_no']
            _object = Transaction.objects.filter(order=out_trade_no).first()

            _object.status = 2
            _object.start_time = current_datetime
            _object.end_time = current_datetime + datetime.timedelta(days=365 * _object.count)
            _object.save()
            return HttpResponse('success')

        return HttpResponse('error')
