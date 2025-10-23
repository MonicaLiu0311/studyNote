"""
任务分配器 (Assigner)
功能：基于负载均衡策略将任务分配给团队成员
设计目标：确保团队成员的任务分配公平，避免某些成员过载
"""

from config.settings import Config
from collections import defaultdict  # 使用默认字典记录任务数

class Assigner:
    def __init__(self):
        """
        初始化任务分配器
        
        属性：
        - member_load : defaultdict[int] 
          键为成员名，值为当前分配的任务数（自动初始化为0）
        - total_assignments : int
          总分配任务数（用于轮询计数）
        """
        self.member_load = defaultdict(int)  # 记录每个成员的任务数
        # 使用Config中的团队成员
        for member in Config.TEAM_MEMBERS:
            self.member_load[member] = 0  # 初始化为0个任务

        self.total_assignments = 0  # 总分配次数计数器

    def get_next_assignee(self) -> str:
        """
        获取下一个应分配任务的成员（基于负载均衡策略）
        
        算法步骤：
        1. 找到当前任务最少的成员列表
        2. 在低负载成员中轮询选择（避免总是选同一个成员）
        3. 更新成员负载计数
        
        返回：
            str: 被选中的成员用户名
        """
        # 确保成员列表不为空
        if not self.member_load:
            raise ValueError("团队成员列表为空，请检查配置")
        
        # Step 1: 确定当前最低负载值
        min_load = min(self.member_load.values())  # 所有成员中的最小任务数
        
        # Step 2: 筛选所有处于最低负载状态的成员
        candidates = [
            member 
            for member, load in self.member_load.items() 
            if load == min_load
        ]
        
        # Step 3: 在候选成员中轮询选择
        # 使用总分配数取模确保公平轮换
        assignee = candidates[self.total_assignments % len(candidates)]
        
        # Step 4: 更新状态
        self.member_load[assignee] += 1  # 增加该成员的任务计数
        self.total_assignments += 1      # 增加总分配次数
        
        return assignee

    def reset(self):
        """
        重置分配器状态（用于测试或重新开始分配）
        """
        self.member_load.clear()
        self.total_assignments = 0

    def get_current_load(self) -> dict:
        """
        获取当前所有成员的任务负载情况
        
        返回：
            dict: {成员名: 任务数} 的字典
        """
        return dict(self.member_load)  # 转换为普通字典返回