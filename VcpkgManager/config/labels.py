"""
Issue/PR 标签分类系统
"""
LABEL_DEFINITIONS = {
    "issues": {
        "bug": {
            "name": "bug",  # 添加name字段
            "color": "d73a4a", 
            "description": "Something isn't working"
        },
        "enhancement": {
            "name": "enhancement",
            "color": "a2eeef", 
            "description": "New feature request"
        },
        "question": {
            "name": "question",
            "color": "d876e3", 
            "description": "Further information is requested"
        }
    },
    "prs": {
        "new-port": {
            "name": "new-port",
            "color": "fbca04", 
            "description": "Adds a new port"
        },
        "port-update": {
            "name": "port-update",
            "color": "0e8a16", 
            "description": "Updates existing port"
        },
        "infra": {
            "name": "infra",
            "color": "006b75", 
            "description": "Infrastructure changes"
        }
    }
}