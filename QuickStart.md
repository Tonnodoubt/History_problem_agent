# 快速开始指南

本指南将帮助您在 10 分钟内启动并运行高中历史智能出题系统。

## 📋 前置条件

在开始之前，请确保您已完成以下准备工作：

- ✅ 已安装 Python 3.12 或更高版本
- ✅ 已安装 `uv` 包管理器（或使用 pip）
- ✅ 已安装并配置 RAGFlow（参考 [RAGFlow安装教程.md](./RAGFlow安装教程.md)）
- ✅ 已获取 RAGFlow 的 API Key 和 Chat ID
- ✅ 已在 RAGFlow 中上传教材 PDF 并完成索引

---

## 🚀 快速开始（5 步）

### 步骤 1：克隆或下载项目

如果您还没有项目代码，请先获取项目：

```bash
# 如果使用 Git
git clone <项目地址>
cd History_problem_agent

# 或直接下载 ZIP 文件并解压
```

### 步骤 2：安装依赖

使用 `uv`（推荐）：

```bash
uv sync
```

或使用 `pip`：

```bash
pip install -r requirements.txt
```

如果没有 `requirements.txt`，可以手动安装：

```bash
pip install fastapi>=0.128.0 requests>=2.32.5 streamlit>=1.52.2 uvicorn>=0.40.0
```

### 步骤 3：配置 RAGFlow 连接

编辑 `backend.py` 文件，修改以下配置：

```python
# 在 backend.py 的第 14-21 行
RAGFLOW_HOST = "http://localhost:80"  # 您的 RAGFlow 地址
RAGFLOW_API_KEY = "ragflow-您的API密钥"  # 您的 API Key
CHAT_ID = "您的Chat ID"  # 您的对话助手 ID
```

**重要提示**：
- `RAGFLOW_HOST`：如果 RAGFlow 运行在其他地址或端口，请相应修改
- `RAGFLOW_API_KEY`：在 RAGFlow 后台的 API 设置中获取
- `CHAT_ID`：在 RAGFlow 后台的 Chat 菜单中，点击您的助手查看 ID

### 步骤 4：启动后端服务

打开第一个终端窗口，运行：

```bash
uvicorn backend:app --reload --port 8000
```

您应该看到类似以下的输出：

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**保持此终端窗口打开**，后端服务需要持续运行。

### 步骤 5：启动前端界面

打开第二个终端窗口，运行：

```bash
streamlit run app.py
```

浏览器会自动打开 `http://localhost:8501`，您将看到出题系统的界面。

---

## 🎯 第一次使用

### 1. 选择出题参数

在左侧边栏中：

1. **选择教材模块**：例如"必修：中外历史纲要（上）中国史"
2. **选择考察专题**：例如"1.7 晚清时期的内忧外患与救亡图存"
3. **选择题目类型**：单项选择题或材料分析题
4. **选择核心素养**：至少选择一项，例如"时空观念"
5. **设置难度等级**：选择"中等"或"困难"
6. **选择史料类型**：例如"文字材料"

### 2. 生成题目

点击 **🚀 开始出题** 按钮，系统将：

1. 发送请求到后端 API
2. 后端调用 RAGFlow 生成题目
3. 解析并返回题目数据
4. 在前端展示完整的题目内容

**注意**：首次生成可能需要 30-120 秒，请耐心等待。

### 3. 查看结果

生成成功后，您将看到：

- **材料**：题目相关的史料内容
- **问题**：题目的题干
- **选项**：如果是选择题，显示 A、B、C、D 四个选项
- **答案与解析**：点击"👁️ 查看答案与解析"展开查看详细解析

---

## 🔧 验证安装

### 测试后端 API

在浏览器中访问：`http://127.0.0.1:8000/docs`

您应该看到 FastAPI 的自动生成文档界面。可以在这里测试 API 接口。

### 测试 RAGFlow 连接

在终端中运行：

```bash
curl -X POST "http://127.0.0.1:8000/generate_question" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "1.7 晚清时期的内忧外患与救亡图存",
    "competencies": ["spacetime"],
    "difficulty": "medium",
    "material_type": "text",
    "question_type": "choice"
  }'
```

如果返回 JSON 格式的题目数据，说明配置成功。

---

## ⚠️ 常见问题排查

### 问题 1：后端启动失败

**错误信息**：`ModuleNotFoundError: No module named 'fastapi'`

**解决方案**：
```bash
# 确保已安装依赖
uv sync
# 或
pip install fastapi uvicorn
```

### 问题 2：前端无法连接后端

**错误信息**：`连接失败: Connection refused`

**解决方案**：
- 确认后端服务正在运行（检查步骤 4）
- 确认后端运行在 `http://127.0.0.1:8000`
- 检查防火墙设置

### 问题 3：RAGFlow API 返回 404

**错误信息**：`404 Not Found: 请检查 backend.py 里的 CHAT_ID`

**解决方案**：
- 检查 `backend.py` 中的 `CHAT_ID` 是否正确
- 确认 RAGFlow 服务正在运行
- 在 RAGFlow 后台确认 Chat 助手已创建

### 问题 4：JSON 解析失败

**错误信息**：`解析 JSON 失败`

**解决方案**：
1. 进入 RAGFlow 后台
2. 找到您的对话助手
3. 编辑 System Prompt，添加：
   ```
   你必须严格按照 JSON 格式输出，不要包含任何其他文字或 Markdown 标记。
   只输出有效的 JSON 对象。
   ```

### 问题 5：生成题目超时

**解决方案**：
- 这是正常现象，复杂题目可能需要 60-120 秒
- 如果经常超时，可以检查 RAGFlow 服务性能
- 尝试选择更简单的参数组合

---

## 📚 下一步

现在您已经成功启动了系统！接下来可以：

1. **阅读完整文档**：查看 [README.md](./README.md) 了解详细功能
2. **探索不同参数**：尝试不同的教材模块、专题和素养组合
3. **调整提示词**：在 RAGFlow 助手的 System Prompt 中优化出题效果
4. **扩展知识库**：上传更多历史资料到 RAGFlow 知识库

---

## 🎓 使用技巧

### 技巧 1：选择合适的素养组合

- **单一素养**：题目更聚焦，适合专项训练
- **多素养组合**：题目更综合，适合综合测试

### 技巧 2：难度选择建议

- **简单**：适合基础复习
- **中等**：适合日常练习（推荐）
- **困难**：适合拔高训练

### 技巧 3：史料类型选择

- **文字材料**：最常见，适合大多数题目
- **图片/表格/地图**：需要 RAGFlow 知识库中包含相应图片资源

### 技巧 4：批量生成

目前系统每次生成一道题目。如需批量生成：
1. 生成一道题目后，修改参数
2. 再次点击"开始出题"
3. 重复此过程

---

## 🆘 获取帮助

如果遇到问题：

1. **查看日志**：后端和前端终端窗口会显示详细日志
2. **检查配置**：确认 `backend.py` 中的配置正确
3. **参考文档**：
   - [README.md](./README.md) - 完整项目文档
   - [RAGFlow安装教程.md](./RAGFlow安装教程.md) - RAGFlow 安装指南
4. **提交 Issue**：在项目仓库提交问题报告

---

## ✅ 检查清单

在开始使用前，请确认：

- [ ] Python 3.12+ 已安装
- [ ] 项目依赖已安装
- [ ] RAGFlow 已安装并运行
- [ ] RAGFlow 知识库已创建并上传教材
- [ ] RAGFlow Chat 助手已创建
- [ ] `backend.py` 中的配置已填写
- [ ] 后端服务已启动（端口 8000）
- [ ] 前端界面已打开（端口 8501）

---

**祝您使用愉快！** 🎉

如有任何问题，欢迎查看完整文档或提交 Issue。
