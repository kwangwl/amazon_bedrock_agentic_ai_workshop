import streamlit as st
import pandas as pd
import uuid
import json
import plotly.graph_objects as go
import re
from amazon.bedrock import BedrockRuntime
import boto3

# config
FINANCIAL_ANALYST_PROMPT_ID = ""
FINANCIAL_ANALYST_REFLECTION_PROMPT_ID = ""

def analyze_finances(user_input):
    financial_analysis = invoke_model(FINANCIAL_ANALYST_PROMPT_ID, json.dumps(user_input))
    reflection_result = invoke_model(FINANCIAL_ANALYST_REFLECTION_PROMPT_ID, financial_analysis)
    return json.loads(financial_analysis), reflection_result

def display_financial_analysis(analysis_container, analysis):
    analysis_container.markdown("## 재무 분석 결과")
    analysis_container.json(analysis)

def display_reflection_result(reflection_container, result):
    reflection_container.markdown("## 검증 결과")
    if result.strip().lower() == "yes":
        reflection_container.success("분석 결과가 적절합니다.")
    else:
        reflection_container.error(f"분석 결과에 문제가 있습니다: {result}")

# main page
st.set_page_config(page_title="재무 분석가")

st.title("AI 재무 분석가")

# User input form
with st.form("finance_form"):
    total_investable_amount = st.number_input("총 투자 가능 금액 (원)", min_value=0, step=1000000)
    age = st.number_input("나이", min_value=0, max_value=120, step=1)
    stock_investment_experience_years = st.number_input("주식 투자 경험 (년)", min_value=0, step=1)
    target_amount = st.number_input("1년 후 목표 금액 (원)", min_value=0, step=1000000)
    
    submit_button = st.form_submit_button("분석 시작")

if submit_button:
    user_input = {
        "total_investable_amount": total_investable_amount,
        "age": age,
        "stock_investment_experience_years": stock_investment_experience_years,
        "target_amount": target_amount
    }
    
    with st.spinner("재무 분석 중..."):
        analysis, reflection = analyze_finances(user_input)
        
        analysis_container = st.container()
        display_financial_analysis(analysis_container, analysis)
        
        reflection_container = st.container()
        display_reflection_result(reflection_container, reflection)
