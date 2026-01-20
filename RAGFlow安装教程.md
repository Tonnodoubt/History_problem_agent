# RAGFlow 安装与配置教程

本教程将指导您完成 RAGFlow 的安装、配置和知识库设置，以便与高中历史智能出题系统配合使用。

## 目录

- [系统要求](#系统要求)
- [安装方式](#安装方式)
  - [方式一：Docker Compose（推荐）](#方式一docker-compose推荐)
  - [方式二：Docker 单容器](#方式二docker-单容器)
- [初始配置](#初始配置)
- [创建知识库](#创建知识库)
- [上传教材 PDF](#上传教材-pdf)
- [创建对话助手](#创建对话助手)
- [获取 API Key 和 Chat ID](#获取-api-key-和-chat-id)
- [验证安装](#验证安装)
- [常见问题](#常见问题)

---

## 系统要求

### 硬件要求

- **CPU**：4 核或以上（推荐 8 核）
- **内存**：16GB 或以上（推荐 32GB）
- **存储**：至少 50GB 可用空间（用于存储向量数据库和模型）
- **GPU**：可选，但推荐使用 NVIDIA GPU 以加速向量检索

### 软件要求

- **操作系统**：Linux、macOS 或 Windows（使用 WSL2）
- **Docker**：20.10 或更高版本
- **Docker Compose**：2.0 或更高版本（如果使用 Docker Compose 方式）

---

## 安装方式

### 方式一：Docker Compose（推荐）

这是最简单和推荐的安装方式，适合大多数用户。

#### 1. 创建项目目录

```bash
mkdir ragflow
cd ragflow
```

#### 2. 下载 Docker Compose 配置文件

```bash
# 下载官方 docker-compose.yml
curl -o docker-compose.yml https://raw.githubusercontent.com/infiniflow/ragflow/main/docker/docker-compose.yml
```

或者手动创建 `docker-compose.yml` 文件：

```yaml
version: '3.8'

services:
  ragflow:
    image: infiniflow/ragflow:latest
    container_name: ragflow
    ports:
      - "80:80"
      - "9380:9380"
    volumes:
      - ./data:/var/lib/ragflow
      - ./books:/ragflow/books
    environment:
      - RAGFLOW_SERVER_PORT=80
      - RAGFLOW_API_PORT=9380
    restart: unless-stopped
```

#### 3. 启动 RAGFlow

```bash
docker-compose up -d
```

#### 4. 查看运行状态

```bash
docker-compose ps
docker-compose logs -f ragflow
```

等待几分钟，直到看到服务启动完成的日志。

#### 5. 访问 Web 界面

打开浏览器访问：`http://localhost:80`

---

### 方式二：Docker 单容器

如果您不想使用 Docker Compose，可以直接运行 Docker 容器。

```bash
docker run -d \
  --name ragflow \
  -p 80:80 \
  -p 9380:9380 \
  -v $(pwd)/data:/var/lib/ragflow \
  -v $(pwd)/books:/ragflow/books \
  infiniflow/ragflow:latest
```

---

## 初始配置

### 1. 首次登录

1. 打开浏览器访问 `http://localhost:80`
2. 首次访问会提示创建管理员账户
3. 设置管理员用户名和密码（请妥善保管）

### 2. 系统设置

登录后，进入 **系统设置** 页面：

- **API 设置**：启用 API 访问
- **模型配置**：选择或配置嵌入模型和 LLM 模型
  - 默认使用内置模型，无需额外配置
  - 如需使用 OpenAI API 或其他模型，可在设置中配置

---

## 创建知识库

### 1. 进入知识库管理

1. 登录 RAGFlow 后台
2. 点击左侧菜单 **知识库**（Knowledge Base）
3. 点击 **创建知识库** 按钮

### 2. 配置知识库

填写知识库信息：

- **知识库名称**：`高中历史教材库`（或您喜欢的名称）
- **描述**：`包含必修和选择性必修教材的完整内容`
- **分块策略**：选择默认策略即可
- **向量模型**：使用默认模型

点击 **创建** 完成知识库创建。

---

## 上传教材 PDF

### 1. 进入知识库

1. 在知识库列表中，点击刚创建的 **高中历史教材库**
2. 进入知识库详情页面

### 2. 上传文件

有两种上传方式：

#### 方式一：通过 Web 界面上传

1. 点击 **上传文档** 按钮
2. 选择 `books/` 目录下的 PDF 文件：
   - 《中外历史纲要》（上）课程正文.pdf
   - 《中外历史纲要》（下）课程正文.pdf
   - 选择性必修1：国家制度与社会治理.pdf
   - 选择性必修2：经济与社会生活.pdf
   - 选择性必修3：文化交流与传播.pdf
3. 等待上传完成

#### 方式二：通过 API 上传

```bash
# 使用 curl 上传文件
curl -X POST "http://localhost:80/api/v1/datasets/{knowledge_base_id}/documents" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "file=@/path/to/your/file.pdf"
```

### 3. 等待解析和索引

上传后，RAGFlow 会自动：
1. **解析文档**：提取文本内容
2. **分块处理**：将文档分割成适合检索的块
3. **向量化**：生成向量索引
4. **完成索引**：状态显示为"已完成"

**注意**：这个过程可能需要几分钟到几十分钟，取决于文档大小。您可以在知识库页面查看处理进度。

---

## 创建对话助手

### 1. 进入 Chat 管理

1. 点击左侧菜单 **Chat**（对话助手）
2. 点击 **创建助手** 按钮

### 2. 配置助手

填写助手信息：

- **助手名称**：`历史出题助手`（或您喜欢的名称）
- **知识库**：选择刚才创建的 **高中历史教材库**
- **模型**：选择可用的 LLM 模型
- **System Prompt**（系统提示词）：建议添加以下内容：

```
你是一位精通《普通高中历史课程标准（2017年版2025年修订）》的命题专家。
你必须严格按照 JSON 格式输出，不要包含任何其他文字或 Markdown 标记。
只输出有效的 JSON 对象。
```

### 3. 保存助手

点击 **保存** 完成创建。

---

## 获取 API Key 和 Chat ID

### 1. 获取 API Key

1. 点击右上角用户头像
2. 选择 **API 密钥** 或 **设置**
3. 在 API 设置页面，点击 **生成新密钥**
4. 复制生成的 API Key（格式类似：`ragflow-xxxxxxxxxxxxx`）
5. **重要**：API Key 只显示一次，请妥善保存

### 2. 获取 Chat ID

1. 进入 **Chat** 菜单
2. 找到刚才创建的 **历史出题助手**
3. 点击助手名称进入详情页
4. 在 URL 中可以看到 Chat ID，或者在助手详情页的 API 信息中查看
5. Chat ID 是一个 32 位的十六进制字符串（例如：`d595c5a0eaa111f0823e5aa3820c5bf3`）

### 3. 配置到项目

将获取到的信息填入 `backend.py`：

```python
# RAGFlow 服务器地址
RAGFLOW_HOST = "http://localhost:80"

# RAGFlow API Key
RAGFLOW_API_KEY = "ragflow-你的API密钥"

# Chat ID（对话助手 ID）
CHAT_ID = "你的Chat ID"
```

---

## 验证安装

### 1. 测试 API 连接

使用 curl 测试 API 是否正常工作：

```bash
curl -X POST "http://localhost:80/api/v1/chats_openai/{CHAT_ID}/chat/completions" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ragflow",
    "messages": [
      {"role": "user", "content": "测试连接"}
    ],
    "stream": false
  }'
```

如果返回 JSON 响应，说明配置成功。

### 2. 测试知识库检索

在 RAGFlow Web 界面中：
1. 进入创建的对话助手
2. 发送测试问题，例如："请介绍一下晚清时期的内忧外患"
3. 如果助手能够基于教材内容回答，说明知识库配置成功

---

## 常见问题

### Q1: Docker 容器无法启动

**解决方案**：
- 检查端口是否被占用：`netstat -tulpn | grep 80`
- 检查 Docker 服务是否运行：`systemctl status docker`
- 查看容器日志：`docker logs ragflow`

### Q2: 无法访问 Web 界面

**解决方案**：
- 确认容器正在运行：`docker ps`
- 检查防火墙设置
- 尝试使用 `http://127.0.0.1:80` 而不是 `localhost`

### Q3: 文档上传后一直显示"处理中"

**解决方案**：
- 等待更长时间（大文件可能需要 10-30 分钟）
- 检查容器资源使用情况：`docker stats ragflow`
- 查看日志排查错误：`docker logs ragflow`

### Q4: API 返回 404 错误

**解决方案**：
- 确认 Chat ID 填写正确
- 确认 API Key 有效
- 检查 RAGFlow 服务地址是否正确

### Q5: 知识库检索结果不准确

**解决方案**：
- 检查文档是否已完全索引（状态应为"已完成"）
- 尝试调整分块策略
- 在 System Prompt 中强调使用知识库内容

### Q6: 内存不足

**解决方案**：
- 增加 Docker 容器的内存限制
- 减少同时处理的文档数量
- 考虑使用 GPU 加速（如果可用）

---

## 下一步

完成 RAGFlow 安装和配置后，请继续阅读 [QuickStart.md](./QuickStart.md) 了解如何启动和使用高中历史智能出题系统。

---

## 参考资源

- [RAGFlow 官方文档](https://github.com/infiniflow/ragflow)
- [RAGFlow API 文档](https://github.com/infiniflow/ragflow/blob/main/docs/api.md)
- [Docker 官方文档](https://docs.docker.com/)

---

**提示**：如果在安装过程中遇到问题，请查看 RAGFlow 的 GitHub Issues 或提交新的 Issue。
