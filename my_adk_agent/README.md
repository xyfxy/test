# My ADK Agent - 智能体项目

本项目是一个基于 Google Agent Development Kit (ADK) 实现的示例智能体，它具备任务分解、工具调用（网页浏览、RAG检索模拟）和多智能体协作（通过编排）的能力。

## 项目结构

```
my_adk_agent/
├── agents/
│   ├── __init__.py
│   ├── orchestrator_agent.py   # 主编排智能体
│   ├── task_decomposition_agent.py # 任务分解智能体
│   └── tool_using_agent.py     # 工具使用智能体
├── tools/
│   ├── __init__.py
│   ├── browser_tool.py         # 网页浏览工具
│   └── rag_tool.py             # RAG 检索工具 (模拟)
├── tests/
│   ├── __init__.py
│   ├── test_agent_initialization.py
│   ├── test_browser_tool.py
│   ├── test_orchestrator_flow.py
│   └── test_rag_tool.py
├── __init__.py
├── llm_config.py             # LiteLLM 模型配置
├── main.py                   # 主应用程序入口 (运行测试和智能体)
├── requirements.txt          # Python 依赖
└── README.md                 # 项目说明文档
```

## 功能特性

*   **任务分解**: `TaskDecompositionAgent` 接收复杂任务，并使用大语言模型 (LLM) 将其分解为一系列有序的子任务。
*   **工具调用**: `ToolUsingAgent` 能够根据任务描述，从提供的工具集中选择并使用合适的工具。
    *   **网页浏览**: `BrowseWebsite` 工具可以访问指定的 URL 并提取其主要文本内容。
    *   **RAG 检索 (模拟)**: `RetrieveFromKnowledgeBase` 工具模拟从知识库中检索信息。
*   **多智能体编排**: `OrchestratorAgent` 是核心协调者。它：
    1.  接收用户的主要请求。
    2.  调用 `TaskDecompositionAgent` 分解任务。
    3.  对于每个子任务，调用 `ToolUsingAgent`（配备了所有可用工具）来执行。
    4.  汇总所有子任务的结果，生成最终答复。
*   **模型配置**: 使用 `LiteLLM` 与自定义 LLM (默认为 `qwen-max` 通过阿里云 DashScope) 进行交互。配置位于 `llm_config.py`。
*   **单元测试**: 包含针对工具和智能体初始化/流程的单元测试。

## 安装与环境设置

1.  **克隆项目 (如果适用)**
    ```bash
    # git clone <repository_url>
    # cd my_adk_agent
    ```

2.  **创建并激活 Python 虚拟环境**
    建议使用 Python 3.8 或更高版本。
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # Linux/macOS
    # .venv\Scripts\activate    # Windows
    ```

3.  **安装依赖**
    项目根目录下 (即 `my_adk_agent/`) 包含 `requirements.txt` 文件。
    ```bash
    pip install -r requirements.txt
    ```
    主要依赖包括: `google-adk`, `litellm`, `requests`, `beautifulsoup4`。

## 配置

### API 密钥配置 (重要!)

本项目需要与大语言模型 (LLM) API 进行交互，这通常需要 API 密钥。

*   **LLM 配置**: `llm_config.py` 文件中定义了 `get_qwen_max_llm()` 函数，它实例化了 `LiteLlm`。
    ```python
    # my_adk_agent/llm_config.py
    model = LiteLlm(
        model="qwen-max",
        api_key="sk-1bc9b29869004aeb9df5790361dca54f", # <--- 在这里配置你的API密钥
        api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
        custom_llm_provider="openai" # LiteLLM 使用此提供商名称来适配 DashScope 的兼容模式
    )
    ```
*   **安全警告**: **请勿将真实的 API 密钥直接硬编码并提交到版本控制系统 (如 Git)。**
    *   **推荐做法**: 使用环境变量。LiteLLM 支持从环境变量中读取特定模型的 API 密钥。例如，对于 OpenAI 兼容的接口，可以设置 `OPENAI_API_KEY`。查阅 LiteLLM 文档了解如何为不同模型/提供商配置环境变量。
    *   或者，使用 `.env` 文件 (配合 `python-dotenv` 库) 来管理本地开发环境的密钥。
    *   对于生产环境，请使用云服务提供商的密钥管理服务。

*   **当前示例密钥**: `llm_config.py` 中的 `api_key` 是一个示例值，您需要将其替换为自己有效的 `qwen-max` (DashScope) API 密钥。

## 如何运行

1.  **确保环境已设置且依赖已安装** (参见 "安装与环境设置"部分)。
2.  **配置 API 密钥** (参见 "配置"部分)。
3.  **运行主程序**:
    在 `my_adk_agent` 目录下执行：
    ```bash
    python main.py
    ```
    程序将首先执行所有单元测试。如果测试通过，它将继续初始化 `OrchestratorAgent` 并使用一个预定义的复杂查询来运行它。

### 预期流程

当运行 `main.py` 时:
1.  将首先执行 `unittest` 测试套件。您将在控制台中看到测试结果。
2.  如果所有测试都通过，程序会提示您 API 密钥的重要性，并等待您按 Enter 键继续。
3.  `OrchestratorAgent` 将被初始化。
4.  一个示例查询 (例如："ADK框架的主要特性有哪些？另外，帮我看看 langchain 的官方文档首页主要讲了什么。") 将被发送给智能体。
5.  您将在控制台中看到智能体执行各个步骤的日志信息，包括：
    *   `OrchestratorAgent` 接收到查询。
    *   调用 `TaskDecompositionAgent` 进行任务分解，以及分解后的子任务列表。
    *   对于每个子任务，调用 `ToolUsingAgent`。
    *   `ToolUsingAgent` 可能会调用 `BrowseWebsite` 工具或 `RetrieveFromKnowledgeBase` 工具。
    *   工具执行的结果。
    *   `OrchestratorAgent` 汇总所有信息并生成最终答复。
6.  最终，智能体的完整响应将被打印出来。

### 注意事项

*   **LLM 响应时间**: 与 LLM API 的交互可能会有延迟，具体取决于网络状况和 LLM 的响应速度。
*   **LLM 输出的稳定性**: LLM 的输出（尤其是任务分解和工具参数选择）可能不总是完全一致或完美。本项目的提示和逻辑是为演示目的而设计的。在生产环境中，可能需要更复杂的提示工程、输出校验和错误处理逻辑。
*   **工具的局限性**:
    *   `BrowseWebsite` 工具提取的是纯文本，可能无法完美处理所有类型的网站结构或动态内容。
    *   `RetrieveFromKnowledgeBase` 工具是一个非常基础的模拟，其实际效果取决于其内部知识库和检索算法。
*   **错误处理**: 项目中包含一些基本的错误处理，但生产级应用需要更全面的错误管理策略。

## 测试

要单独运行测试，可以在 `my_adk_agent` 目录下使用 `unittest` CLI (确保虚拟环境已激活):

```bash
python -m unittest discover -s tests -v
```
或者直接运行 `main.py`，它会在智能体运行前自动执行测试。

## 未来可能的扩展

*   **更强大的 RAG 工具**: 集成真正的 RAG 系统 (如 LlamaIndex, Vertex AI Search)。
*   **更复杂的工具**: 例如代码执行工具、数据库查询工具等。
*   **并行任务执行**: 修改 `OrchestratorAgent` 以支持并行执行独立的子任务。
*   **用户交互式输入**: 修改 `main.py` 以接受用户通过命令行输入的查询。
*   **记忆功能**: 为智能体添加短期或长期记忆。
*   **更精细的错误处理和重试机制**。
*   **使用 `google-adk` 更高级的编排原语**: 例如 `SequentialAgent` (如果流程固定) 或将 Agent 作为工具传递给其他 Agent 的 LLM 进行动态决策。

```
