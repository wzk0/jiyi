import json

def restructure_achievements(input_filepath="achievement.json", output_filepath="achievement.json"):
    try:
        with open(input_filepath, 'r', encoding='utf-8') as f:
            achievements_list = json.load(f)
    except FileNotFoundError:
        print(f"错误:: 文件 {input_filepath} 未找到.")
        return
    except json.JSONDecodeError:
        print(f"错误: 文件 {input_filepath} JSON 格式解码失败，请检查文件内容.")
        return

    categorized_achievements = {
        'earn': [],
        'spend': [],
        'other': []
    }

    for achievement in achievements_list:
        if achievement['earn'] == True:
            categorized_achievements['earn'].append(achievement)
        elif achievement['earn'] == False:
            categorized_achievements['spend'].append(achievement)
        else:
            categorized_achievements['other'].append(achievement)

    for category in categorized_achievements:
        categorized_achievements[category] = sorted(categorized_achievements[category], key=lambda x: x['value'])

    try:
        with open(output_filepath, 'w', encoding='utf-8') as f:
            json.dump(categorized_achievements, f, indent=4, ensure_ascii=False)
        print(f"成功: achievement.json 文件已重构并更新.")
    except Exception as e:
        print(f"错误: 写入文件 {output_filepath} 失败: {e}")


if __name__ == "__main__":
    restructure_achievements()