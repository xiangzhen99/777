import streamlit as st

st.set_page_config(
    page_title='学生成绩分析与预测系统',
    page_icon='🎓',
    layout="wide"  
)

st.title("🎓学生成绩分析与预测系统")
st.subheader("📝项目概述")
st.write("本项目是一个基于Streamlit的学生成绩分析平台，通过数据可视化和机器学习技术，帮助教育工作者和学生深入了解学业表现，并预测期末考试成绩。")

st.markdown("---")
st.header("主要特点：")
st.markdown("""
- 📊 数据可视化：多维度展示学生学业数据
- 🥇 专业分析：按专业分类的详细统计分析
- 📱 智能预测：基于机器学习模型的成绩预测
- 💡 学习建议：根据预测结果提供个性化反馈
""")
st.image("https://github.com/xiangzhen99/777/raw/main/2.png", caption="成绩数据分析可视化",  use_container_width=True)

st.markdown("---")
st.header("🚩项目目标")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("#### 🎯 目标一")
    st.write("分析影响因素")
    st.markdown("""
    - 识别关键学习指标
    - 探索成绩相关因素
    - 提供数据支持决策
    """)

with col2:
    st.markdown("#### 🙈 目标二")
    st.write("可视化展示")
    st.markdown("""
    - 专业对比分析
    - 性别差异研究
    - 学习模式识别
    """)

with col3:
    st.markdown("#### 💯 目标三")
    st.write("成绩预测")
    st.markdown("""
    - 机器学习模型
    - 个性化预测
    - 及时干预预警
    """)

st.markdown("---")
st.header("👩🏻‍💻技术架构")

a, b, c, d = st.columns(4)

with a:
    st.write("前端框架")
    st.info("Streamlit", icon="🌐")  # 用原生信息框

with b:
    st.write("数据处理")
    st.info("Pandas\\NumPy", icon="📊")  # 换行用\n

with c:
    st.write("可视化")
    st.info("plotly\\Matplotlib", icon="📈")

with d:
    st.write("机器学习")
    st.info("Scikit-learn", icon="🤖")

