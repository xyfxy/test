from google.adk.agents import LlmAgent
from google.adk.tools import BaseTool # 导入 BaseTool
from my_adk_agent.llm_config import get_qwen_max_llm # 导入LLM配置
from typing import List

class ToolUsingAgent(LlmAgent):
    """
    一个使用LLM根据任务描述和可用工具来执行任务的智能体。
    它可以决定是否调用工具，以及调用哪个工具。
    """
    def __init__(self, tools: List[BaseTool] = None, **kwargs): #确保导入 List 和 BaseTool
        super().__init__(
            model=get_qwen_max_llm(),
            name="ToolUsingAgent",
            description="根据任务和可用工具执行操作，可以调用工具或直接回答。",
            instruction=(
                "你的任务是分析给定的'任务描述'和'可用工具'列表。\n"
                "1. 理解任务的核心需求。\n"
                "2. 查看可用工具的功能描述，判断是否有工具能帮助完成任务。\n"
                "3. 如果有合适的工具，并且任务需要通过工具执行，请调用该工具。确保你提供的参数符合工具的输入模式。\n"
                "4. 如果没有合适的工具，或者任务可以直接回答，请直接提供答案或完成任务。\n"
                "5. 如果任务是执行一个之前分解好的子任务，请专注于完成这个子任务。\n"
                "请明确说明你是调用了工具还是直接回答。"
            ),
            tools=tools if tools else [], # 接收工具列表
            **kwargs
        )

# 简单的测试
if __name__ == "__main__":
    from google.adk.tools import FunctionTool # 导入 FunctionTool

    # 定义一个简单的示例工具
    def get_current_time(time_zone: str = "UTC") -> str:
        """获取指定时区的当前时间。"""
        import datetime
        import pytz
        now = datetime.datetime.now(pytz.timezone(time_zone))
        return f"The current time in {time_zone} is {now.strftime('%Y-%m-%d %H:%M:%S')}"

    get_current_time_tool = FunctionTool(
        func=get_current_time,
        name="GetCurrentTime",
        description="用于获取指定时区的当前时间。"
    )

    print("正在初始化 ToolUsingAgent...")
    try:
        # 初始化时可以传入工具
        tool_agent = ToolUsingAgent(tools=[get_current_time_tool])
        print("ToolUsingAgent 初始化成功。")

        # 构造一个示例任务
        task_with_tool = "请告诉我当前UTC时间。"
        task_without_tool = "你好吗？"

        print(f"发送任务给智能体: {task_with_tool}")
        # 实际调用需要 Runner
        # from google.adk.runners import Runner
        # runner = Runner(agent=tool_agent)
        # try:
        #     response = runner.run(input=task_with_tool)
        #     print(f"智能体响应 (使用工具): {response.output}")
        #
        #     response_no_tool = runner.run(input=task_without_tool)
        #     print(f"智能体响应 (不使用工具): {response_no_tool.output}")
        # except Exception as e:
        #     print(f"运行智能体时出错: {e}")

        print("注意: 以下为模拟调用演示，实际运行需要 ADK Runner 和有效API密钥。")
        print(f"对于任务 '{task_with_tool}', 预期智能体会调用 GetCurrentTime 工具。")
        print(f"对于任务 '{task_without_tool}', 预期智能体会直接回答。")

    except Exception as e:
        print(f"初始化 ToolUsingAgent 时发生错误: {e}")
