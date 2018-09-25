from mall_web.utils import time_lib
from mall_admin import models
from django.conf import settings
import time
import requests
from multiprocessing import Pool


def get_express_info(order_id, user_id, ship_number, force_refresh=False):
    # 获取订单物流信息
    """
    order_id: 订单ID
    user_id: 用户ID
    ship_number: 物流单号
    force_refresh: 强制刷新
    """
    if force_refresh:
        handle_express_info(order_id, user_id, ship_number)
        return order_id

    ship_info = models.OrderShipInfo.normal.filter(order_id=order_id).count()
    latest_info = models.OrderShipInfo.normal.filter(order_id=order_id, create_at__lte=time_lib.timestamp_to_utc_str(int(time.time())-settings.SHIP_QUERY_TIME_LIMIT))
    if ship_info and len(latest_info) == 0:
        return order_id
    else:
        # 需要更新
        handle_express_info(order_id, user_id, ship_number)
        return order_id


def _get_express_info(order_id, user_id, ship_number):
    # 需要更新
    data = {
        'appKey': settings.SHIP_QUERY_API_KEY,
        'expressNo': ship_number
    }
    res = requests.post(settings.SHIP_QUERY_API_URL, data,  timeout=15).json()
    return res


def handle_express_info(order_id, user_id, ship_number):
    p = Pool()
    result = p.apply_async(_get_express_info, args=(order_id, user_id, ship_number))
    p.close()
    p.join()

    res = result.get()
    if res.get('ERRORCODE') == '0':
        update_ship_info(order_id, res)
    insert_ship_log(order_id, user_id, ship_number, res)


def update_ship_info(order_id, data):
    models.OrderShipInfo.normal.filter(order_id=order_id).hard_delete()
    for info in data['RESULT']['context']:
        o_info = models.OrderShipInfo(
            message_content=info.get('desc'),
            message_time=info.get('time'),
            order_id=order_id
        )
        o_info.save()


def insert_ship_log(order_id, user_id, ship_num, data):
    s_log = models.ShipLog(
        error_code=data.get('ERRORCODE'),
        user_id=user_id,
        order_id=order_id,
        ship_num=ship_num
    )
    s_log.save()
