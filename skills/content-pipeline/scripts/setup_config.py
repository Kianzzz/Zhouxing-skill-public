#!/usr/bin/env python3
"""
配置向导脚本
首次运行 content-pipeline 时，引导用户完成配置
"""

import json
import os
from pathlib import Path

CONFIG_PATH = Path.home() / ".claude" / "skills" / "content-pipeline" / "config.json"

def setup_config():
    """交互式配置向导"""
    print("=== Content Pipeline 配置向导 ===\n")

    config = {}

    # 1. Obsidian Vault 路径
    print("1. Obsidian Vault 路径")
    print("   请输入你的 Obsidian 知识库路径")
    default_vault = str(Path.home() / "Library" / "Mobile Documents" / "iCloud~md~obsidian" / "Documents" / "Obsidian2025")
    vault_path = input(f"   路径 (默认: {default_vault}): ").strip()
    config["obsidian_vault_path"] = vault_path if vault_path else default_vault

    # 2. 默认配图风格
    print("\n2. 默认配图风格")
    print("   nanobanana-illustrator 需要指定配图风格")
    illustration_style = input("   风格名称 (默认: 周行IP的配图资料): ").strip()
    config["illustration_style"] = illustration_style if illustration_style else "周行IP的配图资料"

    # 3. 输出策略
    print("\n3. 输出策略")
    print("   a) 在 vault 根目录创建主题文件夹（推荐）")
    print("   b) 保存在 vault 根目录")
    print("   c) 保存在 Articles/ 文件夹")
    output_choice = input("   选择 (a/b/c, 默认: a): ").strip().lower()
    output_map = {
        "a": "create_folder_in_vault_root",
        "b": "vault_root",
        "c": "articles_folder",
        "": "create_folder_in_vault_root"
    }
    config["output_strategy"] = output_map.get(output_choice, "create_folder_in_vault_root")

    # 4. 素材保留策略
    print("\n4. 素材保留策略")
    print("   是否保留中间素材文件？")
    keep_choice = input("   保留素材 (y/n, 默认: y): ").strip().lower()
    config["keep_materials"] = keep_choice != "n"

    # 5. 失败处理策略
    print("\n5. 失败处理策略")
    print("   a) 遇到问题立即停止并报告（推荐）")
    print("   b) 尽力继续，跳过失败环节")
    failure_choice = input("   选择 (a/b, 默认: a): ").strip().lower()
    config["failure_strategy"] = "continue_on_error" if failure_choice == "b" else "stop_and_report"

    # 保存配置
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"\n✅ 配置已保存到: {CONFIG_PATH}")
    print("\n配置内容：")
    print(json.dumps(config, indent=2, ensure_ascii=False))

    return config

def load_config():
    """加载配置文件"""
    if not CONFIG_PATH.exists():
        return None

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

if __name__ == "__main__":
    config = setup_config()
