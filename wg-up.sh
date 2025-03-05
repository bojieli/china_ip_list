#!/bin/bash

# 文件路径
IP_LIST="/Users/boj/china_ip_list/aggregated_china_ip_list.txt"

# 如果聚合文件不存在，先创建
if [ ! -f "$IP_LIST" ]; then
    echo "Aggregated IP list not found. Creating it now..."
    python3 /Users/boj/china_ip_list/aggregate_routes.py
fi

# 获取默认网关
DEFAULT_GATEWAY=$(netstat -nr | grep default | grep -v "link#" | grep -v "fe80::" | head -1 | awk '{print $2}')
echo "Using default gateway: $DEFAULT_GATEWAY"

# 创建临时脚本
TEMP_SCRIPT=$(mktemp /tmp/routes.XXXXXX)
echo "#!/bin/bash" > "$TEMP_SCRIPT"

# 生成路由命令
while IFS= read -r line; do
    [[ "$line" =~ ^#.*$ ]] || [[ -z "$line" ]] && continue
    echo "route add -net $line $DEFAULT_GATEWAY" >> "$TEMP_SCRIPT"
done < "$IP_LIST"

# 执行批处理
chmod +x "$TEMP_SCRIPT"
echo "Adding routes in batch mode..."
sudo "$TEMP_SCRIPT"
echo "Routes added successfully"

# 清理
rm "$TEMP_SCRIPT"
