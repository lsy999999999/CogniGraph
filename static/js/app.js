// 全局状态
let state = {
    filename: null,
    graphData: null,
    analyticsData: null
};

// DOM元素
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const buildBtn = document.getElementById('buildBtn');
const visualizeBtn = document.getElementById('visualizeBtn');
const analyzeBtn = document.getElementById('analyzeBtn');
const vizType = document.getElementById('vizType');
const layoutType = document.getElementById('layoutType');
const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    updateVizTypeOptions();
});

function setupEventListeners() {
    // 文件选择
    fileInput.addEventListener('change', () => {
        uploadBtn.disabled = !fileInput.files.length;
    });

    // 上传文件
    uploadBtn.addEventListener('click', uploadFile);

    // 构建图谱
    buildBtn.addEventListener('click', buildGraph);

    // 生成可视化
    visualizeBtn.addEventListener('click', visualize);

    // 分析图谱
    analyzeBtn.addEventListener('click', analyzeGraph);

    // 可视化类型改变
    vizType.addEventListener('change', updateVizTypeOptions);
}

function updateVizTypeOptions() {
    const layoutOptions = document.getElementById('layoutOptions');
    const selectedType = vizType.value;

    // 只有2D和3D图谱需要布局选项
    if (selectedType === 'interactive_2d' || selectedType === 'interactive_3d') {
        layoutOptions.style.display = 'block';
    } else {
        layoutOptions.style.display = 'none';
    }
}

async function uploadFile() {
    const file = fileInput.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    showLoading('正在上传文件...');

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            state.filename = data.filename;
            showStatus('uploadStatus', `上传成功！文件大小: ${data.text_length} 字符`, 'success');
            buildBtn.disabled = false;
        } else {
            showStatus('uploadStatus', `上传失败: ${data.error}`, 'error');
        }
    } catch (error) {
        showStatus('uploadStatus', `上传失败: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

async function buildGraph() {
    if (!state.filename) return;

    showLoading('正在构建知识图谱，请稍候...<br>这可能需要1-2分钟');

    try {
        const response = await fetch('/api/build_graph', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ filename: state.filename })
        });

        const data = await response.json();

        if (data.success) {
            state.graphData = data.graph_data;
            showStatus('buildStatus', '图谱构建成功！', 'success');
            vizType.disabled = false;
            visualizeBtn.disabled = false;
            analyzeBtn.disabled = false;

            // 显示图谱基本信息
            displayGraphInfo(state.graphData);
        } else {
            showStatus('buildStatus', `构建失败: ${data.error}`, 'error');
        }
    } catch (error) {
        showStatus('buildStatus', `构建失败: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

async function visualize() {
    if (!state.graphData) return;

    const type = vizType.value;
    const layout = layoutType.value;

    showLoading('正在生成可视化...');

    try {
        const response = await fetch('/api/visualize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                graph_data: state.graphData,
                type: type,
                layout: layout
            })
        });

        const data = await response.json();

        if (data.success) {
            showStatus('vizStatus', '可视化生成成功！', 'success');
            displayVisualization(data.path, data.type);
        } else {
            showStatus('vizStatus', `生成失败: ${data.error}`, 'error');
        }
    } catch (error) {
        showStatus('vizStatus', `生成失败: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

async function analyzeGraph() {
    if (!state.graphData) return;

    showLoading('正在分析图谱...');

    try {
        const response = await fetch('/api/analytics', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ graph_data: state.graphData })
        });

        const data = await response.json();

        if (data.success) {
            state.analyticsData = data.analytics;
            displayAnalytics(state.analyticsData);
            // 切换到分析结果标签
            document.getElementById('analytics-tab').click();
        } else {
            alert(`分析失败: ${data.error}`);
        }
    } catch (error) {
        alert(`分析失败: ${error.message}`);
    } finally {
        hideLoading();
    }
}

function displayVisualization(path, type) {
    const container = document.getElementById('visualizationContainer');

    if (type === 'html') {
        container.innerHTML = `<iframe src="/${path}"></iframe>`;
    } else if (type === 'image') {
        container.innerHTML = `<img src="/${path}" alt="Visualization">`;
    }
}

function displayGraphInfo(graphData) {
    const container = document.getElementById('infoContainer');

    let html = `
        <div class="info-section">
            <h5><i class="bi bi-info-circle"></i> 基本信息</h5>
            <p><strong>标题:</strong> ${graphData.title || '未知'}</p>
            <p><strong>主题:</strong> ${graphData.theme || '未知'}</p>
            <p><strong>摘要:</strong> ${graphData.abstract || '无'}</p>
        </div>
    `;

    if (graphData.aspects && graphData.aspects.length > 0) {
        html += `
            <div class="info-section">
                <h5><i class="bi bi-layers"></i> 分析角度</h5>
                ${graphData.aspects.map(aspect => `<span class="info-badge">${aspect}</span>`).join('')}
            </div>
        `;
    }

    html += `
        <div class="info-section">
            <h5><i class="bi bi-bar-chart"></i> 统计信息</h5>
            <div class="row">
                <div class="col-md-6">
                    <div class="metric-card">
                        <div class="metric-value">${graphData.nodes.length}</div>
                        <div class="metric-label">实体数量</div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="metric-card">
                        <div class="metric-value">${graphData.edges.length}</div>
                        <div class="metric-label">关系数量</div>
                    </div>
                </div>
            </div>
        </div>
    `;

    // 实体列表
    html += `
        <div class="info-section">
            <h5><i class="bi bi-diagram-2"></i> 实体列表</h5>
            <div class="table-responsive">
                <table class="table table-sm table-hover">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>名称</th>
                            <th>类型</th>
                            <th>描述</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${graphData.nodes.map(node => `
                            <tr>
                                <td>${node.id}</td>
                                <td><strong>${node.name}</strong></td>
                                <td><span class="type-badge type-${node.type}">${node.type}</span></td>
                                <td>${node.description || '-'}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;

    // 关系列表
    html += `
        <div class="info-section">
            <h5><i class="bi bi-arrow-left-right"></i> 关系列表</h5>
            <div class="table-responsive">
                <table class="table table-sm table-hover">
                    <thead>
                        <tr>
                            <th>起点</th>
                            <th>关系</th>
                            <th>终点</th>
                            <th>强度</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${graphData.edges.map(edge => {
                            const sourceNode = graphData.nodes.find(n => n.id === edge.source);
                            const targetNode = graphData.nodes.find(n => n.id === edge.target);
                            return `
                                <tr>
                                    <td>${sourceNode ? sourceNode.name : edge.source}</td>
                                    <td><i class="bi bi-arrow-right"></i> ${edge.relation}</td>
                                    <td>${targetNode ? targetNode.name : edge.target}</td>
                                    <td>${edge.weight || 5}/10</td>
                                </tr>
                            `;
                        }).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;

    container.innerHTML = html;
}

function displayAnalytics(analytics) {
    const container = document.getElementById('analyticsContainer');

    let html = '<div class="analytics-results">';

    // 基本统计
    if (analytics.basic_stats) {
        const stats = analytics.basic_stats;
        html += `
            <div class="analytics-section">
                <h5><i class="bi bi-graph-up"></i> 图谱统计</h5>
                <div class="row">
                    <div class="col-md-3">
                        <div class="metric-card">
                            <div class="metric-value">${stats.node_count}</div>
                            <div class="metric-label">节点数</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="metric-card">
                            <div class="metric-value">${stats.edge_count}</div>
                            <div class="metric-label">边数</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="metric-card">
                            <div class="metric-value">${stats.density.toFixed(3)}</div>
                            <div class="metric-label">图密度</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="metric-card">
                            <div class="metric-value">${stats.average_degree.toFixed(2)}</div>
                            <div class="metric-label">平均度数</div>
                        </div>
                    </div>
                </div>
                <p class="mt-3">
                    <strong>连通性:</strong> ${stats.is_connected ? '图是连通的' : '图不连通'}
                    (共 ${stats.num_components} 个连通分量)
                </p>
            </div>
        `;
    }

    // 中心性分析
    if (analytics.centrality) {
        html += '<div class="analytics-section"><h5><i class="bi bi-star"></i> 中心性分析</h5>';

        for (const [key, value] of Object.entries(analytics.centrality)) {
            html += `
                <div class="mb-4">
                    <h6>${value.description}</h6>
                    <ul class="node-list">
                        ${value.top_nodes.map((node, index) => `
                            <li class="node-item">
                                <div>
                                    <span class="node-rank">${index + 1}</span>
                                    <strong>${node.name}</strong>
                                </div>
                                <span class="node-score">${node.score}</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            `;
        }

        html += '</div>';
    }

    // 类型分布
    if (analytics.type_distribution) {
        const dist = analytics.type_distribution;
        html += `
            <div class="analytics-section">
                <h5><i class="bi bi-pie-chart"></i> 类型分布</h5>
                <h6>实体类型</h6>
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>类型</th>
                                <th>数量</th>
                                <th>占比</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${dist.node_types.map(type => `
                                <tr>
                                    <td><span class="type-badge type-${type.type}">${type.type}</span></td>
                                    <td>${type.count}</td>
                                    <td>${type.percentage}%</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }

    // 社区检测
    if (analytics.community && analytics.community.num_communities > 0) {
        html += `
            <div class="analytics-section">
                <h5><i class="bi bi-collection"></i> 社区检测</h5>
                <p>${analytics.community.description}</p>
                <p>检测到 <strong>${analytics.community.num_communities}</strong> 个社区</p>
                ${analytics.community.communities.map(comm => `
                    <div class="mb-3">
                        <h6>社区 ${comm.community_id} (${comm.size} 个节点)</h6>
                        <div>
                            ${comm.nodes.map(node =>
                                `<span class="info-badge">${node.name}</span>`
                            ).join('')}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    html += '</div>';
    container.innerHTML = html;
}

function showStatus(elementId, message, type) {
    const element = document.getElementById(elementId);
    element.innerHTML = `<div class="status-message status-${type}">${message}</div>`;
}

function showLoading(text) {
    document.getElementById('loadingText').innerHTML = text;
    loadingModal.show();
}

function hideLoading() {
    loadingModal.hide();
}
