import streamlit as st
import random

Liu_he_map = {
    "子丑": "土", "土": "子丑",
    "寅亥": "木", "木": "寅亥",
    "卯戌": "火", "火": "卯戌",
    "辰酉": "金", "金": "辰酉",
    "巳申": "水", "水": "巳申",
    "午未": "土火", "土火": "午未"
}

Liu_he = [{"prompt": k, "target": v} for k, v in Liu_he_map.items()]

Liu_chong_map = {
    "子": "午", "午": "子",
    "丑": "未", "未": "丑",
    "寅": "申", "申": "寅",
    "卯": "酉", "酉": "卯",
    "辰": "戌", "戌": "辰",
    "巳": "亥", "亥": "巳"
}

Liu_chong = [{"prompt": k, "target": v} for k, v in Liu_chong_map.items()]

Liu_hai_map = {
    "卯":"辰","辰":"卯",
    "寅":"巳","巳":"寅",
    "丑":"午","午":"丑",
    "子":"未","未":"子",
    "亥":"申","申":"亥",
    "戌":"酉","酉":"戌"
}

Liu_hai = [{"prompt":k, "target":v} for k, v in Liu_hai_map.items()]

Liu_po_map = {
    "子": "酉","酉": "子",
    "午": "卯","卯": "午",
    "巳": "申","申": "巳",
    "寅": "亥","亥": "寅",
    "辰": "丑","丑": "辰",
    "戌": "未","未": "戌"
}

Liu_po = [{"prompt":k, "target":v} for k, v in Liu_po_map.items()]

San_he_map = {
    "水": "申子辰", "申子辰": "水",
    "木": "亥卯未", "亥卯未": "木",
    "火": "寅午戌", "寅午戌": "火",
    "金": "巳酉丑", "巳酉丑": "金"
}

San_he = [{"prompt":k, "target":v} for k, v in San_he_map.items()]

Xiang_xing = [
    {"prompt": "子", "target": "卯"},
    {"prompt": "卯", "target": "子"},
    {"prompt": "寅", "target": "申巳"},
    {"prompt": "巳", "target": "寅申"},
    {"prompt": "申", "target": "寅巳"},
    {"prompt": "丑", "target": "戌未"},
    {"prompt": "戌", "target": "丑未"},
    {"prompt": "未", "target": "丑戌"},
    {"prompt": "辰", "target": "辰"},
    {"prompt": "午", "target": "午"},
    {"prompt": "酉", "target": "酉"},
    {"prompt": "亥", "target": "亥"}
]

DATA_PACK = {
    "六冲": Liu_chong, 
    "六合": Liu_he, 
    "六害": Liu_hai, 
    "六破": Liu_po, 
    "相刑": Xiang_xing, 
    "三合": San_he
}

if 'initialized' not in st.session_state:
    #1. 大关卡的随机顺序
    #获取所有关卡的名字
    all_phase = list(DATA_PACK.keys())
    #顺序打乱
    random.shuffle(all_phase)
    #将打乱后的关卡顺序存入名叫"phase order"的容器里
    st.session_state.phase_order = all_phase
    #为打关卡的顺序做索引
    st.session_state.phase_idx = 0

    #2. 开始当前关卡的建立
    #从all_phase的列表中提取第一个作为第一关
    current_phase = all_phase[0]
    #取出问题，并将顺序打乱
    st.session_state.questions = random.sample(DATA_PACK[current_phase], len(DATA_PACK[current_phase]))
    st.session_state.submitted = False
    #建立随机种子，让浏览器无法提示输入
    st.session_state.random_seed = random.randint(1, 9999)

    #给initialized赋值，下次无需再循环网页建立过程
    st.session_state.initialized = True
    #设置结尾选项
    st.session_state.is_finished = False

def next_phase():
    #进入下一轮，将phase索引+1
    st.session_state.phase_idx += 1
    #确定结束点
    if st.session_state.phase_idx >= len(st.session_state.phase_order):
        st.session_state.is_finished = True
    #如果没有结束，则将字典取出进行题目排列
    else:
        new_p = st.session_state.phase_order[st.session_state.phase_idx]
        st.session_state.questions = random.sample(DATA_PACK[new_p], len(DATA_PACK[new_p]))
        st.session_state.random_seed = random.randint(1, 9999)

st.set_page_config(page_title="地支练习", layout="centered")
st.title("地支合冲")

if st.session_state.is_finished:
    st.balloons()
    st.success("已完成")
    if st.button("重新开始"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
else:
    current_phase_name = st.session_state.phase_order[st.session_state.phase_idx]

    col_a, col_b = st.columns([3,1])
    col_a.subheader(f"当前阶段：{current_phase_name}")
    col_b.write(f"进度：{st.session_state.phase_idx + 1} / {len(st.session_state.phase_order)}")

    with st.form(key = f"form_{current_phase_name}_{st.session_state.phase_idx}"):
        st.info("填写完毕后，点击提交批改")
        user_answer = []

        for i, q in enumerate(st.session_state.questions):
            q_col, a_col = st.columns([2,3])
            q_col.markdown(f"**{i+1}.** {q["prompt"]}")

            ans = a_col.text_input(
                "请输入",
                key = f"input_{i}_{st.session_state.random_seed}",
                label_visibility = "collapsed",
                placeholder="在此输入"
            )
            user_answer.append(ans.strip())
        
        submit_button = st.form_submit_button(label="提交")

    if submit_button or st.session_state.get("all_passed", False):
        all_correct = True
        results_container = st.container()
        with results_container:
            st.markdown("---")
            st.write("### 结果: ")

            for i, (u_ans, q_obj) in enumerate(zip(user_answer, st.session_state.questions)):
                if u_ans == q_obj["target"]:
                    st.write(f"第{i+1}题：✅️ 正确")
                else:
                    all_correct = False
                    st.error(f"第{i+1}题：❌️ 错误，你的回答：{u_ans if u_ans else '空'}")
                    st.caption(f"{q_obj['prompt']}正确答案为：{q_obj["target"]}")
            
            if all_correct:
                st.success("本轮全部正确")
                if st.button("进入下一轮", on_click=next_phase):
                    st.rerun()
            else:
                st.warning("请修改后再次提交")
