from litellm import completion
import json
from dotenv import load_dotenv
import os

load_dotenv()

class KnowledgeGraphBuilder:
    """知识图谱构建器"""

    def __init__(self):
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        if not self.api_key:
            raise ValueError("请配置 DEEPSEEK_API_KEY 环境变量")

    def build(self, text):
        """
        从文本构建知识图谱

        Args:
            text: 输入文本

        Returns:
            dict: 知识图谱数据
        """
        system_prompt = """
        作为知识图谱构建专家，请从文本中提取实体及其关系，并输出以下结构的JSON：
        {
            "theme": 文本的主题,
            "title": 知识图谱的标题,
            "abstract": 文本摘要,
            "aspects": [文本的各个角度，可以从结构或内容分析],
            "reader": 对文本读者的分析,
            "purpose": 这张图对读者的帮助,
            "purposes": [各种具体的帮助],
            "nodes": [{"id": 唯一ID, "name": 实体名称, "type": 实体类型, "description": 实体描述}],
            "edges": [{"source": 起点ID, "target": 终点ID, "relation": 关系描述, "weight": 关系强度(1-10)}]
        }
        要求：
        1. 实体类型简短如[人物/组织/地点/概念/事件]
        2. 关系描述用动宾结构
        3. 确保图结构的连通性
        4. 提取足够多的实体(至少10个)和关系
        5. 为每个关系标注强度weight(1-10)
        6. 为每个实体添加简短描述
        """

        try:
            response = completion(
                model="deepseek/deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                response_format={"type": "json_object", "json_schema": {
                    "name": "knowledge_graph",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "theme": {"type": "string"},
                            "title": {"type": "string"},
                            "abstract": {"type": "string"},
                            "aspects": {"type": "array", "items": {"type": "string"}},
                            "reader": {"type": "string"},
                            "purpose": {"type": "string"},
                            "purposes": {"type": "array", "items": {"type": "string"}},
                            "nodes": {"type": "array", "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "integer"},
                                    "name": {"type": "string"},
                                    "type": {"type": "string"},
                                    "description": {"type": "string"}
                                },
                                "required": ["id", "name", "type"]
                            }},
                            "edges": {"type": "array", "items": {
                                "type": "object",
                                "properties": {
                                    "source": {"type": "integer"},
                                    "target": {"type": "integer"},
                                    "relation": {"type": "string"},
                                    "weight": {"type": "number"}
                                },
                                "required": ["source", "target", "relation"]
                            }}
                        },
                        "required": ["theme", "title", "nodes", "edges"]
                    }
                }}
            )

            result = response.choices[0].message.content
            graph_data = json.loads(result)

            # 数据验证和清理
            graph_data = self._validate_and_clean(graph_data)

            return graph_data

        except Exception as e:
            print(f"Error building knowledge graph: {str(e)}")
            return None

    def _validate_and_clean(self, graph_data):
        """验证和清理图谱数据"""
        # 确保所有必需字段存在
        required_fields = ['theme', 'title', 'nodes', 'edges']
        for field in required_fields:
            if field not in graph_data:
                graph_data[field] = [] if field in ['nodes', 'edges'] else "未知"

        # 确保节点ID唯一
        node_ids = set()
        cleaned_nodes = []
        for node in graph_data.get('nodes', []):
            if node['id'] not in node_ids:
                node_ids.add(node['id'])
                # 确保节点有description
                if 'description' not in node:
                    node['description'] = ''
                cleaned_nodes.append(node)
        graph_data['nodes'] = cleaned_nodes

        # 清理边，确保source和target都存在
        cleaned_edges = []
        for edge in graph_data.get('edges', []):
            if edge['source'] in node_ids and edge['target'] in node_ids:
                # 确保有weight
                if 'weight' not in edge:
                    edge['weight'] = 5
                cleaned_edges.append(edge)
        graph_data['edges'] = cleaned_edges

        # 设置默认值
        if 'abstract' not in graph_data:
            graph_data['abstract'] = ''
        if 'aspects' not in graph_data:
            graph_data['aspects'] = []
        if 'reader' not in graph_data:
            graph_data['reader'] = ''
        if 'purpose' not in graph_data:
            graph_data['purpose'] = ''
        if 'purposes' not in graph_data:
            graph_data['purposes'] = []

        return graph_data
