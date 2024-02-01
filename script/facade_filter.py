import os
import networkx as nx
import matplotlib.pyplot as plt
from typing import List
from collections import defaultdict
from functools import partial
from utils import FileCSV, FileJson, Constant


class FacadeFilter:
    file_path: str
    file_name: str
    relation_types: List[str]

    def __init__(self, file_path: str, file_name: str, relation_types: List[str]):
        self.file_path = file_path
        self.file_name = os.path.join(file_path, file_name)
        self.relation_types = relation_types

    def facade_filter(self):
        res = {}
        file_res = defaultdict(partial(defaultdict, int))
        facade_info = FileJson.read_base_json(self.file_name)
        n2e: List[dict] = facade_info['res']['n2e']
        e2n: List[dict] = facade_info['res']['e2n']
        for rel_type in self.relation_types:
            res[rel_type + '_e2n'] = 0
            res[rel_type + '_n2e'] = 0
        for rel in e2n:
            src_e = rel['src']
            dest_e = rel['dest']
            rel_type: str = ''
            for k in rel['values'].keys():
                rel_type = str(k)
                break
            if rel_type in self.relation_types:
                if rel_type == Constant.R_annotate:
                    if dest_e['category'] == Constant.E_variable:
                        continue
                    file_res[dest_e['File']]['e2n_e'] += 1
                    file_res[src_e['File']]['e2n_n'] += 1
                res[rel_type + '_e2n'] += 1
                file_res[src_e['File']]['e2n_e'] += 1
                file_res[dest_e['File']]['e2n_n'] += 1
        for rel in n2e:
            src_e = rel['src']
            dest_e = rel['dest']
            rel_type: str = ''
            for k in rel['values'].keys():
                rel_type = str(k)
                break
            if rel_type in self.relation_types:
                if rel_type == Constant.R_annotate:
                    if dest_e['category'] == Constant.E_variable:
                        continue
                    if src_e['qualifiedName'] in ["com.android.internal.annotations.GuardedBy",
                                                  "android.telephony.data.ApnSetting.ApnType"]:
                        continue
                    file_res[dest_e['File']]['n2e_n'] += 1
                    file_res[src_e['File']]['n2e_e'] += 1
                res[rel_type + '_n2e'] += 1
                file_res[src_e['File']]['n2e_n'] += 1
                file_res[dest_e['File']]['n2e_e'] += 1
        FileCSV.write_dict_to_csv(self.file_path, 'facade_filter', [res], 'w')
        FileCSV.write_file_to_csv(self.file_path, 'facade_file_filter', file_res, 'file',
                                  ['e2n_e', 'e2n_n', 'n2e_n', 'n2e_e'])

    def filter_hidden(self):
        res = defaultdict(partial(defaultdict, int))
        intrusive_res = {}
        hidden_json = defaultdict(list)
        rel_json = defaultdict(list)
        facade_info = FileJson.read_base_json(self.file_name)
        n2e: List[dict] = facade_info['res']['n2e']
        e2n: List[dict] = facade_info['res']['e2n']
        heads_hd_rel = []
        heads_hd_intrusive = []
        hidden_level = [Constant.HD_blacklist, Constant.HD_greylist,
                        Constant.HD_whitelist] + Constant.HD_greylist_max_list
        for label in hidden_level:
            for rel in Constant.Relations:
                heads_hd_rel.append(f'{label}_{rel}')
        for label in hidden_level:
            heads_hd_intrusive.append(f'{label}_1')
            intrusive_res.update({f'{label}_1': 0, f'{label}_0': 0})
            heads_hd_intrusive.append(f'{label}_0')

        for rel in e2n:
            src_e = rel['src']
            dest_e = rel['dest']
            rel_type: str = ''
            for k in rel['values'].keys():
                rel_type = str(k)
                if rel_type == 'Typed':
                    qualifiedName: str = src_e['qualifiedName']
                    temp = qualifiedName.rsplit('.', 2)
                    if temp[1][0].isupper() and temp[1] not in temp[0]:
                        rel_type = 'Aggregate'
                break
            try:
                if rel_type == Constant.R_annotate:
                    hidden_flag = Constant.hidden_map(src_e['hidden'])
                    is_intrusive = src_e['isIntrusive']
                else:
                    hidden_flag = Constant.hidden_map(dest_e['hidden'])
                    is_intrusive = dest_e['isIntrusive']
                if src_e['not_aosp'] != dest_e['not_aosp'] and \
                        hidden_flag in [Constant.HD_blacklist,
                                        Constant.HD_greylist, Constant.HD_whitelist] + Constant.HD_greylist_max_list:
                    res[dest_e['qualifiedName']][hidden_flag + '_' + rel_type] += 1
                    if rel_type == Constant.call:
                        intrusive_res[f'{hidden_flag}_{is_intrusive}'] += 1
                    hidden_json[hidden_flag + '_' + rel_type + '_e2n'].append(rel)
            except KeyError:
                pass
        for rel in n2e:
            src_e = rel['src']
            dest_e = rel['dest']
            rel_type: str = ''
            for k in rel['values'].keys():
                rel_type = str(k)
                break
            try:
                if rel_type == Constant.R_annotate:
                    hidden_flag = Constant.hidden_map(dest_e['hidden'])
                else:
                    hidden_flag = Constant.hidden_map(src_e['hidden'])
                if src_e['not_aosp'] != dest_e['not_aosp'] and \
                        hidden_flag in [Constant.HD_blacklist,
                                        Constant.HD_greylist, Constant.HD_whitelist] + Constant.HD_greylist_max_list:
                    # res[src_e['qualifiedName']][hidden_flag + '_' + rel_type + '_n2e'] += 1
                    hidden_json[hidden_flag + '_' + rel_type + '_n2e'].append(rel)
            except KeyError:
                pass
        FileCSV.write_file_to_csv(self.file_path, 'facade_hidden_filter', res, 'name', heads_hd_rel)
        FileCSV.write_dict_to_csv(self.file_path, 'facade_hidden_intrusive_count', [intrusive_res], 'w')
        FileJson.write_data_to_json(self.file_path, hidden_json, 'facade_hidden_hidden.json')
        # FileJson.write_data_to_json(self.file_path, rel_json, 'facade_hidden_rel.json')

    def get_facade_files(self):
        e2n, n2e = self.load_facade()
        file_set = set()
        for rel in e2n + n2e:
            src_e = rel['src']
            dest_e = rel['dest']
            file_set.add(src_e['File'])
            file_set.add(dest_e['File'])
        return file_set

    def load_facade(self):
        facade_info = FileJson.read_base_json(self.file_name)
        n2e: List[dict] = facade_info['res']['n2e']
        e2n: List[dict] = facade_info['res']['e2n']
        return e2n, n2e

    def get_facade_conf(self, project: str):
        conf_file_set = []
        inter_set = []
        conf_info = FileCSV.read_from_file_csv(os.path.join(self.file_path, 'conf_files.csv'), False)
        for line in conf_info:
            for file_name in line:
                conf_file_set.append(file_name)
        facade_file_set = self.get_facade_files()
        for conf in conf_file_set:
            if conf in facade_file_set:
                inter_set.append(conf)
        # inter_set = facade_file_set & conf_file_set
        return {'project': project, 'conf_files': len(conf_file_set), 'facade_files': len(facade_file_set),
                'inter_set': len(inter_set), 'rate': float(len(inter_set) / len(conf_file_set)),
                'files': list(inter_set)}

    def get_module_stat(self):
        e2n, n2e = self.load_facade()
        nodes_map = {}
        edges_map = {}
        for rel in e2n + n2e:
            src = rel['src']
            dest = rel['dest']
            rel_type = list(rel["values"].keys())[0]
            if src['category'] == Constant.E_file or src['category'] == Constant.E_package or \
                    dest['category'] == Constant.E_file or dest['category'] == Constant.E_package:
                continue
            if rel_type not in self.relation_types:
                continue
            src_pkg = src['packageName']
            dest_pkg = dest['packageName']
            # 添加src节点
            if src_pkg not in nodes_map.keys():
                new_node = {
                    "name": src_pkg,
                    'src': {
                        'actively native': set(),
                        'intrusive native': set(),
                        'extensive': set(),
                        'obsoletely_native': set()
                    },
                    'dest': {
                        'actively native': set(),
                        'intrusive native': set(),
                        'extensive': set(),
                        'obsoletely_native': set()
                    }
                }
                nodes_map.update({src_pkg: new_node})
            nodes_map[src_pkg]['src'][src['ownership']].add(src['qualifiedName'])
            # 添加dest节点
            if dest_pkg not in nodes_map.keys():
                new_node = {
                    "name": src_pkg,
                    'src': {
                        'actively native': set(),
                        'intrusive native': set(),
                        'extensive': set(),
                        'obsoletely_native': set()
                    },
                    'dest': {
                        'actively native': set(),
                        'intrusive native': set(),
                        'extensive': set(),
                        'obsoletely_native': set()
                    }
                }
                nodes_map.update({dest_pkg: new_node})
            nodes_map[dest_pkg]['dest'][dest['ownership']].add(dest['qualifiedName'])

            # 添加依赖
            if f"{src_pkg}_{dest_pkg}" not in edges_map.keys():
                const_rels = {}
                for const_rel in self.relation_types:
                    const_rels.update({const_rel: 0})
                new_edge = {
                    "name": f"{src_pkg}_{dest_pkg}",
                    "src": src_pkg,
                    "dest": dest_pkg,
                    "relations": const_rels,
                    'weight': 0
                }
                edges_map.update({f"{src_pkg}_{dest_pkg}": new_edge})
            edges_map[f"{src_pkg}_{dest_pkg}"]['relations'][rel_type] += 1
            edges_map[f"{src_pkg}_{dest_pkg}"]['weight'] += 1

        nodes = []
        for pkg in nodes_map.keys():
            temp = nodes_map[pkg]
            src = {}
            dest = {}
            for owner in temp['src'].keys():
                src.update({owner: len(temp['src'][owner])})
                dest.update({owner: len(temp['dest'][owner])})

            nodes.append({'name': pkg, 'src': src, 'dest': dest})
            nodes_map[pkg] = {'name': pkg, 'src': src, 'dest': dest}
        edges = [edges_map[pkgs] for pkgs in edges_map.keys()]
        edges = sorted(edges, key=lambda k: k.get('weight', 0), reverse=True)
        res = {'nodes': nodes,
               "edges": edges}
        FileJson.write_to_json('D:/Honor/merge/facade', res, 'facade_stat')

        res_csv = []
        for edge in edges:
            edge_csv = {}
            edge_csv.update({'src': edge['src'], 'dest': edge['dest']})
            edge_csv.update(edge['relations'])
            src_info = nodes_map[edge['src']]
            for owner, src_weight in src_info['src'].items():
                edge_csv.update({f"src_{owner}": src_weight})
            dest_info = nodes_map[edge['dest']]
            for owner, dest_weight in dest_info['dest'].items():
                edge_csv.update({f"dest_{owner}": dest_weight})
            res_csv.append(edge_csv)
        FileCSV.write_dict_to_csv('D:/Honor/merge/facade', 'facade_stat', res_csv, 'w')
        filter_nodes = []
        filter_edges = edges[0: 10]
        temp_node = set()
        for edge in filter_edges:
            temp_node.add(edge['src'])
            temp_node.add(edge['dest'])
        for node in temp_node:
            filter_nodes.append(nodes_map[node])

        # 生成图
        G = nx.Graph()

        node_label = {}
        edge_label = {}
        for node in filter_nodes:
            G.add_node(node['name'], attr=node)
        for node in G.nodes:
            node_label[node] = G.nodes[node]
        node_label = nx.get_node_attributes(G, 'attr')

        for edge in filter_edges:
            G.add_edge(edge['src'], edge['dest'], attr=edge['relations'])

        for edge in G.edges:
            edge_label[edge] = G.edges[edge]

        pos = nx.shell_layout(G)
        nx.draw(G, pos)

        nx.draw_networkx_nodes(G, pos)

        nx.draw_networkx_edges(G, pos, width=1, edge_color='dodgerblue',
                               arrowstyle="->", arrowsize=30, arrows=True)

        nx.draw_networkx_labels(G, pos, labels=node_label, font_size=7)

        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_label, font_size=7, )
        plt.show()

    def get_module_stat_2(self, out_name):
        e2n, n2e = self.load_facade()
        nodes_map = {}
        edges_map = {}
        for rel in e2n + n2e:
            src = rel['src']
            dest = rel['dest']
            rel_type = list(rel["values"].keys())[0]
            if src['category'] == Constant.E_file or src['category'] == Constant.E_package or \
                    dest['category'] == Constant.E_file or dest['category'] == Constant.E_package:
                continue
            if rel_type not in self.relation_types:
                continue
            src_pkg = src['packageName']
            dest_pkg = dest['packageName']
            # 添加src节点
            if src_pkg not in nodes_map.keys():
                new_node = {
                    "name": src_pkg,
                    'weight': {
                        'actively native': set(),
                        'intrusive native': set(),
                        'extensive': set(),
                        'obsoletely_native': set()
                    }
                }
                nodes_map.update({src_pkg: new_node})
            nodes_map[src_pkg]['weight'][src['ownership']].add(src['qualifiedName'])
            # 添加dest节点
            if dest_pkg not in nodes_map.keys():
                new_node = {
                    "name": dest_pkg,
                    'weight': {
                        'actively native': set(),
                        'intrusive native': set(),
                        'extensive': set(),
                        'obsoletely_native': set()
                    }
                }
                nodes_map.update({dest_pkg: new_node})
            nodes_map[dest_pkg]['weight'][dest['ownership']].add(dest['qualifiedName'])

            # 添加依赖
            if f"{src_pkg}_{dest_pkg}" not in edges_map.keys():
                const_rels = {}
                for const_rel in self.relation_types:
                    const_rels.update({const_rel: 0})
                new_edge = {
                    "name": f"{src_pkg}_{dest_pkg}",
                    "src": src_pkg,
                    "dest": dest_pkg,
                    "relations": const_rels,
                    "owner": {
                        "extensive-actively native": 0,
                        "extensive-intrusive native": 0,
                        "extensive-obsoletely_native": 0,
                        "intrusive native-extensive": 0,
                        'obsoletely_native-extensive': 0,
                        'actively native-extensive': 0
                    },
                    'weight': 0
                }
                edges_map.update({f"{src_pkg}_{dest_pkg}": new_edge})
            edges_map[f"{src_pkg}_{dest_pkg}"]['relations'][rel_type] += 1
            edges_map[f"{src_pkg}_{dest_pkg}"]['owner'][f"{src['ownership']}-{dest['ownership']}"] += 1
            edges_map[f"{src_pkg}_{dest_pkg}"]['weight'] += 1

        nodes = []
        for pkg in nodes_map.keys():
            temp = nodes_map[pkg]
            weight = {}
            for owner in temp['weight'].keys():
                weight.update({owner: len(temp['weight'][owner])})
            nodes.append({'name': pkg, 'weight': weight})
            nodes_map[pkg] = {'name': pkg, 'weight': weight}
        edges = [edges_map[pkgs] for pkgs in edges_map.keys()]
        edges = sorted(edges, key=lambda k: k.get('weight', 0), reverse=True)
        res = {'nodes': nodes,
               "edges": edges}
        FileJson.write_to_json('D:/Honor/merge/facade', res, out_name)

        res_csv = []
        for edge in edges:
            edge_csv = {}
            edge_csv.update({'src': edge['src'], 'dest': edge['dest']})
            edge_csv.update(edge['relations'])
            edge_csv.update(edge['owner'])
            src_info = nodes_map[edge['src']]
            for owner, weight in src_info['weight'].items():
                edge_csv.update({f"src_{owner}": weight})
            dest_info = nodes_map[edge['dest']]
            for owner, weight in dest_info['weight'].items():
                edge_csv.update({f"dest_{owner}": weight})
            res_csv.append(edge_csv)
        FileCSV.write_dict_to_csv('D:/Honor/merge/facade', out_name, res_csv, 'w')
        filter_nodes = []
        filter_edges = edges[0: 10]
        temp_node = set()
        for edge in filter_edges:
            temp_node.add(edge['src'])
            temp_node.add(edge['dest'])
        for node in temp_node:
            filter_nodes.append(nodes_map[node])

    def filter_hidden_in_facade(self):
        res = defaultdict(partial(defaultdict, int))
        intrusive_res = {}
        hidden_json = defaultdict(list)
        rel_json = defaultdict(list)
        facade_info = FileJson.read_base_json(self.file_name)
        n2e: List[dict] = facade_info['res']['n2e']
        e2n: List[dict] = facade_info['res']['e2n']
        heads_hd_rel = []
        heads_hd_intrusive = []
        hidden_level = [Constant.HD_blacklist, Constant.HD_greylist,
                        Constant.HD_whitelist] + Constant.HD_greylist_max_list
        for label in hidden_level:
            for rel in Constant.Relations:
                heads_hd_rel.append(f'{label}_{rel}')
        for label in hidden_level:
            heads_hd_intrusive.append(f'{label}_1')
            intrusive_res.update({f'{label}_1': 0, f'{label}_0': 0})
            heads_hd_intrusive.append(f'{label}_0')

        for rel in e2n:
            src_e = rel['src']
            dest_e = rel['dest']
            rel_type: str = ''
            for k in rel['values'].keys():
                rel_type = str(k)
                break
            try:
                if rel_type == Constant.R_annotate:
                    hidden_flag = Constant.hidden_map(src_e['hidden'].split(" "))
                    is_intrusive = src_e['isIntrusive']
                    qualifiedName = src_e['qualifiedName']
                else:
                    hidden_flag = Constant.hidden_map(dest_e['hidden'].split(" "))
                    is_intrusive = dest_e['isIntrusive']
                    qualifiedName = dest_e['qualifiedName']
                if src_e['not_aosp'] != dest_e['not_aosp'] and \
                        hidden_flag in hidden_level:
                    res[qualifiedName][hidden_flag + '_' + rel_type] += 1
                    if rel_type == Constant.call:
                        intrusive_res[f'{hidden_flag}_{is_intrusive}'] += 1
                    hidden_json[hidden_flag + '_' + rel_type + '_e2n'].append(rel)
            except KeyError:
                pass
        for rel in n2e:
            src_e = rel['src']
            dest_e = rel['dest']
            rel_type: str = ''
            for k in rel['values'].keys():
                rel_type = str(k)
                break
            try:
                if rel_type == Constant.R_annotate:
                    hidden_flag = Constant.hidden_map(dest_e['hidden'])
                else:
                    hidden_flag = Constant.hidden_map(src_e['hidden'])
                if src_e['not_aosp'] != dest_e['not_aosp'] and \
                        hidden_flag in [Constant.HD_blacklist,
                                        Constant.HD_greylist, Constant.HD_whitelist] + Constant.HD_greylist_max_list:
                    # res[src_e['qualifiedName']][hidden_flag + '_' + rel_type + '_n2e'] += 1
                    hidden_json[hidden_flag + '_' + rel_type + '_n2e'].append(rel)
            except KeyError:
                pass
        FileCSV.write_file_to_csv(self.file_path, 'facade_hidden_filter', res, 'name', heads_hd_rel)
        FileCSV.write_dict_to_csv(self.file_path, 'facade_hidden_intrusive_count', [intrusive_res], 'w')
        FileJson.write_data_to_json(self.file_path, hidden_json, 'facade_hidden_hidden.json')
        # FileJson.write_data_to_json(self.file_path, rel_json, 'facade_hidden_rel.json')

if __name__ == '__main__':
    FacadeFilter("D:\\Honor\\match_res\\LineageOS\\base\\lineage-18.1", "facade.json", []).filter_hidden_in_facade()