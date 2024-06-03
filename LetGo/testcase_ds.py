#!/usr/bin/python
import datetime
import logging
import time

import TimiAutomation.uitrace.device.game.ga.GAutomatorAndroid.config
from TimiAutomation.testframework.testbase.testcase import TestCase
from TimiAutomation.uitrace.api import *
from TimiAutomation.uitrace.utils.param import OSType,DriverType
from TimiAutomation import *
from loguru import logger as Logger
from TimiAutomation.uitrace.utils.env import proj_env, DeviceEnv
from TimiAutomation.sdk.envs import CaseEnvs
from TimiAutomation.uitrace.device.game.ga.ga_mgr import *
from TimiAutomation.uitrace.device.android.driver_mgr import AndroidDriver
from TimiAutomation.uitrace.device.game.ga.ga_mgr import GADriver, GA
#from TimiAutomation.uitrace.device.game.ga.GAutomatorAndroid.wpyscripts.wetest.engine import UnRealEngine
#from TimiAutomation.uitrace.device.game.ga.GAutomatorIOS.ga2.engine.protocol import *
from xml.dom.minidom import parse
from operation_demo import *

class machine_stat():
        def __init__(self):
            pass

        STAT_OFFLINE = 0
        STAT_RUNNING = 1
        STAT_DATING = 2
        STAT_SINGLE_ROOM = 3
        STAT_TEAM_ROOM =4
        STAT_UGC = 5
        STAT_GUANKA = 6
        STAT_FU_WAN_FA = 7
        STAT_PLATFORM_LOGIN = 8
        STAT_USER_PLATFORM_AGREE = 9
        STAT_QQ_AUTH_AGREE = 10
        STAT_QQ_AUTH_AGREEED = 11
        STAT_GAME_MODE_SELECT = 12
        STAT_GAME_MATCHING = 13
        STAT_GAME_MAIN_PLAY_DS = 14
        STAT_LOGINING = 15
        STAT_SELECT_SVR_AGAIN = 16
        STAT_SELECT_SVR_BE_CAN = 17 #可以选服

        def stat_string(self,state):
            if state == machine_stat.STAT_OFFLINE:
                return 'STAT_OFFLINE'
            elif state == machine_stat.STAT_OFFLINE:
                return 'STAT_OFFLINE'
            elif state == machine_stat.STAT_RUNNING:
                return 'STAT_RUNNING'
            elif state == machine_stat.STAT_DATING:
                return 'STAT_DATING'
            elif state == machine_stat.STAT_SINGLE_ROOM:
                return 'STAT_SINGLE_ROOM'
            elif state == machine_stat.STAT_TEAM_ROOM:
                return 'STAT_TEAM_ROOM'
            elif state == machine_stat.STAT_UGC:
                return 'STAT_UGC'
            elif state == machine_stat.STAT_GUANKA:
                return 'STAT_GUANKA'
            elif state == machine_stat.STAT_FU_WAN_FA:
                return 'STAT_FU_WAN_FA'
            elif state == machine_stat.STAT_PLATFORM_LOGIN:
                return 'STAT_PLATFORM_LOGIN'
            elif state == machine_stat.STAT_USER_PLATFORM_AGREE:
                return 'STAT_USER_PLATFORM_AGREE'
            elif state == machine_stat.STAT_QQ_AUTH_AGREE:
                return 'STAT_QQ_AUTH_AGREE'
            elif state == machine_stat.STAT_QQ_AUTH_AGREEED:
                return 'STAT_QQ_AUTH_AGREEED'
            elif state == 'STAT_GAME_MODE_SELECT':
                return 'STAT_GAME_MODE_SELECT'
            elif state ==machine_stat.STAT_GAME_MATCHING:
                return 'STAT_GAME_MATCHING'
            elif state == machine_stat.STAT_GAME_MAIN_PLAY_DS:
                return 'STAT_GAME_MAIN_PLAY_DS'
            elif state == machine_stat.STAT_LOGINING:
                return 'STAT_LOGINING'
            elif state == machine_stat.STAT_SELECT_SVR_AGAIN:
                return 'STAT_SELECT_SVR_AGAIN'
            elif state == machine_stat.STAT_SELECT_SVR_BE_CAN:
                return 'STAT_SELECT_SVR_BE_CAN'
            else:
                return 'None String'

class cmd_id():
    def __init__(self):
        pass
    cmd_xiuxian_party = '休闲派对'
    cmd_top_party = '巅峰派对'
    cmd_anmimal_party = '动物派对'
    cmd_dall_run = '公仔快跑'
    cmd_hide_and_seek = '躲猫猫'
    cmd_rank_mode = '排位赛'

    def get_cmd_str(self, id):
        if cmd_id.cmd_xiuxian_party == id:
            return '休闲派对'
        elif cmd_id.cmd_top_party == id:
            return '巅峰派对'
        elif cmd_id.cmd_anmimal_party == id:
            return '公仔快跑'
        elif cmd_id.cmd_hide_and_seek == id:
            return '躲猫猫'
        elif cmd_id.cmd_rank_mode == id:
            return '排位赛'
        else:
            return 'unkown game mode'
class GM():
    DATING_AI_OPEN = 18
    DATING_AI_CLOSE = 19
    DS_AI_OPEN = 20
    DS_AI_CLOSE = 21

class DemoTestCase(TestCase):
    '''
    author:harryxiao
    date:2023.4.23
    '''
    owner = 'harryxiao'
    timeout = 10*60
    priority = TestCase.EnumPriority.High
    status = TestCase.EnumStatus.Ready

    def __init__(self):
        super().__init__()
        self.platform = None
        self.perfdog = None
        self.mode = None
        self.get_uuid()
        self.dom = None
        self.state = None
        #匹配时间记录
        self.matching_start_time = 0
        self.cur_time = 0
        #当前登录的环境
        self.cur_svr = None
        #
        self.auth_sign_xflag = True
        #loging 階段彈框處理
        self.logging__sign_xflag = True
        #
        self.dating_sign_xflag = True
        #系統權限
        self.period_sys_win = True
        #seven day sign
        self.seven_sign_win =True
        #self.load_xml_cfg()

        self.alert_again = True
    def load_xml_cfg(self):
        '''
        通用化处理，通过配置差异，程序逻辑统一，实现一个通用都可以支持xml配置UI测试场景的方法
        '''
        #读取文件
        dom = parse('testconfig.xml')
        data = dom.documentElement
        conf = data.getElementsByTagName('conf')
        init_case = data.getElementsByTagName('init_case')
        acount= data.getElementsByTagName('acount')
        logger.debug(acount)
        pwd = data.getElementsByTagName('pwd')
        logger.debug(pwd)
        actions= data.getElementsByTagName('action')
        for action in actions:
            Cmd = action.getElementsByTagName('Cmd').getAttribute('value')
            Cmdtype = action.getElementsByTagName('Cmdtype').getAttribute('value')
            FindText = action.getElementsByTagName('FindText').getAttribute('value')
            ClickText = action.getElementsByTagName('ClickText').getAttribute('value')
            Timeout = action.getElementsByTagName('Timeout').getAttribute('value')
            SParam = action.getElementsByTagName('SParam').getAttribute('value')
            pass

        testcase = conf.getElementByTagName('testcase')
        for test_node in testcase:
            pass

    def get_uuid(self):
        self.mode = 'tet' if 'smart_id' in os.environ.keys() else 'local'
        if self.mode == 'local':
            # 本地调试
            self.uuid = "D5F7N18626004302"
            self.platform = OSType.ANDROID
            self.package_name = "com.tencent.letsgo"
        else:
            # 通过环境变量初始化
            self.case_envs = CaseEnvs
            device_attr = self.case_envs.device_attribute
            self.platform = OSType.ANDROID if device_attr.platform.lower() == "android" else OSType.IOS
            self.uuid = device_attr.serial
        logger.debug(self.uuid)
    def pre_test(self):
        Logger.debug('TestCase:pre_test')

        init_driver(os_type=self.platform, udid=self.get_uuid(), workspace=os.path.dirname(__file__))
        print("workspace:%s"%(os.path.dirname(__file__)))
        stop_app('com.tencent.letsgo')
        self.state = machine_stat.STAT_OFFLINE
        print(clear_app('com.tencent.letsgo'))
        self.snapshot()

    def get_cmd(self, uuid):
        '''
        通过TET接口，获取操作指令
        '''
        #res = set_operation(self.uuid, self.platform, 'QQ:306754015', self.state, cmdlist[0]['cmd_id'], cmdlist[0]['cmd_para'])
        #logger.debug("操作id:", res)

        ope_id, ope_name, ope_param = get_operation(uuid)
        logger.debug("operation:%s %s %s"%(ope_id, ope_name, ope_param))
        cmd=''
        cmdpara=''
        if ope_id is None:
            return cmd, cmdpara
        else:
            return ope_name, ope_param

    def run_test(self):
        Logger.debug('TestCase:Run_test')
        time.sleep(3)
        self.snapshot()
        self.start_step('元梦之星启动')
        start_app('com.tencent.letsgo')
        self.state = machine_stat.STAT_RUNNING
        time.sleep(5)

        while True:
            webcmd,cmdpara = self.get_cmd(self.uuid)
            self.run_machine_engin(webcmd, cmdpara)
            #try:
             #   self.run_machine_engin(webcmd, cmdpara)
                #每隔一秒钟取一次指令
             #   time.sleep(1)
            #except Exception as e:
                #self.run_machine_engin({'cmd_id': 'init', 'cmd_para': '0'})
             #   logger.debug('++++++++++++++++++++++++++++++++++++++++++++++++++++++++异常：%s'%(e.__str__()))

    def run_machine_engin(self,webcmd,cmdpara):
        checkbox_login_pb=None
        Logger.debug('TestCase:run_machine_engin once time')
        cmd = webcmd
        para = cmdpara
        para_sub = ''
        para_sub2 = []
        if len(webcmd) > 0:
            cmd = webcmd.split(':')[1].replace('\'','')
            para_sub = para.split('{')[1].split('}')[0]
            para_sub2 = para_sub.split(';')
        #logger.debug('self.state：%d %s' % (self.state, machine_stat().stat_string(self.state)))
        self.cur_time = datetime.now(tz=None).strftime('%Y-%m-%d %H-%M-%S')
        if self.state == machine_stat.STAT_RUNNING:
            pos = find('sys_allow.jpg', by=DriverType.CV, timeout=10)
            if pos:
                click(pos, by=DriverType.POS, timeout=10)

        tree = get_uitree(by=DriverType.GA_UE, all_wins=False)
        #今天不再显示
        w_txt_FilterLab = find_ga(xpath="//*[@name='w_txt_FilterLab']", by=DriverType.GA_UE, timeout=5)
        UI_CommonBtn_Ok = find_ga(xpath="//*[@name='w_txt_BtnLab']", by=DriverType.GA_UE, timeout=5)
        protocol_agree_txt = find_ga(xpath="//*[@txt='同意']", by=DriverType.GA_UE, timeout=5)
        logging.debug('time1')
        guid_Text_Name = None
        if self.state == machine_stat.STAT_LOGINING:
            guid_Text_Name = find_ga(xpath="//*[@txt='云宝棉棉']", by=DriverType.GA_UE, timeout=5)
            logging.debug('time2')

        if self.state is not machine_stat.STAT_DATING and find_ocr('开始', timeout=10, is_regular=True) is True:
            self.state = machine_stat.STAT_DATING
            logger.debug('self.state：%d %s' % (self.state, machine_stat().stat_string(self.state)))

        notice_msg_box = find_ga(xpath="//*[@txt='稍后重试']", by=DriverType.GA_UE, timeout=5)
        logging.debug('time3')
        close_btn = find_ga(xpath="//*[@name='w_Button_Close']", by=DriverType.GA_UE, timeout=5)
        logging.debug('time4')
        close_btn_notice = find_ga(xpath="//*[@name='w_btn_Close']", by=DriverType.GA_UE, timeout=5)
        logging.debug('time5')
        #select_svr = find_ga(xpath="//*[@name='w_ComboBox_SelectServer']", by=DriverType.GA_UE, timeout=5)
        #logging.debug('time6')
        if cmd == 'init':
            Logger.debug('TestCase:init: cmd %s'%cmd)
            init_driver(os_type=self.platform, udid=self.get_uuid(), workspace=os.path.dirname(__file__))
            print("workspace:%s" % (os.path.dirname(__file__)))
            stop_app('com.tencent.letsgo')
            time.sleep(2)
            self.snapshot()
            self.start_step('元梦之星启动')
            start_app('com.tencent.letsgo')
            self.state = machine_stat.STAT_RUNNING
            logger.debug('set state：%d %s' % (self.state, machine_stat().stat_string(self.state)))
            set_status(self.uuid, self.platform, '启动中')
            time.sleep(5)
        if self.state == machine_stat.STAT_RUNNING and protocol_agree_txt is not None:
            #用户隐私协议
            click(protocol_agree_txt, by=DriverType.POS, timeout=20)
            Logger.debug('同意隐私政策')
        if self.state == machine_stat.STAT_RUNNING:
            pos = find('sys_allow.jpg', by=DriverType.CV, timeout=10)
            if pos is not None:
                click(pos, by=DriverType.POS, timeout=20)

        if self.state == machine_stat.STAT_RUNNING and UI_CommonBtn_Ok is not None and find_ocr('Alert', timeout=5, is_regular=True) is None:
            if find('pre_login_agree.jpg', by=DriverType.CV, timeout=6):
                click('同意', by=DriverType.OCR, timeout=20)
                Logger.debug('同意用户登陆协议')
        if close_btn_notice is None and UI_CommonBtn_Ok is None:
            if find_ocr('Alert', timeout=5, is_regular=True) is None:
                if find('QQ_login.jpg', by=DriverType.CV, timeout=60):
                    self.state = machine_stat.STAT_SELECT_SVR_BE_CAN
                if self.state == machine_stat.STAT_SELECT_SVR_AGAIN:
                    logger.debug('当前机器已选过服')
                elif self.state == machine_stat.STAT_SELECT_SVR_BE_CAN:
                    self.open_select_svr('Category', 'Test')
                    time.sleep(1)
                    self.open_select_svr('Server', 'QA服')
                    logger.debug('select server')
                    #已选过服
                    self.state = machine_stat.STAT_SELECT_SVR_AGAIN
                    logger.debug('set state：%d %s' % (self.state, machine_stat().stat_string(self.state)))

        if w_txt_FilterLab:
            close_btn = find_ga(xpath="//*[@name='w_Button_Close']", by=DriverType.GA_UE, timeout=5)
            ret = click(close_btn, by=DriverType.POS, timeout=10)
            close_btn = None
            Logger.debug('Click close 今日不再显示 messagebox')
        if guid_Text_Name:
            ret = click(guid_Text_Name, by=DriverType.POS, timeout=10)
            Logger.debug('Close yun bao tips')

        if self.state == machine_stat.STAT_RUNNING:
            if self.alert_again is True:
                if find('Alert.jpg', by=DriverType.CV, timeout=10) is True or find_ocr('Alert', timeout=10, is_regular=True) is True:
                    click('OK', by=DriverType.OCR, timeout=20)
                    Logger.debug('Click alert messagebox')
                    time.sleep(5)
                    self.alert_again = False
                    if close_btn_notice is None:
                        if find('pre_login_agree.jpg', by=DriverType.CV, timeout=10) is None and find_ocr('同意', timeout=10, is_regular=True) is None:
                            if protocol_agree_txt:
                                logger.debug("protocol_agree_txt True")
                            self.state = machine_stat.STAT_SELECT_SVR_BE_CAN
                            logger.debug('set state：%d %s' % (self.state, machine_stat().stat_string(self.state)))
                            self.snapshot()
                            #通过get_uitree转换成的xml格式的元素对象，再通过xml格式拼接成控件xpath
                            tree = get_uitree(by=DriverType.GA_UE, all_wins=True)
                            checkbox_login_pb = find_ga(xpath="//*[@name='w_checkBox_Filter']", by=DriverType.GA_UE, timeout=5)
                            Logger.debug('find checkbox_login_pb :%s' % checkbox_login_pb)
                        elif find('pre_login_agree.jpg', by=DriverType.CV, timeout=10):
                            click('pre_login_agree.jpg', by=DriverType.CV, timeout=10)
                            Logger.debug('user protocol agree done')
            elif self.alert_again is False:
                if close_btn_notice is None:
                    self.state = machine_stat.STAT_SELECT_SVR_BE_CAN
                    logger.debug('set state：%d %s' % (self.state, machine_stat().stat_string(self.state)))

        if self.state == machine_stat.STAT_PLATFORM_LOGIN:
            if close_btn and find('close_x.jpg', by=DriverType.CV, timeout=5):
                close_x = find('close_x.jpg', by=DriverType.CV, timeout=10)
                ret = click(close_x, by=DriverType.POS, timeout=20)
                Logger.debug('Click close_x :%s' % ret)
                time.sleep(5)

        if self.state == machine_stat.STAT_PLATFORM_LOGIN:
            if close_btn and find('close_sign_x.jpg', by=DriverType.CV, timeout=5):
                close_sign_x = find('close_sign_x.jpg', by=DriverType.CV, timeout=5)
                ret = click(close_sign_x, by=DriverType.POS, timeout=20)
                Logger.debug('Click close_sign_x :%s' % ret)
                time.sleep(5)

        if self.state == machine_stat.STAT_SELECT_SVR_AGAIN:
            close_btn = find_ga(xpath="//*[@name='w_Button_Close']", by=DriverType.GA_UE, timeout=10)
            if close_btn is None and find('QQ_login.jpg', by=DriverType.CV, timeout=2):
                #obj = find_ga(xpath="//*[@name='w_Button_QQLogin']", by=DriverType.GA_UE, timeout=5)
                obj = find('QQ_login.jpg', by=DriverType.CV, timeout=2)
                if obj is not None:
                    ret = click(obj, by=DriverType.POS, timeout=20)
                    Logger.debug('Click w_Button_QQLogin :%s' % ret)
                    time.sleep(5)
                    self.state = machine_stat.STAT_QQ_AUTH_AGREE
                    logger.debug('set state：%d %s' % (self.state, machine_stat().stat_string(self.state)))

        if self.state == machine_stat.STAT_QQ_AUTH_AGREE:
            if find_ocr('同意', timeout=5, is_regular=True):
                ret = click('同意', by=DriverType.OCR, timeout=20)
                time.sleep(5)
                logger.debug('click qq鉴权 同意:%s' % str(ret))
                self.state = machine_stat.STAT_QQ_AUTH_AGREEED
                logger.debug('set state：%d %s' % (self.state, machine_stat().stat_string(self.state)))

        if self.state is not machine_stat.STAT_DATING and close_btn:
            if find_ocr('关闭', timeout=5, is_regular=True):
                ret = click('关闭', by=DriverType.OCR, timeout=20)
                time.sleep(5)
                logger.debug('click 弹窗：%s'%str(ret))

        if self.state == machine_stat.STAT_QQ_AUTH_AGREEED:
            if find_ocr('点击任意位置开始游戏', timeout=5, is_regular=True):
                ret = click('点击任意位置开始游戏', by=DriverType.OCR, timeout=20)
                time.sleep(5)
                logger.debug('click3 点击任意位置开始游戏:%s' % str(ret))
                self.state = machine_stat.STAT_LOGINING
                logger.debug('set state：%d %s' % (self.state, machine_stat().stat_string(self.state)))
        if self.state == machine_stat.STAT_LOGINING:
            obj = find_ocr('云宝棉棉', timeout=10, is_regular=True)
            #obj2 = find('云宝棉棉.jpg', by=DriverType.CV, timeout=2):
            if obj is not None:
                click(obj, by=DriverType.POS, timeout=10)
                time.sleep(1)

        if self.state == machine_stat.STAT_PLATFORM_LOGIN or self.state == machine_stat.STAT_LOGINING or self.state == machine_stat.STAT_RUNNING \
                or self.state == machine_stat.STAT_DATING or self.state == machine_stat.STAT_SELECT_SVR_BE_CAN:
            if close_btn or close_btn_notice:
                if close_btn:
                    click(close_btn, by=DriverType.POS, timeout=10)
                if close_btn_notice:
                    close_btn_notice[0] = close_btn_notice[0]
                    click(close_btn_notice, by=DriverType.POS, timeout=10)
                if find('close_sign_x_plus.jpg', by=DriverType.CV, timeout=5):
                    close_sign_pos = find('close_sign_x_plus.jpg', by=DriverType.CV, timeout=5)
                    if close_sign_pos:
                        ret = click(close_sign_pos, by=DriverType.POS, timeout=20)
                        time.sleep(5)
                        logger.debug('click3 close_sign_x_plus:%s' % str(ret))

        if self.state == machine_stat.STAT_LOGINING:
            if find_ocr('保存搭配', timeout=2, is_regular=True):
                ret = click('保存搭配', by=DriverType.OCR, timeout=10)
                time.sleep(5)
                logger.debug('click3 保存搭配:%s' % str(ret))

        if self.state == machine_stat.STAT_LOGINING:
            if find_ocr('跳过', timeout=2, is_regular=True):
                ret = click('跳过', by=DriverType.OCR, timeout=10)
                time.sleep(5)
                logger.debug('click3 跳过:%s' % str(ret))

        if self.state == machine_stat.STAT_DATING or self.state == machine_stat.STAT_LOGINING:
            if find_ocr('关闭', timeout=2, is_regular=True):
                ret = click('关闭', by=DriverType.OCR, timeout=10)
                time.sleep(5)
                logger.debug('click3 签到关闭:%s' % str(ret))

        if self.state is not machine_stat.STAT_DATING:
            if close_btn and self.state is not machine_stat.STAT_GAME_MAIN_PLAY_DS:
                if find('close_cn.jpg', by=DriverType.CV, timeout=5):
                    close_cn = find('close_cn.jpg', by=DriverType.CV, timeout=5)
                    if close_cn:
                        ret = click(close_cn, by=DriverType.POS, timeout=20)
                        time.sleep(5)
                        logger.debug('click3 关闭公告弹框:%s' % str(ret))

        if self.state == machine_stat.STAT_LOGINING:
            if find_ocr('直接进大', timeout=10, is_regular=True) or find_ocr('点击报名', timeout=10, is_regular=True):
                logger.debug('enter 点击报名')
                ret = click('点击报名', by=DriverType.OCR, timeout=10)

                time.sleep(5)
                self.state = machine_stat.STAT_LOGINING
                logger.debug('set state：%d %s' % (self.state, machine_stat().stat_string(self.state)))
                set_status(self.uuid, self.platform, 'loging')

        if self.state == machine_stat.STAT_LOGINING and find('Step', by=DriverType.OCR, timeout=10):
            click('Step', by=DriverType.OCR, timeout=10)

        if self.state == machine_stat.STAT_LOGINING and find('下一步', by=DriverType.OCR, timeout=10):
            # 鉴权完成后，遇到选装流程，检测到后，点击下一步流程
            click('下一步', by=DriverType.OCR, timeout=5)
        if self.state == machine_stat.STAT_LOGINING and find('确认参赛', by=DriverType.OCR, timeout=10):
            # 鉴权完成后，遇到选装，检测到后，点击确认参赛流程
            # 输入名字proc
            # tree = get_uitree(by=DriverType.GA_UE, all_wins=False)
            input_edit = find_ga(xpath="//*[@name='w_editText_input']", by=DriverType.GA_UE, timeout=10)
            click(input_edit, by=DriverType.POS, timeout=10)
            time.sleep(2)
            input_text('harry' + self.uuid[0:3])
            time.sleep(2)
            click('确认参赛', by=DriverType.OCR, timeout=5)

        if self.period_sys_win:
            if self.state == machine_stat.STAT_DATING or self.state == machine_stat.STAT_LOGINING:
                if find('仅使用期间', by=DriverType.OCR, timeout=5):
                    #处理系统权限弹框
                    click('仅使用期间', by=DriverType.OCR, timeout=5)
                    self.period_sys_win = False
                    time.sleep(1)
                    self.state == machine_stat.STAT_DATING
                    logger.debug('set state：%d %s' % (self.state, machine_stat().stat_string(self.state)))
        if self.state == machine_stat.STAT_DATING and self.seven_sign_win:
            if notice_msg_box:
                click('稍后重试', by=DriverType.OCR, timeout=10)
            if notice_msg_box is None:
                if close_btn and find('close_sign_seven.jpg', by=DriverType.CV, timeout=10) or find('close_sign_x.jpg', by=DriverType.CV, timeout=10):
                    close_sign_pos = find('close_sign_x.jpg', by=DriverType.CV, timeout=5)
                    if close_sign_pos:
                        ret = click(close_sign_pos, by=DriverType.POS, timeout=20)
                        time.sleep(5)
                        logger.debug('click3 签到关闭:%s' % str(ret))

        if self.state == machine_stat.STAT_DATING and self.seven_sign_win:
            #七日簽到
            linqu = find_ga(xpath="//*[@txt='待领取']", by=DriverType.GA_UE, timeout=10)
            if linqu:
                close_btn = find_ga(xpath="//*[@name='w_btn_Close']", by=DriverType.GA_UE, timeout=5)
                close_btn[0] = close_btn[0]+0.045
                click(close_btn, by=DriverType.POS, timeout=5)
                self.seven_sign_win = False

        if cmd == cmd_id.cmd_rank_mode and self.state == machine_stat.STAT_DATING:
            start_game = find_ga(xpath="//*[@name='w_btn_StartGame']", by=DriverType.GA_UE, timeout=5)
            #if find_ocr('开始', timeout=10, is_regular=True):
            if start_game:
            #主玩法选择流程
                #tree = get_uitree(by=DriverType.GA_UE, all_wins=False)
                close_btn = find_ga(xpath="//*[@name='w_Button_Close']", by=DriverType.GA_UE, timeout=5)
                close_btn_notice = find_ga(xpath="//*[@name='w_btn_Close']", by=DriverType.GA_UE, timeout=5)
                if close_btn_notice is None and close_btn is None:
                    xiuxian_btn = find_ga(xpath="//*[@name='w_txt_ModeName']", by=DriverType.GA_UE, timeout=5)
                    if xiuxian_btn is not None:
                        logger.debug('enter 排位赛 select')
                        click((xiuxian_btn[0] + 0.04, xiuxian_btn[1] + 0.01), by=DriverType.POS, timeout=5)
                        time.sleep(1)
                        person_count = para.split('{')[1].split(';')[0].split(':')
                        person_count = person_count[1].split('\'')[1]
                        mapid = para.split('{')[1].split(';')[1].split(':')[1].split('\'')[1]

                        if person_count == '单人':
                            pos = find('single_person.jpg', by=DriverType.CV, timeout=10)
                            ret = click(pos, by=DriverType.POS, timeout=10)
                            logger.debug('click 排位赛%s')
                        elif person_count == '双人':
                            pos = find('two_person.jpg', by=DriverType.CV, timeout=10)
                            ret = click(pos, by=DriverType.POS, timeout=10)
                            logger.debug('click 排位赛%s')
                        elif person_count == '四人':
                            pos = find('four_person.jpg', by=DriverType.CV, timeout=10)
                            ret = click(pos, by=DriverType.POS, timeout=10)
                            logger.debug('click 排位赛%s')
                        #tree = get_uitree(by=DriverType.GA_UE, all_wins=False)
                        gm_btn = find_ga(xpath="//*[@name='w_btn_StartGame']", by=DriverType.GA_UE, timeout=10)
                        click((gm_btn[0] + 0.04, gm_btn[1] + 0.01), by=DriverType.POS, timeout=5)
                        click('开始', by=DriverType.OCR, timeout=5)
                        #self.matching_start_time = datetime.datetime.now(tz=None).strftime('%Y-%m-%d %H-%M-%S')
                        time.sleep(5)
                        #点击匹配后处于匹配中
                        self.state = machine_stat.STAT_GAME_MATCHING
                        logger.debug('set state：%d %s' % (self.state, machine_stat().stat_string(self.state)))
                        set_status(self.uuid, self.platform, '匹配中')
                        self.open_gm_exec('20 开启单局AI托管，局内使用')
                        cmd = None
        if cmd == cmd_id.cmd_xiuxian_party and self.state == machine_stat.STAT_DATING:
            start_game = find_ga(xpath="//*[@name='w_btn_StartGame']", by=DriverType.GA_UE, timeout=5)
            # if find_ocr('开始', timeout=10, is_regular=True):
            if start_game:
                # 主玩法选择流程
                # tree = get_uitree(by=DriverType.GA_UE, all_wins=False)
                close_btn = find_ga(xpath="//*[@name='w_Button_Close']", by=DriverType.GA_UE, timeout=5)
                close_btn_notice = find_ga(xpath="//*[@name='w_btn_Close']", by=DriverType.GA_UE, timeout=5)
                if close_btn_notice is None and close_btn is None:
                    xiuxian_btn = find_ga(xpath="//*[@name='w_txt_ModeName']", by=DriverType.GA_UE, timeout=5)
                    if xiuxian_btn is not None:
                        logger.debug('enter 排位赛')
                        click((xiuxian_btn[0] + 0.04, xiuxian_btn[1] + 0.03), by=DriverType.POS, timeout=5)
                        time.sleep(1)
                        click('休闲赛', by=DriverType.OCR, timeout=5)
                        time.sleep(1)
                        person_count = para.split('{')[1].split(';')[0].split(':')
                        person_count = person_count[1].split(':').split('\'')
                        mapid = para.split('{')[1].split(';')[1].split(':')[1]

                        ret = click(person_count[1], by=DriverType.OCR, timeout=10)
                        logger.debug('click 排位赛%s' % str(ret))

                        time.sleep(1)
                        logger.debug('click 休闲派对%s' % str(ret))
                        # tree = get_uitree(by=DriverType.GA_UE, all_wins=False)
                        gm_btn = find_ga(xpath="//*[@name='w_btn_StartGame']", by=DriverType.GA_UE, timeout=5)
                        click((gm_btn[0] + 0.04, gm_btn[1] + 0.01), by=DriverType.POS, timeout=5)
                        click('开始', by=DriverType.OCR, timeout=5)
                        self.matching_start_time = datetime.now(tz=None).strftime('%Y-%m-%d %H-%M-%S')
                        time.sleep(5)
                        # 点击匹配后处于匹配中
                        self.state = machine_stat.STAT_GAME_MATCHING
                        logger.debug('set state：%d %s' % (self.state, machine_stat().stat_string(self.state)))
                        set_status(self.uuid, self.platform, '匹配中')
                        self.open_gm_exec('20 开启单局AI托管，局内使用')
                        cmd = None
        if self.state == machine_stat.STAT_GAME_MATCHING and (self.cur_time - self.matching_start_time).second > 60:
            #匹配超时处理. 匹配超过60s就退出当前匹配任务

            self.state = machine_stat.STAT_DATING
            logger.debug('set state：%d %s'%(self.state,machine_stat().stat_string(self.state)))
            set_status(self.uuid, self.platform, '大厅中')

        if self.state == machine_stat.STAT_GAME_MATCHING:
            if find('ds_main_play.jpg', by=DriverType.CV, timeout=5) \
                or find('ds_main_play_person.jpg', by=DriverType.CV, timeout=5) \
                or find('return_ds_mian_play.jpg', by=DriverType.CV, timeout=5):
                self.state = machine_stat.STAT_GAME_MAIN_PLAY_DS
                logger.debug('set state：%d %s' % (self.state, machine_stat().stat_string(self.state)))
                set_status(self.uuid, self.platform, '对局中')
        if self.state == machine_stat.STAT_GAME_MAIN_PLAY_DS:
            if find('level_up.jpg', by=DriverType.CV, timeout=5):
            #对局结束等级提升弹框流程处理
                click('等级提升', by=DriverType.OCR, timeout=5)
                time.sleep(2)
                click('继续', by=DriverType.OCR, timeout=5)
                time.sleep(2)
                click('返回大厅', by=DriverType.OCR, timeout=5)
                time.sleep(2)
                self.state = machine_stat.STAT_DATING
                logger.debug('set state：%d %s' % (self.state, machine_stat().stat_string(self.state)))

        if cmd == cmd_id.cmd_anmimal_party or cmd_id == cmd_id.cmd_hide_and_seek:
            if self.state == machine_stat.STAT_DATING and find_ocr('巅峰派对', timeout=5, is_regular=True):
                #副玩法选择流程
                click('坏蛋来袭', by=DriverType.OCR,timeout=5)
                #self.state = machine_stat.STAT_GAME_MODE_SELECT

        if self.state == machine_stat.STAT_DATING and find_ocr('恭喜获得', timeout=5, is_regular=True):
            logger.debug('enter 恭喜获得')
            click('确认', by=DriverType.OCR, timeout=20)
            time.sleep(2)

        if self.state == machine_stat.STAT_DATING and find_ocr('立即重连', timeout=5, is_regular=True):
            logger.debug('enter 立即重连')
            click('立即重连', by=DriverType.OCR, timeout=20)
            time.sleep(3)

        if find_ocr('断线重连', timeout=2,is_regular=True):
            click('确定', by=DriverType.OCR, timeout=10)
            time.sleep(1)

        if cmd == 'gm' and self.state == machine_stat.STAT_DATING:
            if para == GM.DATING_AI_OPEN:
                self.open_gm_exec('21 开启全局AI托管，局外使用', 3)
            elif para == GM.DS_AI_OPEN:
                self.open_gm_exec('23 开启单局AI托管，局内使用', 3)
    def open_select_svr(self,svr_name,txt_tag):
        #selectsvr_btn = find_ga(xpath="//*[@name='w_ComboBox_SelectServer']", by=DriverType.GA_UE, timeout=5)
        selectsvr_btn2 = find(svr_name, by=DriverType.OCR, timeout=10)
        logger.debug('enter select svrlist')
        if selectsvr_btn2:
            selectsvr_btn2[0] = selectsvr_btn2[0] + 0.07
        click(selectsvr_btn2, by=DriverType.POS, timeout=5)
        time.sleep(1)
        #click((gm_btn[0] + 0.07, gm_btn[1] + 0.06), by=DriverType.POS, timeout=5)
        time.sleep(2)
        self.find_svr_name_exec(svr_name,txt_tag)
        time.sleep(2)

    def open_gm_exec(self, gm_str):
        gm_btn = find_ga(xpath="//*[@name='w_button_GM']", by=DriverType.GA_UE, timeout=5)
        logger.debug('enter GM')
        click((gm_btn[0] + 0.04, gm_btn[1] + 0.01), by=DriverType.POS, timeout=5)
        time.sleep(2)
        self.find_gm_and_exec(gm_str, 3)
        time.sleep(2)

    def find_svr_name_exec(self, svr_name,txt_tag, times=5):
        '''
        调用前，确保GM面板是打开状态，通过 gm描述找到对应到gm命令所在位置，并执行命令
        '''
        #首次先找到滚动条初始位置x,y
        start_pos = None
        timeout = 0
        while start_pos is None:
            start_pos = find_ocr(svr_name, timeout=15, is_regular=True)
            if start_pos:
                start_pos = (start_pos[0] + 0.05, start_pos[1]+0.06)
        #查找待执行待GM命令坐标，如果找不到，就往下滑动y=+0.3，直到结束
        while True:
            if timeout > times:
                Logger.debug('gm执行超时:%s'%svr_name)
                break
            #svr_btn_pos = find(txt_tag, by=DriverType.OCR, timeout=10)
            if txt_tag=='Test':
                svr_btn_pos = find('Test_svr.jpg', by=DriverType.CV, timeout=10)
            elif txt_tag =='release转测服':
                svr_btn_pos = find('release2test_svr.jpg', by=DriverType.CV, timeout=10)
            elif txt_tag == '稳定服':
                svr_btn_pos = find('stable_svr.jpg', by=DriverType.CV, timeout=10)

            if svr_btn_pos is None:
                # y坐标每次向下滑动0.2个位置
                loc_to = (start_pos[0], start_pos[1]+0.2)
                slide_pos(loc_to, None, pos_shift=(0.0, -0.4), velocity=1)
                timeout = timeout + 1
            else:
                #找到则执行命令
                time.sleep(1)
                self.gm_exec(txt_tag, svr_btn_pos)
                break
        pass
    def find_gm_and_exec(self, gm_str, times):
        '''
        调用前，确保GM面板是打开状态，通过 gm描述找到对应到gm命令所在位置，并执行命令
        '''
        #首次先找到滚动条初始位置x,y
        start_pos = None
        timeout = 0
        while start_pos is None:
            start_pos = find_ocr('打开回放界面', timeout=15, is_regular=True)
            if start_pos is not None:
                start_pos = (start_pos[0] + 0.09, start_pos[1])
            #time.sleep(1)
            continue
        #查找待执行待GM命令坐标，如果找不到，就往下滑动y=+0.3，直到结束
        while True:
            if timeout > times:
                Logger.debug('gm执行超时:%s'%gm_str)
                break
            tree = get_uitree(by=DriverType.GA_UE, all_wins=False)
            _xpath = "//*[@txt=\'"+gm_str+'\']'
            #gm_btn_pos = find_ga(xpath="//*[@txt='18 开启全局AI托管，局外使用']", by=DriverType.GA_UE, timeout=5)
            gm_btn_pos = find_ga(xpath=_xpath, by=DriverType.GA_UE, timeout=5)
            if gm_btn_pos is None:
                # y坐标每次向下滑动0.2个位置
                loc_to = (start_pos[0], (start_pos[1]+0.6)/1)
                slide_pos(loc_to, start_pos, velocity=1)
                timeout = timeout + 1
            else:
                #找到则执行命令
                time.sleep(1)
                self.gm_exec(gm_str, gm_btn_pos)
    def gm_close(self):
        gm_close_pos = find('gm_close.jpg', by=DriverType.CV, timeout=5)
        if gm_close_pos:
            ret = click(gm_close_pos, by=DriverType.POS, timeout=20)
            time.sleep(1)
            logger.debug('click3 gm关闭:%s' % str(ret))

    def gm_exec(self, gm_str, pos):
        '''
        已经找到GM指令的情况下，执行gm指令，这里需要考虑一些带参数输入的GM情况处理
        '''
        if gm_str in '18 开启全局AI托管，局外使用':
            #click(gm_str, by=DriverType.OCR, timeout=20)
            click(pos, by =DriverType.POS, timeout=20)
            time.sleep(1)
            click('执行', by=DriverType.OCR, timeout=20)
            time.sleep(1)
            self.gm_close()
        elif gm_str in '20 开启单局AI托管，局内使用':
            #click(gm_str, by=DriverType.OCR, timeout=20)
            click(pos, by=DriverType.POS, timeout=20)
            time.sleep(1)
            click('执行', by=DriverType.OCR, timeout=20)
            time.sleep(1)
            self.gm_close()
        else:
            #选服处理
            pos[1] = pos[1] - 0.015
            click(pos, by=DriverType.POS, timeout=20)
            time.sleep(1)

    def post_test(self):
        logger.debug('TestCase:post_test')
        self.start_step('stop app')
        stop_driver()

if __name__== '__main__':
    DemoTestCase().run()
