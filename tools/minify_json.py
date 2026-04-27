import json
import os
import sys


def minify_directory(directory_path):
    # 检查路径是否存在
    if not os.path.isdir(directory_path):
        print(f"错误: 找不到目录 '{directory_path}'")
        return

    count = 0
    # os.walk 会递归遍历子文件夹
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.lower().endswith(".json"):
                file_path = os.path.join(root, file)
                try:
                    # 1. 读取并解析
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    # 2. 原地覆盖写入，使用最小化分隔符
                    with open(file_path, "w", encoding="utf-8") as f:
                        # separators=(",", ":") 关键：去掉逗号和冒号后的空格
                        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

                    print(f"已最小化: {file_path}")
                    count += 1
                except Exception as e:
                    print(f"处理失败 {file_path}: {e}")

    print(f"\n--- 任务完成！共处理 {count} 个文件 ---")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python minify_all_json.py <目录路径>")
        sys.exit(1)

    target_dir = sys.argv[1]
    minify_directory(target_dir)
