import os
from TimiAutomation.sdk.envs import CaseEnvs


from TimiAutomation.uitrace.utils.param import OSType


def get_uuid():
    mode = 'tet' if 'smart_id' in os.environ.keys()  else 'local'
    if mode == 'local':
            # 本地调试
            uuid = "TTDUT21C02010497"
            platform = OSType.ANDROID
            package_name = "com.tencent.letsgo"
    else:
            # 通过环境变量初始化
            case_envs =  CaseEnvs()
            device_attr = self.case_envs.device_attribute
            platform = OSType.ANDROID if device_attr.platform.lower() == "android" else OSType.IOS
            uuid = device_attr.serial