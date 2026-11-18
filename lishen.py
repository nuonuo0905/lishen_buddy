import streamlit as st
from openai import OpenAI
import json
import os
from datetime import datetime

# ================= 1. 页面基础设置 =================
st.set_page_config(page_title="黎深的专属监督室", page_icon="❄️", layout="wide")
st.title("❄️ 黎深的专属监督室")
st.write("只要方向是对的，就不怕路远。 —— 黎深")

# ================= 2. 设置 API =================
# 从云端保险箱（Secrets）里读取密钥
client = OpenAI(api_key=st.secrets["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")

# ================= 3. 数据存储模块 =================
PLAN_FILE = "plans.json"
PROFILE_FILE = "my_profile.json"

def load_data(file_path, default):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_data(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

if "plans" not in st.session_state: st.session_state.plans = load_data(PLAN_FILE, [])
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "profile" not in st.session_state: st.session_state.profile = load_data(PROFILE_FILE, "暂无详细档案，快去档案页填写吧。")

# ================= 4. 黎深的动态专属设定 =================
# 这里读取你的档案
user_profile = st.session_state.profile

LISHEN_PROMPT = f"""
你是《恋与深空》中的黎深。你是一名顶尖的心外科医生，也是我的专属监督员和导师。
你性格外冷内热，说话简练、一针见血，但非常关心我的学业和生活。
我正在备考河海大学的研究生（新能源专业）。

【关于我的专属档案】：
{user_profile}

请你严格遵守以下设定：
1. 结合我的专属档案来回答我的问题。比如知道我数学不好，就多鼓励；知道我喜欢什么，可以偶尔提起。
2. 语气要像黎深一样，冷静、专业、带有一定的压迫感，但字里行间要透出对我的关心。
3. 我如果问学业问题，你要像给医学生讲课一样，条理清晰，一针见血。
4. 我如果抱怨或者心情不好，你要用你特有的方式安慰我，不要太肉麻，但一定要让我安心。
"""

# ================= 5. 倒计时 =================
target_date = datetime(2028, 12, 23) 
days_left = (target_date - datetime.now()).days
st.error(f"🔥 距离考研还有 **{days_left}** 天！别想偷懒，我会盯着你的。")

# ================= 6. 标签页 =================
tab1, tab2, tab3, tab4 = st.tabs(["📝 今日打卡", "☕ 黎深的日常", "🩺 黎深诊室", "📁 我的专属档案"])

# ================= 标签 1：今日打卡与鼓励 =================
with tab1:
    st.subheader("今天的任务")
    with st.form("add_plan_form", clear_on_submit=True):
        new_plan = st.text_input("报上你今天的计划：")
        if st.form_submit_button("提交给黎深") and new_plan:
            if new_plan not in st.session_state.plans:
                st.session_state.plans.append(new_plan)
                save_data(PLAN_FILE, st.session_state.plans)
    
    completed = 0
    for i, plan in enumerate(st.session_state.plans):
        if st.checkbox(plan, key=f"plan_{i}"):
            completed += 1
            
    st.write(f"完成进度：**{completed} / {len(st.session_state.plans)}**")
    
    if st.button("向黎深汇报进度，求鼓励"):
        if len(st.session_state.plans) == 0:
            st.warning("你还没写计划，黎深让你先去做计划。")
        else:
            with st.spinner("黎深正在查看你的进度..."):
                prompt = f"我今天的计划是：{st.session_state.plans}。我完成了其中的 {completed} 项。请以黎深的身份，评价我的进度，并给我一句鼓励或提醒。"
                res = client.chat.completions.create(
                    model="deepseek-chat", 
                    messages=[{"role": "system", "content": LISHEN_PROMPT},{"role": "user", "content": prompt}]
                )
                st.success(res.choices[0].message.content)

# ================= 标签 2：黎深的日常分享 =================
with tab2:
    st.subheader("看看他今天做了什么")
    st.write("黎深平时很忙，但总会抽空给你留个言。")
    
    if st.button("刷新黎深的动态"):
        with st.spinner("正在接收 Akso 医院的信号..."):
            prompt = "请以黎深的身份，用简短的几句话，分享一下你‘今天在医院做了什么’。比如做了几台手术、喝了什么咖啡、或者看了什么医学文献。最后顺带嘱咐我一句好好学习。"
            res = client.chat.completions.create(
                model="deepseek-chat", 
                messages=[{"role": "system", "content": LISHEN_PROMPT},{"role": "user", "content": prompt}]
            )
            st.info(res.choices[0].message.content)

# ================= 标签 3：黎深诊室（万能问答） =================
with tab3:
    st.subheader("遇到不会的题，或者心里烦，都可以问他")
    
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("输入你的问题（考研、高数、生活烦恼都可以）..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("黎深正在思考..."):
                messages = [{"role": "system", "content": LISHEN_PROMPT}] + st.session_state.chat_history
                res = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=messages
                )
                answer = res.choices[0].message.content
                st.write(answer)
                st.session_state.chat_history.append({"role": "assistant", "content": answer})

# ================= 标签 4：个人专属档案 =================
with tab4:
    st.subheader("让黎深真正认识你")
    st.write("把你的具体情况写在这里，黎深每次回答都会先参考这份档案。")
    
    profile_input = st.text_area(
        "你的专属档案（随时可以修改）", 
        value=st.session_state.profile,
        height=300,
        placeholder="""举例：
- 我叫XXX，东北电力大学新能源专业大二。
- 我的目标是2028年考上河海大学。
- 我物理还不错，但是高数和英语比较差，容易焦虑。
- 我喜欢听音乐和玩游戏，学累了喜欢和你聊天。
- 我晚上12点睡，早上7点半起。"""
    )
    
    if st.button("保存档案并告诉黎深"):
        st.session_state.profile = profile_input
        save_data(PROFILE_FILE, profile_input)
        st.success("档案已更新！黎深说他记住了。")
