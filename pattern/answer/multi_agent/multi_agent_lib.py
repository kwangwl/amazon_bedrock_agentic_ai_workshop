import boto3

def get_bedrock_response(prompt, model_id):
    session = boto3.Session()
    bedrock = session.client(service_name='bedrock-runtime')

    response = bedrock.converse(
        modelId=model_id,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": 2000, "temperature": 0.0}
    )

    return response['output']['message']['content'][0]['text']

def summarize_news(news):
    prompt = f"다음 뉴스를 1문장으로 요약해주세요:\n\n{news}"
    return get_bedrock_response(prompt, "anthropic.claude-3-5-haiku-20241022-v1:0")

def analyze_sentiment(summary):
    prompt = f"다음 뉴스 요약의 감성을 분석하여 '긍정적', '중립적', '부정적' 중 하나로 평가해주세요:\n\n{summary}"
    return get_bedrock_response(prompt, "anthropic.claude-3-5-haiku-20241022-v1:0")

def classify_topic(summary):
    prompt = f"다음 뉴스 요약의 주제를 '정치', '경제', '사회', '기술', '문화' 중 하나로 분류해주세요:\n\n{summary}"
    return get_bedrock_response(prompt, "anthropic.claude-3-5-haiku-20241022-v1:0")