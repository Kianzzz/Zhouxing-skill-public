#!/bin/bash

# OpenCLI 环境检测脚本
# 检查 OpenCLI 是否安装、守护进程是否运行、浏览器扩展是否连接

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🏥 OpenCLI 环境检查"
echo ""

# 检查 1: OpenCLI 是否安装
echo -n "检查 OpenCLI 安装... "
if command -v opencli &> /dev/null; then
    VERSION=$(opencli --version 2>&1 | head -1)
    echo -e "${GREEN}✅ 已安装${NC} ($VERSION)"
    OPENCLI_INSTALLED=true
else
    echo -e "${RED}❌ 未安装${NC}"
    echo ""
    echo "请安装 OpenCLI:"
    echo "  npm install -g @jackwener/opencli"
    echo ""
    exit 1
fi

# 检查 2: 守护进程状态
echo -n "检查守护进程... "
DAEMON_STATUS=$(opencli daemon status 2>&1 || echo "error")

if echo "$DAEMON_STATUS" | grep -q '"running": true'; then
    PID=$(echo "$DAEMON_STATUS" | grep -o '"pid": [0-9]*' | grep -o '[0-9]*')
    UPTIME=$(echo "$DAEMON_STATUS" | grep -o '"uptime": "[^"]*"' | cut -d'"' -f4)
    echo -e "${GREEN}✅ 运行中${NC} (PID: $PID, 运行时间: $UPTIME)"
    DAEMON_RUNNING=true
else
    echo -e "${YELLOW}⚠️  未运行${NC}"
    echo "  守护进程会在首次使用时自动启动"
    DAEMON_RUNNING=false
fi

# 检查 3: 浏览器扩展连接
echo -n "检查浏览器扩展... "
if [ "$DAEMON_RUNNING" = true ]; then
    if echo "$DAEMON_STATUS" | grep -q '"extensionConnected": true'; then
        echo -e "${GREEN}✅ 已连接${NC}"
        EXTENSION_CONNECTED=true
    else
        echo -e "${RED}❌ 未连接${NC}"
        echo ""
        echo "请安装并启用浏览器扩展:"
        echo "  1. 访问 https://github.com/jackwener/opencli/releases"
        echo "  2. 下载 opencli-extension.zip"
        echo "  3. 解压并在 chrome://extensions 中加载"
        echo "  4. 确保 Chrome/Chromium 正在运行"
        echo ""
        EXTENSION_CONNECTED=false
    fi
else
    echo -e "${YELLOW}⚠️  守护进程未运行，无法检查${NC}"
    EXTENSION_CONNECTED=false
fi

# 检查 4: 测试搜索命令（可选）
if [ "$EXTENSION_CONNECTED" = true ]; then
    echo ""
    echo "测试搜索命令..."

    # 测试小红书搜索
    echo -n "  小红书搜索... "
    if opencli xiaohongshu search "test" --limit 1 --format json &> /dev/null; then
        echo -e "${GREEN}✅${NC}"
    else
        echo -e "${YELLOW}⚠️  失败（可能需要登录）${NC}"
    fi

    # 测试微博搜索
    echo -n "  微博搜索... "
    if opencli weibo search "test" --limit 1 --format json &> /dev/null; then
        echo -e "${GREEN}✅${NC}"
    else
        echo -e "${YELLOW}⚠️  失败（可能需要登录）${NC}"
    fi

    # 测试 Twitter 搜索
    echo -n "  Twitter 搜索... "
    if opencli twitter search "test" --limit 1 --format json &> /dev/null; then
        echo -e "${GREEN}✅${NC}"
    else
        echo -e "${YELLOW}⚠️  失败（可能需要登录）${NC}"
    fi
fi

# 总结
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ "$OPENCLI_INSTALLED" = true ] && [ "$EXTENSION_CONNECTED" = true ]; then
    echo -e "${GREEN}✅ 环境就绪，可以开始搜索${NC}"
    exit 0
elif [ "$OPENCLI_INSTALLED" = true ] && [ "$DAEMON_RUNNING" = false ]; then
    echo -e "${YELLOW}⚠️  守护进程未运行，首次搜索时会自动启动${NC}"
    exit 0
else
    echo -e "${RED}❌ 环境未就绪，请按照上述提示完成配置${NC}"
    exit 1
fi
