from google.adk.models.lite_llm import LiteLlm

def get_qwen_max_llm():
    """
    配置并返回基于 qwen-max 模型的 LiteLlm 实例。
    """
    model = LiteLlm(
        model="qwen-max",
        api_key="sk-1bc9b29869004aeb9df5790361dca54f",  # 注意：实际使用中应通过更安全的方式管理 API密钥
        api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
        custom_llm_provider="openai"
    )
    return model

# 简单的测试，确保函数可以被调用并且 LiteLlm 对象被创建
if __name__ == "__main__":
    llm_instance = get_qwen_max_llm()
    print(f"LiteLlm instance created: {llm_instance}")
    print(f"Model name: {llm_instance.model}")
    # 请注意，API 密钥等敏感信息不应直接打印，此处仅为演示 LiteLlm 对象属性可访问
    # print(f"API Key: {llm_instance.api_key}")
    print(f"API Base: {llm_instance.api_base}")
    print(f"Custom LLM Provider: {llm_instance.custom_llm_provider}")
