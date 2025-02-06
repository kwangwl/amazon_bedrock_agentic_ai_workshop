import boto3

def get_bedrock_response(prompt, model_id):
    session = boto3.Session()
    bedrock = session.client(service_name='bedrock-runtime')

    response = bedrock.converse(
        modelId=model_id,
        messages=[{
            "role": "user",
            "content": [{"text": prompt}]
        }],
        inferenceConfig={
            "maxTokens": 2000,
            "temperature": 0.0
        }
    )

    return response['output']['message']['content'][0]['text']

def solve_math_problem(problem):
    prompt = f"다음 수학 문제를 풀어주세요:\n문제{problem}"

    return get_bedrock_response(prompt, "anthropic.claude-3-5-haiku-20241022-v1:0")


def validate_solution(problem, solution):
    prompt = f" 다음 수학 문제와 그에 대한 풀이를 검토해주세요:\n문제: {problem}\n풀이: {solution}"

    return get_bedrock_response(prompt, "anthropic.claude-3-5-sonnet-20240620-v1:0")

math_problem = "2x + 5 = 13 방정식을 풀어주세요."

solution = solve_math_problem(math_problem)
print(f"AI의 풀이: {solution}\n\n")

validation = validate_solution(math_problem, solution)
print(f"검증 결과: {validation}")