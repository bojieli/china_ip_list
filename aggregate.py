#!/usr/bin/env python3
import ipaddress
import sys
from itertools import groupby

def aggregate_networks(networks):
    """以更可靠的方式聚合IP网络列表"""
    # 确保网络已排序
    networks.sort()
    
    # 初始化结果列表
    result = []
    
    # 跟踪当前的超网
    current = None
    
    for net in networks:
        # 如果是第一个网络，或当前网络与上一个不连续
        if current is None:
            current = net
            continue
        
        # 尝试与当前网络聚合
        if current.overlaps(net) or current.supernet_of(net):
            # 当前网络已包含此网络，跳过
            continue
            
        # 检查是否可以合并（相邻网络）
        if current.broadcast_address + 1 == net.network_address:
            # 尝试将两个网络合并为一个超网
            try:
                # 找到可以包含两个网络的最小超网
                combined = False
                
                # 从最小的超网开始测试
                for prefix_len in range(min(current.prefixlen, net.prefixlen) - 1, -1, -1):
                    try:
                        # 尝试创建一个包含两个网络的超网
                        supernet = ipaddress.ip_network(f"{current.network_address}/{prefix_len}", strict=False)
                        
                        # 检查超网是否恰好包含这两个网络而没有额外的地址范围
                        if (supernet.network_address == current.network_address and 
                            supernet.broadcast_address >= net.broadcast_address and
                            # 确保超网不会包含太多额外的地址
                            (supernet.num_addresses <= 2 * (current.num_addresses + net.num_addresses))):
                            current = supernet
                            combined = True
                            break
                    except ValueError:
                        continue
                
                if not combined:
                    result.append(current)
                    current = net
            except ValueError:
                # 如果无法合并，添加当前网络并继续
                result.append(current)
                current = net
        else:
            # 不相邻的网络，添加当前网络并继续
            result.append(current)
            current = net
    
    # 添加最后一个网络
    if current is not None:
        result.append(current)
    
    return result

def read_ip_list(filename):
    """从文件读取IP列表，跳过注释和空行"""
    networks = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            try:
                networks.append(ipaddress.ip_network(line))
            except ValueError as e:
                print(f"警告: 跳过无效网络 '{line}': {e}")
    return networks

def main():
    input_file = "/Users/boj/china_ip_list/china_ip_list.txt"
    output_file = "/Users/boj/china_ip_list/aggregated_china_ip_list.txt"
    
    print("读取IP列表...")
    networks = read_ip_list(input_file)
    original_count = len(networks)
    print(f"原始路由数量: {original_count}")
    
    print("聚合路由中...")
    # 初步聚合重叠网络
    networks = list(set(networks))  # 移除完全重复的网络
    
    # 进行多轮聚合以处理复杂情况
    prev_count = len(networks) + 1
    while len(networks) < prev_count:
        prev_count = len(networks)
        networks = aggregate_networks(networks)
    
    aggregated_count = len(networks)
    print(f"聚合后路由数量: {aggregated_count}")
    print(f"减少了: {original_count - aggregated_count} 条目 ({(original_count - aggregated_count) / original_count * 100:.2f}%)")
    
    # 将聚合后的路由写入文件
    with open(output_file, 'w') as f:
        for net in networks:
            f.write(f"{net}\n")
    
    print(f"聚合后的路由已保存到: {output_file}")

if __name__ == "__main__":
    main()
