import json
import os
import string
import random
import base64
import zlib
from httpx import get as httpx_get
import csv

achievement_path = 'data/achievement.json'
extension_path = 'data/extension.json'

def check_update(version):
    api_url = "https://api.github.com/repos/wzk0/jiyi/releases/latest"
    try:
        response = httpx_get(api_url)
        response.raise_for_status()
        release_data = response.json()
    except Exception as e:
        error_msg = f"获取 release 信息时出错: {e}"
        print(error_msg)
        return {"new": False, "log": error_msg, "link": ""}
    github_version = release_data.get("tag_name")
    release_log = release_data.get("body", "")
    release_link = release_data.get("html_url", "")
    if not github_version:
        error_msg = "无法从 GitHub release 数据中获取版本号。"
        print(error_msg)
        return {"new": False, "log": error_msg, "link": release_link}
    has_update = (github_version != version)
    return {"new": has_update, "log": release_log, "link": release_link}

def done_achievement(sublist_name, code_to_find):
    if not os.path.exists(achievement_path):
        return False
    try:
        with open(achievement_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    except json.JSONDecodeError:
        return False
    except Exception:
        return False

    if sublist_name not in json_data:
        return False
    sublist = json_data[sublist_name]
    if not isinstance(sublist, list):
        return False
    for item in sublist:
        if isinstance(item, dict) and 'code' in item and item['code'] == code_to_find:
            if 'done' in item:
                item['done'] = True
                try:
                    with open(achievement_path, 'w', encoding='utf-8') as f:
                        json.dump(json_data, f, indent=4, ensure_ascii=False)
                    return True
                except Exception:
                    return False
            else:
                return False
    else:
        return False

def undone_achievement(sublist_name, code_to_find):
    if not os.path.exists(achievement_path):
        return False
    try:
        with open(achievement_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    except json.JSONDecodeError:
        return False
    except Exception:
        return False

    if sublist_name not in json_data:
        return False
    sublist = json_data[sublist_name]
    if not isinstance(sublist, list):
        return False
    for item in sublist:
        if isinstance(item, dict) and 'code' in item and item['code'] == code_to_find:
            if 'done' in item:
                item['done'] = False
                try:
                    with open(achievement_path, 'w', encoding='utf-8') as f:
                        json.dump(json_data, f, indent=4, ensure_ascii=False)
                    return True
                except Exception:
                    return False
            else:
                return False
    else:
        return False

def get_sublist_by_name(sublist_name):
    if not os.path.exists(achievement_path):
        return None
    try:
        with open(achievement_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    except json.JSONDecodeError:
        return None
    except Exception:
        return None

    if sublist_name not in json_data:
        return None
    sublist = json_data[sublist_name]
    if not isinstance(sublist, list):
        return None
    return sublist

def generate_random_string(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def delete_achievement(sublist_name, code_to_find):
    if not os.path.exists(achievement_path):
        return False
    try:
        with open(achievement_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    except json.JSONDecodeError:
        return False
    except Exception:
        return False

    if sublist_name not in json_data:
        return False
    target_sublist = json_data[sublist_name]  # 使用 sublist_name 参数
    if not isinstance(target_sublist, list):
        return False

    index_to_delete = -1 # 初始化为 -1 表示未找到
    for index, item in enumerate(target_sublist): # 遍历目标子列表
        if isinstance(item, dict) and 'code' in item and item['code'] == code_to_find:
            index_to_delete = index
            break # 找到匹配项后跳出循环

    if index_to_delete != -1:
        del target_sublist[index_to_delete] # 删除指定索引的元素
        try:
            with open(achievement_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=4, ensure_ascii=False)
            return True
        except Exception:
            return False
    else:
        return False # 未找到指定 code 的字典
    
def add_mine(title, description):
    if not os.path.exists(achievement_path):
        return False, None
    try:
        with open(achievement_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    except json.JSONDecodeError:
        return False, None
    except Exception:
        return False, None

    if 'mine' not in json_data:
        json_data['mine'] = []
    if not isinstance(json_data['mine'], list):
        return False, None

    code = generate_random_string()
    new_item = {
        "title": title,
        "description": description,
        "code": code,
        "done": False
    }
    json_data['mine'].append(new_item)

    try:
        with open(achievement_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)
        return True, code
    except Exception:
        return False, None
    
def get_color():
    with open('data/color.json', 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    return json_data

def encode_json(data):
    json_str=json.dumps(data, separators=(',', ':'), ensure_ascii=False)
    return base64.urlsafe_b64encode(zlib.compress(json_str.encode('utf-8'))).decode('utf-8')

def decode_json(data):
    compressed_data = base64.urlsafe_b64decode(data.encode('utf-8'))
    return json.loads(zlib.decompress(compressed_data).decode('utf-8'))

def get_extension_list():
    with open(extension_path, encoding="utf-8") as f:
        extensions = json.load(f)
    return [e['name'] for e in extensions]

def load_extension_config(name):
    with open(extension_path, encoding="utf-8") as f:
        extensions = json.load(f)
    for ext in extensions:
        if ext["name"] == name:
            return ext
    raise ValueError(f"未找到名为 {name} 的插件配置")

def open_csv_file(csv_path):
    try:
        return open(csv_path, newline="", encoding="utf-8")
    except UnicodeDecodeError:
        return open(csv_path, newline="", encoding="gbk", errors="ignore")

def parse_rule(row, rule):
    parsed_data = {}
    for field, expression in rule.items():
        if field == "value":
            try:
                parsed_data[field] = round(float(row[int(expression.strip("$"))].replace('￥','')), 2)
            except (ValueError, IndexError):
                parsed_data[field] = 0.0
        elif field == "tag" and isinstance(expression, list):
            tag = [row[int(col.strip("$"))] for col in expression if int(col.strip("$")) < len(row)]
            bug = ['',' ','/','\\']
            tags = [x for x in tag if x not in bug]
            parsed_data[field] = tags
        elif field == "earn" and "earn_list" in rule:
            earn_value = row[int(expression.strip("$"))] if int(expression.strip("$")) < len(row) else ""
            parsed_data[field] = earn_value in rule["earn_list"]
        elif field == 'date':
            value = expression
            for i, cell in enumerate(row):
                value = value.replace(f"${i}", cell).replace('/', '-')
                if value.count(':')==0:
                    value = value + ' 00:00:00'
                elif value.count(':')==1:
                    value = value + ':00'
                elif value.count(':')==2:
                    value = value
            parsed_data[field] = value
        elif field != 'earn_list':
            value = expression
            for i, cell in enumerate(row):
                value = str(value).replace(f"${i}", cell)
            parsed_data[field] = value
    return parsed_data

def read_billing_csv(csv_path, name, new_ext=False):
    if new_ext == False:
        config = load_extension_config(name)
        start_line = config.get("start_line", 0)
        end_line = config.get("end_line", False)
        rule = {k: v for d in config.get("rule", []) for k, v in d.items()}
    else:
        start_line = new_ext['start_line']
        end_line = new_ext['end_line']
        rule = new_ext
    with open_csv_file(csv_path) as f:
        reader = csv.reader(f)
        rows = list(reader)
    if start_line >= len(rows):
        raise ValueError("start_line 超出文件范围")
    data_rows = rows[start_line + 1 :] if end_line is False else rows[start_line + 1 : end_line]
    return [parse_rule(row, rule) for row in data_rows]

# print(encode_json(read_billing_csv("data/2.csv", "支付宝")))