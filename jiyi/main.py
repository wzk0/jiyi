import flet as ft
import datetime
from tool import tool

JIYI_VERSION = '0.4.1'
HELP_URL = 'https://github.com/wzk0/jiyi/blob/main/HELP.md#45-%E5%AF%BC%E5%85%A5%E8%B4%A6%E5%8D%95'

def convert_to_float(value):
    try:
        return round(float(value), 2)
    except ValueError:
        return None

def get_date_difference(first_date, last_date):
    try:
        start_date = datetime.datetime.strptime(first_date, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(last_date, '%Y-%m-%d').date()
    except ValueError:
        print("日期格式错误，日期格式应为 'YYYY-MM-DD'，例如 '2025-02-08'。")
        return None
    time_difference = end_date - start_date
    days_difference = time_difference.days
    return days_difference

def get_source_data(data, earn):
    result = []
    if earn:
        for d in [s for s in data if s['earn']]:
            if d['source'] not in [r['name'] for r in result]:
                result.append({'name': d['source'], 'value': d['value']})
            else:
                for r in result:
                    if r['name'] == d['source']:
                        r['value'] += d['value']
    else:
        for d in [s for s in data if not s['earn']]:
            if d['source'] not in [r['name'] for r in result]:
                result.append({'name': d['source'], 'value': d['value']})
            else:
                for r in result:
                    if r['name'] == d['source']:
                        r['value'] += d['value']
    return [{'name': r['name'], 'value': convert_to_float(r['value'])} for r in result]

def analyze_tag(data):
    tags = []
    for d in data:
        for t in d['tag']:
            tags.append(t) 
    frequency = {}
    for item in tags:
        if item in frequency:
            frequency[item] += 1
        else:
            frequency[item] = 1
    sorted_frequency = sorted(frequency.items(), key=lambda item: item[1], reverse=True)
    result = []
    for item in sorted_frequency:
        result.append({'name':item[0], 'value': item[1]})
    return result

def make_old_to_new(old_data):
    new_data = []
    for item in old_data:
        old_tag = item.get('tag', '')
        tag_list = old_tag.split(' ')
        try:
            tag_list.remove('')
        except ValueError:
            pass
        source = tag_list[0] if tag_list and tag_list[0] else ''
        date = item.get('time', '')
        if date.count(':')==0:
            date = date + ' 00:00:00'
        elif date.count(':')==1:
            date = date + ':00'
        elif date.count(':')==2:
            date = date
        new_item = {
            'name': item.get('name', '未命名'),
            'value': convert_to_float(item.get('price', 0)),
            'tag': tag_list,
            'source': source,
            'date': date,
            'earn': item.get('earn', False)
        }
        new_data.append(new_item)
    return new_data

def main(page: ft.Page):
    
    color = page.client_storage.get('COLOR')
    dark = page.client_storage.get('DARK')
    color = color if color!=None else 'blue'
    page.theme = ft.Theme(color_scheme_seed=color)
    page.theme_mode = ft.ThemeMode.DARK if dark else ft.ThemeMode.LIGHT

    def get_account_data():
        account = page.client_storage.get('account')
        source = page.client_storage.get('source')
        account = account if account!=None else []
        source = source if source!=None else []
        earn_data = [a for a in account if a['earn']]
        earn_value = sum([convert_to_float(e['value']) for e in earn_data])
        earn_source = []
        earn_other = [a for a in earn_data if a['source'] == '']
        for e in [a for a in account if a['source'] != '']:
            if e['earn']:
                if e['source'] not in [s['source'] for s in earn_source]:
                    earn_source.append({'source':e['source'], 'times':1, 'value':convert_to_float(e['value'])})
                else:
                    for c in earn_source:
                        if c['source'] == e['source']:
                            c['times']+=1
                            c['value'] += convert_to_float(e['value'])
        spend_data = [a for a in account if a['earn'] == False]
        spend_value = sum([convert_to_float(s['value']) for s in spend_data])
        spend_source = []
        spend_other = [a for a in spend_data if a['source'] == '']
        for s in [a for a in account if a['source'] != '']:
            if s['earn']==False:
                if s['source'] not in [s['source'] for s in spend_source]:
                    spend_source.append({'source':s['source'], 'times':1, 'value':convert_to_float(s['value'])})
                else:
                    for c in spend_source:
                        if c['source'] == s['source']:
                            c['times']+=1
                            c['value'] += convert_to_float(s['value'])
        balance = []
        for b in source:
            plus_number = 0.00
            cost_number = 0.00
            if b['name'] in [e['source'] for e in earn_source]:
                plus_number = next((e['value'] for e in earn_source if e['source'] == b['name']), 0.00)
            if b['name'] in [s['source'] for s in spend_source]:
                cost_number = next((s['value'] for s in spend_source if s['source'] == b['name']), 0.00)
            balance.append({'name':b['name'], 'value':convert_to_float(plus_number)+convert_to_float(b['value'])-convert_to_float(cost_number)})
        other_balance = convert_to_float(sum([convert_to_float(e['value']) for e in earn_other]))-convert_to_float(sum([convert_to_float(s['value']) for s in spend_other]))
        return {'earn':{'total':convert_to_float(earn_value), 'times':len(earn_data), 'source':earn_source, 'total_other':convert_to_float(sum([convert_to_float(e['value']) for e in earn_other])), 'other_times':len(earn_other)}, 'spend':{'total':convert_to_float(spend_value), 'times':len(spend_data), 'source':spend_source, 'total_other':convert_to_float(sum([convert_to_float(s['value']) for s in spend_other])), 'other_times':len(spend_other)}, 'balance':{'total':convert_to_float(sum([b['value'] for b in balance])+(other_balance if int(other_balance)!=0 else 0)), 'times':len(balance), 'source':balance, 'total_other':other_balance if int(other_balance)!=0 else 0}}

    def get_account_data_by_date(first_date, last_date):
        filtered_data = []
        try:
            start_date = datetime.datetime.strptime(first_date, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(last_date, '%Y-%m-%d').date()
        except ValueError:
            print("日期格式错误，日期格式应为 'YYYY-MM-DD'，例如 '2025-02-08'。")
            return filtered_data
        if start_date > end_date:
            print("起始日期不能晚于结束日期。")
            return filtered_data
        data = page.client_storage.get('account')
        data = data if data!=None else []
        for item in data:
            if isinstance(item, dict) and 'date' in item:
                try:
                    item_datetime = datetime.datetime.strptime(item['date'], '%Y-%m-%d %H:%M:%S')
                    item_date = item_datetime.date()
                    if start_date <= item_date <= end_date:
                        filtered_data.append(item)
                except ValueError:
                    print(f"数据项日期格式错误: '{item['date']}'，应为 'YYYY-MM-DD HH:MM:SS'，已跳过该数据项。")
                    continue
            else:
                print("数据项格式错误，缺少 'date' 键或不是字典，已跳过该数据项。")
                continue

        return filtered_data

    def drawer_change(e):
        e = e.control.selected_index

        if e == 1:
            def color_change(e):
                color = e.control.parent.color.replace('200','')
                page.theme = ft.Theme(color_scheme_seed=color)
                page.client_storage.set('COLOR', color)
                page.close(color_dialog)
                page.update()
            color_dialog = ft.AlertDialog(scrollable=True, title=ft.Text('主题色'), content=ft.Column(spacing=5, controls=[
                ft.Card(color='%s200'%color['name'], content=ft.Container(on_click=color_change, padding=10, content=ft.Row(controls=[ft.Column(spacing=3, controls=[ft.Text(color['zh'], weight=ft.FontWeight.BOLD, size=15, color=ft.Colors.ON_PRIMARY), ft.Text(color['description'], color=ft.Colors.ON_PRIMARY)])]))) for color in tool.get_color()
            ]))
            page.open(color_dialog)

        if e == 2:
            dark = page.client_storage.get('DARK')
            if dark:
                page.theme_mode = ft.ThemeMode.LIGHT
                page.client_storage.set('DARK', False)
            else:
                page.theme_mode = ft.ThemeMode.DARK
                page.client_storage.set('DARK', True)
            page.update()

        if e == 3:
            def update_data_manage_dialog():
                data_manage_dialog.content.controls[0].content.content.controls[0].value = tool.encode_json(page.client_storage.get('account'))
                data_manage_dialog.content.controls[2].content.content.controls[0].value = page.client_storage.get('account')
            def update_import_dialog(e):
                def save_import(e):
                    data = tool.decode_json(import_dialog.content.controls[0].value)
                    if old:
                        try:
                            data = make_old_to_new(tool.decode_json(import_dialog.content.controls[0].value))
                        except:
                            page.open(ft.AlertDialog(title=ft.Text('错误'), content=ft.Text('数据格式错误.')))
                    page.client_storage.set('account', data)
                    page.open(ft.AlertDialog(title=ft.Text('成功!'), content=ft.Text('已成功导入%s组账目! 请切换页面以刷新.'%len(data))))
                old = True if e.control.text == '旧版数据导入' else False
                import_dialog = ft.AlertDialog(title=ft.Text('数据导入'), content=ft.Column(tight=True, controls=[
                    ft.TextField(label='请输入账目密文数据', multiline=True),
                ]), actions=[ft.TextButton(text='导入', on_click=save_import)])
                if old:
                    import_dialog.content.controls.append(ft.Text('由于新版与旧版在处理"来源"上的做法不同, 旧版数据导入后, 将会自动把旧版数据中的第一个"标签"转变为新版的"来源", 请在导入完成后添加同名来源.'))
                page.open(import_dialog)
            data_manage_dialog = ft.AlertDialog(scrollable=True, title=ft.Text('数据管理'), content=ft.Column(tight=True, controls=[
                ft.Card(content=ft.Container(padding=5, content=ft.ExpansionTile(shape=ft.RoundedRectangleBorder(12), title=ft.Text('密文数据'), controls=[ft.Text(selectable=True)]))),
                ft.Row(controls=[ft.TextButton(text='数据导入', on_click=update_import_dialog), ft.TextButton(text='旧版数据导入', on_click=update_import_dialog)], alignment=ft.MainAxisAlignment.END),
                ft.Card(content=ft.Container(padding=5, content=ft.ExpansionTile(shape=ft.RoundedRectangleBorder(12), title=ft.Text('明文数据'), controls=[ft.Text(selectable=True)]))),
            ]))
            update_data_manage_dialog()
            page.open(data_manage_dialog)
        
        if e == 4:
            def delete_data(e):
                page.client_storage.clear()
                page.close(warning_dialog)
                page.update()
            warning_dialog = ft.AlertDialog(title=ft.Text('确认清除所有数据?'), content=ft.Text('包括所有账目, 自定义目标等信息.'), actions=[ft.TextButton('确定', on_click=delete_data), ft.TextButton('取消', on_click=lambda e: page.close(warning_dialog))])
            page.open(warning_dialog)

        if e == 5:
            def update_ext_dialog(e):
                file_path = ''
                ext_name = e.control.parent.controls[0].value

                def file_picker_result(e: ft.FilePickerResultEvent):
                    for f in e.files:
                        nonlocal file_path
                        file_path = f.path
                
                def show_import(e):
                    def save_import(data, add=True):
                        if add:
                            account = page.client_storage.get('account')+data
                        else:
                            account = data
                        page.client_storage.set('account', account)
                        ext_dialog.title.value = '导入成功!'
                        ext_dialog.content = ft.Text('成功导入%s笔数据, 切换页面以刷新.'%len(data))
                        ext_dialog.actions = [
                            ft.TextButton('完成', on_click=lambda _:page.close(ext_dialog))
                        ]
                        page.update()
                    controls = e.control.parent.content.controls
                    new_ext = {}
                    for c in controls[:-1]:
                        new_ext[c.label] = c.value
                    if file_path=='':
                        ext_dialog.content = None
                        ext_dialog.title = '没有选择导入文件'
                    else:
                        data = tool.read_billing_csv(file_path, ext_name, new_ext)
                        result_view = ft.Column(spacing=1, tight=True)
                        for a in data[::-1]:
                            color = ft.Colors.TERTIARY if a['earn'] else ft.Colors.PRIMARY
                            bgcolor = ft.Colors.TERTIARY_CONTAINER if a['earn'] else ft.Colors.PRIMARY_CONTAINER
                            a_name = ft.Text(a['name'], weight=ft.FontWeight.BOLD, size=15)
                            a_tag = ft.Row(spacing=5, tight=True, controls=[ft.Container(padding=3, border_radius=5, content=ft.Text('#%s'%t, color=ft.Colors.ON_PRIMARY, size=9), bgcolor=color) for t in a['tag']]) if a['tag'] not in ['',[],['']] else ft.Container()
                            a_title = ft.Row(tight=True, controls=[a_name, a_tag], vertical_alignment=ft.CrossAxisAlignment.CENTER)
                            a_subtitle = ft.Text('%s'%a['date'].split(' ')[0]+(' │ %s'%a['source'] if a['source']!='' else ''), size=10)
                            a_trailing = ft.Text('¥%s'%(convert_to_float(a['value']) if a['earn'] else -convert_to_float(a['value'])), weight=ft.FontWeight.BOLD, size=12)
                            a_listtile = ft.Card(content=ft.Container(padding=10, content=ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[ft.Row(controls=[ft.Icon(ft.Icons.SAVINGS_OUTLINED if a['earn'] else ft.Icons.SHOPPING_BAG_OUTLINED, color=color), ft.Column(spacing=3, controls=[ft.Row(controls=[a_title], scroll=ft.ScrollMode.HIDDEN), a_subtitle])]), a_trailing])), color=bgcolor)
                            result_view.controls.append(a_listtile)
                        ext_dialog.content = result_view
                        ext_dialog.title.value = '%s的导入结果(%s条):'%(ext_name, len(data))
                        ext_dialog.actions = [
                            ft.TextButton('覆盖导入', on_click=lambda _:save_import(data, False)),
                            ft.TextButton('追加导入', on_click=lambda _:save_import(data))
                        ]
                    page.update()

                ext = tool.load_extension_config(ext_name)
                rule = ext['rule']
                show_rule = []
                for r in rule:
                    for k, v in r.items():
                        show_rule.append({'name':k, 'rule':v})
                file_picker = ft.FilePicker(on_result=file_picker_result)
                page.overlay.append(file_picker)
                ext_dialog.title.value = '%s插件的预设:'%ext_name
                ext_dialog.content.controls = [ft.TextField(label='start_line', hint_text='表头所在行, 第一行为0, 以此类推', value=ext['start_line'])]+[ft.TextField(label='end_line', hint_text='数据结束列, 为false则为全部', value=ext['end_line'])]+[
                    ft.TextField(label='%s'%r['name'], value=r['rule'], hint_text='第一列为0, $1代表第二列', dense=True) for r in show_rule
                ]+[
                    ft.TextButton('选择从%s导出的%s文件'%(ext_name, ext['file']), on_click=lambda _:file_picker.pick_files())
                ]
                ext_dialog.actions = [
                    ft.TextButton('帮助', url=HELP_URL),
                    ft.TextButton('导入', on_click=show_import),
                ]
                page.update()
            extentions = tool.get_extension_list()
            ext_dialog = ft.AlertDialog(scrollable=True, title=ft.Text('请选择要导入的平台:'), content=ft.Column(tight=True, controls=[
                ft.Row(alignment=ft.MainAxisAlignment.SPACE_AROUND, controls=[ft.Text(e, weight=ft.FontWeight.BOLD), ft.IconButton(ft.Icons.CHEVRON_RIGHT, on_click=update_ext_dialog)]) for e in extentions
            ]))
            page.open(ext_dialog)

        if e == 6:
            with open('VERSION', 'r', encoding='utf-8') as f:
                v = f.read().split('\n')
            data = [{'name': '记易', 'version':JIYI_VERSION}, {"name": "Flet", "version": v[0]},{"name": "Flutter", "version": v[1]},{"name": "Dart", "version": v[5]},{"name": "Python3", "version": v[6]},{"name": "Pip3", "version": v[7]},]
            page.open(ft.AlertDialog(scrollable=True, title=ft.Text('构建信息'), content=ft.Column(tight=True, controls=[
                ft.Card(content=ft.Container(padding=10, content=ft.Column(spacing=3, controls=[ft.Text('%s 版本'%d['name'], weight=ft.FontWeight.BOLD, color=ft.Colors.ON_PRIMARY_CONTAINER), ft.Text(d['version'], color=ft.Colors.ON_PRIMARY_CONTAINER)]))) for d in data
            ])))

        if e == 7:
            with open('HELP.md', 'r', encoding='utf-8') as f:
                page.open(ft.AlertDialog(scrollable=True, title=ft.Text('感谢使用记易!'), content=ft.Column(controls=[
                    ft.Markdown('记易是一款**简洁, 但功能不局限于记账**的账本应用. 以下是记易不同页面主要功能的介绍, 希望可以帮助你更快地上手记易!'),
                    ft.Divider()
                ]+[ft.Card(content=ft.Container(content=ft.Markdown(p, extension_set=ft.MarkdownExtensionSet.GITHUB_WEB), padding=10)) for p in f.read().split('---')]
                )))

        if e == 8:
            def handle_update(e):
                ring = ft.AlertDialog(title=ft.Text('检测更新中...'), content=ft.ProgressBar())
                updata_dialog = ft.AlertDialog(scrollable=True, title=ft.Text('检测到更新'), content=ring)
                page.open(ring)
                data = tool.check_update(JIYI_VERSION)
                ring.open=False
                if data['new']:
                    updata_dialog.content=ft.Markdown(data['log'])
                    updata_dialog.actions=[ft.TextButton('下载', url=data['link'])]
                else:
                    updata_dialog.title=ft.Text('当前已是最新版本')
                    updata_dialog.actions=[ft.TextButton('确定', on_click=lambda e: page.close(updata_dialog))]
                page.open(updata_dialog)
            handle_dialog = ft.AlertDialog(scrollable=True, title=ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[ft.Icon(ft.Icons.SAVINGS), ft.Text('记易')]), content=ft.Column(controls=[
                ft.Text('一个Material Design 3的全平台记账应用, 支持数据导入 / 导出, 自定义成就系统, 以及一键查看数据报告等功能.')
            ]), actions=[
                ft.TextButton('检测更新', on_click=handle_update),
                ft.TextButton('完成', on_click=lambda e: page.close(handle_dialog))
            ])
            page.open(handle_dialog)

    page.navigation_bar = ft.NavigationBar(destinations=[
        ft.NavigationBarDestination(label='记账', icon=ft.Icons.SAVINGS_OUTLINED, selected_icon=ft.Icons.SAVINGS), 
        ft.NavigationBarDestination(label='成就', icon=ft.Icons.EMOJI_EVENTS_OUTLINED, selected_icon=ft.Icons.EMOJI_EVENTS), 
        ft.NavigationBarDestination(label='报告', icon=ft.Icons.THEATERS_OUTLINED, selected_icon=ft.Icons.THEATERS)
        ], on_change=lambda e: page.go(["/", "/achievement", '/show'][e.control.selected_index]), label_behavior=ft.NavigationBarLabelBehavior.ONLY_SHOW_SELECTED)
    page.appbar = ft.AppBar(leading=ft.IconButton(icon=ft.Icons.MENU, on_click=lambda _:page.open(page.drawer)), title=ft.Text(weight=ft.FontWeight.BOLD), center_title=True, actions=[])
    page.drawer = ft.NavigationDrawer(on_change=drawer_change, controls=[
        ft.Container(height=12), 
        ft.NavigationDrawerDestination(),
        ft.Divider(),
        ft.NavigationDrawerDestination(label='主题色', icon=ft.Icons.PALETTE_OUTLINED, selected_icon=ft.Icons.PALETTE),
        ft.NavigationDrawerDestination(label='暗色模式', icon=ft.Icons.DARK_MODE_OUTLINED, selected_icon=ft.Icons.DARK_MODE),
        ft.Divider(),
        ft.NavigationDrawerDestination(label='数据管理', icon=ft.Icons.FOLDER_OUTLINED, selected_icon=ft.Icons.FOLDER),
        ft.NavigationDrawerDestination(label='重置', icon=ft.Icons.FOLDER_DELETE_OUTLINED, selected_icon=ft.Icons.FOLDER_DELETE),
        ft.Divider(),
        ft.NavigationDrawerDestination(label='导入账单', icon=ft.Icons.RECEIPT_LONG_OUTLINED, selected_icon=ft.Icons.RECEIPT_LONG),
        ft.Divider(),
        ft.NavigationDrawerDestination(label='构建信息', icon=ft.Icons.BUBBLE_CHART_OUTLINED, selected_icon=ft.Icons.BUBBLE_CHART),
        ft.NavigationDrawerDestination(label='帮助', icon=ft.Icons.HELP_OUTLINE, selected_icon=ft.Icons.HELP),
        ft.NavigationDrawerDestination(label='关于', icon=ft.Icons.INFO_OUTLINE, selected_icon=ft.Icons.INFO),
        ])

    def route_change(e: ft.RouteChangeEvent):

        page.controls.clear()
        page.scroll = None
        page.floating_action_button = None

        if e.route == '/':

            def remove_account(a, earn):
                account  = page.client_storage.get('account')
                account.remove(a)
                page.client_storage.set('account', account)
                update_account_panel(earn)
                update_data_panel(None)

            def update_account_panel(earn):
                account = page.client_storage.get('account')
                account = account if account!=None else []
                account = [a for a in account if a['earn'] == (True if earn == {'收入'} else False)] if earn!={'全部'} else account
                result = []
                for a in account[::-1]:
                    color = ft.Colors.TERTIARY if a['earn'] else ft.Colors.PRIMARY
                    bgcolor = ft.Colors.TERTIARY_CONTAINER if a['earn'] else ft.Colors.PRIMARY_CONTAINER
                    a_name = ft.Text(a['name'], weight=ft.FontWeight.BOLD, size=15)
                    a_tag = ft.Row(spacing=5, tight=True, controls=[ft.Container(padding=3, border_radius=5, content=ft.Text('#%s'%t, color=ft.Colors.ON_PRIMARY, size=9), bgcolor=color) for t in a['tag']]) if a['tag'] not in ['',[],['']] else ft.Container()
                    a_title = ft.Row(wrap=True, tight=True, controls=[a_name, a_tag], vertical_alignment=ft.CrossAxisAlignment.CENTER)
                    a_subtitle = ft.Text('%s'%a['date']+(' │ %s'%a['source'] if a['source']!='' else ''), size=12)
                    a_trailing = ft.Text('¥%s'%(convert_to_float(a['value']) if a['earn'] else -convert_to_float(a['value'])), weight=ft.FontWeight.BOLD, size=12)
                    a_listtile = ft.Card(content=ft.Container(padding=10, content=ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[ft.Row(controls=[ft.Icon(ft.Icons.SAVINGS_OUTLINED if a['earn'] else ft.Icons.SHOPPING_BAG_OUTLINED, color=color), ft.Column(spacing=3, controls=[ft.Row(controls=[a_title], scroll=ft.ScrollMode.HIDDEN), a_subtitle])]), a_trailing])), color=bgcolor)
                    a_card = ft.Dismissible(content=ft.Container(content=a_listtile, border_radius=12, on_long_press=lambda e:update_edit_dialog(e.control.parent.background.controls[3].value)), 
                                            dismiss_thresholds={ft.DismissDirection.START_TO_END: 0.6}, 
                                            dismiss_direction=ft.DismissDirection.START_TO_END, 
                                            background=ft.Row(controls=[ft.Container(width=5), ft.Icon(ft.Icons.DELETE, color=color), ft.Text('继续右滑以删除 >>>', color=color, weight=ft.FontWeight.BOLD), ft.Text(a, size=0)]),
                                            on_dismiss=lambda e:remove_account(e.control.background.controls[3].value, earn))
                    result.append(a_card)
                account_panel.controls = result
                update_data_panel(None)
                page.update()

            def update_edit_dialog(a):

                def save_edit(controls, old_a):
                    bug = ['', None]
                    name = controls[0].value if controls[0].value not in bug else '未命名'
                    value = controls[1].value if controls[1].value not in bug else 0
                    tag = controls[2].value.split(' ')
                    try:
                        tag.remove('')
                    except:
                        pass
                    source = controls[3].controls[1].controls[0].value if controls[3].controls[1].controls[0].value not in bug else ''
                    date = controls[4].value if controls[4].value not in bug else datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    earn = True if controls[5].controls[1].controls[0].selected == {'收入'} else False
                    a = {'name':name, 'value':convert_to_float(value), 'tag':tag, 'source':source, 'date':date, 'earn':earn}
                    account = page.client_storage.get('account')
                    account = account if account!=None else []
                    account[account.index(old_a)] = a
                    page.client_storage.set('account', account)
                    page.close(set_dialog)
                    update_data_panel(None)
                    # button_group.controls[0].selected = controls[5].controls[1].controls[0].selected
                    update_account_panel(button_group.controls[0].selected)

                source = page.client_storage.get('source')
                source = source if source!=None else []
                set_dialog = ft.AlertDialog(title=ft.Text('记一笔账'), content=ft.Column(tight=True))
                set_dialog.content.controls = [
                    ft.TextField(label='名称', hint_text='如: 工资/冰红茶', dense=True, value=a['name']),
                    ft.TextField(label='价值', hint_text='如: 2000', dense=True, value=a['value']),
                    ft.TextField(label='标签', hint_text='多个标签空格分隔', dense=True, value=' '.join(a['tag'])),
                    ft.Column(spacing=3, tight=True, controls=[ft.Text('选择来源:'), ft.Row(scroll=ft.ScrollMode.HIDDEN, alignment=ft.MainAxisAlignment.CENTER, controls=[ft.RadioGroup(value=a['source'], content=ft.Row(controls=[ft.Radio(label=s['name'], value=s['name']) for s in source], tight=True, scroll=ft.ScrollMode.HIDDEN))])]),
                    ft.TextField(label='日期', hint_text=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), dense=True, value=a['date']),
                    ft.Column(tight=True, controls=[ft.Text('这是一笔:'), ft.Row(controls=[ft.SegmentedButton(segments=[ft.Segment(label=ft.Text('收入'), value='收入'), ft.Segment(label=ft.Text('支出'), value='支出')], selected=({'收入'} if a['earn'] else {'支出'}))], alignment=ft.MainAxisAlignment.CENTER)]),
                ]
                set_dialog.actions = [ft.TextButton(text='确定', on_click=lambda _:save_edit(set_dialog.content.controls, a)), ft.TextButton(text='取消', on_click=lambda _:page.close(set_dialog))]
                page.open(set_dialog)

            def update_add_dialog(e):

                def add_account(controls):
                    bug = ['', None]
                    name = controls[0].value if controls[0].value not in bug else '未命名'
                    value = controls[1].value if controls[1].value not in bug else 0
                    tag = controls[2].value.split(' ')
                    try:
                        tag.remove('')
                    except ValueError:
                        pass
                    source = controls[3].controls[1].controls[0].value if controls[3].controls[1].controls[0].value not in bug else ''
                    date = controls[4].value if controls[4].value not in bug else datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    earn = True if controls[5].controls[1].controls[0].selected == {'收入'} else False
                    a = {'name':name, 'value':convert_to_float(value), 'tag':tag, 'source':source, 'date':date, 'earn':earn}
                    account = page.client_storage.get('account')
                    account = account if account!=None else []
                    account.append(a)
                    page.client_storage.set('account', account)
                    page.close(add_dialog)
                    update_data_panel(None)
                    button_group.controls[0].selected = controls[5].controls[1].controls[0].selected
                    update_account_panel(controls[5].controls[1].controls[0].selected)

                source = page.client_storage.get('source')
                source = source if source!=None else []
                add_dialog = ft.AlertDialog(title=ft.Text('记一笔账'), content=ft.Column(tight=True))
                add_dialog.content.controls = [
                    ft.TextField(label='名称', hint_text='如: 工资/冰红茶', dense=True),
                    ft.TextField(label='价值', hint_text='如: 2000', dense=True),
                    ft.TextField(label='标签', hint_text='多个标签空格分隔', dense=True),
                    ft.Column(spacing=3, tight=True, controls=[ft.Text('选择来源:'), ft.Row(expand=True, scroll=ft.ScrollMode.HIDDEN, tight=True, alignment=ft.MainAxisAlignment.CENTER, controls=[ft.RadioGroup(content=ft.Row(controls=[ft.Radio(label=s['name'], value=s['name']) for s in source]))])]),
                    ft.TextField(label='日期', hint_text='', dense=True, value=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                    ft.Column(tight=True, controls=[ft.Text('这是一笔:'), ft.Row(controls=[ft.SegmentedButton(segments=[ft.Segment(label=ft.Text('收入'), value='收入'), ft.Segment(label=ft.Text('支出'), value='支出')], selected={'支出'})], alignment=ft.MainAxisAlignment.CENTER)]),
                ]
                add_dialog.actions = [ft.TextButton(text='确定', on_click=lambda _:add_account(add_dialog.content.controls)), ft.TextButton(text='取消', on_click=lambda _:page.close(add_dialog))]
                page.open(add_dialog)

            def update_source_dialog(e):

                def remove_source(name):
                    for c in source_dialog.content.controls[0].controls:
                        if c.controls[0].label and c.controls[0].label == name:
                            source_dialog.content.controls[0].controls.remove(c)
                    page.update()

                def add_source_field(e):
                    source_dialog.content.controls[2].controls.append(ft.Row(tight=True, controls=[ft.TextField(dense=True, expand=True, label='来源', hint_text='来源名称'), ft.TextField(dense=True, expand=True, label='底金', hint_text='来源底金')]))
                    page.update()

                def save_source(controls):
                    old_source = [{'name':c.controls[0].label, 'value':c.controls[0].value} for c in controls[0].controls]
                    new_source = [{'name':c.controls[0].value if c.controls[0].value!='' else '未命名', 'value':(convert_to_float(c.controls[1].value) if c.controls[1].value!='' else 0)} for c in controls[2].controls]
                    source = []
                    for s in old_source+new_source:
                        if s['name'] not in [s['name'] for s in source]:
                            source.append(s)
                    page.client_storage.set('source', source)
                    page.close(source_dialog)
                    update_data_panel(None)

                source = page.client_storage.get('source')
                source = source if source!=None else []
                source_dialog = ft.AlertDialog(title=ft.Text('管理来源'), content=ft.Column(spacing=0, tight=True, controls=[ft.Column(tight=True), ft.IconButton(icon=ft.Icons.ADD, on_click=add_source_field), ft.Column(tight=True)]))
                source_dialog.content.controls[0].controls = [ft.Row(tight=True, controls=[ft.TextField(dense=True, expand=True, label=s['name'], value=s['value'], hint_text='请输入底金金额'), ft.IconButton(icon=ft.Icons.REMOVE_CIRCLE, on_click=lambda e:remove_source(e.control.parent.controls[0].label))]) for s in source]
                source_dialog.actions = [ft.TextButton('保存', on_click=lambda _:save_source(source_dialog.content.controls)), ft.TextButton('取消', on_click=lambda _:page.close(source_dialog))]
                page.open(source_dialog)

            def update_data_panel(e):
                data = get_account_data()
                title_list = ['总收入', '总支出', '流水', '结余']
                icon_list = [ft.Icons.WALLET, ft.Icons.PAID, ft.Icons.LEADERBOARD, ft.Icons.MONEY]
                subtitle_list = [' │ '.join(['%s ¥%s(%s笔)'%(s['source'], convert_to_float(s['value']), s['times']) for s in list(data['earn']['source']+([{'source':'其他','value':data['earn']['total_other'],'times':data['earn']['other_times']}] if int(data['earn']['total_other'])!=0 else []))]), 
                                 ' │ '.join(['%s ¥%s(%s笔)'%(s['source'], convert_to_float(s['value']), s['times']) for s in list(data['spend']['source']+([{'source':'其他','value':data['spend']['total_other'],'times':data['spend']['other_times']}] if int(data['spend']['total_other'])!=0 else []))]), 
                                 '收入 %s 笔 │ 支出 %s 笔'%(data['earn']['times'], data['spend']['times']), 
                                 ' │ '.join(['%s ¥%s'%(s['name'], convert_to_float(s['value'])) for s in data['balance']['source']]+(['其他 ¥%s'%data['balance']['total_other']] if data['balance']['total_other']!=0 else []))]
                trailing_list = ['¥%s'%data['earn']['total'], '¥%s'%data['spend']['total'], data['earn']['times']+data['spend']['times'], 
                                 '¥%s'%data['balance']['total']]
                for d in data_panel.content.controls:
                    d.title.value = title_list[data_panel.content.controls.index(d)]
                    d.leading.name = icon_list[data_panel.content.controls.index(d)]
                    d.subtitle.value = subtitle_list[data_panel.content.controls.index(d)]
                    d.trailing.value = trailing_list[data_panel.content.controls.index(d)]
                page.update()

            def update_search_dialog(e):
                def show_search_result(e):
                    controls = e.control.parent.content.controls
                    name = controls[1].value
                    tag = controls[2].value.split(' ')
                    source = [s.label for s in controls[3].controls[1].controls if s.value]
                    date = date_picker.value.strftime('%Y-%m-%d') if date_picker != None and controls[4].controls[1].value == True else None
                    earn = controls[6].controls[0].selected
                    money_range = [controls[0].controls[1].start_value, controls[0].controls[1].end_value]
                    account = page.client_storage.get('account')
                    account = account if account!=None else []
                    bug = ['', None, [], ['']]
                    if account in bug:
                        search_dialog.content = ft.Text('还没有没有添加任何账单记录...')
                    else:
                        account = [a for a in account if a['value']>money_range[0] and a['value']<money_range[1]]
                        if name not in bug:
                            account = [a for a in account if name in a['name']]
                        else:
                            account = account
                        if tag not in bug:
                            result = []
                            for a in account:
                                for t in tag:
                                    if t in a['tag']:
                                        result.append(a)
                            account = result
                        else:
                            account = account
                        if source not in bug:
                            if '全部' in source:
                                account = account
                            else:
                                result = []
                                for s in source:
                                    for a in account:
                                        if a['source'] == s:
                                            result.append(a) 
                                account = result
                        else:
                            account = account
                        if date not in bug:
                            account = [a for a in account if datetime.datetime.strptime(a['date'], "%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d') in date]
                        else:
                            account = account
                        if earn == {'earn'}:
                            account = [a for a in account if a['earn']]
                        elif earn == {'spend'}:
                            account = [a for a in account if not a['earn']]
                        else:
                            account = account
                    result_view = ft.Column(spacing=1, tight=True)
                    for a in account[::-1]:
                        color = ft.Colors.TERTIARY if a['earn'] else ft.Colors.PRIMARY
                        bgcolor = ft.Colors.TERTIARY_CONTAINER if a['earn'] else ft.Colors.PRIMARY_CONTAINER
                        a_name = ft.Text(a['name'], weight=ft.FontWeight.BOLD, size=15)
                        a_tag = ft.Row(spacing=5, tight=True, controls=[ft.Container(padding=3, border_radius=5, content=ft.Text('#%s'%t, color=ft.Colors.ON_PRIMARY, size=9), bgcolor=color) for t in a['tag']]) if a['tag'] not in ['',[],['']] else ft.Container()
                        a_title = ft.Row(tight=True, controls=[a_name, a_tag], vertical_alignment=ft.CrossAxisAlignment.CENTER)
                        a_subtitle = ft.Text('%s'%a['date'].split(' ')[0]+(' │ %s'%a['source'] if a['source']!='' else ''), size=10)
                        a_trailing = ft.Text('¥%s'%(convert_to_float(a['value']) if a['earn'] else -convert_to_float(a['value'])), weight=ft.FontWeight.BOLD, size=12)
                        a_listtile = ft.Card(content=ft.Container(padding=10, content=ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[ft.Row(controls=[ft.Icon(ft.Icons.SAVINGS_OUTLINED if a['earn'] else ft.Icons.SHOPPING_BAG_OUTLINED, color=color), ft.Column(spacing=3, controls=[ft.Row(scroll=ft.ScrollMode.HIDDEN, controls=[a_title]), a_subtitle])]), a_trailing])), color=bgcolor)
                        a_card = ft.Dismissible(content=ft.Container(content=a_listtile, border_radius=12, on_long_press=lambda e:update_edit_dialog(e.control.parent.background.controls[3].value)), 
                                                dismiss_thresholds={ft.DismissDirection.START_TO_END: 0.6}, 
                                                dismiss_direction=ft.DismissDirection.START_TO_END, 
                                                background=ft.Row(controls=[ft.Container(width=5), ft.Icon(ft.Icons.DELETE, color=color), ft.Text('继续右滑以删除 >>>', color=color, weight=ft.FontWeight.BOLD), ft.Text(a, size=0)]),
                                                on_dismiss=lambda e:remove_account(e.control.background.controls[3].value, earn))
                        result_view.controls.append(a_card)
                    search_dialog.content = result_view
                    search_dialog.title.value = '筛选结果(共%s条):'%(len(result_view.controls))
                    search_dialog.actions = [ft.TextButton('重新筛选', on_click=update_search_dialog), ft.TextButton('完成', on_click=lambda _:page.close(search_dialog))]
                    page.update()

                source = page.client_storage.get('source')
                source = source if source!=None else []
                search_dialog = ft.AlertDialog(scrollable=True, title=ft.Text('筛选'), content=None, actions=[ft.TextButton('筛选', on_click=show_search_result), ft.TextButton('取消', on_click=lambda _:page.close(search_dialog))])
                keyword_field = ft.TextField(label='关键词筛选', hint_text='请输入关键词', dense=True)
                tag_field = ft.TextField(label='标签筛选', hint_text='请输入标签', dense=True)
                sourece_checkbox = ft.Row(spacing=3, controls=[ft.Checkbox(label='全部', value=True)]+[ft.Checkbox(label=s['name'], value=False) for s in source], tight=True, scroll=ft.ScrollMode.HIDDEN)
                money_rangeslider = ft.RangeSlider(start_value=0, end_value=2000, min=0, max=2000, divisions=9, label='{value}')
                date_picker = ft.DatePicker(cancel_text='取消', confirm_text='确定')
                date_switch = ft.Switch(value=False, on_change=lambda _:page.open(date_picker) if date_switch.value else None)
                scope_segment = ft.SegmentedButton(segments=[ft.Segment(label=ft.Text('全部'), value='all'), ft.Segment(label=ft.Text('收入'), value='earn'), ft.Segment(label=ft.Text('支出'), value='spend')], selected={'all'})
                search_dialog.content = ft.Column(controls=[
                    ft.Column(controls=[ft.Text('金额范围限制'), money_rangeslider], tight=True, spacing=0), 
                    keyword_field, tag_field,
                    ft.Column(controls=[ft.Text('来源范围:'), sourece_checkbox], tight=True),
                    ft.Row(controls=[ft.Text('日期筛选'), date_switch], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), 
                    ft.Text('筛选范围'), 
                    ft.Row(controls=[scope_segment], alignment=ft.MainAxisAlignment.CENTER)
                    ], tight=True)
                page.open(search_dialog)

            title = '记易 │ 记账'
            icon = ft.Icons.SAVINGS_OUTLINED
            selected_icon = ft.Icons.SAVINGS
            page.title = title
            page.appbar.title.value = title
            page.appbar.actions = [ft.IconButton(icon=ft.Icons.FILTER_ALT_OUTLINED, selected_icon=ft.Icons.FILTER_ALT, on_click=update_search_dialog)]
            page.drawer.controls[1].label = title
            page.drawer.controls[1].icon = icon
            page.drawer.controls[1].selected_icon = selected_icon
            page.floating_action_button = ft.FloatingActionButton(icon=ft.Icons.ADD, on_click=update_add_dialog)

            data_panel = ft.Container(content=ft.Column(spacing=0, controls=[
                ft.ListTile(bgcolor=ft.Colors.PRIMARY, dense=True, visual_density=ft.VisualDensity.ADAPTIVE_PLATFORM_DENSITY, title=ft.Text(weight=ft.FontWeight.BOLD, color=ft.Colors.ON_PRIMARY), leading=ft.Icon(color=ft.Colors.ON_PRIMARY), trailing=ft.Text(weight=ft.FontWeight.BOLD, color=ft.Colors.ON_PRIMARY), subtitle=ft.Text(color=ft.Colors.ON_SECONDARY)), 
                ft.ListTile(bgcolor=ft.Colors.PRIMARY, dense=True, visual_density=ft.VisualDensity.ADAPTIVE_PLATFORM_DENSITY, title=ft.Text(weight=ft.FontWeight.BOLD, color=ft.Colors.ON_PRIMARY), leading=ft.Icon(color=ft.Colors.ON_PRIMARY), trailing=ft.Text(weight=ft.FontWeight.BOLD, color=ft.Colors.ON_PRIMARY), subtitle=ft.Text(color=ft.Colors.ON_SECONDARY)), 
                ft.ListTile(bgcolor=ft.Colors.PRIMARY, dense=True, visual_density=ft.VisualDensity.ADAPTIVE_PLATFORM_DENSITY, title=ft.Text(weight=ft.FontWeight.BOLD, color=ft.Colors.ON_PRIMARY), leading=ft.Icon(color=ft.Colors.ON_PRIMARY), trailing=ft.Text(weight=ft.FontWeight.BOLD, color=ft.Colors.ON_PRIMARY), subtitle=ft.Text(color=ft.Colors.ON_SECONDARY)), 
                ft.ListTile(bgcolor=ft.Colors.PRIMARY, dense=True, visual_density=ft.VisualDensity.ADAPTIVE_PLATFORM_DENSITY, title=ft.Text(weight=ft.FontWeight.BOLD, color=ft.Colors.ON_PRIMARY), leading=ft.Icon(color=ft.Colors.ON_PRIMARY), trailing=ft.Text(weight=ft.FontWeight.BOLD, color=ft.Colors.ON_PRIMARY), subtitle=ft.Text(color=ft.Colors.ON_SECONDARY), on_long_press=update_source_dialog)
                ]), border_radius=12)
            button_group = ft.Row(controls=[ft.SegmentedButton(selected_icon=ft.Icon(ft.Icons.RADIO_BUTTON_CHECKED), on_change=lambda _:update_account_panel(button_group.controls[0].selected), segments=[ft.Segment(label=ft.Text('收入', size=13), value='收入'), ft.Segment(label=ft.Text('全部', size=13), value='全部'), ft.Segment(label=ft.Text('支出', size=13), value='支出')], selected={'全部'})], alignment=ft.MainAxisAlignment.CENTER)
            account_panel = ft.ListView(expand=True, spacing=3)
            update_account_panel({'全部'})
            update_data_panel(None)
            page.add(data_panel, button_group, account_panel)

        if e.route == '/achievement':

            def done_achievement(done, sublist, code, pass_check=False):
                if pass_check:
                    sub_list = sublist
                else:
                    if sublist == {'收入'}:
                        sub_list = 'earn'
                    elif sublist == {'支出'}:
                        sub_list = 'spend'
                    elif sublist == {'其他'}:
                        sub_list = 'other'
                    elif sublist == {'自定义'}:
                        sub_list = 'mine'
                if done:
                    tool.done_achievement(sub_list, code)
                else:
                    tool.undone_achievement(sub_list, code)
                update_achievement_panel(sublist, pass_check=pass_check)
                update_status_panel()

            def remove_achievement(sublist, code, pass_check=False):
                if pass_check:
                    sub_list = sublist
                else:
                    if sublist == {'收入'}:
                        sub_list = 'earn'
                        button_group.controls[0].selected = sublist
                    elif sublist == {'支出'}:
                        sub_list = 'spend'
                        button_group.controls[0].selected = sublist
                    elif sublist == {'其他'}:
                        sub_list = 'other'
                        button_group.controls[0].selected = sublist
                    elif sublist == {'自定义'}:
                        sub_list = 'mine'
                        button_group.controls[0].selected = sublist
                tool.delete_achievement(sub_list, code)
                update_achievement_panel(sublist, pass_check=pass_check)
                update_status_panel()

            def update_add_achievement(e):

                def save_add(title, description):
                    tool.add_mine(title, description)
                    update_achievement_panel({'自定义'})
                    page.close(add_bottom_sheet)
                    update_status_panel()

                sheet_content = ft.Column(controls=[
                    ft.Text('添加一项成就', size=25), 
                    ft.TextField(label='成就', hint_text='如: 我是歌手'), 
                    ft.TextField(label='描述', hint_text='如: KTV消费超10000'),
                    ft.Text('提示: 成就添加后, 无法进行编辑.'),
                    ft.Row(alignment=ft.MainAxisAlignment.END, controls=[ft.ElevatedButton(text='保存', on_click=lambda _:save_add(sheet_content.controls[1].value, sheet_content.controls[2].value))])
                    ])
                add_bottom_sheet = ft.BottomSheet(maintain_bottom_view_insets_padding=70, enable_drag=True, show_drag_handle=True, content=ft.Container(padding=20, content=sheet_content))
                page.open(add_bottom_sheet)

            def update_achievement_panel(choose, pass_check=False):
                if pass_check:
                    data = tool.get_sublist_by_name(choose)
                else:
                    if choose == {'收入'}:
                        data = tool.get_sublist_by_name('earn')
                    elif choose == {'支出'}:
                        data = tool.get_sublist_by_name('spend')
                    elif choose == {'其他'}:
                        data = tool.get_sublist_by_name('other')
                    elif choose == {'自定义'}:
                        data = tool.get_sublist_by_name('mine')
                result = []
                for d in data: # 
                    d_title = ft.Text(d['title'], weight=ft.FontWeight.BOLD, style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH) if d['done'] else None)
                    d_subtitle = ft.Text(d['description'], style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH) if d['done'] else None)
                    d_trailing = ft.Checkbox(value=d['done'], on_change=lambda e:done_achievement(e.control.value, e.control.parent.controls[0].controls[3].value, e.control.parent.controls[0].controls[2].value))
                    d_card = ft.Card(content=ft.Container(padding=10, content=ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[ft.Row(spacing=15, controls=[ft.Icon(ft.Icons.random()), ft.Column(controls=[d_title, d_subtitle], spacing=3), ft.Text(d['code'], size=0), ft.Text(choose, size=0)]), d_trailing])))
                    result.append(ft.Dismissible(content=d_card, on_dismiss=lambda e:remove_achievement(e.control.content.content.content.controls[0].controls[3].value, e.control.content.content.content.controls[0].controls[2].value), dismiss_thresholds={ft.DismissDirection.START_TO_END: 0.6}, dismiss_direction=ft.DismissDirection.START_TO_END, background=ft.Row(controls=[ft.Container(width=5), ft.Icon(ft.Icons.DELETE), ft.Text('继续右滑以删除 >>>', weight=ft.FontWeight.BOLD)]),))
                if choose == {'自定义'}:
                    result = [ft.Row(controls=[ft.TextButton(icon=ft.Icons.ADD, text='添加', on_click=update_add_achievement)], alignment=ft.MainAxisAlignment.CENTER)]+result
                achievement_panel.controls = result
                page.update()

            def update_status_panel():
                earn = tool.get_sublist_by_name('earn')
                spend = tool.get_sublist_by_name('spend')
                other = tool.get_sublist_by_name('other')
                mine = tool.get_sublist_by_name('mine')
                earn_data = len([e for e in earn if e['done']])
                spend_data = len([s for s in spend if s['done']])
                other_data = len([o for o in other if o['done']])
                mine_data = len([m for m in mine if m['done']])
                status_panel.subtitle.value = '收入类 %s/%s │ 支出类 %s/%s\n其他类 %s/%s │ 自定义 %s/%s'%(earn_data, len(earn), spend_data, len(spend), other_data, len(other), mine_data, len(mine))
                status_panel.trailing.controls[0].value =  '%s/%s'%(earn_data+spend_data+other_data+mine_data, len(earn)+len(spend)+len(other)+len(mine))
                status_panel.trailing.controls[1].value =  (earn_data+spend_data+other_data+mine_data)/(len(earn)+len(spend)+len(other)+len(mine))
                page.update()

            def update_search_dialog(e):
                def show_result(e):
                    controls = e.control.parent.content.controls
                    keyword = controls[0].value
                    types = controls[2].value if controls[2].value!=None else 'mine'
                    print(types)
                    result = []
                    [result.append(d) for d in tool.get_sublist_by_name(types) if keyword in d['title'] or keyword in d['description']]
                    controls = []
                    for d in result:
                        d_title = ft.Text(d['title'], weight=ft.FontWeight.BOLD, style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH) if d['done'] else None)
                        d_subtitle = ft.Text(d['description'], style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH) if d['done'] else None)
                        d_trailing = ft.Checkbox(value=d['done'], on_change=lambda e:done_achievement(e.control.value, e.control.parent.controls[0].controls[3].value, e.control.parent.controls[0].controls[2].value, True))
                        d_card = ft.Card(content=ft.Container(padding=10, content=ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[ft.Row(spacing=15, controls=[ft.Icon(ft.Icons.random()), ft.Column(controls=[d_title, d_subtitle], spacing=3), ft.Text(d['code'], size=0), ft.Text(types, size=0)]), d_trailing])))
                        controls.append(ft.Dismissible(content=d_card, on_dismiss=lambda e:remove_achievement(e.control.content.content.content.controls[0].controls[3].value, e.control.content.content.content.controls[0].controls[2].value, True), dismiss_thresholds={ft.DismissDirection.START_TO_END: 0.6}, dismiss_direction=ft.DismissDirection.START_TO_END, background=ft.Row(controls=[ft.Container(width=5), ft.Icon(ft.Icons.DELETE), ft.Text('继续右滑以删除 >>>', weight=ft.FontWeight.BOLD)]),))
                    search_dialog.content.controls = controls
                    search_dialog.actions = [ft.TextButton('重新搜索', on_click=update_search_dialog), ft.TextButton('完成', on_click=lambda _:page.close(search_dialog))]
                    page.update()

                search_dialog = ft.AlertDialog(title=ft.Text('搜索'), content=ft.Column(tight=True, controls=[
                    ft.TextField(label='关键词', hint_text='请输入关键词'),
                    ft.Text('类型范围:'), 
                    ft.RadioGroup(content=ft.Row(scroll=ft.ScrollMode.HIDDEN, controls=[
                        ft.Radio(value='earn', label='收入类'),
                        ft.Radio(value='spend', label='支出类'),
                        ft.Radio(value='other', label='其他类'),
                        ft.Radio(value='mine', label='自定义'),
                    ]))
                ]))
                search_dialog.actions = [ft.TextButton('搜索', on_click=show_result), ft.TextButton('取消', on_click=lambda _:page.close(search_dialog))]
                page.open(search_dialog)

            title = '记易 │ 成就'
            icon = ft.Icons.EMOJI_EVENTS_OUTLINED
            selected_icon = ft.Icons.EMOJI_EVENTS
            page.title = title
            page.appbar.title.value = title
            page.appbar.actions = [ft.IconButton(icon=ft.Icons.SEARCH, on_click=update_search_dialog)]
            page.drawer.controls[1].label = title
            page.drawer.controls[1].icon = icon
            page.drawer.controls[1].selected_icon = selected_icon

            status_panel = ft.ListTile(leading=ft.Icon(ft.Icons.EMOJI_EVENTS_OUTLINED, size=53), title=ft.Text('我的成就', weight=ft.FontWeight.BOLD), subtitle=ft.Text(size=12), trailing=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=7, controls=[ft.Text(), ft.ProgressRing(width=30, height=30, bgcolor=ft.Colors.PRIMARY_CONTAINER, color=ft.Colors.PRIMARY)]))
            button_group = ft.Row(controls=[ft.SegmentedButton(selected_icon=ft.Icon(ft.Icons.RADIO_BUTTON_CHECKED), on_change=lambda _:update_achievement_panel(button_group.controls[0].selected), segments=[ft.Segment(label=ft.Text('收入类', size=13), value='收入'), ft.Segment(label=ft.Text('支出类', size=13), value='支出'), ft.Segment(label=ft.Text('其他类', size=13), value='其他'), ft.Segment(label=ft.Text('自定义', size=13), value='自定义')], selected={'收入'})], alignment=ft.MainAxisAlignment.CENTER)
            achievement_panel = ft.ListView(expand=True, spacing=3)
            update_status_panel()
            update_achievement_panel({'收入'})
            page.add(status_panel, button_group, achievement_panel)

        if e.route == '/show':

            def update_setting_panel():
                source = page.client_storage.get('source')
                source = source if source != None else []
                setting_panel.content.content.controls = [
                    ft.Text('时间范围', size=17, weight=ft.FontWeight.BOLD),
                    ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[ft.TextField(expand=True, dense=True, label='起始日期', hint_text='如: 2025-1-1'), ft.IconButton(icon=ft.Icons.CALENDAR_MONTH, on_click=update_datepicker)]),
                    ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[ft.TextField(expand=True, dense=True, label='截止日期', hint_text='如: 2025-1-1', value = datetime.datetime.now().strftime('%Y-%m-%d')), ft.IconButton(icon=ft.Icons.CALENDAR_MONTH, on_click=update_datepicker)]),
                    ft.Divider(),
                    ft.Text('数据来源', size=17, weight=ft.FontWeight.BOLD),
                    ft.RadioGroup(value='all', content=ft.Row(controls=[ft.Radio(label='全部', value='all')]+[ft.Radio(label=s['name'], value=s['name']) for s in source], tight=True, scroll=ft.ScrollMode.HIDDEN)),
                    ft.Divider(),
                    ft.Row([ft.TextButton(text='生成报告', icon=ft.Icons.COFFEE, on_click=lambda _: generate_report(setting_panel.content.content.controls))], alignment=ft.MainAxisAlignment.END)
                ]
                
            def update_datepicker(field):
                def save_to_field(date):
                    nonlocal field
                    if field == '起始日期':
                        field = 1
                    else:
                        field = 2
                    setting_panel.content.content.controls[field].controls[0].value = date.data.split('T')[0]
                    page.update()
                field = field.control.parent.controls[0].label
                date_picker = ft.DatePicker(cancel_text='取消', confirm_text='确认', error_format_text='格式错误', error_invalid_text='超出范围', help_text='选择日期', field_label_text='请输入日期', on_change=save_to_field)
                page.open(date_picker)

            def generate_report(controls):
                first_date = controls[1].controls[0].value
                first_date = first_date if first_date not in [''] else datetime.datetime.now().strftime('%Y-%m-%d')
                last_date = controls[2].controls[0].value
                source = controls[5].value
                user_source = page.client_storage.get('source')
                user_source = user_source if user_source != None else []
                data = get_account_data_by_date(first_date, last_date)
                if source == 'all':
                    data = data
                    pure_balance = convert_to_float(convert_to_float(sum([s['value'] for s in data if s['earn']]))-convert_to_float(sum([s['value'] for s in data if not s['earn']])))
                    text1 = '底金之和:'
                    total = convert_to_float(sum([convert_to_float(s['value']) for s in user_source]))
                    text2 = total
                else:
                    data = [s for s in data if s['source'] == source]
                    pure_balance = convert_to_float(convert_to_float(sum([s['value'] for s in data if s['earn']]))-convert_to_float(sum([s['value'] for s in data if not s['earn']])))
                    text1 = '%s底金:'%source
                    for s in user_source:
                        if s['name'] == source:
                            total = convert_to_float(s['value'])
                            break
                    text2 = total
                if pure_balance<total and pure_balance>0:
                    text3 = '日进斗金(¥%s)'%(total+pure_balance)
                elif pure_balance==total:
                    text3 = '收支平衡(¥0.0)'
                elif pure_balance>total:
                    text3 = '绰绰有余(¥%s)'%(total+pure_balance)
                else:
                    text3 = '入不敷出(¥%s)'%(total+pure_balance)
                
                setting_panel.content.content.controls.clear()
                color = page.client_storage.get('COLOR')
                color = color if color!=None else 'blue'
                color_list = ['%s%s00'%(color, i) for i in range(1,10)]
                all_earn_money = convert_to_float(sum([s['value'] for s in data if s['earn']]))
                all_spend_money = convert_to_float(sum([s['value'] for s in data if not s['earn']]))
                earn_source_data = get_source_data(data, True)
                spend_source_data = get_source_data(data, False)
                try:
                    earn_chart = ft.PieChart(center_space_radius=60, expand=True, sections=[ft.PieChartSection(e['value'], radius=70, title_style=ft.TextStyle(weight=ft.FontWeight.BOLD), title='%s\n%s%%'%(e['name'], convert_to_float(e['value']/all_earn_money*100)), color=color_list[earn_source_data.index(e)]) for e in earn_source_data])
                    spend_chart = ft.PieChart(center_space_radius=60, expand=True, sections=[ft.PieChartSection(s['value'], radius=70, title_style=ft.TextStyle(weight=ft.FontWeight.BOLD), title='%s\n%s%%'%(s['name'], convert_to_float(s['value']/all_spend_money*100)), color=color_list[spend_source_data.index(s)]) for s in spend_source_data])
                except ZeroDivisionError:
                    page.open(ft.AlertDialog(title=ft.Text('错误'), content=ft.Text('有账目的价值为0, 无法生成图表, 请修改后重试(点击空白处关闭此弹窗).')))
                tags = analyze_tag(data)[:6]
                tag_chart = ft.BarChart(bottom_axis=ft.ChartAxis(labels=[ft.ChartAxisLabel(value=tags.index(t), label=ft.Text(t['name'])) for t in tags]), bar_groups=[ft.BarChartGroup(x=tags.index(t), bar_rods=[ft.BarChartRod(from_y=0, to_y=t['value'], color=color_list[tags.index(t)], tooltip='%s次'%t['value'])]) for t in tags])
                setting_panel.content.content.controls=[
                    ft.Text('在 %s - %s 期间(共%s天), '%(first_date, last_date, get_date_difference(first_date, last_date)), size=15, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Row(controls=[ft.Text('你收入了:'), ft.Text('¥%s (共%s笔)'%(all_earn_money, len([s for s in data if s['earn']])))], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row(controls=[ft.Text('你支出了:'), ft.Text('¥%s (共%s笔)'%(all_spend_money, len([s for s in data if not s['earn']])))], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row(controls=[ft.Text('净结余:'), ft.Text('¥%s (共%s笔)'%(pure_balance, len(data)))], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row(controls=[ft.Text(text1), ft.Text('¥%s'%text2)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row(controls=[ft.Text('财务状况:'), ft.Text(text3)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(),
                    ft.Text('来源收入占比:'),
                    earn_chart,
                    ft.Text('来源支出占比:'),
                    spend_chart,
                    ft.Divider(),
                    ft.Text('标签出现频次:'),
                    tag_chart,
                ]
                page.update()

            title = '记易 │ 报告'
            icon = ft.Icons.THEATERS_OUTLINED
            selected_icon = ft.Icons.THEATERS
            page.title = title
            page.appbar.title.value = title
            page.appbar.actions = [ft.IconButton(icon=ft.Icons.SHARE)]
            page.drawer.controls[1].label = title
            page.drawer.controls[1].icon = icon
            page.drawer.controls[1].selected_icon = selected_icon
            
            setting_panel = ft.Card(content=ft.Container(padding=15, content=ft.Column()))
            update_setting_panel()
            page.scroll=ft.ScrollMode.HIDDEN
            page.add(setting_panel)

        page.update()
    page.on_route_change = route_change
    page.go('/')

ft.app(main)