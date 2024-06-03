import json
from datetime import datetime

from TimiAutomation.sdk.http_api import get_sign_params, http_post, http_get, http_patch, TET_HOST, TET_ID, TET_KEY, SUCCESS_CODE

# 测试环境, 重置下TET_HOST
#TET_HOST = "9.135.100.58:2300"



def set_operation(serial, platform_type, account, status, cmd, params):
    """ 设置设备指令
    :param serial: 设备uuid
    :param platform_type: 设备类型
    :param account: 游戏账户
    :param status: 游戏状态
    :param cmd: 操作名称
    :param params: 操作数据
    :return:
    """
    header = dict(
        sign=get_sign_params(TET_ID, TET_KEY)
    )
    params = dict(
        serial=serial,
        platform_type=platform_type,
        game_account=account,
        game_status=status,
        cmd=cmd,
        params=params
    )
    is_ok, data = http_post(TET_HOST, '/api/device_manage/custom_operation', None, params, headers=header)
    # print(is_ok, data)
    if is_ok and data['code'] == SUCCESS_CODE:
        return data['data']
    return None


def get_operation(serial):
    """
        请求设备指令, 最多返回1个
        :param serial: 设备uuid
        :return: Tuple, db_id, cmd, params
    """
    header = dict(
        sign=get_sign_params(TET_ID, TET_KEY)
    )
    params = dict(
        serial=serial
    )
    is_ok, data = http_get(TET_HOST, '/api/device_manage/custom_operation', params, headers=header)
    # print(is_ok, data)
    if is_ok and data['code'] == SUCCESS_CODE:
        result = data['data']
        if result:
            return result.get('id'), result.get('cmd'), result.get('params')
    return None, None, None


def set_operation_result(operation_id, result, finish_time):
    """
        设置手机执行指令结果
        :param operation_id: operation_id
        :param result: 执行结果
        :param finish_time: 结束时间
        :return:
    """
    header = dict(
        sign=get_sign_params(TET_ID, TET_KEY)
    )
    params = dict(
        id=operation_id,
        result=result,
        finish_time=finish_time
    )
    is_ok, data = http_patch(TET_HOST, '/api/device_manage/custom_operation', None, params, headers=header)
    # print(is_ok, data)
    if is_ok and data['code'] == SUCCESS_CODE:
        return data['data']
    return None


def get_device_operations(serial, cmd=None, s_time=None, e_time=None, is_distributed=True):
    """
        获取设备已执行的
        :param serial: 设备uuid
        :param cmd: 指令名称
        :param s_time: 时间段查询的起始时间
        :param e_time: 时间段查询的结束时间
        :param is_distributed: 1：只返回设备已经获取过的, 0：设备所有的
        :return:
    """
    header = dict(
        sign=get_sign_params(TET_ID, TET_KEY)
    )
    params = dict(
        serial=serial,
        cmd=cmd,
        s_time=s_time,
        e_time=e_time,
        is_distributed=1 if is_distributed else 0
    )
    is_ok, data = http_get(TET_HOST, '/api/device_manage/custom_operation/history', params, headers=header)
    # print(is_ok, data)
    if is_ok and data['code'] == SUCCESS_CODE:
        return data['data']
    return None



def add_project_operations(operations, device_group_id=1034):
    """ 设置项目的指令集合
    :param device_group_id: string, 项目设备组id
    :param operations: list, 操作指令集

    :return:
    """
    header = dict(
        sign=get_sign_params(TET_ID, TET_KEY)
    )
    params = dict(
        device_group_id=device_group_id,
        operations=operations
    )
    is_ok, data = http_post(TET_HOST, '/api/device_manage/device_group/operations', None, params, headers=header)
    # print(is_ok, data)
    if is_ok and data['code'] == SUCCESS_CODE:
        return data['data']
    return None


def get_project_operations(device_group_id=1034):
    """
        请求设备组的自定义指令集, 最多返回1个
        :param device_group_id: 项目设备组id
        :return: Tuple, cmd, params
    """
    header = dict(
        sign=get_sign_params(TET_ID, TET_KEY)
    )
    params = dict(
        device_group_id=device_group_id
    )
    is_ok, data = http_get(TET_HOST, '/api/device_manage/device_group/operations', params, headers=header)
    # print(is_ok, data)
    if is_ok and data['code'] == SUCCESS_CODE:
        return data['data']
    return None


def set_status(serial, platform_type, status):
    """ 设置设备状态
    :param serial: 设备uuid
    :param platform_type: 设备类型
    :param status: 游戏状态
    :return:
    """
    header = dict(
        sign=get_sign_params(TET_ID, TET_KEY)
    )
    params = dict(
        serial=serial,
        platform_type=platform_type,
        game_status=status
    )
    is_ok, data = http_post(TET_HOST, '/api/device_manage/custom_status', None, params, headers=header)
    # print(is_ok, data)
    if is_ok and data['code'] == SUCCESS_CODE:
        return data['data']
    return None


def get_status(serial):
    """
        查询设备最新状态
        :param serial: 设备uuid
        :return: Tuple, cmd, params
    """
    header = dict(
        sign=get_sign_params(TET_ID, TET_KEY)
    )
    params = dict(
        serial=serial
    )
    is_ok, data = http_get(TET_HOST, '/api/device_manage/custom_status', params, headers=header)
    # print(is_ok, data)
    if is_ok and data['code'] == SUCCESS_CODE:
        return data['data']
    return None


if __name__ == '__main__':
    dev_uuid = "sedx8188"
    dev_platform_type = "android"
    game_account = "1233344"
    game_status = "lobby"
    cmd = "login_to_game"
    cmd_params = {
        "server": "test",
        "zone": "1"
    }
    # cmd_params = ["aaa", "bbb", "cccc"]
    cmd_params = json.dumps(cmd_params)

    ope1 = dict(cmd=cmd, params=json.dumps(cmd_params))
    ope2 = dict(cmd="休闲派对", params="单人")
    pre_set_operations = [ope1, ope2]
    pre_set_operations = json.dumps(pre_set_operations)

    print("增加设备组指令集")
    res = add_project_operations(pre_set_operations)
    print(res)

    print("获取设备组指令集")
    res = get_project_operations()
    print(res)

    print("获取设备状态")
    res = get_status(dev_uuid)
    print(res)

    print("设置设备状态")
    res = set_status(dev_uuid, dev_platform_type, "over")
    print(res)

    print("获取设备状态")
    res = get_status(dev_uuid)
    print(res)

    # print("设置指令(后续在web上设置")
    # res = set_operation(dev_uuid, dev_platform_type, game_account, game_status, cmd, cmd_params)
    # print(res)
    #
    # print("获取设备的指令")
    # res = get_operation(dev_uuid)
    # print(res)
    #
    # if res:
    #     operation_id = res[0]
    #     print("设置指令结果及执行结束时间（可选）")
    #     res = set_operation_result(operation_id, "success", datetime.now())
    #     print(res)
    #
    # print("获取设备历史指令")
    # res = get_device_operations(dev_uuid, cmd=cmd, is_distributed=1)
    # for info in res:
    #     print(info)
    #
    # operation_id = 6
    # print("设置指令结果及执行结束时间（可选）")
    # res = set_operation_result(operation_id, "success", datetime.now())
    # print(res)
