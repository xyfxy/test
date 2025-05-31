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
├── main.py                   # 主应用程序入口 (运行测试和编程式智能体调用)
├── main_agent.py             # `adk web` 服务入口点
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
*   **Web 服务接口**: 通过 `main_agent.py` 和 `adk web` 命令，可以将智能体作为 Web 服务启动。

## 安装与环境设置

1.  **克隆项目 (如果适用)**
    ```bash
    # git clone <repository_url>
    # cd my_adk_agent
    ```

2.  **创建并激活 Python 虚拟环境**
    建议使用 Python 3.8 或更高版本。在项目根目录 (`my_adk_agent/`) 下执行：
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # Linux/macOS
    # .venv\Scripts\activate    # Windows PowerShell
    # .venv\Scripts\activate.bat # Windows CMD
    ```

3.  **安装依赖**
    确保虚拟环境已激活，然后在项目根目录下执行：
    ```bash
    pip install -r requirements.txt
    ```
    主要依赖包括: `google-adk`, `litellm`, `requests`, `beautifulsoup4`。

## 配置

### API 密钥配置 (重要!)

本项目需要与大语言模型 (LLM) API 进行交互，这通常需要 API 密钥。配置位于 `my_adk_agent/llm_config.py`。

*   **优先使用环境变量**:
    *   脚本会优先尝试从名为 `DASHSCOPE_API_KEY` 的环境变量中读取您的阿里云 DashScope API 密钥。
    *   **Linux/macOS (在当前终端会话中设置)**:
        ```bash
        export DASHSCOPE_API_KEY="your_actual_api_key_here"
        ```
    *   **Windows (PowerShell - 在当前终端会话中设置)**:
        ```powershell
        $env:DASHSCOPE_API_KEY="your_actual_api_key_here"
        ```
    *   **Windows (CMD - 在当前终端会话中设置)**:
        ```cmd
        set DASHSCOPE_API_KEY=your_actual_api_key_here
        ```
    *   为了使环境变量永久生效，您可能需要将其添加到您的 shell 配置文件中（如 `.bashrc`, `.zshrc` for Linux/macOS）或通过系统属性设置系统级环境变量 (Windows)。
*   **后备密钥 (不推荐)**:
    *   如果未设置 `DASHSCOPE_API_KEY` 环境变量，`llm_config.py` 会使用一个在代码中定义的后备 API 密钥 (`sk-1bc9b29869004aeb9df5790361dca54f`)。
    *   **安全警告**: **这是一个示例密钥，您必须将其替换为自己有效的密钥，即便只是为了测试后备机制。强烈建议始终使用环境变量来管理 API 密钥，而不是依赖代码中的后备值，尤其是在共享或部署代码时。** 如果使用后备密钥，您会在控制台看到警告。
*   **LiteLLM 的通用环境变量**:
    *   `LiteLLM` 本身也支持通过更通用的环境变量（如 `OPENAI_API_KEY`，因为我们使用了 `custom_llm_provider="openai"` 来适配 DashScope 的兼容模式）来配置密钥。如果 `DASHSCOPE_API_KEY` 未设置，但 `OPENAI_API_KEY` 设置了，`LiteLLM` 可能会尝试使用它。为确保行为可控，建议明确设置 `DASHSCOPE_API_KEY`。

## 如何运行

1.  **确保环境已设置且依赖已安装** (参见 "安装与环境设置"部分)。
2.  **配置 API 密钥** (参见 "配置"部分)。强烈建议通过设置 `DASHSCOPE_API_KEY` 环境变量来提供您的 API 密钥。

### 方式一：通过 `main.py` (编程式运行和测试)

此方式会先运行所有单元测试，然后以编程式调用 `OrchestratorAgent`。
在 `my_adk_agent` 目录下执行：
```bash
python main.py
```
程序将：
1.  首先执行所有单元测试。您将在控制台中看到测试结果。
2.  如果所有测试都通过，程序会提示您 API 密钥的重要性（此提示后的 `input()` 在 `main.py` 中可能被注释掉了以方便自动化测试，您可以根据需要取消注释）。
3.  `OrchestratorAgent` 将被初始化。
4.  一个示例查询 (例如："ADK框架的主要特性有哪些？另外，帮我看看 langchain 的官方文档首页主要讲了什么。") 将被发送给智能体。
5.  您将在控制台中看到智能体执行各个步骤的日志信息和最终答复。

### 方式二：通过 `adk web` (Web 服务交互)

ADK 提供了 `adk web` 命令，可以快速启动一个 Web 服务来与您的智能体交互。

1.  **启动服务**:
    确保您的终端当前工作目录是 `my_adk_agent/` (即包含 `main_agent.py` 的目录)。然后运行：
    ```bash
    adk web
    ```
    该命令会自动查找并加载在 `main_agent.py` 中定义的 `main_agent` 实例。
    您应该会看到类似以下的输出，表明服务已启动：
    ```
    INFO:     my_adk_agent.main_agent - OrchestratorAgent 导入成功。
    INFO:     my_adk_agent.llm_config - LiteLlm 实例已配置使用 qwen-max 模型。API 密钥来源: ...
    INFO:     my_adk_agent.main_agent - 主智能体 'OrchestratorAgent' 已成功实例化，准备好由 adk web 使用。
    INFO:     my_adk_agent.main_agent - 智能体描述: 接收复杂任务，通过任务分解和工具使用来完成任务。
    INFO:     my_adk_agent.main_agent - 智能体工具: ['BrowseWebsite', 'RetrieveFromKnowledgeBase']
    INFO:     mercury/main_agent - Agent 'OrchestratorAgent' is loaded.
    INFO:     mercury/main_agent - Tools for 'OrchestratorAgent': BrowseWebsite, RetrieveFromKnowledgeBase
    INFO:     Started server process [xxxxx]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    ```
    如果启动时出现关于 API 密钥的警告，请检查您的环境变量配置。

2.  **与智能体交互**:
    *   **通过浏览器**: 打开浏览器并访问 `http://127.0.0.1:8000`。您会看到一个简单的聊天界面，可以在其中输入您的请求。
    *   **通过 `curl`** (或其他API工具):
        ```bash
        curl -X POST http://127.0.0.1:8000/invoke \
             -H "Content-Type: application/json" \
             -d '{"input": "请告诉我什么是ADK以及它的主要特性"}'
        ```
        您将会收到一个 JSON 响应，其中包含会话ID和智能体的输出。例如：
        ```json
        {
            "session_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
            "output": "关于 '使用RAG工具查找ADK的主要特性': ADK (Agent Development Kit) 是一个用于开发和部署 AI 智能体的灵活模块化框架。ADK 的关键特性包括灵活编排、多智能体架构、丰富的工具生态系统和可部署性。"
        }
        ```

### 注意事项 (同样适用于 `adk web`)
*   确保 `DASHSCOPE_API_KEY` 环境变量在运行 `adk web` 的终端会话中是可用的。
*   LLM 响应时间和输出稳定性等因素依然适用。本项目的提示和逻辑是为演示目的而设计的。
*   工具的局限性：`BrowseWebsite` 提取纯文本，`RetrieveFromKnowledgeBase` 是基础模拟。
*   错误处理: 项目中包含一些基本的错误处理，但生产级应用需要更全面的错误管理策略。

## 测试

1.  **通过 `main.py` 自动运行**:
    运行 `python main.py` 会首先执行所有测试。

2.  **单独运行测试**:
    要单独运行测试，请确保虚拟环境已激活，然后在 `my_adk_agent` 目录下使用 `unittest` CLI:
    ```bash
    python -m unittest discover -s tests -v
    ```
    或者，您可以运行特定的测试文件：
    ```bash
    python -m unittest tests.test_browser_tool -v
    ```

## 未来可能的扩展

*   **更强大的 RAG 工具**: 集成真正的 RAG 系统 (如 LlamaIndex, Vertex AI Search)。
*   **更复杂的工具**: 例如代码执行工具、数据库查询工具等。
*   **并行任务执行**: 修改 `OrchestratorAgent` 以支持并行执行独立的子任务。
*   **用户交互式输入**: 修改 `main.py` 以接受用户通过命令行输入的查询。
*   **记忆功能**: 为智能体添加短期或长期记忆。
*   **更精细的错误处理和重试机制**。
*   **使用 `google-adk` 更高级的编排原语**: 例如 `SequentialAgent` (如果流程固定) 或将 Agent 作为工具传递给其他 Agent 的 LLM 进行动态决策。

```
