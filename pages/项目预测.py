import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.impute import SimpleImputer

# ----------------------1. 全局配置与初始化----------------------
st.set_page_config(
    page_title="期末成绩预测",
    page_icon=":book:",
    layout="wide"
)

# 定义文件路径
DATA_PATH = "student_data_adjusted_rounded.csv"  # 确保该文件与代码同目录
MODEL_PATH = "grade_rfr_model.pkl"
FEATURE_PATH = "grade_feature_names.pkl"

# 图片路径
CONGRATS_IMAGE_PATH = "images/congratulations.png"  # 庆祝图片（可选）

# ----------------------2. 数据预处理与模型训练工具函数----------------------
def preprocess_data(df):
    """数据预处理：处理缺失值、编码分类特征"""
    # 1. 确定特征列（严格与数据集列名匹配）
    num_features = ["每周学习时长（小时）", "上课出勤率", "期中考试分数", "作业完成率"]
    cat_features = ["性别", "专业"]
    target = "期末考试分数"

    # 2. 处理缺失值
    # 数值特征用中位数填充
    num_imputer = SimpleImputer(strategy="median")
    df[num_features] = num_imputer.fit_transform(df[num_features])

    # 分类特征用众数填充
    cat_imputer = SimpleImputer(strategy="most_frequent")
    df[cat_features] = cat_imputer.fit_transform(df[cat_features])

    # 3. 编码分类特征
    # 专业：One-Hot编码
    encoder_major = OneHotEncoder(sparse_output=False, drop="first")
    major_encoded = encoder_major.fit_transform(df[["专业"]])
    major_df = pd.DataFrame(
        major_encoded,
        columns=[f"专业_{cat}" for cat in encoder_major.categories_[0][1:]]
    )

    # 性别：Label编码
    encoder_sex = LabelEncoder()
    df["性别_编码"] = encoder_sex.fit_transform(df["性别"])

    # 4. 构建特征矩阵X和目标y
    X = pd.concat([
        df[num_features],
        major_df,
        df[["性别_编码"]]
    ], axis=1)
    y = df[target]

    # 定义特征名
    feature_names = num_features + list(major_df.columns) + ["性别_编码"]
    X.columns = feature_names

    # 返回预处理结果与编码器
    return X, y, feature_names, encoder_major, encoder_sex

def train_and_save_model():
    """训练并保存随机森林回归模型"""
    # 1. 加载数据集
    if not os.path.exists(DATA_PATH):
        st.error(f"请将{DATA_PATH}放在代码同一目录！")
        st.stop()
    df = pd.read_csv(DATA_PATH)

    # 2. 数据预处理
    X, y, feature_names, encoder_major, encoder_sex = preprocess_data(df)

    # 3. 划分训练集与测试集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 4. 训练模型
    rfr_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rfr_model.fit(X_train, y_train)

    # 5. 验证模型
    train_r2 = rfr_model.score(X_train, y_train)
    test_r2 = rfr_model.score(X_test, y_test)
    st.success(f"模型训练完成！训练R²：{train_r2:.2f}，测试R²：{test_r2:.2f}")

    # 6. 保存模型、特征名与编码器
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(rfr_model, f)
    with open(FEATURE_PATH, "wb") as f:
        pickle.dump(feature_names, f)
    # 保存编码器（用于后续用户输入处理）
    with open("encoder_major.pkl", "wb") as f:
        pickle.dump(encoder_major, f)
    with open("encoder_sex.pkl", "wb") as f:
        pickle.dump(encoder_sex, f)

    return rfr_model, feature_names, encoder_major, encoder_sex

def load_model_or_train():
    """加载模型，若不存在则训练"""
    if os.path.exists(MODEL_PATH) and os.path.exists(FEATURE_PATH) and os.path.exists("encoder_major.pkl") and os.path.exists("encoder_sex.pkl"):
        with open(MODEL_PATH, "rb") as f:
            rfr_model = pickle.load(f)
        with open(FEATURE_PATH, "rb") as f:
            feature_names = pickle.load(f)
        with open("encoder_major.pkl", "rb") as f:
            encoder_major = pickle.load(f)
        with open("encoder_sex.pkl", "rb") as f:
            encoder_sex = pickle.load(f)
        return rfr_model, feature_names, encoder_major, encoder_sex
    else:
        st.info("未检测到预训练模型，正在自动训练...")
        return train_and_save_model()

# ----------------------3. 用户输入处理函数----------------------
def process_user_input(sex, major, study_hours, attendance, midterm_score, homework_completion, feature_names, encoder_major, encoder_sex):
    """将用户输入转换为模型可接受的特征格式"""
    # 1. 编码专业（One-Hot）
    major_encoded = encoder_major.transform([[major]])
    major_df = pd.DataFrame(
        major_encoded,
        columns=[f"专业_{cat}" for cat in encoder_major.categories_[0][1:]]
    )

    # 2. 编码性别（Label）
    sex_encoded = encoder_sex.transform([sex])[0]

    # 3. 构建特征列表（严格匹配模型训练时的特征顺序）
    num_features = ["每周学习时长（小时）", "上课出勤率", "期中考试分数", "作业完成率"]
    input_data = [
        study_hours,          
        attendance,           
        midterm_score,        
        homework_completion,  
    ]
    input_data.extend(major_encoded[0])
    input_data.append(sex_encoded)

    # 4. 转换为DataFrame
    input_df = pd.DataFrame([input_data], columns=feature_names)
    return input_df

# ----------------------4. 页面内容与交互逻辑----------------------
def main():
    rfr_model, feature_names, encoder_major, encoder_sex = load_model_or_train()

    st.title("🎓 期末成绩预测")
    st.markdown("请输入学生的学习信息，系统将预测其期末成绩并提供学习建议")

    # 获取数据集中的所有专业类别（用于下拉框选项）
    df = pd.read_csv(DATA_PATH)
    major_options = df["专业"].unique().tolist()

    # 输入表单
    with st.form("student_info_form"):
        col1, col2 = st.columns(2)
        with col1:
            student_id = st.text_input("学号", "2023000001")
            sex = st.selectbox("性别", ["男", "女"])
            major = st.selectbox("专业", major_options)  # 动态匹配数据集的专业类别
        with col2:
            study_hours = st.number_input("每周学习时长（小时）", min_value=0.0, max_value=40.0, value=17.0)
            attendance = st.number_input("上课出勤率", min_value=0.0, max_value=1.0, value=0.98)
            midterm_score = st.number_input("期中考试分数", min_value=0.0, max_value=100.0, value=82.0)
            homework_completion = st.number_input("作业完成率", min_value=0.0, max_value=1.0, value=0.78)
        
        predict_button = st.form_submit_button("预测期末成绩", type="primary")

    # 预测结果展示
    if predict_button:
        input_df = process_user_input(sex, major, study_hours, attendance, midterm_score, homework_completion, feature_names, encoder_major, encoder_sex)
        predicted_grade = rfr_model.predict(input_df)[0]
        predicted_grade = round(predicted_grade, 1)

        st.success(f"🎉 预测期末成绩: {predicted_grade} 分")
        if os.path.exists(CONGRATS_IMAGE_PATH):
            st.image(CONGRATS_IMAGE_PATH, caption="Congratulations!")
        else:
            st.markdown("### Congratulations!")

        # 学习建议
        st.header("学习建议")
        if predicted_grade < 60:
            st.warning("建议增加学习时长，重点复习期中考试薄弱知识点，提高作业完成质量和上课出勤率。")
        elif 60 <= predicted_grade < 80:
            st.info("建议针对性巩固知识点，保持作业完成率，可适当增加学习时长冲刺更高分数。")
        else:
            st.success("继续保持当前学习状态，可针对性突破难点，向更高分冲刺！")

if __name__ == "__main__":
    main()

