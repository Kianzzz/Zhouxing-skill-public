#!/bin/bash

# Voice Collector - 自动从日常对话中提取口语表达特征
# 每天定时运行，完全自动化，无需手动触发

set -e

SKILL_DIR="$HOME/.claude/skills/writing-copilot"
BUFFER_DIR="$SKILL_DIR/references/conversation-buffer"
SPOKEN_VOICE="$SKILL_DIR/references/spoken-voice.md"
TODAY=$(date +%Y-%m-%d)
BUFFER_FILE="$BUFFER_DIR/$TODAY.txt"

# 检查今天是否有对话记录
if [ ! -f "$BUFFER_FILE" ]; then
    echo "[$(date)] 今天没有对话记录，跳过分析"
    exit 0
fi

# 检查文件是否为空
if [ ! -s "$BUFFER_FILE" ]; then
    echo "[$(date)] 对话记录为空，跳过分析"
    rm -f "$BUFFER_FILE"
    exit 0
fi

# 调用Claude分析对话内容
echo "[$(date)] 开始分析今天的对话..."

claude --model sonnet << 'EOF'
你是一个语言风格分析专家。

任务：从用户的日常对话中提取口语化表达特征。

对话记录文件：~/.claude/skills/writing-copilot/references/conversation-buffer/$(date +%Y-%m-%d).txt

步骤：
1. 读取今天的对话记录文件
2. 过滤掉非自然语言内容：
   - 命令式输入（"读取文件"、"运行测试"、"写入XX"）
   - 代码片段
   - 文件路径
   - 单纯的"好的"、"谢谢"、"明白了"
3. 提取有特色的口语表达：
   - 语气词：出现3次以上的（"其实"、"就是"、"真的"、"确实"）
   - 转场词：用于话题转换的（"说来惭愧"、"老实说"、"不过"）
   - 口头禅：用户特有的高频表达
   - 句式习惯：反问句、设问句、短句风格
4. 读取 ~/.claude/skills/writing-copilot/references/spoken-voice.md
5. 与已有内容对比去重，只保留新发现的表达
6. 如果有新发现，追加到 spoken-voice.md，格式：

## YYYY-MM-DD 自动提取

**语气词**：
- "表达" - 出现X次，使用场景说明

**转场词**：
- "表达" - 使用场景说明

**句式习惯**：
- 具体描述

7. 删除今天的缓冲文件（已分析完毕）

重要：
- 只提取真正有特色的表达，不要记录平淡无奇的
- 严格去重，不要重复记录
- 如果今天没有新发现，不要追加任何内容
- 静默执行，只在有错误时输出

开始执行。
EOF

echo "[$(date)] 分析完成"
