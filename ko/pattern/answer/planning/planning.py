import boto3
import json

def get_bedrock_response(prompt, model_id, tool_config):
    session = boto3.Session()
    bedrock = session.client(service_name='bedrock-runtime')

    response = bedrock.converse(
        modelId=model_id,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        toolConfig=tool_config,
        inferenceConfig={"maxTokens": 2000,  "temperature": 0.0}
    )

    return response['output']['message']['content'][0]['text']

tool_config = {
    "tools": [
        {
            "toolSpec": {
                "name": "get_stock_price",
                "description": "주어진 ticker의 현재 주식 가격을 가져옵니다.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "ticker": {
                                "type": "string",
                                "description": "주식의 ticker"
                            }
                        },
                        "required": [
                            "ticker"
                        ]
                    }
                }
            }
        }
    ]
}

tool_config["tools"].append({
    "toolSpec": {
        "name": "get_company_info",
        "description": "주어진 ticker의 기업 정보(회사명, 산업, 시가총액 등)를 가져옵니다.",
        "inputSchema": {
            "json": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "기업의 ticker"
                    }
                },
                "required": [
                    "ticker"
                ]
            }
        }
    }
})

def plan_company_analysis(ticker):
    prompt = f"당신은 AI 기업 분석가입니다. 당신의 목표는 {ticker} 기업에 대한 종합적인 분석을 수행합니다. 목표를 달성하기 위한 당신의 계획을 알려주세요"
    return get_bedrock_response(prompt, "anthropic.claude-3-5-sonnet-20240620-v1:0", tool_config)

ticker = sys.argv[1]
analysis_plan = plan_company_analysis(ticker)
print(analysis_plan)