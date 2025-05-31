from google.adk.agents import LlmAgent #, SequentialAgent, BaseAgent # SequentialAgent, BaseAgent 暂时注释掉，因为当前简化版未使用
from google.adk.events import Event
from my_adk_agent.llm_config import get_qwen_max_llm
from my_adk_agent.agents.task_decomposition_agent import TaskDecompositionAgent
from my_adk_agent.agents.tool_using_agent import ToolUsingAgent
from my_adk_agent.tools.browser_tool import browse_tool
from my_adk_agent.tools.rag_tool import rag_tool
# from typing import List, Dict, Any # 暂时注释掉，因为当前简化版未使用

class OrchestratorAgent(LlmAgent):
    """
    一个编排智能体，负责接收复杂任务，将其分解，并协调其他智能体和工具来执行子任务。
    """
    def __init__(self, **kwargs):
        super().__init__(
            name="OrchestratorAgent",
            description="接收复杂任务，通过任务分解和工具使用来完成任务。",
            model=get_qwen_max_llm(),
            instruction=(
                "你是一个高级任务编排器。你的主要工作流程如下：\n"
                "1. 接收一个复杂的用户请求。\n"
                "2. **调用 'TaskDecompositionAgent'** 将其分解为一系列有序的子任务列表 (你会得到一个Python列表的字符串表示)。\n"
                "3. **按顺序处理每个子任务**: 对于每个子任务，你需要：\n"
                "    a. 分析子任务，判断它需要什么操作（例如，浏览网页，从知识库检索，或简单回答）。\n"
                "    b. **调用 'ToolUsingAgent'** 来执行这个子任务。你需要向 ToolUsingAgent 提供子任务描述和所有可用的工具 (BrowseWebsite, RetrieveFromKnowledgeBase)。\n"
                "    c. 收集 ToolUsingAgent 的执行结果。\n"
                "4. 在所有子任务完成后，根据收集到的结果，**生成一个最终的、全面的答案**给用户。\n"
                "请确保最终答案整合了所有子任务的执行结果，并清晰地呈现给用户。\n"
                "工具列表: [BrowseWebsite, RetrieveFromKnowledgeBase]"
            ),
            tools=[browse_tool, rag_tool],
            **kwargs
        )
        # 初始化子智能体
        self.task_decomposition_agent = TaskDecompositionAgent()
        self.tool_using_agent = ToolUsingAgent(tools=[browse_tool, rag_tool])

    async def _run_async(self, input: str, context) -> Event:
        """
        自定义运行逻辑以实现编排。 (简化版)
        """
        print(f"[OrchestratorAgent] 接收到输入: {input}")
        final_response_parts = []
        sub_tasks_str_representation = ""

        # 步骤 1: 任务分解 (模拟LLM调用TaskDecompositionAgent)
        # 在一个更完善的系统中，Orchestrator的LLM会生成一个调用TaskDecompositionAgent的请求
        # 这里我们直接调用并获取其输出（假设其输出是子任务列表的字符串形式）
        print("[OrchestratorAgent] 步骤 1: 调用 TaskDecompositionAgent 进行任务分解...")
        try:
            # 模拟ADK LlmAgent的调用方式：输入是简单字符串，输出在Event.output
            # 注意：TaskDecompositionAgent的instruction要求它返回Python列表格式的字符串
            # 例如: "['子任务1', '子任务2']"
            decomposition_event = await self.task_decomposition_agent._run_llm(
                Event(input=f"请将以下任务分解为子任务列表: {input}"), context
            )
            sub_tasks_str_representation = decomposition_event.output
            print(f"[OrchestratorAgent] TaskDecompositionAgent 返回的原始分解结果: {sub_tasks_str_representation}")

            # 解析这个字符串表示的列表
            # TODO: 使用更安全的方式解析，例如 ast.literal_eval，并添加错误处理
            try:
                # 尝试去除可能的外部引号和转义字符
                if isinstance(sub_tasks_str_representation, str):
                    if sub_tasks_str_representation.startswith("'") and sub_tasks_str_representation.endswith("'"):
                         sub_tasks_str_representation = sub_tasks_str_representation[1:-1]
                    if sub_tasks_str_representation.startswith('"') and sub_tasks_str_representation.endswith('"'):
                         sub_tasks_str_representation = sub_tasks_str_representation[1:-1]

                    # 替换模型可能产生的非标准 Python 列表字符串中的单引号为双引号以适应json解析
                    # 这部分非常脆弱，取决于LLM输出的稳定性
                    # cleaned_str = sub_tasks_str_representation.replace("'", '"')
                    # sub_tasks = json.loads(cleaned_str)

                    # 使用 ast.literal_eval 更安全
                    import ast
                    sub_tasks = ast.literal_eval(sub_tasks_str_representation)

                    if not isinstance(sub_tasks, list):
                        print(f"[OrchestratorAgent] 错误: TaskDecompositionAgent未能返回预期的列表格式。得到: {sub_tasks}")
                        sub_tasks = [f"任务分解失败，原始输入为: {input}"] # 后备
                else: # 如果输出直接是列表（不太可能通过_run_llm直接得到，除非output_schema起了作用）
                    sub_tasks = sub_tasks_str_representation if isinstance(sub_tasks_str_representation, list) else [f"任务分解器返回类型错误: {type(sub_tasks_str_representation)}"]


            except Exception as e:
                print(f"[OrchestratorAgent] 错误: 解析任务分解结果失败: {e}. 分解结果: {sub_tasks_str_representation}")
                final_response_parts.append(f"任务分解步骤失败: {e}. 分解器原始输出: {sub_tasks_str_representation}")
                sub_tasks = [f"任务分解解析失败，原始输入为: {input}"] # 后备

        except Exception as e:
            print(f"[OrchestratorAgent] 错误: 调用 TaskDecompositionAgent 失败: {e}")
            final_response_parts.append(f"调用任务分解器失败: {e}")
            sub_tasks = [f"调用任务分解器失败，原始输入为: {input}"] # 后备

        print(f"[OrchestratorAgent] 解析后的子任务列表: {sub_tasks}")

        # 步骤 2: 执行子任务
        if isinstance(sub_tasks, list) and sub_tasks:
            for i, sub_task_description in enumerate(sub_tasks):
                if not isinstance(sub_task_description, str): # 确保子任务是字符串
                    print(f"[OrchestratorAgent] 跳过非字符串子任务: {sub_task_description}")
                    final_response_parts.append(f"子任务 '{sub_task_description}' 不是文本，已跳过。")
                    continue

                print(f"[OrchestratorAgent] 步骤 2.{i+1}: 调用 ToolUsingAgent 执行子任务: '{sub_task_description}'")
                try:
                    # 模拟LLM调用ToolUsingAgent
                    # ToolUsingAgent的instruction会引导它使用提供的工具
                    tool_event = await self.tool_using_agent._run_llm(
                        Event(input=sub_task_description), # ToolUsingAgent会从其tools参数中选择
                        context
                    )
                    tool_agent_output = tool_event.output
                    print(f"[OrchestratorAgent] ToolUsingAgent 返回结果: {tool_agent_output}")
                    final_response_parts.append(f"子任务 '{sub_task_description}' 的结果: {tool_agent_output}")
                except Exception as e:
                    print(f"[OrchestratorAgent] 错误: 调用 ToolUsingAgent 执行子任务 '{sub_task_description}' 失败: {e}")
                    final_response_parts.append(f"执行子任务 '{sub_task_description}' 失败: {e}")
        elif not final_response_parts: # 如果sub_tasks不是列表但之前没有记录分解错误
             final_response_parts.append(f"任务分解未能产生有效的子任务列表。分解器输出: {sub_tasks_str_representation}")


        # 步骤 3: 汇总结果 (由Orchestrator的LLM完成)
        print("[OrchestratorAgent] 步骤 3: 汇总所有结果...")
        if not final_response_parts: # 如果前面步骤完全失败，没有收集到任何部分
            summary_input = f"任务 '{input}' 执行失败，未能获取任何子任务结果。"
        else:
            summary_input = (
                f"请根据以下针对复杂任务 '{input}' 的子任务执行日志，生成一个最终的、全面的答案给用户。确保整合所有相关信息并清晰呈现：\n\n"
                f"任务分解输出的子任务列表字符串: {sub_tasks_str_representation}\n\n"
                f"子任务执行详情:\n" +
                "\n".join(final_response_parts)
            )

        # 调用Orchestrator自身的LLM进行最终总结
        # super()._run_llm() 是调用LlmAgent基类的核心LLM处理逻辑
        final_summary_event = await super()._run_llm(Event(input=summary_input), context)

        print(f"[OrchestratorAgent] 最终总结: {final_summary_event.output}")
        return final_summary_event # 返回包含最终总结的事件

# 简单的测试 (概念性)
if __name__ == "__main__":
    print("正在初始化 OrchestratorAgent...")
    orchestrator = OrchestratorAgent()
    print("OrchestratorAgent 初始化成功。")

    complex_query = "帮我查找ADK框架的主要特性并告诉我当前北京的天气。"
    print(f"发送复杂查询给 OrchestratorAgent: {complex_query}")

    print("\n注意: 以下测试代码需要asyncio事件循环和ADK Runner才能实际运行。")
    print("当前版本的 OrchestratorAgent._run_async 是一个简化的实现。")
    print("要实际运行此测试，你需要：")
    print("1. 取消注释掉 main.py (下一步骤创建) 中的相关运行代码。")
    print("2. 确保你的 LiteLLM 配置 (api_key 等) 是有效的。")
    print("3. 在一个支持 asyncio 的环境中运行 main.py。")

    # 示例: 如何在实际环境中运行 (将在 main.py 中实现)
    # import asyncio
    # from google.adk.runners import Runner
    # from google.adk.sessions import InMemorySessionService
    #
    # async def run_orchestrator():
    #     runner = Runner(
    #         agent=orchestrator,
    #         session_service=InMemorySessionService()
    #     )
    #     session = await runner.session_service.create_session()
    #     print(f"Created session: {session.id}")
    #
    #     response_event = await runner.run_async(session_id=session.id, input=complex_query)
    #     print(f"\nOrchestratorAgent 最终响应:\n{response_event.output}")
    #
    # if __name__ == "__main__": # 嵌套的 if __name__ 仅为说明
    #     # 为了避免在这个文件中直接尝试运行asyncio代码 (因为子任务环境可能不支持)
    #     # 我们只打印说明
    #     print("请通过 main.py 来运行完整的测试。")
    #     pass
