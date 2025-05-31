import os
from google.adk.models.lite_llm import LiteLlm

# 推荐的环境变量名，用于存储 DashScope API Key
DASHSCOPE_API_KEY_ENV_VAR = "DASHSCOPE_API_KEY"

# 之前硬编码的API密钥，现在作为后备，但不推荐在生产中使用
FALLBACK_API_KEY = "sk-1bc9b29869004aeb9df5790361dca54f"

def get_qwen_max_llm():
    """
    配置并返回基于 qwen-max 模型的 LiteLlm 实例。
    优先从环境变量 DASHSCOPE_API_KEY 读取 API 密钥。
    如果环境变量未设置，则使用代码中定义的后备密钥（不推荐）。
    """
    api_key = os.environ.get(DASHSCOPE_API_KEY_ENV_VAR)
    key_source_message = "" # 用于日志

    if api_key:
        key_source_message = f"成功从环境变量 {DASHSCOPE_API_KEY_ENV_VAR} 加载 API 密钥。"
    else:
        api_key = FALLBACK_API_KEY
        key_source_message = (
            f"警告: 未找到环境变量 {DASHSCOPE_API_KEY_ENV_VAR}。"
            f"将使用 llm_config.py 中定义的后备 API 密钥。"
            "强烈建议通过设置环境变量来管理 API 密钥以确保安全。"
        )
        print(key_source_message) # 打印警告

    # 实例化 LiteLlm
    # LiteLLM 本身在找不到 api_key 参数时，也会尝试从更通用的环境变量（如 OPENAI_API_KEY）中查找
    # 此处我们明确传递 api_key，使其行为更可控
    model_instance = LiteLlm(
        model="qwen-max",
        api_key=api_key, # 明确传递获取到的 api_key
        api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
        custom_llm_provider="openai" # DashScope 使用 OpenAI 兼容模式
    )

    # 打印最终使用的密钥来源（主要用于调试和启动时确认）
    # 不直接打印 api_key 本身以保安全
    if api_key == FALLBACK_API_KEY and os.environ.get(DASHSCOPE_API_KEY_ENV_VAR) is None:
        print(f"LiteLlm 实例已配置使用 qwen-max 模型。API 密钥来源: 代码中的后备值 (不推荐)。")
    else:
        print(f"LiteLlm 实例已配置使用 qwen-max 模型。API 密钥来源: 环境变量 '{DASHSCOPE_API_KEY_ENV_VAR}'。")

    return model_instance

# 简单的测试，确保函数可以被调用并且 LiteLlm 对象被创建
if __name__ == "__main__":
    print("测试 get_qwen_max_llm():")

    original_env_value = os.environ.get(DASHSCOPE_API_KEY_ENV_VAR) # 保存原始值

    # 测试1: 不设置环境变量，应使用后备密钥并打印警告
    print("\n--- 测试场景 1: 未设置环境变量 (或原值不存在) ---")
    if DASHSCOPE_API_KEY_ENV_VAR in os.environ:
        del os.environ[DASHSCOPE_API_KEY_ENV_VAR]

    llm_instance_fallback = get_qwen_max_llm()
    print(f"获取到的 LiteLlm 实例 (应为后备): {llm_instance_fallback}")
    # 实际测试中，我们会检查 llm_instance_fallback.api_key 是否等于 FALLBACK_API_KEY
    # 但这里避免直接访问或打印敏感属性

    # 测试2: 设置环境变量，应使用环境变量中的密钥
    print("\n--- 测试场景 2: 已设置环境变量 ---")
    test_api_key_from_env = "env_provided_test_key_12345"
    os.environ[DASHSCOPE_API_KEY_ENV_VAR] = test_api_key_from_env

    llm_instance_env = get_qwen_max_llm()
    print(f"获取到的 LiteLlm 实例 (应来自环境变量): {llm_instance_env}")
    # 实际测试中，我们会检查 llm_instance_env.api_key 是否等于 test_api_key_from_env

    # 恢复原始环境变量值
    if original_env_value is not None:
        os.environ[DASHSCOPE_API_KEY_ENV_VAR] = original_env_value
    elif DASHSCOPE_API_KEY_ENV_VAR in os.environ: # 如果原本不存在，但被测试设置了
        del os.environ[DASHSCOPE_API_KEY_ENV_VAR]

    print("\nllm_config.py 测试完成。")
