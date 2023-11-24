import os

from baseline.entity_owner import EntityOwner

from baseline.gumtree import Gumtree
from utils import FileCSV


class Compare:

    def compare_file_gumtree(self, out_path: str):
        our_path = os.path.join(out_path, 'intrusive_analysis', 'intrusive_file_count.csv')
        gum_path = os.path.join(out_path, 'gumdiff')
        our_files = EntityOwner.get_diff_files(our_path)
        gum_files = Gumtree.get_diff_files(gum_path)
        same_files = set(our_files) & set(gum_files)
        left_files = set(gum_files) - set(same_files)
        right_files = set(our_files) - set(same_files)
        FileCSV.write_dict_to_csv(out_path, 'compare_gum', [
            {'intersection': len(same_files), 'gum_diff': len(left_files), 'our': len(right_files), "left": left_files,
             "right": right_files}], 'w')
        FileCSV.write_dict_to_csv('D\\Honor\\gumdiff', 'compare_gum', [
            {'intersection': len(same_files), 'gum_diff': len(left_files), 'our': len(right_files)}], 'a')


if __name__ == '__main__':
    Compare().compare_file_gumtree("D:\\Honor\\match_res\\LineageOS\\base\\lineage-18.1")
