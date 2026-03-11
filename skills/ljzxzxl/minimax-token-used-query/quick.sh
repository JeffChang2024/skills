#!/bin/bash
# MiniMax Token 快速查询 - V3 版本
# 更新日期: 2026-03-09
# 基于实际页面测试更新（修复协议勾选问题）

echo "🔍 正在打开 MiniMax Coding Plan 页面..."

# 打开页面
browser-use --browser real --profile "Default" open "https://platform.minimaxi.com/user-center/payment/coding-plan"

# 等待页面加载
sleep 3

# 检查是否需要登录
PAGE_TEXT=$(browser-use --browser real --profile "Default" eval "document.body.innerText" 2>/dev/null)

if echo "$PAGE_TEXT" | grep -q "开放平台账户登录"; then
    echo "📱 需要登录，正在跳转登录页..."
    
    # 检查是否在登录页，如果是则直接进行登录流程
    if echo "$PAGE_TEXT" | grep -q "手机验证码登录"; then
        echo "📱 页面已是登录页，点击手机验证码登录..."
        browser-use --browser real --profile "Default" click 33
        sleep 2
    fi
    
    # 获取当前页面状态
    STATE=$(browser-use --browser real --profile "Default" state)
    
    # 提示用户输入手机号
    echo "⚠️ 请提供手机号："
    read -r PHONE
    
    # 输入手机号（先点击输入框获取焦点）
    echo "📱 输入手机号: $PHONE"
    # 找到手机号输入框（通常是 shadow DOM 内的 register_mail）
    PHONE_INPUT=$(echo "$STATE" | grep -oP 'register_mail.*?id=\K[0-9]+' | head -1 || echo "362")
    if [ -z "$PHONE_INPUT" ] || [ "$PHONE_INPUT" = "362" ]; then
        browser-use --browser real --profile "Default" click 362
    else
        browser-use --browser real --profile "Default" click $PHONE_INPUT
    fi
    browser-use --browser real --profile "Default" type "$PHONE"
    
    # 勾选用户协议 - 重要：点击 label 元素，不是链接！
    echo "📱 勾选用户协议（点击 label）..."
    # 尝试多个可能的元素 ID
    browser-use --browser real --profile "Default" click 390 2>/dev/null || \
    browser-use --browser real --profile "Default" click 420 2>/dev/null || \
    browser-use --browser real --profile "Default" click 176 2>/dev/null
    
    # 点击获取验证码
    echo "📱 点击获取验证码..."
    browser-use --browser real --profile "Default" click 389 2>/dev/null || \
    browser-use --browser real --profile "Default" click 654 2>/dev/null || \
    browser-use --browser real --profile "Default" click 257 2>/dev/null
    
    # 提示用户输入验证码
    echo "⚠️ 请提供验证码："
    read -r CODE
    
    # 输入验证码
    echo "📱 输入验证码: $CODE"
    # 找到验证码输入框
    CODE_INPUT=$(echo "$STATE" | grep -oP 'register_captcha.*?id=\K[0-9]+' | head -1 || echo "363")
    if [ -z "$CODE_INPUT" ] || [ "$CODE_INPUT" = "363" ]; then
        browser-use --browser real --profile "Default" click 363
    else
        browser-use --browser real --profile "Default" click $CODE_INPUT
    fi
    browser-use --browser real --profile "Default" type "$CODE"
    
    # 点击登录按钮
    echo "📱 点击登录..."
    browser-use --browser real --profile "Default" click 360 2>/dev/null || \
    browser-use --browser real --profile "Default" click 407 2>/dev/null || \
    browser-use --browser real --profile "Default" click 10 2>/dev/null
    
    # 等待登录完成
    sleep 3
fi

# 刷新页面获取最新数据
echo "🔄 刷新页面获取最新数据..."
browser-use --browser real --profile "Default" eval "location.reload()"
sleep 3

# 获取页面内容
PAGE_TEXT=$(browser-use --browser real --profile "Default" eval "document.body.innerText" 2>/dev/null)

# 提取使用百分比
USED=$(echo "$PAGE_TEXT" | grep -oE '[0-9]+% 已使用' | grep -oE '[0-9]+' || echo "0")

# 提取重置剩余时间 - 支持多种格式
# 格式1: "X 小时 Y 分钟后重置"
# 格式2: "X 分钟后重置"  
# 格式3: 从时间窗口计算

RESET_MINUTES=""

# 尝试提取 "X 小时 Y 分钟后" 格式
TEMP=$(echo "$PAGE_TEXT" | grep -oP '\d+\s*小时\s*\d+\s*分钟' | head -1)
if [ -n "$TEMP" ]; then
    HOURS=$(echo "$TEMP" | grep -oP '\d+(?=\s*小时)' | head -1)
    MINS=$(echo "$TEMP" | grep -oP '\d+(?=\s*分钟)' | head -1)
    if [ -n "$HOURS" ] && [ -n "$MINS" ]; then
        RESET_MINUTES=$((HOURS * 60 + MINS))
    fi
fi

# 如果没找到，尝试提取 "X 分钟后重置"
if [ -z "$RESET_MINUTES" ]; then
    TEMP=$(echo "$PAGE_TEXT" | grep -oP '\d+\s*分钟\s*后' | head -1)
    if [ -n "$TEMP" ]; then
        RESET_MINUTES=$(echo "$TEMP" | grep -oP '\d+' | head -1)
    fi
fi

# 如果还没找到，尝试提取 "X 小时后重置"
if [ -z "$RESET_MINUTES" ]; then
    TEMP=$(echo "$PAGE_TEXT" | grep -oP '\d+\s*小时\s*后' | head -1)
    if [ -n "$TEMP" ]; then
        HOURS=$(echo "$TEMP" | grep -oP '\d+' | head -1)
        if [ -n "$HOURS" ]; then
            RESET_MINUTES=$((HOURS * 60))
        fi
    fi
fi

# 如果都没找到，使用默认值
if [ -z "$RESET_MINUTES" ]; then
    RESET_MINUTES="0"
fi

# 提取时间窗口
TIME_WINDOW=$(echo "$PAGE_TEXT" | grep -oE '[0-9]+:[0-9]+-[0-9]+:[0-9+]+(UTC+8)?' | head -1 || echo "")

# 提取可用额度
TOTAL_PROMPTS=$(echo "$PAGE_TEXT" | grep -oE '[0-9]+ prompts' | grep -oE '[0-9]+' || echo "0")
TOTAL_HOURS=$(echo "$PAGE_TEXT" | grep -oE '[0-9]+ 小时' | grep -oE '[0-9]+' | head -1 || echo "0")

echo ""
echo "📊 MiniMax Token 使用情况："
echo "========================"
echo "已使用: ${USED}%"
echo "重置剩余: ${RESET_MINUTES} 分钟"
echo "可用额度: ${TOTAL_PROMPTS} prompts / ${TOTAL_HOURS} 小时"
if [ -n "$TIME_WINDOW" ]; then
    echo "时间窗口: $TIME_WINDOW"
fi
echo "========================"

# 如果使用超过 90%，发出警告
if [ "$USED" -ge 90 ]; then
    echo ""
    echo "⚠️ 警告：Token 使用量已达 ${USED}%！即将耗尽，请注意！"
fi

# 截图保存
browser-use --browser real --profile "Default" screenshot /tmp/minimax-token-query.png 2>/dev/null
echo "📸 截图已保存到 /tmp/minimax-token-query.png"
