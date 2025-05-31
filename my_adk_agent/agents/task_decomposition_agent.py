from google.adk.agents import LlmAgent
from my_adk_agent.llm_config import get_qwen_max_llm # 导入我们之前创建的LLM配置

class TaskDecompositionAgent(LlmAgent):
    """
    一个使用 LLM 将复杂任务分解为子任务列表的智能体。
    """
    def __init__(self, **kwargs):
        super().__init__(
            model=get_qwen_max_llm(), # 使用配置好的 qwen-max 模型
            name="TaskDecompositionAgent",
            description="负责将复杂任务分解为一系列有序的、更小的、可执行的子任务。",
            instruction=(
                "你的任务是将用户提出的复杂目标分解为一系列清晰、简洁、有序的子任务。"
                "每个子任务都应该是可操作的，并且是实现最终目标的一个步骤。"
                "请以Python列表的格式返回子任务，例如：\n"
                "['子任务1描述', '子任务2描述', '子任务3描述']\n"
                "确保子任务的顺序是合乎逻辑的。"
                "例如，如果用户说：'帮我计划一次去北京的旅行，并预订机票和酒店。'\n"
                "你应该输出类似：\n"
                "['确定旅行日期和预算', '研究北京的景点和活动', '搜索并比较往返北京的机票价格', '预订选定的机票', '搜索并比较北京的酒店选项', '预订选定的酒店', '制定详细的每日行程']"
            ),
            output_schema=list[str], #期望输出是一个字符串列表
            **kwargs
        )

# 简单的测试
if __name__ == "__main__":
    # 注意：直接运行此测试需要有效的 API 密钥和网络连接
    # 并且 litellm 和 google-adk 已正确安装。
    # 在没有实际运行环境的情况下，这部分代码主要用于结构演示。
    print("正在初始化 TaskDecompositionAgent...")
    try:
        decomposition_agent = TaskDecompositionAgent()
        print("TaskDecompositionAgent 初始化成功。")

        # 构造一个示例复杂任务
        complex_task = "我需要开发一个天气应用，它可以显示当前天气、未来几天的预报，并允许用户搜索不同城市的天气。"
        print(f"发送复杂任务给智能体: {complex_task}")

        # 在ADK中，通常通过 Runner 来运行智能体
        # from google.adk.runners import Runner
        # runner = Runner(agent=decomposition_agent)
        # result = runner.run(input=complex_task)
        # print(f"任务分解结果: {result}")

        # 此处我们模拟调用（实际调用需要 Runner 和会话）
        # 真实的调用会是异步的，并且通过 event loop 处理
        print("注意: 以下为模拟调用演示，实际运行需要 ADK Runner。")
        print("预期输出格式: ['子任务1', '子任务2', ...]")

        # 你可以在实际测试环境中取消注释以下行，并确保你的 API 密钥配置正确
        # from google.adk.runners import Runner
        # runner = Runner(agent=decomposition_agent)
        # # 确保你的 LiteLLM 配置中的 API 密钥是有效的
        # try:
        #     response = runner.run(input=complex_task)
        #     print(f"任务分解结果: {response.output}")
        # except Exception as e:
        #     print(f"运行智能体时出错: {e}")
        #     print("请确保您的 API 密钥已正确配置并且网络连接正常。")

    except Exception as e:
        print(f"初始化 TaskDecompositionAgent 时发生错误: {e}")
        print("这可能是由于缺少 API 密钥配置或网络问题。")
