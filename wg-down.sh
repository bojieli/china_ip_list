#!/bin/bash

# 文件路径
IP_LIST="/Users/boj/china_ip_list/aggregated_china_ip_list.txt"

# 检查聚合文件是否存在
if [ ! -f "$IP_LIST" ]; then
    echo "错误：聚合IP列表文件不存在"
    exit 1
fi

# 创建临时脚本
TEMP_SCRIPT=$(mktemp /tmp/routes.XXXXXX)
echo "#!/bin/bash" > "$TEMP_SCRIPT"

# 生成删除路由命令
while IFS= read -r line; do
    # 跳过注释和空行
    [[ "$line" =~ ^#.*$ ]] || [[ -z "$line" ]] && continue
    # 添加删除路由命令
    echo "route delete -net $line 2>/dev/null || true" >> "$TEMP_SCRIPT"
done < "$IP_LIST"

# 执行批处理
chmod +x "$TEMP_SCRIPT"
echo "删除路由中..."
sudo "$TEMP_SCRIPT"
echo "路由已成功删除"

# 清理
rm "$TEMP_SCRIPT"
