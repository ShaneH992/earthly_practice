#version v2.2
#修改在输入时因为字符顺序而导致的批改错误
#version v3
#将地支数据库使用外在csv文件作为导入使用

import streamlit as st
import random
import pandas as pd
from collections import defaultdict

#-> dict表示该函数会返回一个字典，但是如果最后返回的不是字典，程序也不会报错
def load_dizhi_data(filepath:str) -> dict:
    df = pd.read_csv(filepath, encoding="utf-8-sig")
    pack = defaultdict(list)
    no_reverse = {"十灵日", "五行长生", "乾造十神亲", "十二长生"}

    for _, row in df.iterrows():
        p, t, rel = row["prompt"], row["target"], row["relation_type"]
        pack[rel].append({"prompt": p, "target": t})
        if p != t and rel not in no_reverse:
            pack[rel].append({"prompt":t, "target":p})
        
    return dict(pack)

DATA_PACK = load_dizhi_data("dz_data.csv")

def next_phase():
    #进入下一轮，将phase索引+1
    st.session_state.phase_idx += 1
    #确定结束点
    if st.session_state.phase_idx >= len(st.session_state.phase_order):
        st.session_state.is_finished = True
    #如果没有结束，则将字典取出进行题目排列
    else:
        #这是确定一个新的phase，因为之前index已经+1变到了下一轮
        new_p = st.session_state.phase_order[st.session_state.phase_idx]
        st.session_state.questions = random.sample(DATA_PACK[new_p], len(DATA_PACK[new_p]))
        st.session_state.random_seed = random.randint(1, 9999)


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

st.set_page_config(page_title="地支练习", layout="centered")
st.title("地支合冲")

if st.session_state.is_finished:
    st.balloons()
    st.success("已完成")
    if st.button("重新开始"):
        #st keys()是为了获取当前所有的标签名，如phase order, phase idx, questions等
        #转换成一个列表
        #然后删除
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
else:
    current_phase_name = st.session_state.phase_order[st.session_state.phase_idx]

    col_a, col_b = st.columns([2,1])
    col_a.subheader(f"当前阶段：{current_phase_name}")
    col_b.markdown(f"### 进度：{st.session_state.phase_idx + 1} / {len(st.session_state.phase_order)}")

    with st.form(key = f"form_{current_phase_name}_{st.session_state.phase_idx}"):
        st.info("填写完毕后，点击提交批改")
        user_answer = []

        for i, q in enumerate(st.session_state.questions):
            q_col, a_col = st.columns([2,3])
            q_col.markdown(f"**{i+1}.** {q["prompt"]}")

            ans = a_col.text_input(
                "请输入",
                #用key来保障输入的唯一性，否则streamlit会报错
                key = f"input_{i}_{st.session_state.random_seed}",
                label_visibility = "collapsed",
                placeholder="在此输入"
            )
            #strip()用来去除不小心打的空格
            user_answer.append(ans.strip())
        
        submit_button = st.form_submit_button(label="提交")

    if submit_button or st.session_state.get("all_passed", False):
        all_correct = True
        results_container = st.container()
        with results_container:
            st.markdown("---")
            st.write("### 结果: ")

            for i, (u_ans, q_obj) in enumerate(zip(user_answer, st.session_state.questions)):
                #v2_2版本修改，对输入的数据做set处理，不用再在意输入的顺序
                if sorted(list(u_ans)) == sorted(list(q_obj["target"])):
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
