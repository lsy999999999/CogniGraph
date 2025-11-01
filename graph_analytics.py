import networkx as nx
from collections import Counter
import numpy as np

class GraphAnalytics:
    """图谱分析器"""

    def analyze(self, graph_data):
        """
        对知识图谱进行全面分析

        Args:
            graph_data: 图谱数据

        Returns:
            dict: 分析结果
        """
        G = self._build_networkx_graph(graph_data)

        analysis = {
            'basic_stats': self._basic_statistics(G, graph_data),
            'centrality': self._centrality_analysis(G),
            'community': self._community_detection(G),
            'connectivity': self._connectivity_analysis(G),
            'type_distribution': self._type_distribution(graph_data)
        }

        return analysis

    def _build_networkx_graph(self, graph_data):
        """构建NetworkX图"""
        G = nx.DiGraph()

        for node in graph_data['nodes']:
            G.add_node(
                node['id'],
                name=node['name'],
                type=node['type'],
                description=node.get('description', '')
            )

        for edge in graph_data['edges']:
            G.add_edge(
                edge['source'],
                edge['target'],
                relation=edge['relation'],
                weight=edge.get('weight', 5)
            )

        return G

    def _basic_statistics(self, G, graph_data):
        """基本统计信息"""
        # 转换为无向图以计算某些指标
        G_undirected = G.to_undirected()

        stats = {
            'node_count': G.number_of_nodes(),
            'edge_count': G.number_of_edges(),
            'density': nx.density(G),
            'average_degree': sum(dict(G.degree()).values()) / G.number_of_nodes() if G.number_of_nodes() > 0 else 0,
            'is_connected': nx.is_weakly_connected(G),
            'num_components': nx.number_weakly_connected_components(G),
        }

        # 计算直径（仅对连通图）
        if stats['is_connected']:
            try:
                stats['diameter'] = nx.diameter(G_undirected)
                stats['average_shortest_path'] = nx.average_shortest_path_length(G_undirected)
            except:
                stats['diameter'] = None
                stats['average_shortest_path'] = None
        else:
            stats['diameter'] = None
            stats['average_shortest_path'] = None

        return stats

    def _centrality_analysis(self, G):
        """中心性分析"""
        # 度中心性
        degree_centrality = nx.degree_centrality(G)
        # 介数中心性
        betweenness_centrality = nx.betweenness_centrality(G)
        # 接近中心性
        try:
            closeness_centrality = nx.closeness_centrality(G)
        except:
            closeness_centrality = {node: 0 for node in G.nodes()}

        # PageRank
        pagerank = nx.pagerank(G)

        # 获取TOP节点
        def get_top_nodes(centrality_dict, top_n=5):
            sorted_nodes = sorted(centrality_dict.items(), key=lambda x: x[1], reverse=True)
            return [
                {
                    'id': node_id,
                    'name': G.nodes[node_id]['name'],
                    'score': round(score, 4)
                }
                for node_id, score in sorted_nodes[:top_n]
            ]

        return {
            'degree_centrality': {
                'top_nodes': get_top_nodes(degree_centrality),
                'description': '度中心性：衡量节点的直接连接数量'
            },
            'betweenness_centrality': {
                'top_nodes': get_top_nodes(betweenness_centrality),
                'description': '介数中心性：衡量节点在网络中的桥梁作用'
            },
            'closeness_centrality': {
                'top_nodes': get_top_nodes(closeness_centrality),
                'description': '接近中心性：衡量节点到其他节点的平均距离'
            },
            'pagerank': {
                'top_nodes': get_top_nodes(pagerank),
                'description': 'PageRank：衡量节点的重要性和影响力'
            }
        }

    def _community_detection(self, G):
        """社区检测"""
        # 转换为无向图
        G_undirected = G.to_undirected()

        try:
            # 使用Louvain算法检测社区
            from networkx.algorithms import community
            communities = community.greedy_modularity_communities(G_undirected)

            community_list = []
            for i, comm in enumerate(communities):
                nodes = [
                    {
                        'id': node_id,
                        'name': G.nodes[node_id]['name'],
                        'type': G.nodes[node_id]['type']
                    }
                    for node_id in comm
                ]
                community_list.append({
                    'community_id': i + 1,
                    'size': len(comm),
                    'nodes': nodes
                })

            return {
                'num_communities': len(communities),
                'communities': community_list,
                'description': '使用Louvain算法检测到的社区结构'
            }
        except Exception as e:
            return {
                'num_communities': 0,
                'communities': [],
                'description': f'社区检测失败: {str(e)}'
            }

    def _connectivity_analysis(self, G):
        """连通性分析"""
        components = list(nx.weakly_connected_components(G))

        component_list = []
        for i, comp in enumerate(components):
            nodes = [
                {
                    'id': node_id,
                    'name': G.nodes[node_id]['name']
                }
                for node_id in comp
            ]
            component_list.append({
                'component_id': i + 1,
                'size': len(comp),
                'nodes': nodes
            })

        return {
            'num_components': len(components),
            'components': component_list,
            'largest_component_size': max([len(c) for c in components]) if components else 0
        }

    def _type_distribution(self, graph_data):
        """实体类型分布"""
        node_types = [node['type'] for node in graph_data['nodes']]
        type_counts = Counter(node_types)

        # 关系类型分布
        relation_types = [edge['relation'] for edge in graph_data['edges']]
        relation_counts = Counter(relation_types)

        return {
            'node_types': [
                {'type': t, 'count': c, 'percentage': round(c / len(node_types) * 100, 2)}
                for t, c in type_counts.most_common()
            ],
            'relation_types': [
                {'relation': r, 'count': c}
                for r, c in relation_counts.most_common(10)  # 只显示前10个
            ],
            'total_node_types': len(type_counts),
            'total_relation_types': len(relation_counts)
        }
