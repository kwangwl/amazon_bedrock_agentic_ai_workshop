import portfolio_architect_lib as plib
import json
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import os
import uuid


# config
PORTFOLIO_ARCHITECT_AGENT_ID = ""
PORTFOLIO_ARCHITECT_AGENT_ALIAS_ID = ""


def display_available_products(trace_container, trace):
    """사용 가능한 투자 상품 목록을 테이블 형태로 표시"""
    # JSON 데이터 파싱
    products_text = trace.get('observation', {}).get('actionGroupInvocationOutput', {}).get('text')
    products = json.loads(products_text)

    # DataFrame 생성
    df = pd.DataFrame(
        [[ticker, desc] for ticker, desc in products.items()],
        columns=['티커', '설명']
    )

    # 결과 표시
    trace_container.markdown(f"**사용 가능한 투자 상품**")
    trace_container.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "티커": st.column_config.TextColumn(width="small"),
            "설명": st.column_config.TextColumn(width="large")
        }
    )


def display_product_data(trace_container, trace):
    """투자 상품의 가격 데이터를 차트로 표시"""
    # JSON 데이터 파싱
    data_text = trace.get('observation', {}).get('actionGroupInvocationOutput', {}).get('text')
    data = json.loads(data_text)

    # 각 상품별로 차트 생성
    for ticker, prices in data.items():
        # DataFrame 생성
        df = pd.DataFrame.from_dict(prices, orient='index', columns=['Price'])
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()

        # 차트 생성
        fig = go.Figure()

        # 가격 선 추가
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['Price'],
                mode='lines',
                name=ticker,
                line=dict(width=2)
            )
        )

        # 차트 레이아웃 설정
        fig.update_layout(
            title=f"{ticker} 가격 추이",
            xaxis_title="날짜",
            yaxis_title="가격 ($)",
            height=400,
            showlegend=True,
            hovermode='x unified'
        )

        # 차트 표시
        trace_container.plotly_chart(fig, use_container_width=True)


def create_pie_chart(data, chart_title=""):
    """파이 차트 생성 함수"""
    fig = go.Figure(data=[go.Pie(
        labels=list(data.keys()),
        values=list(data.values()),
        hole=.3,
        textinfo='label+percent',
        marker=dict(colors=px.colors.qualitative.Set3)
    )])

    fig.update_layout(
        title=chart_title,
        showlegend=True,
        width=400,
        height=400
    )
    return fig


def display_portfolio_suggestion(place_holder, input_content):
    """포트폴리오 제안 결과 표시 함수"""
    data = json.loads(input_content, strict=False)
    sub_col1, sub_col2 = place_holder.columns([1, 1])

    with sub_col1:
        st.markdown("**포트폴리오**")
        # 파이 차트로 포트폴리오 배분 표시
        fig = create_pie_chart(
            data["portfolio_allocation"],
            "포트폴리오 자산 배분"
        )
        st.plotly_chart(fig)

    with sub_col2:
        st.markdown("**투자 전략**")
        st.info(data["strategy"])

    place_holder.markdown("**상세 근거**")
    place_holder.write(data["reason"])


# Page setup
st.set_page_config(page_title="Portfolio Architect")

st.title("🤖 Portfolio Architect")

with st.expander("아키텍처", expanded=True):
    st.image(os.path.join("../dataset/images/portfolio_architect.png"))

# Input form
st.markdown("**📊 재무 분석 결과 **")
input_text = st.text_input(label="asdf")

submitted = st.button("분석 시작", use_container_width=True)

if submitted:
    # 답변 출력
    st.divider()
    placeholder = st.container()

    with st.spinner("AI가 분석 중입니다..."):
        response = plib.get_agent_response(
            PORTFOLIO_ARCHITECT_AGENT_ID,
            PORTFOLIO_ARCHITECT_AGENT_ALIAS_ID,
            str(uuid.uuid4()),
            input_text
        )

        placeholder.subheader("Bedrock Reasoning")

        output_text = ""
        function_name = ""

        for event in response.get("completion"):
            if "chunk" in event:
                chunk = event["chunk"]
                output_text += chunk["bytes"].decode()

            if "trace" in event:
                each_trace = event["trace"]["trace"]

                if "orchestrationTrace" in each_trace:
                    trace = event["trace"]["trace"]["orchestrationTrace"]

                    if "rationale" in trace:
                        with placeholder.chat_message("ai"):
                            st.markdown(trace['rationale']['text'])

                    elif function_name != "":
                        if function_name == "get_available_products":
                            display_available_products(placeholder, trace)
                        elif function_name == "get_product_data":
                            display_product_data(placeholder, trace)

                        function_name = ""

                    else:
                        function_name = trace.get('invocationInput', {}).get('actionGroupInvocationInput', {}).get(
                            'function', "")

        placeholder.divider()
        placeholder.markdown(f"🤖 **Portfolio Architect**")
        placeholder.subheader(f"📌 포트폴리오 설계")
        display_portfolio_suggestion(placeholder, output_text)
