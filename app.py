import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import base64
import datetime

# 載入環境變數
load_dotenv()
env_api_key = os.getenv("GROQ_API_KEY")

st.set_page_config(
    page_title="Groq Pro Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 初始化 Session State ---
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {"新對話": []}
if "current_session" not in st.session_state:
    st.session_state.current_session = "新對話"
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "當使用者詢問現在時間、日期時，呼叫此函數獲取當前本地時間。",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    }
]

# --- 功能函式：自動生成標題 ---
def generate_title(api_key, first_msg):
    try:
        client = Groq(api_key=api_key)
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f"根據以下內容，生成一個 5 字以內的繁體中文標題，不要有引號或句號：\n{first_msg}"}],
            max_completion_tokens=20
        )
        title = res.choices[0].message.content.strip().replace('"', '').replace('「', '').replace('」', '')
        return title if title else first_msg[:10]
    except:
        return first_msg[:10]
    
def get_best_model(prompt, current_choice):
    # 1. 如果有關鍵字，直接覆蓋原本的選項
    prompt_lower = prompt.lower()
    
    if any(k in prompt_lower for k in ["搜尋", "查詢", "網路上找", "search"]):
        return "groq/compound" # 適合搜尋
        
    if any(k in prompt_lower for k in ["圖片", "picture"]):
        return "meta-llama/llama-4-scout-17b-16e-instruct"
        
    # 2. 如果沒偵測到特殊意圖，使用使用者在側邊欄選的模型
    return current_choice

def get_current_time():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

available_functions = {
    "get_current_time": get_current_time,
}

# --- 側邊欄 ---
with st.sidebar:
    st.title("🚀 Groq 控制台")
    api_key = st.text_input("Groq API Key", value=env_api_key if env_api_key else "", type="password")
    
    st.divider()
    
    # 1. 新增對話按鈕
    if st.button("➕ 開啟新對話", use_container_width=True):
        new_id = f"新對話 {len(st.session_state.chat_sessions)}"
        st.session_state.chat_sessions[new_id] = []
        st.session_state.current_session = new_id  # 自動跳轉
        st.rerun()

    st.subheader("📥 匯出工具")
    
    # 修正點：先獲取當前對話名稱與內容，確保變數存在
    curr_sess_name = st.session_state.get("current_session")
    
    if curr_sess_name and curr_sess_name in st.session_state.chat_sessions:
        # 從 session_state 拿取對話紀錄
        export_messages = st.session_state.chat_sessions[curr_sess_name]
        
        if export_messages:
            # 1. 格式化為 Markdown
            export_text = f"# Groq Chat Log: {curr_sess_name}\n\n"
            for m in export_messages:
                role_name = "🧑 User" if m["role"] == "user" else "🤖 Assistant"
                export_text += f"### {role_name}\n{m['content']}\n\n---\n\n"
            
            # 2. 下載按鈕
            st.download_button(
                label="💾 匯出當前對話 (Markdown)",
                data=export_text,
                file_name=f"{curr_sess_name}.md",
                mime="text/markdown",
                use_container_width=True,
                key="export_btn" # 加上 key 避免與其他按鈕衝突
            )
        else:
            st.info("尚無對話內容可供匯出")
    else:
        st.info("請先開啟一個對話")

    st.subheader("歷史對話")
    # 建立一個函式來處理刪除邏輯
    def delete_session(target_name):
        if target_name in st.session_state.chat_sessions:
            del st.session_state.chat_sessions[target_name]
            # 如果刪除的是當前對話，則切換回剩下的第一個對話，或清空
            if st.session_state.current_session == target_name:
                remaining = list(st.session_state.chat_sessions.keys())
                st.session_state.current_session = remaining[0] if remaining else "新對話"
                if not remaining:
                    st.session_state.chat_sessions["新對話"] = []
            st.rerun()

    # 2. 將列表改為「切換按鈕 + 刪除按鈕」組合
    for session_name in list(st.session_state.chat_sessions.keys()):
        # 使用 columns 讓刪除按鈕排在右側
        col_btn, col_del = st.columns([0.8, 0.2])
        
        with col_btn:
            label = f"💬 {session_name}"
            button_type = "primary" if session_name == st.session_state.current_session else "secondary"
            if st.button(label, key=f"btn_{session_name}", use_container_width=True, type=button_type):
                st.session_state.current_session = session_name
                st.rerun()
        
        with col_del:
            # 刪除按鈕，使用垃圾桶圖標
            if st.button("🗑️", key=f"del_{session_name}", use_container_width=True):
                delete_session(session_name)

    st.divider()
    st.subheader("參數設定")
    model_option = st.selectbox("模型", ["groq/compound", "qwen/qwen3-32b", "llama-3.3-70b-versatile", "meta-llama/llama-4-scout-17b-16e-instruct"])
    # 側邊欄加入
    role_choice = st.selectbox("切換 AI 模式", ["一般助手", "程式碼專家", "學術論文助手", "中英翻譯官"])
    temp_value = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1)

# 設定對應內容
prompts = {
    "一般助手": "你是一個親切的 AI 助手。如果呼叫工具，請根據工具回傳的數據準確回答使用者的問題。",
    "程式碼專家": "你是一位資深工程師，請用專業、精簡的風格回答，並注重程式碼的效能與安全性。如果呼叫工具，請根據工具回傳的數據準確回答使用者的問題。",
    "學術論文助手": "請以學術寫作風格回答，強調邏輯與證據。如果呼叫工具，請根據工具回傳的數據準確回答使用者的問題。",
    "中英翻譯官": "請將所有輸入內容翻譯成流暢的對應語言（中轉英或英轉中）。如果呼叫工具，請根據工具回傳的數據準確回答使用者的問題。"
}

# --- 主畫面 ---
current_session = st.session_state.current_session
st.title(f" {current_session}")

messages = st.session_state.chat_sessions[current_session]

# 顯示歷史訊息
chat_container = st.container()
with chat_container:
    for message in messages:
        if message["role"] == "tool" or message['content'] == None: continue
        with st.chat_message(message["role"]):
            content = message["content"]
            if isinstance(content, list):
                # 如果是 list (多模態)，取出文字並顯示圖片
                for item in content:
                    if item["type"] == "text":
                        st.markdown(item["text"])
                    elif item["type"] == "image_url":
                        st.image(item["image_url"]["url"], width=300)
            else:
                # 原本的純文字模式
                st.markdown(content)

with st.container():
    uploaded_file = st.file_uploader(
        "選擇圖片 (選填)", 
        type=["jpg", "jpeg", "png"], 
        key=f"image_uploader_{st.session_state.uploader_key}",
        label_visibility="collapsed"
    )
    
    # 原本的聊天輸入框
    prompt = st.chat_input("輸入訊息...")

# 處理輸入
if prompt:
    if not api_key:
        st.error("請輸入 API Key!")
    else:
        # 建立訊息內容結構
        content_payload = [{"type": "text", "text": prompt}]
        
        if uploaded_file:
            bytes_data = uploaded_file.getvalue()
            b64_str = base64.b64encode(bytes_data).decode('utf-8')
            image_url = f"data:{uploaded_file.type};base64,{b64_str}"
            
            content_payload.append({
                "type": "image_url",
                "image_url": {"url": image_url}
            })
            st.session_state.uploader_key += 1

        messages.append({"role": "user", "content": content_payload})

        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
                if uploaded_file:
                    st.image(image_url, width=300)

        client = Groq(api_key=api_key)
        
        target_model = get_best_model(prompt, model_option)

        # 根據模型決定參數
        params = {
            "model": target_model,
            "messages": [{"role": "system", "content": prompts[role_choice]}] + [m for m in messages],
            "temperature": temp_value,
            "top_p": 1.0,
            "stream": True,
        }

        if target_model == "groq/compound":
            params["max_completion_tokens"] = 4096
            params["compound_custom"] = {"tools": {"enabled_tools": ["web_search", "code_interpreter", "visit_website"]}}
        elif target_model == "qwen/qwen3-32b":
            params["tools"] = tools
            params["tool_choice"] = "auto"
            params["max_completion_tokens"] = 4096
        elif target_model == "llama-3.3-70b-versatile":
            params["tools"] = tools
            params["tool_choice"] = "auto"
            params["max_completion_tokens"] = 4096
        else:
            params["tools"] = tools
            params["tool_choice"] = "auto"
            params["max_completion_tokens"] = 4096

        with chat_container:
            with st.chat_message("assistant"):
                resp_place = st.empty()
                params_no_stream = params.copy()
                params_no_stream["stream"] = False

                try:
                    response = client.chat.completions.create(**params_no_stream)
                    msg = response.choices[0].message
                    
                    if msg.tool_calls:
                        messages.append({
                            "role": "assistant",
                            "content": msg.content,
                            "tool_calls": msg.tool_calls
                        })
                        # --- 執行工具邏輯 ---
                        for tool_call in msg.tool_calls:
                            func_name = tool_call.function.name
                            func_to_call = available_functions[func_name]
                            
                            tool_output = func_to_call()
                            
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": tool_output
                            })
                        
                        params_no_stream = params.copy()
                        params_no_stream["messages"] = [{"role": "system", "content": prompts[role_choice]}] + [m for m in messages]
                        params_no_stream["tool_choice"] = "none"
                        params_no_stream["stream"] = False

                        response = client.chat.completions.create(**params_no_stream)
                        msg = response.choices[0].message

                        full_res = msg.content
                        resp_place.markdown(full_res)
                        messages.append({"role": "assistant", "content": full_res})

                    else:
                        # --- 沒有工具呼叫，直接處理原本的串流 ---
                        full_res = msg.content
                        resp_place.markdown(full_res)
                        messages.append({"role": "assistant", "content": full_res})
                    
                    print(messages)

                    # 自動生成標題並更新 Session Name
                    if len(messages) >= 2 and current_session.startswith("新對話"):
                        new_title = generate_title(api_key, prompt)
                        # 避免標題重複
                        if new_title in st.session_state.chat_sessions:
                            new_title += f"_{len(st.session_state.chat_sessions)}"
                        
                        st.session_state.chat_sessions[new_title] = st.session_state.chat_sessions.pop(current_session)
                        st.session_state.current_session = new_title
                    else:
                        st.session_state.chat_sessions[current_session] = messages
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"發生錯誤：{e}")
                    assert False