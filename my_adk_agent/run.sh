#!/bin/bash

# run.sh - 辅助脚本，用于测试和运行 My ADK Agent 项目

# 函数：显示用法
usage() {
    echo "用法: $0 [test|run|web|all]"
    echo "  test: 仅运行单元测试。"
    echo "  run:  通过 main.py 运行智能体 (main.py 内部会先运行测试)。"
    echo "  web:  通过 adk web 启动智能体Web服务。"
    echo "  all:  运行测试，然后通过 main.py 运行智能体 (如果测试通过)。"
    echo "如果未提供参数，则默认为 'all'。"
    exit 1
}

# 函数：检查并提示API密钥
check_api_key() {
    if [ -z "$DASHSCOPE_API_KEY" ]; then
        echo ""
        echo "---------------------------------------------------------------------"
        echo "警告: 环境变量 DASHSCOPE_API_KEY 未设置。"
        echo "智能体需要此API密钥才能与LLM服务交互。"
        echo "您可以按如下方式设置它 (在当前终端会话中):"
        echo "  export DASHSCOPE_API_KEY=\"your_actual_api_key_here\""
        echo "为了使其永久生效, 请将其添加到您的 .bashrc, .zshrc 或类似shell配置文件中。"
        echo "或者，您可以在 my_adk_agent/llm_config.py 中修改后备密钥，"
        echo "但这不推荐用于生产或共享代码。"
        echo "---------------------------------------------------------------------"
        # 等待用户阅读，但允许脚本继续，因为llm_config有后备机制
        read -t 5 -p "按 Enter键 继续，或等待5秒自动继续 (智能体功能可能受限或失败)..." || true
        echo ""
    else
        echo "环境变量 DASHSCOPE_API_KEY 已设置。"
    fi
}

# 函数：激活虚拟环境 (如果存在)
activate_venv() {
    if [ -d ".venv" ]; then
        echo "正在激活虚拟环境 .venv ..."
        source .venv/bin/activate
        echo "虚拟环境已激活。"
    else
        echo "警告: 未找到 .venv 虚拟环境目录。"
        echo "请确保您已按照 README 中的说明创建了虚拟环境并安装了依赖。"
        echo "例如: 'python3 -m venv .venv' 后跟 'source .venv/bin/activate' 和 'pip install -r requirements.txt'"
    fi
}

# 函数：运行测试
run_tests() {
    echo ""
    echo "---------------------------------------------------------------------"
    echo "正在运行单元测试..."
    echo "---------------------------------------------------------------------"
    python -m unittest discover -s tests -v
    # 保存测试结果
    # $? 是上一条命令的退出码。0表示成功。
    return $?
}

# 函数：通过main.py运行智能体
run_main_py() {
    echo ""
    echo "---------------------------------------------------------------------"
    echo "正在通过 main.py 运行智能体..."
    echo "(main.py 内部会再次运行测试)"
    echo "---------------------------------------------------------------------"
    # 之前已经提示过一次API密钥，main.py内部也会提示
    # input() 在main.py中可能被注释掉了，所以这里不再加read
    python main.py
}

# 函数：通过adk web启动服务
run_adk_web() {
    echo ""
    echo "---------------------------------------------------------------------"
    echo "正在通过 adk web 启动智能体服务..."
    echo "确保您的API密钥已正确配置 (通过环境变量 DASHSCOPE_API_KEY)。"
    echo "服务启动后，请访问 http://127.0.0.1:8000"
    echo "---------------------------------------------------------------------"
    adk web # 假设 main_agent.py 在当前目录
}

# --- 主逻辑 ---

echo "My ADK Agent - 辅助运行脚本"
echo "============================"

# 激活虚拟环境
activate_venv

# 检查API密钥 (仅提示)
check_api_key

ACTION=${1:-all} # 如果没有参数，默认为 "all"

case "$ACTION" in
    test)
        run_tests
        ;;
    run)
        run_main_py # main.py 内部会先运行测试
        ;;
    web)
        run_adk_web
        ;;
    all)
        run_tests
        tests_exit_code=$?
        if [ $tests_exit_code -eq 0 ]; then
            echo ""
            echo "所有可执行的测试通过。"
            run_main_py
        else
            echo ""
            echo "部分测试失败 (退出码: $tests_exit_code)。请检查错误。"
            echo "跳过通过 main.py 运行智能体。"
        fi
        ;;
    *)
        usage
        ;;
esac

echo ""
echo "脚本执行完毕。"
exit 0
