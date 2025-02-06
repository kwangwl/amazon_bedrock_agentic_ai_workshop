import boto3
import yfinance as yf 
import sys

def get_stock_price(ticker):
    stock_data = yf.Ticker(ticker)
    historical_data = stock_data.history(period='1d')

    date = historical_data.index[0].strftime('%Y-%m-%d')
    current_price = historical_data['Close'].iloc[0]
    return f"{ticker} 종가는 {date} 기준 {current_price:.2f}입니다"

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

def get_response(user_question):
    session = boto3.Session()
    bedrock = session.client(service_name='bedrock-runtime')

    response = bedrock.converse(
        modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
        messages=[{"role": "user", "content": [{"text": user_question}]}],
        toolConfig=tool_config,
        inferenceConfig={"maxTokens": 2000,  "temperature": 0.0}
    )
    return response

def handle_tool_use(response):
    if response.get('stopReason') == 'tool_use':
        tool_requests = response['output']['message']['content']
        for tool_request in tool_requests:
            if 'toolUse' in tool_request:
                tool_use = tool_request['toolUse']
                print(f"Bedrock Response : {tool_request}")

                if tool_use['name'] == 'get_stock_price':
                    ticker = tool_use['input']['ticker']
                    return get_stock_price(ticker)

    return response['output']['message']['content'][0]['text']

user_question = sys.argv[1]
response = get_response(user_question)
result = handle_tool_use(response)
print(result)