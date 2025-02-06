import streamlit as st
import multi_agent_lib as ma

st.set_page_config(page_title="뉴스 분석 시스템")
st.title("뉴스 분석 시스템")

news = st.text_area("뉴스 기사를 입력하세요:", height=200)

if st.button("분석 시작"):
    with st.spinner("뉴스 분석 중..."):
        st.subheader("뉴스 요약")
        summary = ma.summarize_news(news)
        st.write(summary)

        st.subheader("감성 분석 결과")
        sentiment = ma.analyze_sentiment(summary)
        st.write(sentiment)

        topic = ma.classify_topic(summary)
        st.subheader("주제 분류 결과")
        topic = ma.classify_topic(summary)
        st.write(topic)
