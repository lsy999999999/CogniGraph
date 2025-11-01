import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
from pyvis.network import Network
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
from wordcloud import WordCloud
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import numpy as np
import os
import warnings

class GraphVisualizer:
    """图谱可视化器"""

    def __init__(self, output_dir='outputs'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.setup_matplotlib_font()
        # 延迟加载模型
        self._model = None

    @property
    def model(self):
        """延迟加载词向量模型"""
        if self._model is None:
            self._model = SentenceTransformer('./model')
        return self._model

    def setup_matplotlib_font(self):
        """设置matplotlib中文字体"""
        chinese_fonts = [
            'SimHei', 'Microsoft YaHei', 'PingFang SC', 'Hiragino Sans GB',
            'WenQuanYi Micro Hei', 'Source Han Sans CN', 'Noto Sans CJK SC'
        ]
        fonts = [f.name for f in fm.fontManager.ttflist]

        for font in chinese_fonts:
            if font in fonts:
                plt.rcParams['font.family'] = font
                plt.rcParams['axes.unicode_minus'] = False
                return

        warnings.warn("未找到中文字体，可能无法正确显示中文")

    def _build_networkx_graph(self, graph_data):
        """构建NetworkX图"""
        G = nx.DiGraph()

        # 添加节点
        for node in graph_data['nodes']:
            G.add_node(
                node['id'],
                name=node['name'],
                type=node['type'],
                description=node.get('description', '')
            )

        # 添加边
        for edge in graph_data['edges']:
            G.add_edge(
                edge['source'],
                edge['target'],
                relation=edge['relation'],
                weight=edge.get('weight', 5)
            )

        return G

    def _get_node_colors(self, G):
        """获取节点颜色"""
        color_map = {
            '人物': '#3498db',      # 蓝色
            '组织': '#2ecc71',      # 绿色
            '地点': '#e74c3c',      # 红色
            '概念': '#95a5a6',      # 灰色
            '事件': '#f39c12',      # 橙色
        }

        colors = []
        for node in G.nodes():
            node_type = G.nodes[node]['type']
            colors.append(color_map.get(node_type, '#95a5a6'))

        return colors

    def _get_semantic_layout(self, G, dimensions=2):
        """使用词向量生成语义布局"""
        node_names = [G.nodes[node]['name'] for node in G.nodes()]
        embeddings = self.model.encode(node_names)

        if dimensions == 2:
            pca = PCA(n_components=2)
            positions = pca.fit_transform(embeddings)
        elif dimensions == 3:
            pca = PCA(n_components=3)
            positions = pca.fit_transform(embeddings)
        else:
            raise ValueError("dimensions must be 2 or 3")

        return {node: positions[i] for i, node in enumerate(G.nodes())}

    def _get_layout(self, G, layout_type='semantic'):
        """获取图布局"""
        if layout_type == 'semantic':
            return self._get_semantic_layout(G, dimensions=2)
        elif layout_type == 'spring':
            return nx.spring_layout(G, k=1, iterations=50)
        elif layout_type == 'circular':
            return nx.circular_layout(G)
        elif layout_type == 'kamada_kawai':
            return nx.kamada_kawai_layout(G)
        elif layout_type == 'spectral':
            return nx.spectral_layout(G)
        else:
            return nx.spring_layout(G)

    def create_interactive_2d(self, graph_data, layout='semantic'):
        """创建交互式2D可视化（使用Plotly）"""
        G = self._build_networkx_graph(graph_data)
        pos = self._get_layout(G, layout)

        # 准备边数据
        edge_trace = []
        for edge in G.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]

            edge_trace.append(go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(width=0.5, color='#888'),
                hoverinfo='text',
                text=edge[2].get('relation', ''),
                showlegend=False
            ))

        # 准备节点数据
        node_x = []
        node_y = []
        node_text = []
        node_color = []
        node_size = []

        color_map = {
            '人物': '#3498db',
            '组织': '#2ecc71',
            '地点': '#e74c3c',
            '概念': '#95a5a6',
            '事件': '#f39c12',
        }

        for node in G.nodes(data=True):
            x, y = pos[node[0]]
            node_x.append(x)
            node_y.append(y)

            # 节点信息
            text = f"<b>{node[1]['name']}</b><br>"
            text += f"类型: {node[1]['type']}<br>"
            if node[1].get('description'):
                text += f"描述: {node[1]['description']}<br>"
            text += f"连接数: {G.degree(node[0])}"
            node_text.append(text)

            node_color.append(color_map.get(node[1]['type'], '#95a5a6'))
            node_size.append(20 + G.degree(node[0]) * 5)

        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            text=[G.nodes[n]['name'] for n in G.nodes()],
            textposition='top center',
            textfont=dict(size=10),
            hovertext=node_text,
            hoverinfo='text',
            marker=dict(
                size=node_size,
                color=node_color,
                line=dict(width=2, color='white')
            )
        )

        # 创建图表
        fig = go.Figure(data=edge_trace + [node_trace],
                        layout=go.Layout(
                            title=dict(
                                text=graph_data.get('title', '知识图谱'),
                                x=0.5,
                                xanchor='center'
                            ),
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=20, l=5, r=5, t=40),
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            plot_bgcolor='white',
                            height=800
                        ))

        # 保存文件
        output_file = os.path.join(self.output_dir, 'interactive_2d.html')
        fig.write_html(output_file)
        return output_file

    def create_interactive_3d(self, graph_data, layout='semantic'):
        """创建交互式3D可视化"""
        G = self._build_networkx_graph(graph_data)
        pos_3d = self._get_semantic_layout(G, dimensions=3)

        # 准备边数据
        edge_x = []
        edge_y = []
        edge_z = []

        for edge in G.edges():
            x0, y0, z0 = pos_3d[edge[0]]
            x1, y1, z1 = pos_3d[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_z.extend([z0, z1, None])

        edge_trace = go.Scatter3d(
            x=edge_x, y=edge_y, z=edge_z,
            mode='lines',
            line=dict(color='#888', width=2),
            hoverinfo='none',
            showlegend=False
        )

        # 准备节点数据
        node_x = []
        node_y = []
        node_z = []
        node_text = []
        node_color = []

        color_map = {
            '人物': '#3498db',
            '组织': '#2ecc71',
            '地点': '#e74c3c',
            '概念': '#95a5a6',
            '事件': '#f39c12',
        }

        for node in G.nodes(data=True):
            x, y, z = pos_3d[node[0]]
            node_x.append(x)
            node_y.append(y)
            node_z.append(z)
            node_text.append(f"{node[1]['name']}<br>类型: {node[1]['type']}")
            node_color.append(color_map.get(node[1]['type'], '#95a5a6'))

        node_trace = go.Scatter3d(
            x=node_x, y=node_y, z=node_z,
            mode='markers+text',
            text=[G.nodes[n]['name'] for n in G.nodes()],
            textposition='top center',
            hovertext=node_text,
            hoverinfo='text',
            marker=dict(
                size=10,
                color=node_color,
                line=dict(width=2, color='white')
            )
        )

        # 创建图表
        fig = go.Figure(data=[edge_trace, node_trace],
                        layout=go.Layout(
                            title=graph_data.get('title', '3D知识图谱'),
                            showlegend=False,
                            hovermode='closest',
                            scene=dict(
                                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                zaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            ),
                            height=800
                        ))

        output_file = os.path.join(self.output_dir, 'interactive_3d.html')
        fig.write_html(output_file)
        return output_file

    def create_similarity_heatmap(self, graph_data):
        """创建实体语义相似度热力图"""
        G = self._build_networkx_graph(graph_data)
        node_names = [G.nodes[node]['name'] for node in G.nodes()]

        # 计算词向量
        embeddings = self.model.encode(node_names)

        # 计算相似度矩阵
        from sklearn.metrics.pairwise import cosine_similarity
        similarity_matrix = cosine_similarity(embeddings)

        # 创建热力图
        plt.figure(figsize=(12, 10))
        sns.heatmap(
            similarity_matrix,
            xticklabels=node_names,
            yticklabels=node_names,
            cmap='YlOrRd',
            annot=False,
            fmt='.2f',
            square=True,
            cbar_kws={'label': '相似度'}
        )
        plt.title('实体语义相似度热力图', fontsize=16, pad=20)
        plt.xlabel('实体', fontsize=12)
        plt.ylabel('实体', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()

        output_file = os.path.join(self.output_dir, 'similarity_heatmap.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        return output_file

    def create_entity_wordcloud(self, graph_data):
        """创建实体词云"""
        G = self._build_networkx_graph(graph_data)

        # 根据节点度数生成词频
        word_freq = {}
        for node in G.nodes(data=True):
            word_freq[node[1]['name']] = G.degree(node[0]) + 1

        # 生成词云
        wordcloud = WordCloud(
            font_path=self._get_chinese_font_path(),
            width=1200,
            height=800,
            background_color='white',
            colormap='viridis',
            relative_scaling=0.5,
            min_font_size=10
        ).generate_from_frequencies(word_freq)

        # 保存图片
        plt.figure(figsize=(15, 10))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.title(f"{graph_data.get('title', '知识图谱')} - 实体词云", fontsize=16, pad=20)
        plt.axis('off')
        plt.tight_layout()

        output_file = os.path.join(self.output_dir, 'entity_wordcloud.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        return output_file

    def _get_chinese_font_path(self):
        """获取中文字体路径"""
        chinese_fonts = [
            'SimHei', 'Microsoft YaHei', 'PingFang SC', 'Hiragino Sans GB'
        ]
        for font_name in chinese_fonts:
            font_path = fm.findfont(font_name)
            if font_path and os.path.exists(font_path):
                return font_path
        return None
