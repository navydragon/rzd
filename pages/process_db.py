import dash
from dash import html, dcc, Dash, dash_table, callback
import sqlite3
from pages.constants import Constants
import pandas as pd
import time

dash.register_page(__name__, name='Обработка данных', path='/process_db', order=99)


def layout():

    return html.Div(['Выключено'])
    start_time = time.time()
    conn = sqlite3.connect('from/db4.db')
    # query = '''
    # SELECT a.*, b.[2019 Пропорц распр между Расходами полными ВСЕ,%],
    # b.[2019 Пропорц распр между Расходами полными ПО НАПРАВЛЕНИЯМ,%],
    # b.[Направление],
    # b.[2026 ИНВЕСТ(ПРОЕКТЫ)_на_сеть, млрд. руб.],
    # b.[2026 ИНВЕСТ(ПРОЕКТЫ)_по_направлениям, млрд. руб.]
    # FROM [ЦПС_ПРОПРОЦ_ИНЕВСТ_РЕМОНТ] a
    # INNER JOIN [ЦПС_ПРОПРОЦ_ИНЕВСТ(ПРОЕКТЫ)] b
    # ON a.[index] = b.[index]
    # '''
    query = '''
        SELECT * 
        FROM [ЦПС_отформат]
    '''

    CON = Constants(2026)

    df = pd.read_sql_query(query, conn)
    conn.close()
    # new_column_names = {
    #     '2019 год факт (базовый) | Погрузка, тыс. тонн': 'Погрузка, тыс. тонн',
    #     '2019 год факт (базовый) | Количество вагоноотправок': 'Количество вагоноотправок',
    #     '2019 год факт (базовый) | Погрузка, ваг': 'Погрузка, ваг',
    #     '2019 год факт (базовый) | Грузооборот брутто млн. ткм': 'Грузооборот брутто млн. ткм',
    #     '2019 год факт (базовый) | Провозная плата из накладных, тыс. руб': 'Провозная плата из накладных, тыс. руб',
    #     '2019 год факт (базовый) | Условно-переменные расходы, руб': 'Условно-переменные расходы, тыс. руб',
    #     '2019 год факт (базовый) | Условно-постоянные расходы, руб': 'Условно-постоянные расходы, тыс. руб',
    #     '2019 год факт (базовый) | Плоская помаршрутная СО': 'Плоская помаршрутная СО, тыс. руб',
    #     '2019 год факт (базовый) | Плоская вариант по 3м зонам СО': 'Плоская вариант по 3м зонам СО, тыс. руб',
    #     '2019 год факт (базовый) | Плоская среднесетевая СО': 'Плоская среднесетевая СО, тыс. руб',
    #     '2019 год факт (базовый) | Плоская комбинированная СО': 'Плоская комбинированная СО, тыс. руб',
    #     '2019 год факт (базовый) | помаршрутная СО с дифференциацией': 'Помаршрутная СО с дифференциацией, тыс. руб',
    #     '2019 год факт (базовый) | вариант по 3м зонам СО с дифференциацией': 'Вариант по 3м зонам СО с дифференциацией, тыс. руб',
    #     '2019 год факт (базовый) | среднесетевая СО с дифференциацией': 'Среднесетевая СО с дифференциацией, тыс. руб',
    #     '2019 год факт (базовый) | комбинированная СО с дифференциацией': 'Комбинированная СО с дифференциацией, тыс. руб',
    #     '2019 Расходы полные, руб.': 'Расходы полные, тыс. руб',
    #     '2019 ИНВЕСТ_ремонт, руб.': 'Инвест ремонт, тыс. руб'
    # }
    # Переименование колонок
    # df = df.rename(columns=new_column_names)
    #
    # df['Условно-переменные расходы, тыс. руб'] = df[
    #                                                  'Условно-переменные расходы, тыс. руб'] / 1000
    # df['Условно-постоянные расходы, тыс. руб'] = df[
    #                                                  'Условно-постоянные расходы, тыс. руб'] / 1000
    # df['Расходы полные, тыс. руб'] = df['Расходы полные, тыс. руб'] / 1000
    # df['Инвест ремонт, тыс. руб'] = df['Инвест ремонт, тыс. руб'] / 1000
    #
    # SO_PM = 'Плоская помаршрутная СО, тыс. руб'
    # SO_3Z = 'Плоская вариант по 3м зонам СО, тыс. руб'
    # SO_SS = 'Плоская среднесетевая СО, тыс. руб'
    # SO_KB = 'Плоская комбинированная СО, тыс. руб'
    # PER = 'Условно-переменные расходы, тыс. руб'
    # PER_DOL = 'Доля переменных расходов'
    # POST = 'Условно-постоянные расходы, тыс. руб'
    # POST_DOL = 'Доля постоянных расходов'
    # POL = 'Расходы полные, тыс. руб'
    # CAP = 'Инвест ремонт, тыс. руб'
    # POL_CAP = 'Расходы полные + инвест ремонт, тыс. руб'
    # df[PER_DOL] = df[PER] / df[POL]
    # df[POST_DOL] = df[POST] / df[POL]
    # df[POL_CAP] = df[POL] + df[CAP]

    # процент общесетевые
    sum_rash = df['Расходы полные, тыс. руб'].sum()
    df['Доля от расходов на общесетевые проекты'] = df['Расходы полные, тыс. руб'] / sum_rash

    # процент по направлениям
    grouped = df.groupby('Направление')['Расходы полные, тыс. руб'].sum()
    df['Доля от расходов на проекты по направлениям'] = df.apply(
        lambda row: (row['Расходы полные, тыс. руб'] / grouped[row['Направление']]), axis=1
    )

    columns_to_drop = [
        'index','Наименование станции входа',
        'Наименование станции выхода',
        'Наим отправителя',
        'ключ_маршруты_грузы',
        'ключ_груз_направление_вид-сообщения',
        'Индекс_привед_Грузооборота',
    ]
    df = df.drop(columns_to_drop, axis=1)
    # df.to_csv('data/output2.csv', index=False)
    AGG_PARAMS = {
        CON.P: 'sum',
        CON.EPL: 'sum',
        CON.PR_P: 'sum',
        CON.SO_PM: 'sum',
        CON.SO_SS: 'sum',
        CON.SO_3Z: 'sum',
        CON.SO_KB: 'sum',
        CON.SO_PM_DIFF: 'sum',
        CON.SO_3Z_DIFF: 'sum',
        CON.SO_SS_DIFF: 'sum',
        CON.SO_KB_DIFF: 'sum',
        CON.PER: 'sum',
        CON.POST: 'sum',
        CON.POL: 'sum',
        CON.INVEST_REMONT: 'sum',
        CON.VAG: 'sum',
    }

    # тест короткой базы
    gr_df = df.groupby([
        'Наименование груза ЦО-12',
        'Код группы по ЦО-12',
        'Наименование дороги входа',
        'Наименование дороги выхода',
        'Холдинг отправителя',
        'Вид сообщения',
        'Направление'
    ]).agg(AGG_PARAMS)
    gr_df = gr_df.reset_index()
    # процент общесетевые
    sum_rash = df['Расходы полные, тыс. руб'].sum()
    gr_df['Доля от расходов на общесетевые проекты'] = gr_df['Расходы полные, тыс. руб'] / sum_rash

    # процент по направлениям
    grouped = df.groupby('Направление')['Расходы полные, тыс. руб'].sum()
    gr_df['Доля от расходов на проекты по направлениям'] = gr_df.apply(
        lambda row: (row['Расходы полные, тыс. руб'] / grouped[row['Направление']]), axis=1
    )

    gr_df['Доля условно-переменных расходов'] = gr_df['Условно-переменные расходы, тыс. руб'] / (gr_df['Условно-переменные расходы, тыс. руб'] + gr_df['Условно-постоянные расходы, тыс. руб'])
    gr_df['Доля условно-постоянных расходов'] = gr_df['Условно-постоянные расходы, тыс. руб'] / (gr_df['Условно-переменные расходы, тыс. руб'] + gr_df['Условно-постоянные расходы, тыс. руб'])

    gr_df.to_csv('data/output_grouped.csv', index=False)
    gr_df.to_excel('data/output_grouped.xlsx', index=False)
    # df.to_csv('data/output.csv', index=False)
    execution_time = time.time() - start_time
    return html.Div([
        "Строк:"+str(len(gr_df))+"<br>"
        "Время выполнения: %.2f секунд" % execution_time
    ])
    # # Исполнение запроса и чтение результатов в DataFrame

    #
    #

    # # Закрытие соединения с базой данных
    conn.close()
