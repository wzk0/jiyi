import json
import random
import string
import os

def generate_random_string(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def add_code_to_json_data(json_data):
    for key in json_data:
        if isinstance(json_data[key], list):
            for item in json_data[key]:
                if isinstance(item, dict):
                    item['code'] = generate_random_string()
    return json_data

def process_achievement_json(filepath='achievement.json'):
    if not os.path.exists(filepath): # 检查文件是否存在
        print(f"错误: 文件 '{filepath}' 不存在。请先创建该文件并放入 JSON 数据。")
        return

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"错误: 文件 '{filepath}' 内容不是有效的 JSON 格式。")
        return
    except Exception as e:
        print(f"读取文件时发生错误: {e}")
        return

    updated_data = add_code_to_json_data(data)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, indent=4, ensure_ascii=False)
        print(f"成功更新 '{filepath}' 文件，并添加了 'code' 字段。")
    except Exception as e:
        print(f"写入文件时发生错误: {e}")

process_achievement_json()