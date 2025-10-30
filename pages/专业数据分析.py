import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ----------------------1. 页面配置与数据加载----------------------
st.set_page_config(
    page_title="专业数据分析仪表盘",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 数据集路径
DATA_PATH = "student_data_adjusted_rounded.csv"

# 加载并缓存数据集
@st.cache_data
def load_data():
    if not os.path.exists(DATA_PATH):
        st.error(f"请将数据集 {DATA_PATH} 放在代码同一目录！")
        st.stop()
    return pd.read_csv(DATA_PATH)

df = load_data()

# 深色主题样式
st.markdown(
    """
    <style>
    .stApp {{ background-color: #121212; color: #ffffff; }}
    .stTable, .stPlotlyChart {{ background-color: #1e1e1e; }}
    .stHeader {{ color: #ffffff; }}
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------------2. 专业数据分析核心函数----------------------
def analyze_major_data():
    st.title("📊 专业数据分析仪表盘")

    # （1）各专业核心指标统计表格
    st.header("1. 各专业核心指标对比")
    stats_df = df.groupby("专业").agg({
        "每周学习时长（小时）": "mean",
        "期中考试分数": "mean",
        "期末考试分数": "mean"
    }).reset_index().round(2)
    stats_df.columns = ["专业", "每周平均学时", "期中平均分", "期末平均分"]
    st.table(stats_df)

    # （2）各专业男女性别比例（双层柱状图 + 数据明细）
    st.header("2. 各专业男女性别比例")
    gender_df = df.groupby(["专业", "性别"])["学号"].count().reset_index(name="人数")
    fig_gender = px.histogram(
        gender_df,
        x="专业",
        y="人数",
        color="性别",
        barmode="group",
        title="各专业男女性别人数分布",
        color_discrete_map={"男": "#636efa", "女": "#00bfa5"},
        template="plotly_dark"
    )
    fig_gender.update_layout(plot_bgcolor="#1e1e1e", paper_bgcolor="#1e1e1e")
    col_chart, col_table = st.columns([2, 1])
    with col_chart:
        st.plotly_chart(fig_gender, use_container_width=True)
    with col_table:
        gender_pivot = gender_df.pivot(index="专业", columns="性别", values="人数").fillna(0).astype(int)
        st.table(gender_pivot)

    # （3）各专业学习指标对比（背景填充折线图 + 数据明细）
    st.header("3. 各专业学习指标对比")
    指标_df = df.groupby("专业").agg({
        "每周学习时长（小时）": "mean",
        "期中考试分数": "mean",
        "期末考试分数": "mean"
    }).reset_index().round(2)
    # 重命名列以匹配需求
    指标_df.columns = ["专业", "每周平均学时", "期中平均分", "期末平均分"]
    
    fig_指标 = go.Figure()
    # 学习时长（左轴，背景填充 + 柱状图样式）
    fig_指标.add_trace(go.Bar(
        x=指标_df["专业"], 
        y=指标_df["每周平均学时"], 
        name="平均学习时间", 
        marker_color="#00bfa5",
        yaxis="y"
    ))
    # 期中成绩（右轴，折线）
    fig_指标.add_trace(go.Scatter(
        x=指标_df["专业"], 
        y=指标_df["期中平均分"], 
        name="平均期中成绩", 
        mode="lines+markers",
        line=dict(color="#ffc107"),
        yaxis="y2"
    ))
    # 期末成绩（右轴，折线）
    fig_指标.add_trace(go.Scatter(
        x=指标_df["专业"], 
        y=指标_df["期末平均分"], 
        name="平均期末成绩", 
        mode="lines+markers",
        line=dict(color="#2ca02c"),
        yaxis="y2"
    ))
    # 布局设置
    fig_指标.update_layout(
        title="各专业平均学习时间与成绩对比",
        xaxis_title="专业",
        yaxis=dict(
            title="平均学习时间（小时）",
            side="left",
            range=[0, 指标_df["每周平均学时"].max() + 5]
        ),
        yaxis2=dict(
            title="平均分数",
            side="right",
            range=[0, 100],
            overlaying="y"
        ),
        plot_bgcolor="#1e1e1e",
        paper_bgcolor="#1e1e1e",
        template="plotly_dark",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    # 分栏展示图表和数据
    col_chart, col_table = st.columns([2, 1])
    with col_chart:
        st.plotly_chart(fig_指标, use_container_width=True)
    with col_table:
        st.table(指标_df.rename(columns={
            "每周平均学时": "study_hours",
            "期中平均分": "midterm_score",
            "期末平均分": "final_score"
        }))

    # （4）各专业平均出勤率（柱状图 + 排名表）
    st.header("4. 各专业上课出勤率分析")
    attendance_df = df.groupby("专业")["上课出勤率"].mean().reset_index()
    attendance_df["出勤率（%）"] = (attendance_df["上课出勤率"] * 100).round(2)
    fig_attendance = px.bar(
        attendance_df,
        x="专业",
        y="出勤率（%）",
        title="各专业平均上课出勤率",
        color="出勤率（%）",
        color_continuous_scale="Viridis",
        template="plotly_dark"
    )
    fig_attendance.update_layout(plot_bgcolor="#1e1e1e", paper_bgcolor="#1e1e1e")
    col_chart, col_table = st.columns([2, 1])
    with col_chart:
        st.plotly_chart(fig_attendance, use_container_width=True)
    with col_table:
        attendance_rank = attendance_df.sort_values("出勤率（%）", ascending=False).reset_index(drop=True)
        attendance_rank.index += 1  # 排名从1开始
        st.table(attendance_rank[["专业", "出勤率（%）"]].rename(columns={"index": "排名"}))

    # （5）大数据管理专业专项分析
    st.header("5. 大数据管理专业深度分析")
    if "大数据管理" in df["专业"].unique():
        bdm_df = df[df["专业"] == "大数据管理"]
        bdm_attendance = bdm_df["上课出勤率"].mean() * 100
        bdm_mid = bdm_df["期中考试分数"].mean()
        bdm_final = bdm_df["期末考试分数"].mean()
        bdm_hours = bdm_df["每周学习时长（小时）"].mean()

        # 关键指标卡片
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("平均出勤率", f"{bdm_attendance:.1f}%")
        with col2:
            st.metric("期中平均分", f"{bdm_mid:.1f}分")
        with col3:
            st.metric("期末平均分", f"{bdm_final:.1f}分")
        with col4:
            st.metric("每周平均学时", f"{bdm_hours:.1f}小时")

        # 成绩分布与学习时长分布
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            fig_grade_dist = px.histogram(
                bdm_df,
                x="期末考试分数",
                title="大数据管理专业期末成绩分布",
                nbins=8,
                template="plotly_dark"
            )
            fig_grade_dist.update_layout(plot_bgcolor="#1e1e1e", paper_bgcolor="#1e1e1e")
            st.plotly_chart(fig_grade_dist, use_container_width=True)
        with col_chart2:
            fig_hours_box = px.box(
                bdm_df,
                y="每周学习时长（小时）",
                title="大数据管理专业学习时长分布",
                template="plotly_dark"
            )
            fig_hours_box.update_layout(plot_bgcolor="#1e1e1e", paper_bgcolor="#1e1e1e")
            st.plotly_chart(fig_hours_box, use_container_width=True)
    else:
        st.warning("数据集中未包含“大数据管理”专业，该模块已隐藏。")

# ----------------------3. 主程序入口----------------------
if __name__ == "__main__":
    analyze_major_data()
