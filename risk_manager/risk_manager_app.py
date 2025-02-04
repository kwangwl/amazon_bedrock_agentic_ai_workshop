import risk_manager_lib as rlib
import json
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import os
import uuid

# Config
RISK_MANAGER_AGENT_ID = ""
RISK_MANAGER_AGENT_ALIAS_ID = ""

# Functions
def display_product_news(trace_container, trace):
    """Display news for investment products"""
    news_text = trace.get('observation', {}).get('actionGroupInvocationOutput', {}).get('text')
    news = json.loads(news_text)
    
    trace_container.markdown(f"**{news['ticker']} 관련 뉴스**")
    for item in news['news']:
        trace_container.markdown(f"**{item['title']}**")
        trace_container.markdown(f"*{item['publish_date']}*")
        trace_container.markdown(item['summary'])
        trace_container.markdown("---")

def display_market_data(trace_container, trace):
    """Display market data"""
    data_text = trace.get('observation', {}).get('actionGroupInvocationOutput', {}).get('text')
    data = json.loads(data_text)
    
    df = pd.DataFrame(
        [[key, value['description'], value['value']] for key, value in data.items()],
        columns=['지표', '설명', '값']
    )
    
    trace_container.markdown("**시장 지표**")
    trace_container.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "지표": st.column_config.TextColumn(width="medium"),
            "설명": st.column_config.TextColumn(width="large"),
            "값": st.column_config.NumberColumn(width="small")
        }
    )

def create_pie_chart(data, chart_title=""):
    """Create a pie chart for portfolio allocation"""
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

def display_risk_analysis(place_holder, input_content):
    """Display risk analysis results"""
    data = json.loads(input_content, strict=False)
    
    for scenario in ["scenario1", "scenario2"]:
        place_holder.subheader(f"시나리오: {data[scenario]['name']}")
        place_holder.markdown(data[scenario]['description'])
        
        sub_col1, sub_col2 = place_holder.columns([1, 1])
        
        with sub_col1:
            fig = create_pie_chart(
                data[scenario]["allocation_management"],
                "조정된 포트폴리오 자산 배분"
            )
            st.plotly_chart(fig)
        
        with sub_col2:
            st.markdown("**조정 이유 및 전략**")
            st.info(data[scenario]["reason"])
        
        place_holder.markdown("---")

# Page setup
st.set_page_config(page_title="Risk Manager")

st.title("🤖 Risk Manager")

with st.expander("아키텍처", expanded=True):
    st.image(os.path.join("../dataset/images/risk_manager.png"))

# Input form
st.markdown("**포트폴리오 구성 입력(🤖 Portfolio Architect)**")

portfolio_composition = st.text_area(
    "JSON 형식",
    height=200
)

submitted = st.button("분석 시작", use_container_width=True)

if submitted and portfolio_composition:
    st.divider()
    placeholder = st.container()
    
    with st.spinner("AI is processing..."):
        response = rlib.get_agent_response(
            RISK_MANAGER_AGENT_ID,
            RISK_MANAGER_AGENT_ALIAS_ID,
            str(uuid.uuid4()),
            portfolio_composition
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
                        if function_name == "get_product_news":
                            display_product_news(placeholder, trace)
                        elif function_name == "get_market_data":
                            display_market_data(placeholder, trace)
                        
                        function_name = ""
                    
                    else:
                        function_name = trace.get('invocationInput', {}).get('actionGroupInvocationInput', {}).get(
                            'function', "")
        
        placeholder.divider()
        placeholder.markdown("🤖 **Risk Manager**")
        placeholder.subheader("📌 리스크 분석")
        display_risk_analysis(placeholder, output_text)
