import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os  # 新增：导入os模块

# ----------------------1. 全局配置与初始化----------------------
st.set_page_config(
    page_title="专业数据分析",
    page_icon=":chart_with_upwards_trend:",
    layout="wide"
)

# 定义文件路径
DATA_PATH = "student_data_adjusted_rounded.csv"

# 加载数据集
@st.cache_data
def load_dataset():
    if not os.path.exists(DATA_PATH):
        st.error(f"数据集文件 {DATA_PATH} 未找到，请放在代码同一目录！")
        st.stop()
    return pd.read_csv(DATA_PATH)

df = load_dataset()

# ----------------------2. 专业数据分析可视化函数----------------------
def show_data_analysis():
    """展示专业数据分析可视化内容"""
    st.title("📊 专业数据分析")
    
    # （1）各专业核心指标统计表格
    st.header("1. 各专业核心指标对比")
    stats_df = df.groupby("专业").agg({
        "每周学习时长（小时）": "mean",
        "期中考试分数": "mean",
        "期末考试分数": "mean"
    }).reset_index()
    stats_df.columns = ["专业", "每周平均学时", "期中考试平均分", "期末考试平均分"]
    st.table(stats_df.round(2))
    
    # （2）各专业男女性别比例（双层柱状图）
    st.header("2. 各专业男女性别分布")
    gender_df = df.groupby(["专业", "性别"])["学号"].count().reset_index(name="人数")
    fig_gender = px.histogram(
        gender_df,
        x="专业",
        y="人数",
        color="性别",
        barmode="group",
        title="各专业男女生人数分布",
        labels={"人数": "学生人数", "专业": "专业名称"},
        color_discrete_map={"男": "#1f77b4", "女": "#ff7f0e"}
    )
    st.plotly_chart(fig_gender, use_container_width=True)
    
    # （3）各专业期中与期末成绩对比（折线图）
    st.header("3. 各专业成绩趋势对比")
    score_df = df.groupby("专业").agg({
        "期中考试分数": "mean",
        "期末考试分数": "mean"
    }).reset_index()
    fig_score = go.Figure()
    fig_score.add_trace(go.Scatter(
        x=score_df["专业"], 
        y=score_df["期中考试分数"], 
        name="期中考试", 
        mode="lines+markers",
        line=dict(color="#2ca02c")
    ))
    fig_score.add_trace(go.Scatter(
        x=score_df["专业"], 
        y=score_df["期末考试分数"], 
        name="期末考试", 
        mode="lines+markers",
        line=dict(color="#d62728")
    ))
    fig_score.update_layout(
        title="各专业期中与期末平均分对比",
        xaxis_title="专业",
        yaxis_title="平均分",
        yaxis_range=[0, 100]
    )
    st.plotly_chart(fig_score, use_container_width=True)
    
    # （4）各专业平均上课出勤率（单层柱状图）
    st.header("4. 各专业平均上课出勤率")
    attendance_df = df.groupby("专业")["上课出勤率"].mean().reset_index()
    attendance_df["上课出勤率"] = attendance_df["上课出勤率"] * 100  # 转换为百分比
    fig_attendance = px.bar(
        attendance_df,
        x="专业",
        y="上课出勤率",
        title="各专业平均上课出勤率（%）",
        labels={"上课出勤率": "平均出勤率（%）", "专业": "专业名称"},
        color="上课出勤率",
        color_continuous_scale="Viridis"
    )
    st.plotly_chart(fig_attendance, use_container_width=True)
    
    # （5）大数据管理专业专项分析（若存在该专业）
    st.header("5. 大数据管理专业专项分析")
    if "大数据管理" in df["专业"].unique():
        bdm_df = df[df["专业"] == "大数据管理"]
        bdm_attendance = bdm_df["上课出勤率"].mean() * 100  # 百分比
        bdm_final = bdm_df["期末考试分数"].mean()
        
        fig_bdm = go.Figure()
        # 出勤率柱状图
        fig_bdm.add_trace(go.Bar(
            x=["大数据管理专业"],
            y=[bdm_attendance],
            name="平均上课出勤率（%）",
            yaxis="y",
            marker_color="#1f77b4"
        ))
        # 期末成绩折线图（右侧轴）
        fig_bdm.add_trace(go.Scatter(
            x=["大数据管理专业"],
            y=[bdm_final],
            name="期末平均分",
            yaxis="y2",
            mode="markers",
            marker=dict(size=15, color="#ff7f0e")
        ))
        fig_bdm.update_layout(
            title="大数据管理专业出勤率与期末成绩关系",
            yaxis=dict(title="平均上课出勤率（%）", range=[0, 100]),
            yaxis2=dict(title="期末平均分", overlaying="y", side="right", range=[0, 100])
        )
        st.plotly_chart(fig_bdm, use_container_width=True)
    else:
        st.warning("数据集中未找到'大数据管理'专业")

# ----------------------3. 主页面逻辑----------------------
def main():
    show_data_analysis()

# ----------------------4. 启动应用----------------------
if __name__ == "__main__":
    main()
