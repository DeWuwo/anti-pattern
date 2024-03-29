import re
from typing import List


class Constant:
    # entity type
    E_method: str = "Method"
    E_variable: str = "Variable"
    E_class: str = "Class"
    E_file: str = "File"
    E_package: str = "Package"
    E_interface: str = "Interface"
    E_annotation: str = 'Annotation'
    E_annotation_mem: str = 'Annotation Member'
    E_enum: str = 'Enum'
    E_enum_cnt: str = 'Enum Constant'
    E_type_parameter: str = 'Type Parameter'

    # relation type
    contain: str = "Contain"
    define: str = "Define"
    call: str = "Call"
    param: str = "Parameter"
    use: str = "UseVar"
    implement: str = "Implement"
    inherit: str = "Inherit"
    override: str = 'Override'
    typed: str = 'Typed'
    reflect: str = 'Reflect'
    R_import: str = 'Import'
    R_cast: str = 'Cast'
    R_annotate: str = 'Annotate'
    R_super_call: str = 'Call non-dynamic'
    R_modify: str = 'Modify'
    R_aggregate: str = 'Aggregate'
    R_set: str = 'Set'

    entities: List[str] = [E_package, E_file, E_class, E_interface, E_method, E_variable, E_annotation,
                           E_annotation_mem, E_enum, E_enum_cnt, E_type_parameter]

    Relations: List[str] = [call, define, use, R_aggregate, typed, R_set, R_modify, R_annotate, param, reflect,
                            override, implement, inherit, R_cast, R_super_call, contain, R_import]
    CoreRelation: List[str] = [R_aggregate, R_annotate, implement, inherit, call, param, reflect, override]
    relation_count_score = {
        call: 100,
        define: 200,
        R_aggregate: 10,
        typed: 5,
        R_annotate: 5,
        param: 3,
        reflect: 3,
        override: 3,
        implement: 2,
        inherit: 1,
        contain: 100,
    }

    # anti-pattern name
    ACM: str = "AOSPAccessModify"
    APM: str = "AOSPParameterModify"
    AAM: str = "AOSPAnnotationModify"
    ACAPC: str = "AOSPClassADDParentClass"
    AFD: str = "AOSPFinalDelete"

    # modifier
    accessible_list: List[str] = ['private', 'protected', 'public', 'null']
    accessible_level: dict = {
        'private': 0,
        'null': 1,
        'protected': 2,
        'public': 3
    }

    M_abstract: str = 'abstract'
    M_final: str = 'final'
    M_static: str = 'static'
    un_define: str = 'null'

    # rule_type
    sing_rule: int = 0
    multi_rule: int = 1

    # file_name
    file_mc = 'mc/file-mc.csv'

    # ano
    anonymous_class = 'Anonymous_Class'

    # hidden api sign
    HD_blocked: str = 'blocked'
    HD_unsupported: str = 'unsupported'
    HD_max_target = re.compile('max-target-(.*)')
    HD_sdk: str = 'sdk'
    HD_blacklist: str = 'blacklist'
    HD_greylist: str = 'greylist'
    HD_greylist_max = re.compile('greylist-max-(.*)')
    HD_whitelist: str = 'whitelist'
    HD_greylist_max_label = 'greylist-max-'
    versions = ['o', 'p', 'q', 'r', 's', 't', 'u']
    HD_greylist_max_list: List[str] = [f"greylist-max-{ver}" for ver in versions]

    HD_hidden = 'hidden'

    @classmethod
    def hidden_map(cls, label: List[str]) -> str:
        if cls.HD_blocked in label or cls.HD_blacklist in label:
            return cls.HD_blacklist
        elif cls.HD_unsupported in label or cls.HD_greylist in label:
            return cls.HD_greylist
        elif cls.HD_sdk in label or cls.HD_whitelist in label:
            return cls.HD_whitelist
        elif cls.HD_hidden in label:
            return cls.HD_hidden
        else:
            for max_label in label:
                match = cls.HD_max_target.match(max_label)
                if match:
                    return cls.HD_greylist_max_label + match.group(1)
                match = cls.HD_greylist_max.match(max_label)
                if match:
                    return max_label
                return "null"

    Owner_actively_native = 'actively native'
    Owner_obsoletely_native = 'obsoletely native'
    Owner_intrusive_native = 'intrusive native'
    Owner_extensive = 'extensive'

    core_list = [
        # others
        'services/core/java/com/android/server/audio/AudioService.java',
        'core/java/android/view/ViewRootImpl.java',
        'services/core/java/com/android/server/notification/NotificationManagerService.java',
        'services/core/java/com/android/server/power/PowerManagerService.java',
        'services/core/java/com/android/server/display/DisplayPowerController.java',
        "services/core/java/com/android/server/vibrator/VibrationThread.java",
        "services/core/java/com/android/server/input/InputManagerService.java",

        # AMS
        'services/core/java/com/android/server/am/ActiveServices.java',
        "services/core/java/com/android/server/am/BroadcastQueue.java",
        "services/core/java/com/android/server/am/ActivityManagerService.java",

        # WMS
        "services/core/java/com/android/server/wm/ActivityRecord.java",
        "services/core/java/com/android/server/wm/WindowManagerService.java",
        "services/core/java/com/android/server/wm/Task.java",
        "services/core/java/com/android/server/wm/DisplayContent.java",
        "services/core/java/com/android/server/wm/DisplayPolicy.java",
        "services/core/java/com/android/server/wm/WindowState.java",

        # PMS
        "services/core/java/com/android/server/pm/InstallPackageHelper.java",
        "services/core/java/com/android/server/pm/PackageManagerService.java",
        "services/core/java/com/android/server/pm/Settings.java",
        "services/core/java/com/android/server/pm/permission/PermissionManagerService.java",
        "services/core/java/com/android/server/pm/BackgroundDexOptService.java",

    ]
    # "packages/services/HnSystemService"
    module_list = {}

    module_files = []

    filter_list = ['android.util', 'android.os.Message', 'com.android.internal.logging',
                   'com.android.internal.os', 'android.os', 'com.android.server.utils',
                   'hihonor.android.utils', 'android.os.ServiceManager', 'com.android.server.LocalServices',
                   'android.provider.Settings.Secure', 'android.provider.Settings.System',
                   'com.android.telephony.Rlog']

    @staticmethod
    def load_core_files(file_path):
        file_list = []
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                if '/' in line:
                    file_list.append(line.strip().strip('/'))
            Constant.core_list = file_list

    @staticmethod
    def load_module_files(file_path):
        module_name = "default"
        total_list = []
        file_list = []
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                if '#' in line:
                    if file_list:
                        module = {module_name: file_list}
                        if module_name not in Constant.module_list.keys():
                            Constant.module_list.update(module)
                        file_list = []
                    module_name = line[1:].strip()
                if '/' in line:
                    file_list.append(line.strip().strip('/'))
                    total_list.append(line.strip().strip('/'))
            if file_list:
                module = {module_name: file_list}
                if module_name not in Constant.module_list.keys():
                    Constant.module_list.update(module)
        Constant.module_files = total_list
