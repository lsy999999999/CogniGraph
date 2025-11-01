from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import json
from werkzeug.utils import secure_filename
from knowledge_graph import KnowledgeGraphBuilder
from visualizations import GraphVisualizer
from graph_analytics import GraphAnalytics
import traceback

app = Flask(__name__)
CORS(app)

# 配置
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 确保文件夹存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """处理文件上传"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有文件上传'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '文件名为空'}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # 读取文本内容，尝试多种编码
            text = None
            for encoding in ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']:
                try:
                    with open(filepath, 'r', encoding=encoding) as f:
                        text = f.read()
                    break
                except UnicodeDecodeError:
                    continue

            if text is None:
                return jsonify({'error': '无法读取文件，请确保文件为文本格式'}), 400

            return jsonify({
                'success': True,
                'filename': filename,
                'text_preview': text[:500] + ('...' if len(text) > 500 else ''),
                'text_length': len(text)
            })
        else:
            return jsonify({'error': '不支持的文件类型'}), 400

    except Exception as e:
        print(f"Upload error: {str(e)}")  # 添加服务器日志
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'上传失败: {str(e)}'}), 500

@app.route('/api/build_graph', methods=['POST'])
def build_graph():
    """构建知识图谱"""
    try:
        data = request.get_json()
        filename = data.get('filename')

        if not filename:
            return jsonify({'error': '缺少文件名'}), 400

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(filepath):
            return jsonify({'error': '文件不存在'}), 404

        # 读取文本
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()

        # 构建知识图谱
        builder = KnowledgeGraphBuilder()
        graph_data = builder.build(text)

        if not graph_data:
            return jsonify({'error': '图谱构建失败'}), 500

        # 保存图谱数据
        graph_file = os.path.join(app.config['OUTPUT_FOLDER'], 'graph.json')
        with open(graph_file, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, ensure_ascii=False, indent=2)

        return jsonify({
            'success': True,
            'graph_data': graph_data
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'构建图谱失败: {str(e)}'}), 500

@app.route('/api/visualize', methods=['POST'])
def visualize():
    """生成可视化"""
    try:
        data = request.get_json()
        graph_data = data.get('graph_data')
        viz_type = data.get('type', 'interactive_2d')
        layout = data.get('layout', 'semantic')

        if not graph_data:
            return jsonify({'error': '缺少图谱数据'}), 400

        visualizer = GraphVisualizer()

        if viz_type == 'interactive_2d':
            html_file = visualizer.create_interactive_2d(graph_data, layout)
            return jsonify({
                'success': True,
                'type': 'html',
                'path': html_file
            })
        elif viz_type == 'interactive_3d':
            html_file = visualizer.create_interactive_3d(graph_data, layout)
            return jsonify({
                'success': True,
                'type': 'html',
                'path': html_file
            })
        elif viz_type == 'heatmap':
            img_file = visualizer.create_similarity_heatmap(graph_data)
            return jsonify({
                'success': True,
                'type': 'image',
                'path': img_file
            })
        elif viz_type == 'wordcloud':
            img_file = visualizer.create_entity_wordcloud(graph_data)
            return jsonify({
                'success': True,
                'type': 'image',
                'path': img_file
            })
        else:
            return jsonify({'error': '不支持的可视化类型'}), 400

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'可视化失败: {str(e)}'}), 500

@app.route('/api/analytics', methods=['POST'])
def analytics():
    """图谱分析"""
    try:
        data = request.get_json()
        graph_data = data.get('graph_data')

        if not graph_data:
            return jsonify({'error': '缺少图谱数据'}), 400

        analyzer = GraphAnalytics()
        analysis_results = analyzer.analyze(graph_data)

        return jsonify({
            'success': True,
            'analytics': analysis_results
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'分析失败: {str(e)}'}), 500

@app.route('/outputs/<path:filename>')
def serve_output(filename):
    """提供输出文件"""
    return send_file(os.path.join(app.config['OUTPUT_FOLDER'], filename))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
