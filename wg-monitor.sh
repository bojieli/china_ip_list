#!/bin/bash

WG_INTERFACE="utun4"  # 根据您实际使用的WireGuard接口名称修改
LAST_STATE="down"

while true; do
    # 检查WireGuard接口状态
    if ifconfig $WG_INTERFACE &>/dev/null; then
        CURRENT_STATE="up"
    else
        CURRENT_STATE="down"
    fi
    
    # 状态变化时执行脚本
    if [ "$CURRENT_STATE" != "$LAST_STATE" ]; then
        if [ "$CURRENT_STATE" = "up" ]; then
            /Users/boj/china_ip_list/wg-up.sh
            echo "WireGuard up, routing script executed."
        else
            /Users/boj/china_ip_list/wg-down.sh
            echo "WireGuard down, routes removed."
        fi
        LAST_STATE=$CURRENT_STATE
    fi
    
    sleep 5
done
