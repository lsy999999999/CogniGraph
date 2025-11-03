# CogniGraph - 智能知识图谱可视化系统

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Flask-3.0-green.svg" alt="Flask">
  <img src="https://img.shields.io/badge/License-Apache%202.0-orange.svg" alt="License">
</p>

## 📖 项目简介

CogniGraph 是一个基于词向量语义空间的智能知识图谱构建与可视化系统。它能够自动从文本中提取实体和关系，利用深度学习模型构建语义空间，并通过多种交互式可视化方式展现知识结构。

### ✨ 核心特性

- 🤖 **AI驱动的图谱构建**：使用 DeepSeek API 自动提取实体和关系
- 🎨 **多样化可视化**：支持2D/3D交互式图谱、热力图、词云等多种展现形式
- 🧮 **智能语义布局**：基于词向量的语义相似度进行节点布局
- 📊 **深度图谱分析**：提供中心性分析、社区检测、连通性分析等功能
- 🌐 **现代Web界面**：直观的操作流程，实时可视化展示
- 🔄 **多种布局算法**：支持语义布局、力导向、环形、Kamada-Kawai等

## 🚀 快速开始

### 环境要求

- Python 3.8 或更高版本
- pip 包管理器
- DeepSeek API Key（用于图谱构建）

### 安装步骤

#### 1. 克隆项目

```bash
git clone https://github.com/lsy999999999/CogniGraph.git
cd CogniGraph
```

#### 2. 创建虚拟环境

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Mac/Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
```

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

或使用国内镜像加速：
```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

#### 4. 配置API密钥

1. 复制示例配置文件：
```bash
cp sample.env .env
```

2. 编辑 `.env` 文件，填入你的 DeepSeek API Key：
```
DEEPSEEK_API_KEY=your_api_key_here
```

> 💡 如何获取 DeepSeek API Key？访问 [DeepSeek 官网](https://platform.deepseek.com/) 注册并获取。

#### 5. 下载词向量模型

如果 `model` 文件夹不存在，运行：
```bash
python download_model.py
```

这将下载预训练的中文词向量模型（约 400MB）。

### 🎯 使用方法

#### 启动Web服务

```bash
python app.py
```

服务启动后，在浏览器中访问：
```
http://localhost:5000
```

#### 使用流程

**步骤1：上传文本文件**
- 点击"选择文件"上传 .txt 格式的文本
- 建议文本长度在 500-5000 字之间
- 点击"上传"按钮

**步骤2：构建知识图谱**
- 上传成功后，点击"开始构建"
- AI 将自动分析文本，提取实体和关系
- 这个过程通常需要 1-2 分钟

**步骤3：选择可视化方式**
- 选择可视化类型：
  - **交互式2D图谱**：可缩放、拖拽的平面图谱
  - **交互式3D图谱**：可旋转的三维空间图谱
  - **语义相似度热力图**：展示实体间语义相似度
  - **实体词云**：按重要性展示实体
- 选择布局算法（2D/3D图谱）
- 点击"生成可视化"

**步骤4：图谱分析**
- 点击"分析图谱"获取深度分析
- 查看中心性分析、社区结构等信息

## 📁 项目结构

```
CogniGraph/
├── app.py                      # Flask 主应用
├── knowledge_graph.py          # 知识图谱构建模块
├── visualizations.py           # 可视化生成模块
├── graph_analytics.py          # 图谱分析模块
├── download_model.py           # 模型下载脚本
├── main.py                     # 旧版命令行脚本（已弃用）
│
├── templates/                  # HTML 模板
│   └── index.html             # 主界面
│
├── static/                     # 静态资源
│   ├── css/
│   │   └── style.css          # 样式文件
│   └── js/
│       └── app.js             # 前端交互逻辑
│
├── model/                      # 词向量模型（自动下载）
├── uploads/                    # 用户上传的文件
├── outputs/                    # 生成的可视化文件
│
├── requirements.txt            # Python 依赖
├── .env                        # 环境变量配置（需创建）
└── README.md                   # 本文档
```

## 🔧 核心功能详解

### 1. 知识图谱构建 (`knowledge_graph.py`)

**功能说明：**
- 调用 DeepSeek API 分析文本
- 自动提取实体（人物、组织、地点、概念、事件）
- 识别实体间的关系和强度
- 生成结构化的图谱数据

**输出格式：**
```json
{
  "title": "图谱标题",
  "theme": "主题",
  "abstract": "摘要",
  "nodes": [...],  // 实体列表
  "edges": [...]   // 关系列表
}
```

### 2. 可视化生成 (`visualizations.py`)

**2D交互式图谱**
- 使用 Plotly 创建可交互的图谱
- 支持鼠标悬停查看节点详情
- 支持缩放和平移操作
- 节点大小表示连接数，颜色表示类型

**3D交互式图谱**
- 三维空间展示实体关系
- 可通过鼠标旋转、缩放查看
- 基于PCA降维到3D空间

**语义相似度热力图**
- 计算所有实体间的余弦相似度
- 使用颜色深浅表示相似程度
- 帮助发现语义相关的实体

**实体词云**
- 根据实体的连接数生成词云
- 字体大小表示重要性
- 快速识别核心实体

### 3. 图谱分析 (`graph_analytics.py`)

**基本统计**
- 节点数、边数、图密度
- 平均度数、连通性分析
- 图直径、平均最短路径

**中心性分析**
- **度中心性**：连接最多的实体
- **介数中心性**：最具桥梁作用的实体
- **接近中心性**：最容易到达其他实体的节点
- **PageRank**：综合重要性评分

**社区检测**
- 使用 Louvain 算法识别社区结构
- 发现密切相关的实体群组

**类型分布**
- 统计各类型实体的数量和占比
- 分析关系类型分布

## 🎨 可视化示例

### 交互式2D图谱
![2D示例](graph-2d.jpg)

### 交互式3D图谱
![3D示例](graph-3d.jpg)

## 🔍 使用场景

### 学术研究
- 文献综述可视化
- 研究主题关联分析
- 学术谱系构建

### 教育学习
- 课程知识点整理
- 概念关系理解
- 学习笔记可视化

### 内容分析
- 新闻事件脉络梳理
- 小说人物关系图
- 历史事件关联分析

### 商业应用
- 市场竞争分析
- 产品关联研究
- 客户关系管理

## 🦁 配置说明

### 环境变量 (`.env`)

```bash
# DeepSeek API配置
DEEPSEEK_API_KEY=your_api_key_here

# Flask配置（可选）
FLASK_ENV=development
FLASK_DEBUG=True
```

### 高级配置

在 `app.py` 中可以修改：
- `MAX_CONTENT_LENGTH`：最大文件大小（默认16MB）
- 服务器端口（默认5000）

## 🐛 常见问题

### Q1: 上传文件后提示"构建失败"？
**A**: 检查以下几点：
1. 确认 `.env` 文件中的 API Key 正确
2. 检查网络连接，确保能访问 DeepSeek API
3. 文本内容不应过短（建议至少300字）

### Q2: 可视化生成很慢？
**A**:
- 首次使用时会加载词向量模型，需要一些时间
- 实体数量过多（>100）时生成会较慢
- 建议控制文本长度在5000字以内

### Q3: 中文显示为方框？
**A**:
- 系统会自动检测中文字体
- Windows 用户通常不会遇到此问题
- Linux用户需安装中文字体：`sudo apt-get install fonts-wqy-microhei`

### Q4: 模型下载失败？
**A**:
- 检查网络连接
- 尝试使用镜像源
- 或手动下载模型到 `model/` 文件夹

## 🔄 版本更新

### v2.0.0 (当前版本)
- ✨ 全新的 Web 界面
- ✨ 交互式可视化（2D/3D）
- ✨ 多种布局算法支持
- ✨ 图谱深度分析功能
- ✨ 热力图和词云可视化
- 🔧 代码重构，模块化设计

### v1.0.0 (旧版本)
- 基本的命令行工具
- 静态图片生成
- 简单的2D/3D布局

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 开源协议

本项目采用 Apache 2.0 开源协议。详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [DeepSeek](https://www.deepseek.com/) - 提供强大的语言模型API
- [Sentence Transformers](https://www.sbert.net/) - 词向量模型
- [NetworkX](https://networkx.org/) - 图算法库
- [Plotly](https://plotly.com/) - 交互式可视化
- [Flask](https://flask.palletsprojects.com/) - Web框架

## 📧 联系方式

如有问题或建议，欢迎：
- 提交 [Issue](https://github.com/lsy999999999/CogniGraph/issues)

---

<p align="center">
  Made with ❤️ for Knowledge Visualization
</p>
