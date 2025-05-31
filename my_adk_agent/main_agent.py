# -*- coding: utf-8 -*-
"""
ADK Web 服务入口点。

此文件用于 `adk web` 命令加载主智能体。
最佳实践是在 `my_adk_agent` 目录内运行 `adk web` 命令。
例如:
cd path/to/your/my_adk_agent
adk web
"""
import sys
import os

# 如果直接在 my_adk_agent 目录下运行 adk web，模块应该能被直接找到。
# 如果是从外部目录通过 adk web --agent_file my_adk_agent/main_agent.py 调用，
# 则可能需要确保 my_adk_agent 的父目录在 sys.path 中，以便 my_adk_agent 本身可以被当作包导入。
# 然而，ADK 的 adk web 通常会将 agent_file 所在的目录临时添加到 sys.path。

# 我们首先尝试直接导入，这在使用 `cd my_adk_agent && adk web` 时应该有效。
OrchestratorAgent_imported = False
DummyAgent = None
ErrorAgent = None
CriticalErrorAgent = None

try:
    from agents.orchestrator_agent import OrchestratorAgent
    OrchestratorAgent_imported = True
    print("OrchestratorAgent 导入成功。")
except ImportError as e:
    print(f"错误: 无法导入 OrchestratorAgent: {e}")
    print("请确保您在 `my_adk_agent` 目录下运行 `adk web`，")
    print("或者 `my_adk_agent` 包已正确安装或其路径已在 PYTHONPATH 中。")
    print(f"当前 Python 路径: {sys.path}")

    # 定义一个虚拟的 main_agent 以避免 adk web 启动时直接因 NameError 失败
    # 并使其能够报告错误
    class _DummyAgent: # 加下划线以避免与全局 DummyAgent 混淆
        def __init__(self, error_message):
            self.name = "DummyAgentOnError"
            self.description = "由于导入错误而使用的虚拟智能体"
            self._error_message = error_message
        async def _run_async(self, input_event, context):
            from google.adk.events import Event
            return Event(output=f"错误：主智能体 OrchestratorAgent 未能正确加载。导入错误: {self._error_message}")
    DummyAgent = _DummyAgent # 赋值给全局变量
    main_agent = DummyAgent(str(e)) # 使用 DummyAgent
    print("已使用 DummyAgent 作为后备。")
except Exception as e: # 捕获其他可能的导入时异常，比如依赖问题
    print(f"导入 OrchestratorAgent 时发生预料之外的错误: {e}")
    class _CriticalErrorAgentImport:
        def __init__(self, error_message):
            self.name = "CriticalErrorAgentImport"
            self._error_message = error_message
        async def _run_async(self, input_event, context):
            from google.adk.events import Event
            return Event(output=f"严重错误：加载主智能体时发生预料之外的错误: {self._error_message}。请检查控制台日志。")
    CriticalErrorAgent = _CriticalErrorAgentImport
    main_agent = CriticalErrorAgent(str(e))
    print("已使用 CriticalErrorAgentImport 作为后备。")


# 仅当 OrchestratorAgent 成功导入时才尝试实例化
if OrchestratorAgent_imported:
    try:
        main_agent_instance = OrchestratorAgent()
        # 将实例化的 agent 赋值给 `main_agent` 变量，ADK 会查找这个变量
        main_agent = main_agent_instance
        print(f"主智能体 '{main_agent.name}' 已成功实例化，准备好由 adk web 使用。")
        if hasattr(main_agent, 'description'):
            print(f"智能体描述: {main_agent.description}")
        if hasattr(main_agent, 'tools') and main_agent.tools:
             print(f"智能体工具: {[tool.name for tool in main_agent.tools]}")
        else:
            print("智能体没有配置工具或工具列表为空。")

    except Exception as e:
        print(f"错误: 实例化 OrchestratorAgent 时发生错误: {e}")
        print("这通常是由于：")
        print("1. `llm_config.py` 中的 API 密钥无效或未设置。")
        print("2. 网络连接问题，无法访问 LLM 服务。")
        print("3. `litellm` 或其他依赖未能正确初始化。")
        print("请检查上述配置和环境。")

        class _ErrorAgentInit: # 加下划线
            def __init__(self, error_message):
                self.name = "ErrorAgentOnInit"
                self.description = "实例化 OrchestratorAgent 失败"
                self._error_message = error_message
            async def _run_async(self, input_event, context):
                from google.adk.events import Event
                return Event(output=f"错误：实例化主智能体 OrchestratorAgent 失败: {self._error_message}")
        ErrorAgent = _ErrorAgentInit
        main_agent = ErrorAgent(str(e)) # 使用 ErrorAgent
        print("已使用 ErrorAgentOnInit 作为后备。")

elif not ('main_agent' in globals() and (isinstance(main_agent, DummyAgent) or isinstance(main_agent, CriticalErrorAgent)) ):
    # 如果 OrchestratorAgent 未导入，并且 main_agent 也不是之前设置的 DummyAgent 或 CriticalErrorAgent
    # 这是一个不太可能发生的情况，但作为最终的保险措施
    class _CriticalErrorAgentUndefined:
        def __init__(self):
            self.name = "CriticalErrorAgentUndefined"
            self.description = "主智能体未定义"
        async def _run_async(self, input_event, context):
            from google.adk.events import Event
            return Event(output="严重错误：主智能体 `main_agent` 未能定义。请检查 `main_agent.py` 的逻辑。")
    CriticalErrorAgent = _CriticalErrorAgentUndefined
    main_agent = CriticalErrorAgent()
    print("严重错误：OrchestratorAgent 未导入，且 main_agent 也未被正确设置为后备智能体。adk web 可能无法正常工作。")

# 为了调试，打印最终确定的 main_agent 类型
if 'main_agent' in globals() and main_agent is not None:
    print(f"最终确定的 `main_agent` 类型: {type(main_agent)}")
else:
    print("错误: `main_agent` 在脚本末尾仍未定义!")
