import pandas as pd
from dash import html, dcc, callback
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from pages.constants import Constants

CON = Constants(2026)

def get_base_routes_data():
    raw = pd.read_excel('data/base_routes.xlsx', sheet_name=None, skiprows=1)
    del raw['СВОД']
    df = raw.pop("Уголь 100")
    df = df.drop([0, 1])
    n = 1
    df['order'] = n
    n += 1
    for sheet_name, df1 in raw.items():
        df1 = df1.drop([0, 1])
        df1['order'] = n
        n += 1
        df = pd.concat([df, df1])

    df = df.dropna(subset=['Наименование дороги выхода'])
    df = df.reset_index(drop=True)
    directions = pd.read_excel('data/references/road_direction.xlsx')
    df = pd.merge(df, directions, left_on='Наименование дороги выхода',
                  right_on='Дорога', how='inner')
    return df


def get_data(file):
    df = pd.read_csv('data/'+file, delimiter=";", decimal=",",
                     thousands=" ", encoding='utf-8')
    df = df.dropna(subset=['Наименование дороги выхода'])
    df = df.reset_index(drop=True)
    directions = pd.read_excel('data/references/road_direction.xlsx')
    df = pd.merge(df, directions, left_on='Наименование дороги выхода',
                  right_on='Дорога', how='inner')

    # yper = 'Условно-переменные расходы, руб'
    # ypos = 'Условно-постоянные расходы, руб'
    # df[yper] = df[yper] / 1000
    # df[ypos] = df[ypos] / 1000
    return df


def get_indexes_data():
    df = pd.read_excel('data/indexes.xlsx', sheet_name='Лист1')
    return df

def get_invest_data():
    invest_df = pd.read_excel('data/initial/invest.xlsx')
    return invest_df


def percentage_change(old_value, new_value):
    try:
        percentage_change = ((new_value - old_value) / old_value) * 100
        return round(percentage_change, 2)
    except ZeroDivisionError:
        return 0.0


# Глобальная переменная для хранения загруженных данных
loaded_data = None

def load_data():
    global loaded_data
    # Проверка, были ли данные уже загружены
    if loaded_data is None:
        # Загрузка файла и создание dataframe
        df = pd.read_csv('data/output_grouped.csv', encoding='utf-8')

        # Выполните здесь необходимую предварительную обработку данных, если требуется

        # Кэширование данных
        loaded_data = df
    return loaded_data







