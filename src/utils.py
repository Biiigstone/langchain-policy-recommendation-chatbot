import tiktoken

def count_tokens(text, model="text-embedding-3-large"):
    # OpenAI 임베딩 모델들은 cl100k_base 인코딩 사용
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


    avg = 0;
    for i in docs:
        token_count = count_tokens(i.page_content)
        avg += token_count
        if token_count >= 1000:
            print(f"토큰 수: {token_count}")
    print(f"총 토큰 수: {avg}")
