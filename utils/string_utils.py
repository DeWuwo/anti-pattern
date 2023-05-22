from typing import List


class StringUtils:
    @classmethod
    def replace_str(cls, old_string, start_index, end_index, replace_str: str):
        old_string = str(old_string)
        new_string = old_string[:start_index] + replace_str + old_string[end_index + 1:]
        return new_string

    @classmethod
    def replace_char(cls, old_string, index, char: str):
        old_string = str(old_string)
        new_string = old_string[:index] + char + old_string[index + 1:]
        return new_string

    @classmethod
    def find_str(cls, string: str, char: str):
        index_list = []
        for index in range(0, len(string)):
            if string[index] == char:
                index_list.append(index)
        return index_list

    @classmethod
    def find_char(cls, string: str, char: str):
        index_list = []
        for index in range(0, len(string)):
            if string[index] == char:
                index_list.append(index)
        return index_list

    @classmethod
    def find_str_in_list(cls, string: str, str_list: List[str]):
        if string in str_list:
            return True
        for single_str in str_list:
            if single_str.endswith(string):
                return True
        return False

    @classmethod
    def find_str_in_short_list(cls, string: str, str_list: List[str]):
        if string in str_list:
            return True
        for single_str in str_list:
            if string.startswith(single_str):
                return True
        return False


if __name__ == '__main__':
    a = '12315'
    print(StringUtils.find_str_in_short_list('android.util.Slog.w', ['android.util', 'android.os.Message', 'com.android.internal.logging',
                   'com.android.internal.os', 'android.os', 'com.android.server.utils',
                   'hihonor.android.utils', 'android.os.ServiceManager', 'com.android.server.LocalServices',
                   'android.provider.Settings.Secure', 'android.provider.Settings.System',
                   'com.android.telephony.Rlog']))
