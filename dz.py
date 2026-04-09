import streamlit as st
import random

Liu_he_map = {
    "子丑": "合土", "合土": "子丑",
    "寅亥": "合木", "合木": "寅亥",
    "卯戌": "合火", "合火": "卯戌",
    "辰酉": "合金", "合金": "辰酉",
    "巳申": "合水", "合水": "巳申",
    "午未": "合土火", "合土火": "午未"
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
    "水局": "申子辰", "申子辰": "水局",
    "木局": "亥卯未", "亥卯未": "木局",
    "火局": "寅午戌", "寅午戌": "火局",
    "金局": "巳酉丑", "巳酉丑": "金局"
}

San_he = [{"prompt":k, "target":v} for k, v in San_he_map.items()]

Xiang_xing = [
    {"prompt": "子", "target": "卯"},
    {"prompt": "卯", "target": "子"},
    {"prompt": "寅", "target": "巳申"},
    {"prompt": "巳", "target": "申寅"},
    {"prompt": "申", "target": "寅巳"},
    {"prompt": "丑", "target": "戌未"},
    {"prompt": "戌", "target": "未丑"},
    {"prompt": "未", "target": "丑戌"},
    {"prompt": "辰", "target": "辰"},
    {"prompt": "午", "target": "午"},
    {"prompt": "酉", "target": "酉"},
    {"prompt": "亥", "target": "亥"}
]

DATA_PACK = {
    "Liu_chong":Liu_chong, 
    "Liu_he": Liu_he, 
    "Liu_hai": Liu_hai, 
    "Liu_po": Liu_po, 
    "Xiang_xing": Xiang_xing, 
    "San_he": San_he
}

if 'initialized' not in st.session_state:
    all_phase = list(DATA_PACK.keys())
    random.shuffle(all_phase)
    st.session_state.phase_order = all_phase
    st.session_state.phase_idx = 0
    current_phase = all_phase[0]
    st.session_state.questions = random.sample(DATA_PACK[current_phase], len(DATA_PACK[current_phase]))
    st.session_state.submitted = False
    st.session_state.random_seed = random.randint(1, 9999)
    st.session_state.initialized = True
    st.session_state.is_finished = False

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

        if submit_button:
            st.session_state.submitted = True
            all_correct = True

            st.markdown("---")
            st.write("### 结果: ")

            for i, (u_ans, q_obj) in enumerate(zip(user_answer, st.session_state.questions)):
                if u_ans == q_obj["target"]:
                    st.write(f"第{i+1}题： ✅️ 正确")
                else:
                    all_correct = False
                    st.error(f"第{i+1}题错误，{q_obj['prompt']}正确答案为：{q_obj["target"]}")
            
            if all_correct:
                st.success("本轮全部正确")
                if st.button("进入下一轮"):
                    st.session_state.phase_idx += 1
                    if st.session_state.phase_idx >= len(st.session_state.phase_order):
                        st.session_state.is_finished = True
                    else:
                        new_p = st.session_state.phase_order[st.session_state.phase_idx]
                        st.session_state.questions = random.sample(DATA_PACK[new_p], len(DATA_PACK[new_p]))
                    st.rerun()
            else:
                st.warning("请修改后再次提交")