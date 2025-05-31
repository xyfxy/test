import asyncio
import unittest
import sys
import os

# 确保 my_adk_agent 在 Python 路径中
current_dir = os.path.dirname(os.path.abspath(__file__))
# sys.path.insert(0, current_dir) # 通常执行 main.py 时，其所在目录已在路径中，但为了保险可以加上
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)


ADK_AVAILABLE = False
OrchestratorAgent = None
Runner = None
InMemorySessionService = None
Session = None
TestBrowserTool = None
TestRagTool = None
TestAgentInitialization = None
TestOrchestratorFlow = None

try:
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService, Session
    from agents.orchestrator_agent import OrchestratorAgent
    from tests.test_browser_tool import TestBrowserTool
    from tests.test_rag_tool import TestRagTool
    from tests.test_agent_initialization import TestAgentInitialization
    from tests.test_orchestrator_flow import TestOrchestratorFlow
    ADK_AVAILABLE = True
except ImportError as e:
    print(f"错误：导入 ADK 或项目组件失败: {e}")
    print("请确保 google-adk 已安装，并且脚本从 'my_adk_agent' 目录内部运行，")
    print("或者 my_adk_agent 的父目录已在 PYTHONPATH 中。")

    # 定义虚拟类以便脚本的其余部分可以被解析
    class DummyTestCase(unittest.TestCase):
        def test_dummy(self): self.skipTest("ADK or project components not available")
    class DummyAsyncTestCase(unittest.IsolatedAsyncioTestCase):
        async def test_dummy(self): self.skipTest("ADK or project components not available")

    OrchestratorAgent = type('OrchestratorAgent', (object,), {})
    Runner = type('Runner', (object,), {})
    InMemorySessionService = type('InMemorySessionService', (object,), {})
    Session = type('Session', (object,), {})
    TestBrowserTool = type('TestBrowserTool', (DummyTestCase,), {})
    TestRagTool = type('TestRagTool', (DummyTestCase,), {})
    TestAgentInitialization = type('TestAgentInitialization', (DummyTestCase,), {})
    TestOrchestratorFlow = type('TestOrchestratorFlow', (DummyAsyncTestCase,), {})


async def run_agent_with_query(agent_instance, query: str): # Removed OrchestratorAgent type hint for dummy class
    """
    使用给定的查询运行智能体。
    """
    if not ADK_AVAILABLE or OrchestratorAgent is None or not hasattr(agent_instance, 'name') : # Check if it's a real agent
        print("ADK组件不可用或Agent实例化失败，无法运行查询。")
        return

    print(f"\n{'='*20} 运行智能体 {'='*20}")
    print(f"输入查询: {query}\n")

    runner = Runner(
        agent=agent_instance,
        session_service=InMemorySessionService()
    )

    session: Session = await runner.session_service.create_session()
    print(f"会话已创建: {session.id}")

    try:
        response_event = await runner.run_async(session_id=session.id, input=query)

        print("\n智能体最终响应:")
        print("=" * 50)
        if response_event and hasattr(response_event, 'output'):
            print(response_event.output)
        else:
            print("未能从智能体获取有效响应。")
        print("=" * 50)

    except Exception as e:
        print(f"运行智能体时发生错误: {e}")
        print("请检查：")
        print("1. LiteLLM 配置中的 API 密钥是否有效且具有足够配额。")
        print("2. 网络连接是否正常，是否可以访问 DashScope API base。")
        print("3. `litellm` 和 `google-adk` 库是否已正确安装在环境中。")
        print("4. 查看 `my_adk_agent/llm_config.py` 中的 API 密钥和模型名称是否正确。")
    finally:
        if 'runner' in locals() and hasattr(runner, 'session_service') and runner.session_service:
             if hasattr(runner.session_service, 'close_session'):
                await runner.session_service.close_session(session.id)
                print(f"\n会话已关闭: {session.id}")


def run_tests():
    """
    运行项目中的所有测试用例。
    """
    print(f"\n{'='*20} 运行测试用例 {'='*20}")
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加测试套件, 只有当测试类被成功导入时才添加
    if TestBrowserTool and not isinstance(TestBrowserTool, type): suite.addTest(loader.loadTestsFromTestCase(TestBrowserTool))
    if TestRagTool and not isinstance(TestRagTool, type): suite.addTest(loader.loadTestsFromTestCase(TestRagTool))
    if TestAgentInitialization and not isinstance(TestAgentInitialization, type): suite.addTest(loader.loadTestsFromTestCase(TestAgentInitialization))
    if TestOrchestratorFlow and not isinstance(TestOrchestratorFlow, type): suite.addTest(loader.loadTestsFromTestCase(TestOrchestratorFlow))

    if not suite.countTestCases() > 0 and ADK_AVAILABLE: # ADK is available but no tests loaded
        print("警告: ADK 可用但未能加载任何测试用例。请检查测试文件和类名。")
    elif not ADK_AVAILABLE and not suite.countTestCases() > 0:
        print("ADK组件或测试文件未能正确导入，跳过测试执行。")
        return False # 表示测试未运行或失败

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    print(f"{'='*50}")
    return result.wasSuccessful() if hasattr(result, 'wasSuccessful') else False


async def main():
    tests_passed = run_tests()

    if not ADK_AVAILABLE:
        print("\n由于 ADK 组件导入失败，无法继续运行智能体。")
        sys.exit(1)

    if tests_passed:
        print("\n所有可执行的测试通过。现在尝试运行智能体...")
        agent_instance = None
        try:
            agent_instance = OrchestratorAgent()
            print("OrchestratorAgent 初始化成功。")

            complex_query = "ADK框架的主要特性有哪些？另外，帮我看看 langchain 的官方文档首页主要讲了什么。"
            await run_agent_with_query(agent_instance, complex_query)

        except Exception as e:
            print(f"初始化 OrchestratorAgent 或运行查询时发生顶层错误: {e}")
            print("请确保您的API密钥和网络配置正确。")
    else:
        print("\n部分测试未通过或未能运行。请检查错误并修复后再运行智能体。")


if __name__ == "__main__":
    print("="*60)
    print("重要提示:")
    print("此应用需要一个有效的 API 密钥才能与 LLM (qwen-max) 交互。")
    print("请确保 `my_adk_agent/llm_config.py` 中的 API 密钥是正确的，")
    print("或者已经通过环境变量等方式为 LiteLLM 进行了配置。")
    print("如果API密钥无效或网络不通，智能体运行将会失败。")
    print("="*60)
    print("\n按 Enter键 继续运行测试和智能体...")
    # input() # 在自动化环境中运行时，input()可能会导致阻塞，暂时注释掉

    asyncio.run(main())
