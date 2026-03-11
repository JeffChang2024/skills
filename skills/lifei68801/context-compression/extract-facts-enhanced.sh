#!/bin/bash
# Extract Facts Enhanced - v2.0
# 更智能的事实提取，结构化存储

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
MEMORY_FILE="$WORKSPACE/MEMORY.md"
FACTS_DIR="$WORKSPACE/memory/facts"
LOG_FILE="${LOG_FILE:-$HOME/.openclaw/logs/truncation.log}"

# Feature toggles
ENABLE_FACT_EXTRACTION="${ENABLE_FACT_EXTRACTION:-true}"

mkdir -p "$FACTS_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# ===== 高价值模式检测 =====

# 用户偏好模式
detect_preference() {
    local text=$1
    local patterns=(
        "我喜欢"
        "我偏好"
        "我讨厌"
        "我反感"
        "我想要"
        "我不想要"
        "我习惯"
        "我的风格"
        "我喜欢的是"
        "我倾向于"
        "我更喜欢"
        "我不喜欢"
        "千万别"
        "一定要"
        "绝对不要"
        "最讨厌"
        "最喜欢"
    )
    
    for pattern in "${patterns[@]}"; do
        if [[ "$text" == *"$pattern"* ]]; then
            return 0
        fi
    done
    return 1
}

# 重要决策模式
detect_decision() {
    local text=$1
    local patterns=(
        "决定了"
        "确定是"
        "选定"
        "就选"
        "定下了"
        "最终方案"
        "确认使用"
        "达成共识"
        "一致决定"
        "拍板"
        "定了"
        "就用这个"
    )
    
    for pattern in "${patterns[@]}"; do
        if [[ "$text" == *"$pattern"* ]]; then
            return 0
        fi
    done
    return 1
}

# 任务状态模式
detect_task() {
    local text=$1
    local patterns=(
        "TODO"
        "待办"
        "任务"
        "要完成"
        "需要做"
        "正在进行"
        "进行中"
        "待处理"
        "优先级"
        "截止日期"
        "deadline"
        "里程碑"
    )
    
    for pattern in "${patterns[@]}"; do
        if [[ "$text" == *"$pattern"* ]]; then
            return 0
        fi
    done
    return 1
}

# 重要提醒模式
detect_important() {
    local text=$1
    local patterns=(
        "记住"
        "重要"
        "关键"
        "别忘"
        "提醒我"
        "注意"
        "务必"
        "一定要"
        "千万别忘"
        "特别注意"
    )
    
    for pattern in "${patterns[@]}"; do
        if [[ "$text" == *"$pattern"* ]]; then
            return 0
        fi
    done
    return 1
}

# 时间相关模式
detect_time() {
    local text=$1
    local patterns=(
        "明天"
        "后天"
        "下周"
        "下个月"
        "周一"
        "周二"
        "周三"
        "周四"
        "周五"
        "周六"
        "周日"
        "[0-9]月[0-9]日"
        "[0-9]月[0-9]号"
        "[0-9]:[0-9]"
        "上午"
        "下午"
        "晚上"
        "几点"
    )
    
    for pattern in "${patterns[@]}"; do
        if [[ "$text" =~ $pattern ]]; then
            return 0
        fi
    done
    return 1
}

# 人物关系模式
detect_relationship() {
    local text=$1
    local patterns=(
        "同事"
        "老板"
        "领导"
        "客户"
        "朋友"
        "家人"
        "老婆"
        "老公"
        "孩子"
        "父母"
        "合作伙伴"
        "供应商"
    )
    
    for pattern in "${patterns[@]}"; do
        if [[ "$text" == *"$pattern"* ]]; then
            return 0
        fi
    done
    return 1
}

# 从 JSONL 提取文本
extract_text_from_jsonl() {
    local line=$1
    
    # 尝试解析 JSON 提取 content/text 字段
    if command -v jq &> /dev/null; then
        local content=$(echo "$line" | jq -r '.content // .text // .message.content // empty' 2>/dev/null)
        [ -n "$content" ] && echo "$content" && return
    fi
    
    # Fallback: 正则匹配
    if [[ "$line" =~ '"content"[[:space:]]*:[[:space:]]*"([^"]+)"' ]]; then
        echo "${BASH_REMATCH[1]}"
    elif [[ "$line" =~ '"text"[[:space:]]*:[[:space:]]*"([^"]+)"' ]]; then
        echo "${BASH_REMATCH[1]}"
    fi
}

# 提取事实并分类存储
extract_and_classify() {
    local text=$1
    local source=$2
    local timestamp=$(date '+%Y-%m-%d_%H%M%S')
    
    [ -z "$text" ] && return
    
    # 分类存储
    local facts_found=0
    
    if detect_preference "$text"; then
        echo "[PREFERENCE] $text" >> "$FACTS_DIR/preferences.log"
        echo "$timestamp|$source|$text" >> "$FACTS_DIR/preferences.tsv"
        ((facts_found++))
    fi
    
    if detect_decision "$text"; then
        echo "[DECISION] $text" >> "$FACTS_DIR/decisions.log"
        echo "$timestamp|$source|$text" >> "$FACTS_DIR/decisions.tsv"
        ((facts_found++))
    fi
    
    if detect_task "$text"; then
        echo "[TASK] $text" >> "$FACTS_DIR/tasks.log"
        echo "$timestamp|$source|$text" >> "$FACTS_DIR/tasks.tsv"
        ((facts_found++))
    fi
    
    if detect_important "$text"; then
        echo "[IMPORTANT] $text" >> "$FACTS_DIR/important.log"
        echo "$timestamp|$source|$text" >> "$FACTS_DIR/important.tsv"
        ((facts_found++))
    fi
    
    if detect_time "$text"; then
        echo "[TIME] $text" >> "$FACTS_DIR/time.log"
        echo "$timestamp|$source|$text" >> "$FACTS_DIR/time.tsv"
        ((facts_found++))
    fi
    
    if detect_relationship "$text"; then
        echo "[RELATIONSHIP] $text" >> "$FACTS_DIR/relationships.log"
        echo "$timestamp|$source|$text" >> "$FACTS_DIR/relationships.tsv"
        ((facts_found++))
    fi
    
    return $facts_found
}

# 同步到 MEMORY.md（合并同一天的事实）
sync_to_memory() {
    local today=$(date '+%Y-%m-%d')
    local section="## Truncated Facts - $today"
    
    # 检查今天是否已有章节
    if ! grep -q "$section" "$MEMORY_FILE" 2>/dev/null; then
        echo "" >> "$MEMORY_FILE"
        echo "$section" >> "$MEMORY_FILE"
        echo "> Auto-extracted from session truncation" >> "$MEMORY_FILE"
        echo "" >> "$MEMORY_FILE"
    fi
    
    # 追加新事实
    for category in preferences decisions tasks important time relationships; do
        local tsv_file="$FACTS_DIR/${category}.tsv"
        if [ -f "$tsv_file" ]; then
            local today_facts=$(grep "^$today" "$tsv_file" 2>/dev/null | tail -5)
            if [ -n "$today_facts" ]; then
                echo "### ${category^}" >> "$MEMORY_FILE"
                echo "$today_facts" | cut -d'|' -f3 | while read -r fact; do
                    echo "- $fact" >> "$MEMORY_FILE"
                done
                echo "" >> "$MEMORY_FILE"
            fi
        fi
    done
}

# 主处理逻辑
process_content() {
    local content=$1
    local source=$2
    local total_facts=0
    
    while IFS= read -r line; do
        [ -z "$line" ] && continue
        
        # 从 JSONL 提取文本
        local text=$(extract_text_from_jsonl "$line")
        [ -z "$text" ] && continue
        
        # 分类提取
        extract_and_classify "$text" "$source"
        local facts=$?
        [ $facts -gt 0 ] && ((total_facts += facts))
    done <<< "$content"
    
    echo $total_facts
}

# 入口
if [ -p /dev/stdin ]; then
    content=$(cat)
    source="${1:-unknown-session}"
    
    facts_count=$(process_content "$content" "$source")
    
    if [ "$facts_count" -gt 0 ]; then
        sync_to_memory
        log "📝 Extracted $facts_count facts from $source"
    fi
    
    echo "$facts_count"
fi
