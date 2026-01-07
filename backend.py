from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json
import re

app = FastAPI()

# ================= 配置区域 (请务必修改这里) =================

# 1. RAGFlow 服务器地址 (根据你提供的文档是 http://localhost)
# 如果你是 Docker 部署且没改端口，通常是 80 或 9380，请根据实际情况保留或删除端口号
RAGFLOW_HOST = "http://localhost:80" 

# 2. 你的 API Key
RAGFLOW_API_KEY = "ragflow-PCzIelPh9Q4gBp6ggQnin_U7sNNtxNXNrHJUUmi-rsY" 

# 3. 【关键】你的 Chat ID (对话助手 ID)
# 必须去 RAGFlow 后台 -> Chat 菜单 -> 找到你的助手 ID 填在这里
CHAT_ID = "d595c5a0eaa111f0823e5aa3820c5bf3" 

# ==========================================================

class QuestionRequest(BaseModel):
    topic: str
    competencies: list[str]
    difficulty: str
    material_type: str
    question_type: str

def clean_json_string(raw_str: str) -> str:
    """清洗 LLM 返回的字符串，提取纯净的 JSON"""
    # 移除 Markdown 代码块标记
    clean_str = re.sub(r'```json\s*', '', raw_str)
    clean_str = re.sub(r'```', '', clean_str)
    # 移除可能的开头废话，尝试找到第一个 { 和最后一个 }
    start_idx = clean_str.find('{')
    end_idx = clean_str.rfind('}')
    if start_idx != -1 and end_idx != -1:
        clean_str = clean_str[start_idx : end_idx + 1]
    return clean_str.strip()

def call_ragflow_api(prompt: str):
    """
    根据文档使用 RAGFlow 的 OpenAI 兼容接口
    文档路径: POST /api/v1/chats_openai/{chat_id}/chat/completions
    """
    
    # 构造文档中指定的准确 URL
    url = f"{RAGFLOW_HOST}/api/v1/chats_openai/{CHAT_ID}/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {RAGFLOW_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 构造符合 OpenAI 标准的请求体
    payload = {
        "model": "ragflow", # 文档说这个字段必填，但服务器会自动处理，填啥都行
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False # 我们需要一次性拿到完整 JSON，所以关掉流式
    }
    
    print(f"📡 正在请求 RAGFlow 助手 (ID: {CHAT_ID})...")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        
        # 1. 检查 HTTP 状态码
        if response.status_code != 200:
            error_msg = f"API Error {response.status_code}: {response.text}"
            print(f"❌ {error_msg}")
            # 如果是 404，说明 Chat ID 填错了或者 URL 拼错了
            if response.status_code == 404:
                raise Exception("404 Not Found: 请检查 backend.py 里的 CHAT_ID 是否填写正确，以及 RAGFlow 地址是否正确。")
            raise Exception(error_msg)
            
        # 2. 解析返回结果
        resp_json = response.json()
        
        # 3. 提取内容 (OpenAI 格式: choices[0].message.content)
        if 'choices' not in resp_json or len(resp_json['choices']) == 0:
            raise Exception(f"API 返回结构异常: {resp_json}")
            
        raw_answer = resp_json['choices'][0]['message']['content']
        print("✅ RAGFlow 返回成功，正在解析 JSON...")
        
        # 4. 清洗并解析 JSON
        json_str = clean_json_string(raw_answer)
        return json.loads(json_str)
        
    except json.JSONDecodeError:
        print(f"⚠️ 解析 JSON 失败。模型原始返回:\n{raw_answer}")
        return {
            "question_body": "模型生成了内容，但格式不是标准的 JSON，无法渲染。",
            "material": raw_answer, # 把原始内容展示出来
            "options": {},
            "answer": "格式错误",
            "analysis": "请尝试在 RAGFlow 助手的 System Prompt 中强调：'只输出 JSON，不要输出其他文字'。"
        }
    except Exception as e:
        print(f"❌ 发生系统错误: {str(e)}")
        raise e

@app.post("/generate_question")
def generate_question(req: QuestionRequest):
    # 组装提示词
    safe_prompt = f"""
    你是一个高中历史出题专家。请基于知识库内容，设计一道关于【{req.topic}】的【{req.question_type}】。
    
    【出题要求】
    1. 考察素养：{', '.join(req.competencies)}
    2. 难度等级：{req.difficulty}
    3. 史料类型：请包含【{req.material_type}】。
    4. 核心规则：
       - 必须以严格的 JSON 格式输出，不要包含 Markdown 标记。
       - JSON 包含字段：material(材料内容), question_body(题干), options(字典,如选择题), answer(答案), analysis(解析)。
       - 如果是选择题，options 必须包含 A, B, C, D。
       - 如果是非选择题，options 留空字典 {{}}。
    """
    
    try:
        if "请在这里填入你的chat_id" in CHAT_ID:
             raise HTTPException(status_code=500, detail="请先在 backend.py 文件中填入您的 RAGFlow Chat ID！")

        result_data = call_ragflow_api(safe_prompt)
        result_data['type'] = req.question_type
        return {"status": "success", "data": result_data}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


# 加载 JSON 配置 (为了在后端获取素养对应的 prompt_rule)
# 注意：你需要确保 backend.py 同级目录下有 curriculum_data.json
def load_competency_rules():
    try:
        # 获取 backend.py 所在的绝对目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, 'curriculum_data.json')
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {c['id']: c.get('prompt_rule', '') for c in data['competencies']}
    except Exception as e:
        print(f"⚠️ 加载素养规则失败: {e}")
        return {}

COMPETENCY_RULES = load_competency_rules()

@app.post("/generate_question")
def generate_question(req: QuestionRequest):
    # 1. 获取前端选中的素养对应的具体出题策略
    # req.competencies 传过来的是 id 列表 (如 ['spacetime', 'evidence'])
    # 我们把这些规则拼接起来
    specific_rules = []
    for comp_id in req.competencies:
        if comp_id in COMPETENCY_RULES:
            specific_rules.append(f"- 针对【{comp_id}】素养：{COMPETENCY_RULES[comp_id]}")
    
    rules_text = "\n    ".join(specific_rules)

    # 2. 组装更高级的 Prompt
    # 核心变化：加入了 "Step-by-Step Thinking" (思维链) 和 "Negative Constraints" (负面约束)
    safe_prompt = f"""
    你是一位精通《普通高中历史课程标准（2017年版2025年修订）》的命题专家。
    请基于知识库内容，设计一道关于【{req.topic}】的【{req.question_type}】。

    【核心素养考察目标 - 必须严格执行】
    {rules_text}

    【出题参数】
    1. 难度等级：{req.difficulty} (请确保题目不仅考查记忆，更考查思维深度)
    2. 史料类型：必须包含【{req.material_type}】。
    
    【出题逻辑链 (请在内心按此步骤思考)】
    第一步：在知识库中找到与{req.topic}相关的核心史实。
    第二步：寻找该史实中能体现上述“素养规则”的矛盾点、变化点或深层逻辑。
    第三步：构建情境。不要直接问史实，要问“材料反映了什么”或“由于什么原因导致了该现象”。
    第四步：如果是选择题，设计3个具有迷惑性的干扰项（看起来对但逻辑有误）。

    【负面约束 (做不到将受到惩罚)】
    - 严禁出“死记硬背”的题目（如直接问哪一年发生了什么）。
    - 严禁直接抄录教材原文作为题干。
    - 严禁解析过于简单，解析必须解释清楚为什么选A而不选B（知识迁移）。

    【输出格式】
    必须为严格的 JSON，包含：material, question_body, options, answer, analysis。
    """
    
    try:
        if "请在这里填入你的chat_id" in CHAT_ID:
             raise HTTPException(status_code=500, detail="请先配置 Chat ID")

        result_data = call_ragflow_api(safe_prompt)
        result_data['type'] = req.question_type
        return {"status": "success", "data": result_data}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))