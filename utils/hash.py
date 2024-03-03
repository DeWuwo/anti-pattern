import hashlib
from typing import List
from utils import FileCommon


class Hash:

    @classmethod
    def get_hash(cls, string: str):
        return hashlib.md5(string.encode('utf-8')).hexdigest()

    @classmethod
    def get_hash_from_list(cls, strings: List[str]):
        return hashlib.md5("".join(strings).encode('utf-8')).hexdigest()


if __name__ == '__main__':
    print(Hash.get_hash(''.join(FileCommon.read_file_to_scope(
        'D:\\Honor\\source_code\\android\\base\\packages/SystemUI/src/com/android/systemui/statusbar/phone/StatusBar.java',
        498, 44, 520, 4))))
    print(Hash.get_hash(''.join(FileCommon.read_file_to_scope(
        'D:\\Honor\\source_code\\aospa\\base\\packages/SystemUI/src/com/android/systemui/statusbar/phone/StatusBar.java',
        4215, 44, 4237, 4))))
