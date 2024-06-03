from AutoTest.DrivingFunc.moudle_import import *
from ga2.engine.engine import EventType

TESTRESTPYE = Tuple[AutoTestRetType, str]


def open_gm_panel(device: Device) -> TESTRESTPYE:
    """打开GM面板

    Args:
        device (Device): _description_

    Returns:
        TESTRESTPYE: _description_
    """
    engine = device.engine_connector()
    engine: UE4Engine
    ele = engine.find_elements_by_xpath("//*[@name='w_button_gm']")[0]
    engine.broad_cast_event(ele, event_type=EventType.ONCLICKED)

    return AutoTestRetType.SUCCESS, "open gm success"


def close_gm_panel(device: Device) -> TESTRESTPYE:
    """关闭GM面板

    Args:
        device (Device): _description_

    Returns:
        TESTRESTPYE: _description_
    """
    engine = device.engine_connector()
    engine: UE4Engine
    ele = engine.find_elements_by_xpath("//*[@name='w_button_close']")[0]
    engine.broad_cast_event(ele, event_type=EventType.ONCLICKED)

    return AutoTestRetType.SUCCESS, "close gm success"


def choose_gm_group(device: Device, group_type: str) -> TESTRESTPYE:
    engine = device.engine_connector()
    eles = engine.find_elements_by_xpath(f"//*[@txt='{group_type.lower()}']/../../..")
    if eles:
        engine.broad_cast_event(eles[0], event_type=EventType.ONCLICKED)

    return AutoTestRetType.SUCCESS, "choose gm group success"


def choose_sub_gm_type(device: Device, gm_type_id: int) -> TESTRESTPYE:
    """选择GM类型

    Args:
        device (Device): _description_
        gm_type_id (str): _description_

    Returns:
        TESTRESTPYE: _description_
    """
    engine = device.engine_connector()
    ret = None
    if isinstance(engine, UE4Engine):
        engine: UE4Engine

        CmdSendEngine = partial(CmdSend, send_method=engine.call_function_handler)

        ExecuteConsoleCommand = CmdSendEngine(
            OrderedDict(
                CommandsList=get_func_from_private('FindUWidgetObjectByName', ['w_list_view_commands']),
                ret=get_non_static_op('#CommandsList', "NavigateToIndex", [gm_type_id]),
                out='ret'
            )
        )
        ret = ExecuteConsoleCommand.exec_cmd()

        eles = engine.find_elements_by_xpath(f"//*[starts-with(@txt, '{gm_type_id + 1} ')]/../..")
        if eles:
            engine.broad_cast_event(eles[0], event_type=EventType.ONCLICKED)

        return AutoTestRetType.SUCCESS, "choose gm success"

    return AutoTestRetType.FAIL, "choose gm fail"


def set_game_quality(device: Device, quality: int) -> TESTRESTPYE:
    """设置游戏画质

    Args:
        device (Device): _description_
        quality (int): _description_

    Returns:
        TESTRESTPYE: _description_
    """
    engine = device.engine_connector()
    engine: UE4Engine
    ret = None
    if isinstance(engine, UE4Engine):
        engine: UE4Engine

        choose_gm_group(device, 'Test')

        choose_sub_gm_type(device, 0)

        CmdSendEngine = partial(CmdSend, send_method=engine.call_function_handler)

        ExecuteConsoleCommand = CmdSendEngine(
            OrderedDict(
                InputParam=get_func_from_private('FindUWidgetObjectByName', ['w_input_param']),
                ret=get_non_static_op('#InputParam', "SetText", [str(quality)]),
                out='ret'
            )
        )
        ret = ExecuteConsoleCommand.exec_cmd()

        return AutoTestRetType.SUCCESS, "set game quality success"

    return AutoTestRetType.FAIL, "set game quality fail"

def execution_gm(device: Device) -> TESTRESTPYE:
    engine = device.engine_connector()
    eles = engine.find_elements_by_xpath(f"//*[@name='w_button_commit']")
    if eles:
        engine.broad_cast_event(eles[0], event_type=EventType.ONCLICKED)

    return AutoTestRetType.SUCCESS, "execution gm success"

def set_level_seq(device: Device, level_seq: list[int]) -> TESTRESTPYE:
    """设置关卡序列

    Args:
        device (Device): _description_
        level_seq (list[int]): _description_

    Returns:
        TESTRESTPYE: _description_
    """
    engine = device.engine_connector()
    engine: UE4Engine
    ret = None
    if isinstance(engine, UE4Engine):
        engine: UE4Engine

        eles = engine.find_elements_by_xpath("//*[contains(@txt,'关卡ID序列')]/preceding-sibling::*")
        if eles:
            path_name = eles[0].path.split(" ")[-1]
        CmdSendEngine = partial(CmdSend, send_method=engine.call_function_handler)

        ExecuteConsoleCommand = CmdSendEngine(
            OrderedDict(
                InputParam=get_func_from_private('FindObjectByPathName', [path_name]),
                ret=get_non_static_op('#InputParam', "SetText", [";".join(list(map(str, level_seq)))]),
                out='ret'
            )
        )
        ret = ExecuteConsoleCommand.exec_cmd()

        return AutoTestRetType.SUCCESS, "set level seq success"

    return AutoTestRetType.FAIL, "set level seq fail"

def set_game_model(device: Device, game_model: int) -> TESTRESTPYE:
    """设置游戏模式

    Args:
        device (Device): _description_
        game_model (int): _description_

    Returns:
        TESTRESTPYE: _description_
    """
    engine = device.engine_connector()
    engine: UE4Engine
    ret = None
    if isinstance(engine, UE4Engine):
        engine: UE4Engine

        eles = engine.find_elements_by_xpath("//*[@txt='模式ID']/preceding-sibling::*")
        if eles:
            path_name = eles[0].path.split(" ")[-1]
            
            CmdSendEngine = partial(CmdSend, send_method=engine.call_function_handler)

            ExecuteConsoleCommand = CmdSendEngine(
                OrderedDict(
                    InputParam=get_func_from_private('FindObjectByPathName', [path_name]),
                    ret=get_non_static_op('#InputParam', "SetText", [str(game_model)]),
                    out='ret'
                )
            )
            ret = ExecuteConsoleCommand.exec_cmd()

            return AutoTestRetType.SUCCESS, "set game model success"

    return AutoTestRetType.FAIL, "set game model fail"