# CogniGraph 快速开始指南

## 🚀 5分钟快速上手

### 步骤 1: 安装依赖

```bash
# 确保你在虚拟环境中
pip install -r requirements.txt
```

**注意事项：**
- 如果遇到依赖冲突，请使用：`pip install -r requirements.txt --upgrade`
- 建议使用 Python 3.8 或更高版本

### 步骤 2: 配置API密钥

1. 复制环境变量模板：
```bash
cp sample.env .env
```

2. 编辑 `.env` 文件，填入你的 DeepSeek API Key：
```
DEEPSEEK_API_KEY=your_actual_api_key_here
```

> 💡 **获取API Key:** 访问 https://platform.deepseek.com/ 注册并获取

### 步骤 3: 下载词向量模型

```bash
python download_model.py
```

这将下载中文词向量模型（约400MB），需要几分钟时间。

**如果下载失败：**
- 检查网络连接
- 确保有足够的磁盘空间
- 可以使用镜像源（脚本会自动尝试）

### 步骤 4: 启动应用

```bash
python app.py
```

看到以下提示表示启动成功：
```
 * Running on http://127.0.0.1:5000
```

### 步骤 5: 使用Web界面

1. 打开浏览器访问：`http://localhost:5000`

2. 上传文本文件（.txt格式）

3. 点击"开始构建"生成知识图谱

4. 选择可视化方式查看结果

## 🎯 示例文本

如果你想快速体验，可以使用项目中的 `document.txt` 文件，它包含了《红楼梦》的一段文字。

## ❗ 常见问题

### Q: ImportError: cannot import name 'cached_download'

**A:** 这是版本兼容性问题，已在最新版本中修复。请重新安装依赖：

```bash
pip uninstall sentence-transformers huggingface-hub -y
pip install sentence-transformers==2.7.0 huggingface-hub==0.23.0
```

### Q: 模型下载很慢怎么办？

**A:** 可以手动下载模型：

1. 访问 HuggingFace: https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
2. 下载所有文件到 `model/` 文件夹
3. 跳过 `download_model.py` 步骤

### Q: 构建图谱失败

**A:** 检查：
1. API Key 是否正确配置
2. 网络连接是否正常
3. 文本内容是否为UTF-8编码

## 📚 下一步

- 查看 [完整文档](README.md)
- 阅读 [使用指南](USAGE_GUIDE.md)
- 探索不同的可视化选项

## 💬 获取帮助

- [提交Issue](https://github.com/lsy999999999/CogniGraph/issues)
- 查看示例文件：`document.txt`

---

祝你使用愉快！🎉
