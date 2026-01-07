import streamlit as st
import json
import requests
import os

# ===========================
# 1. 页面配置
# ===========================
st.set_page_config(page_title="高中历史出题 Agent", page_icon="📚", layout="wide")
st.title("🎓 高中历史智能出题系统")
st.markdown("基于《普通高中历史课程标准（2017年版2025年修订）》")

# ===========================
# 2. 加载配置数据
# ===========================
@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, 'curriculum_data.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

data = load_data()
if not data:
    st.error("配置文件加载失败")
    st.stop()

# ===========================
# 3. 侧边栏：出题控制台
# ===========================
with st.sidebar:
    st.header("🛠️ 出题参数设置")
    
    # 1. 教材模块
    module_map = {m['label']: m['id'] for m in data['modules']}
    sel_mod_label = st.selectbox("1. 选择教材模块", list(module_map.keys()))
    current_mod = next(m for m in data['modules'] if m['label'] == sel_mod_label)

    # 2. 专题
    sel_topic = st.selectbox("2. 考察专题", current_mod['topics'])

    # 3. 题型选择 (新增功能)
    q_type_map = {qt['label']: qt['id'] for qt in data.get('questionTypes', [])}
    # 默认选中第一个（单项选择题）
    sel_q_type_label = st.radio("3. 题目类型", list(q_type_map.keys()))

    # 4. 核心素养
    comp_map = {c['label']: c['id'] for c in data['competencies']}
    default_comp = ["时空观念 (学科本质)"] if "时空观念 (学科本质)" in comp_map else []
    sel_comps = st.multiselect("4. 核心素养", list(comp_map.keys()), default=default_comp)

    # 5. 难度 & 史料
    col_a, col_b = st.columns(2)
    with col_a:
        level_map = {l['label']: l['id'] for l in data['levels']}
        sel_level = st.selectbox("5. 难度", list(level_map.keys()), index=1)
    with col_b:
        mat_map = {m['label']: m['id'] for m in data['materialTypes']}
        sel_mat = st.selectbox("6. 史料", list(mat_map.keys()), index=3)

    st.markdown("---")
    generate_btn = st.button("🚀 开始出题", type="primary", use_container_width=True)

# ===========================
# 4. 主界面：题目展示区
# ===========================
if 'q_data' not in st.session_state:
    st.session_state.q_data = None

if generate_btn:
    with st.spinner('正在生成题目...'):
        payload = {
            "topic": sel_topic,
            "competencies": [comp_map[c] for c in sel_comps],
            "difficulty": level_map[sel_level],
            "material_type": mat_map[sel_mat],
            "question_type": q_type_map[sel_q_type_label]  # 传给后端
        }
        
        try:
            api_url = "http://127.0.0.1:8000/generate_question"
            response = requests.post(api_url, json=payload)
            if response.status_code == 200:
                st.session_state.q_data = response.json()['data']
            else:
                st.error(f"出题失败: {response.text}")
        except Exception as e:
            st.error(f"连接失败: {e}")

# 渲染逻辑
if st.session_state.q_data:
    q = st.session_state.q_data
    current_type = q.get('type', 'choice') # 获取后端返回的题型

    with st.container(border=True):
        st.subheader(f"📜 {sel_topic}")
        st.caption(f"题型：{sel_q_type_label} | 难度：{sel_level}")
        
        # 1. 材料区
        st.markdown("**【材料】**")
        st.info(q.get('material', ''))
        
        # 2. 题干区
        st.markdown(f"**【问题】** {q.get('question_body', '')}")
        
        # 3. 选项区 (只有选择题才显示)
        if current_type == 'choice':
            st.markdown("---")
            opts = q.get('options', {})
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**A.** {opts.get('A','')}")
                st.markdown(f"**C.** {opts.get('C','')}")
            with c2:
                st.markdown(f"**B.** {opts.get('B','')}")
                st.markdown(f"**D.** {opts.get('D','')}")
        else:
            # 大题显示一条分隔线即可
            st.markdown("---")
            st.markdown("*（请根据材料并在纸上作答，点击下方按钮查看评分标准）*")

    # 4. 答案区
    with st.expander("👁️ 查看答案与解析"):
        if current_type == 'choice':
            st.success(f"**正确答案：{q.get('answer')}**")
        else:
            st.warning("**【参考答案 / 评分标准】**")
            st.text(q.get('answer')) # 大题答案通常很长，用 text 显示保留格式
            
        st.markdown("### 💡 专家解析")
        st.write(q.get('analysis'))

else:
    st.info("👈 请在左侧选择参数（新增题型选择），点击“开始出题”。")