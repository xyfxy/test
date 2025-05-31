import unittest
from unittest.mock import MagicMock, patch

# Mock LiteLLM and its base class if ADK or LiteLLM is not fully available in the test environment
try:
    from google.adk.models.lite_llm import LiteLlm
except ImportError:
    class LiteLlm: # Dummy class
        def __init__(self, model, api_key, api_base, custom_llm_provider):
            self.model = model
            self.api_key = api_key
            self.api_base = api_base
            self.custom_llm_provider = custom_llm_provider
    print("Warning: google.adk.models.lite_llm.LiteLlm not found, using dummy.")


with patch('my_adk_agent.llm_config.LiteLlm', new=LiteLlm if 'LiteLlm' not in globals() else globals()['LiteLlm']):
    from my_adk_agent.llm_config import get_qwen_max_llm
    from my_adk_agent.agents.task_decomposition_agent import TaskDecompositionAgent
    from my_adk_agent.agents.tool_using_agent import ToolUsingAgent
    from my_adk_agent.agents.orchestrator_agent import OrchestratorAgent
    from my_adk_agent.tools.browser_tool import browse_tool
    from my_adk_agent.tools.rag_tool import rag_tool


class TestAgentInitialization(unittest.TestCase):

    def test_get_llm_instance(self):
        llm = get_qwen_max_llm()
        self.assertIsNotNone(llm)
        self.assertEqual(llm.model, "qwen-max")

    @patch('my_adk_agent.llm_config.get_qwen_max_llm') # Mock the LLM getter
    def test_task_decomposition_agent_init(self, mock_get_llm):
        mock_get_llm.return_value = MagicMock() # Return a mock LLM
        agent = TaskDecompositionAgent()
        self.assertIsNotNone(agent)
        self.assertEqual(agent.name, "TaskDecompositionAgent")

    @patch('my_adk_agent.llm_config.get_qwen_max_llm')
    def test_tool_using_agent_init(self, mock_get_llm):
        mock_get_llm.return_value = MagicMock()
        agent = ToolUsingAgent(tools=[browse_tool, rag_tool])
        self.assertIsNotNone(agent)
        self.assertEqual(agent.name, "ToolUsingAgent")
        self.assertEqual(len(agent.tools), 2)

    @patch('my_adk_agent.llm_config.get_qwen_max_llm')
    @patch('my_adk_agent.agents.orchestrator_agent.TaskDecompositionAgent') # Mock sub-agents
    @patch('my_adk_agent.agents.orchestrator_agent.ToolUsingAgent')
    def test_orchestrator_agent_init(self, MockToolUsingAgent, MockTaskDecompositionAgent, mock_get_llm):
        mock_get_llm.return_value = MagicMock()
        MockTaskDecompositionAgent.return_value = MagicMock()
        MockToolUsingAgent.return_value = MagicMock()

        agent = OrchestratorAgent()
        self.assertIsNotNone(agent)
        self.assertEqual(agent.name, "OrchestratorAgent")
        self.assertIsNotNone(agent.task_decomposition_agent)
        self.assertIsNotNone(agent.tool_using_agent)
        self.assertEqual(len(agent.tools), 2)

if __name__ == '__main__':
    unittest.main()
