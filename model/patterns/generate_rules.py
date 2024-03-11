from constant.constant import Constant


class RuleGen:
    direction = {
        'native': '0',
        'extensive': '1'
    }

    direction_score = {
        '00': 20,
        '11': 10,
        '01': 1,
        '10': 5
    }

    def get_direction(self, ownership):
        return self.direction[ownership]

    def graph_to_rules(self, nodes, edges):
        rules = []
        entity_index = {}
        for edg_index, edg in enumerate(edges):
            src_index = -1
            dest_index = -1
            try:
                src_index = entity_index[edg['src']]
            except KeyError:
                pass
            try:
                dest_index = entity_index[edg['dest']]
            except KeyError:
                pass
            rule = {'src': {'id': [src_index], 'category': nodes[edg['src']]['category'], 'attr': {}},
                    'rel': {'type': edg['rel']},
                    'dest': {'id': [dest_index], 'category': nodes[edg['src']]['category'], 'attr': {}},
                    'direction': self.get_direction(nodes[edg['src']]['ownership']) + self.get_direction(
                        nodes[edg['dest']]['ownership'])
                    }
            entity_index[edg['src']] = [edg_index, 0]
            entity_index[edg['dest']] = [edg_index, 1]
            rules.append(rule)
        return rules

    def heuristic_sort(self, nodes, edges, nodes_flag: set, res: list):
        if not edges:
            return res

        for edg in edges:
            rel_type = Constant.relation_count_score[edg['rel']]
            rel_dir = self.direction_score[self.get_direction(nodes[edg['src']]['ownership']) + self.get_direction(
                nodes[edg['dest']]['ownership'])]
            linjie = 1 if edg['src'] in nodes_flag or edg['src'] in nodes_flag else 10 * 1000
            edg['weight'] = rel_type * rel_dir * linjie
        sorted_edge = sorted(edges, key=lambda k: k.get('weight', 0))
        res.append(sorted_edge[0])
        nodes_flag.add(sorted_edge[0]['src'])
        nodes_flag.add(sorted_edge[0]['dest'])
        return self.heuristic_sort(nodes, sorted_edge[1: len(sorted_edge)], nodes_flag, res)

    def run(self, nodes, edges):
        return self.graph_to_rules(nodes, self.heuristic_sort(nodes, edges, set(), []))


if __name__ == '__main__':
    exa_nodes = [
        {
            "id": 0,
            "category": "Class",
            "ownership": 'extensive'
        },
        {
            "id": 1,
            "category": "Method",
            "ownership": 'extensive'
        },
        {
            "id": 2,
            "category": "Class",
            "ownership": 'native'
        },
        {
            "id": 3,
            "category": "Method",
            "ownership": 'native'
        }
    ]
    exa_edges = [
        {
            'src': 0,
            'rel': 'Define',
            'dest': 1
        },
        {
            'src': 0,
            'rel': 'Inherit',
            'dest': 2
        },
        {
            'src': 2,
            'rel': 'Define',
            'dest': 3
        },
        {
            'src': 1,
            'rel': 'Override',
            'dest': 3
        }
    ]
    print(RuleGen().run(exa_nodes, exa_edges))
