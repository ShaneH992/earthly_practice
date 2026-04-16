#v3.1，代码优化

import streamlit as st
import random
import pandas as pd
from collections import defaultdict

#现将无需正反向的项先拉出来
#大写变量约定俗成是不会变更的变量，python看来无所谓而已
NO_REVERSE = {"十灵日", "五行长生", "乾造十神亲", "十二长生"}

#csv读取函数
def load_csv_file(filepath: str) -> dict:
    df = pd.read_csv(filepath, encoding="utf-8-sig")
    #使用defaultdict来创建字典类，defaultdict(list)默认值为[]
    #访问不存在的键时，自动创建默认值，而不是抛出KeyError
    pack = defaultdict(list)
    for _, row in df.iterrows():
        p, t, rel = row["prompt"], row["target"], row["relation_type"]
        pack[rel].append({"prompt": p, "target": t})
        if p != t and rel not in NO_REVERSE:
            pack[rel].append({"prompt": t, "target": p})
    #再将defaultdict转换为普通字典，这样防止以后有额外错误信息录入
    return dict(pack)

DATA_PACK = load_csv_file("dz_data.csv")

#将DATA_PACK中因键值而读取的数据进行随机打乱顺序
def shuffle_questions(phase: str) -> list:
    return random.sample(DATA_PACK[phase], len(DATA_PACK[phase]))

#关于阶段性变幻
def next_phase():
    st.session_state.phase_idx += 1
    if st.session_state.phase_idx >= len(st.session_state.phase_order):
        st.session_state.is_finished = True
    else:
        phase = st.session_state.phase_order[st.session_state.phase_idx]
        st.session_state.questions = shuffle_questions(phase)
        st.session_state.random_seed = random.randint(1, 9999)

#session_state初始化
if "initialized" not in st.session_state:
    #将所有的relation_type提出来作为每个phase的名称
    all_phases = list(DATA_PACK.keys())
    #打乱顺序
    random.shuffle(all_phases)
    #因为st.session_state本质上是一个类字典对象
    #使用python自有函数.update来统一更新，而非一行行的来写
    #update会覆盖已有值
    st.session_state.update(
        #将所有阶段作为session_state的一份子
        phase_order = all_phases,
        phase_idx = 0,
        questions = shuffle_questions(all_phases[0]),
        random_seed = random.randint(1, 9999),
        is_finished = False,
        initialized = True,
    )

st.set_page_config(page_title="Practice", layout="centered")
st.title("Earthly Branches")

if st.session_state.is_finished:
    st.balloons()
    st.success("Done all practices")
    if st.button("Restart"):
        #删除所有键值，然后重启程序
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
    st.stop()

#这里不需要else，没有其他状态需要分割
phase_name = st.session_state.phase_order[st.session_state.phase_idx]
col_a, col_b = st.columns([2, 1])
col_a.subheader(f"Current stage: {phase_name}")
col_b.markdown(f"### Process: {st.session_state.phase_idx + 1} / {len(st.session_state.phase_order)}")

# 使用表格的形式将内容规范起来一起批改，而非单次
with st.form(key=f"form_{phase_name}_{st.session_state.phase_idx}"):
    st.info("Submit after finished")
    user_answer = []
    for i, q in enumerate(st.session_state.questions):
        q_col, a_col = st.columns([2, 3])
        q_col.markdown(f"**{i+1}.** {q['prompt']}")
        ans = a_col.text_input(
            "Please input your answer",
            key=f"input_{i}_{st.session_state.random_seed}",
            label_visibility="collapsed",
            placeholder="Input here",
        )
        user_answer.append(ans.strip())
    submitted = st.form_submit_button("Submit")

if submitted:
    with st.sidebar:
        st.write("### Results: ")
        wrongs = []
        for i, (ans, q) in enumerate(zip(user_answer, st.session_state.questions)):
            if "target" not in q:
                st.error(f"{q}")
                continue

            if sorted(list(ans)) == sorted(list(q["target"])):
                st.write(f"No.{i+1} is ✅ correct!")
            else:
                wrongs.append(i)
                st.error(f"No.{i+1} is ❌ wrong, your answer is {ans or 'Void'}")
                st.caption(f"The correct answer of {q['prompt']} is {q['target']}")
        st.markdown("---")
        if not wrongs:
            st.success("All correct!")
            st.button("Next phase", on_click=next_phase)
        else:
            st.warning("Please correct your answer.")
