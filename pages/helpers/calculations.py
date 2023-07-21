import pandas as pd

from pages.constants import Constants
from pages.helper import get_invest_data

CON = Constants(2026)


# функция, рассчитывающая параметры на уровне маршрутов
def calculate_data(df, index_df, params):
    so_column = get_so_column(params)
    # costs_column = get_costs_column (params['costs_variant'])

    # если выбраны переменные расходы, то выбираем макс из переменных
    # и помаршрутного
    if so_column == CON.PER:
        df['so_start'] = df[[CON.PER, CON.SO_PM]].max(axis=1)
        df['so_column'] = df['so_start']
        # condition = df[CON.PER] > df[CON.SO_PM]
        # count = condition.sum()
        # print(count)
    else:
        df['so_start'] = df[so_column]
        df['so_column'] = df[so_column]

    if 'option1' in params['invest_variant']:
        df['so_start'] = df['so_start'] + df[CON.INVEST_REMONT]

    invest_df = get_invest_data()
    # инвест проекты
    invest_grouped = invest_df.query('`Участие в расчете` == "Да"').groupby('Направление')['Сумма расходов на проекты, млрд руб'].sum()

    network_value = invest_grouped['Сеть'] * 1000000
    df[CON.INVEST_NETWORK] = df[CON.NETWORK_PART] * network_value
    df[CON.INVEST_DIRECTION] = df[CON.DIRECTION_PART] * df['Направление'].map(invest_grouped) * 1000000
    # инвестиции общесетевые и по направлениям
    if 'option2' in params['invest_variant']:
        df['so_start'] = df['so_start'] + df[CON.INVEST_NETWORK] * params['invest_percent'] / 100
        df['so_start'] = df['so_start'] + df[CON.INVEST_DIRECTION] * params['invest_percent'] / 100

    df['delta_start'] = df['so_start'] - df[CON.PR_P]

    df['growth_percent'] = (df['so_start'] - df[CON.PR_P]) / df[CON.PR_P] * 100
    df['market_coefficient'] = df.apply(market_coefficient, axis=1, args=(params.get("market"),))

    if params['year_variant'][0] != '2026':
        if params['turnover_variant'] == 'option2':
            fp_df = pd.read_csv('data/initial/fin_plan_types.csv')
            fp_df = fp_df.query('`Вид сообщения` == "общий уровень"')
        if params['turnover_variant'] == 'option3':
            fp_df = pd.read_csv('data/initial/fin_plan_05.csv', delimiter=';', decimal=',', encoding='windows-1251')

        for year in params["year_variant"]:
            year_int = int(year)
            if params['turnover_variant'] == 'option1':
                turn_index = 1
            elif params['turnover_variant'] == 'option2':
                df2 = fp_df.query('Год == @year_int')
                df = df.merge(
                    df2[['Груз', 'Индекс грузооборота']],
                    left_on=['Наименование груза ЦО-12'],
                    right_on=['Груз'],
                    how='inner'
                )
                turn_index = df['Индекс грузооборота']
                df = df.rename(columns={'Индекс грузооборота': 'Индекс грузооборота_' + year})
            elif params['turnover_variant'] == 'option3':
                df2 = fp_df.query('Год == @year_int')
                df = df.merge(
                    df2[['Наименование груза ЦО-12', 'Направление', 'Вид сообщения', 'Индекс грузооборота']],
                    left_on=['Наименование груза ЦО-12', 'Направление', 'Вид сообщения'],
                    right_on=['Наименование груза ЦО-12', 'Направление', 'Вид сообщения'],
                    how='inner'
                )
                turn_index = df['Индекс грузооборота']
                df = df.rename(columns={'Индекс грузооборота': 'Индекс грузооборота_' + year})

            # индекс изменения себестоимости
            so_index = cost_index_multiply(index_df, int(year), CON.START_YEAR)
            # индекс изменения тарифов
            tf_index = tarif_index_multiply(index_df, int(year), CON.START_YEAR)
            # грузооборот_новый
            df['epl_' + year] = df[CON.EPL] * turn_index
            # провозная плата
            df['pp_' + year] = df[CON.PR_P] * tf_index * turn_index
            # расходы полные без изменения грузооборота
            df['costs_wo_epl_' + year] = (df[CON.POST] * so_index) + (df[CON.PER] * so_index)
            # расходы полные с изменением грузооборота
            df['costs_w_epl_' + year] = (df[CON.POST] * so_index) + (df[CON.PER] * so_index * turn_index)
            # индекс изменения полных расходов
            df['ipr'] = df['costs_w_epl_' + year] / df['costs_wo_epl_' + year]
            # стоимостная основа
            df['so_' + year] = df['so_start'] * df['ipr'] * so_index
            df['growth_percent'] = ( df['so_' + year] - df['pp_' + year]) / df[
                df['pp_' + year]] * 100
            df['delta_' + year] = df['so_' + year] - df['pp_' + year]


    df['so_market'] = df['so_start'] * df[CON.PER_DOL] * df['market_coefficient'] + df['so_start'] * df[CON.POST_DOL]
    # df['so_market'] = df['so_start'] * df['market_coefficient']
    # df.to_excel('data/test.xlsx', index=False)
    return df


# функция, грппирующая данные маршрутов
def group_data(df, params):
    group1_variant = params['group1_variant']
    group2_variant = params['group2_variant']

    # рассчитываем параметры
    agg_params = {
        CON.P: 'sum',
        CON.EPL: 'sum',
        CON.PR_P: 'sum',
        CON.SO_PM: 'sum',
        CON.SO_SS: 'sum',
        CON.SO_3Z: 'sum',
        CON.SO_KB: 'sum',
        CON.PER: 'sum',
        CON.POST: 'sum',
        CON.POL: 'sum',
        CON.INVEST_REMONT: 'sum',
        CON.INVEST_NETWORK: 'sum',
        CON.INVEST_DIRECTION: 'sum',
        CON.VAG: 'sum',
        'so_start': 'sum',
        'so_market': 'sum',
        'so_column': 'sum',
        'delta_start': 'sum',
        'Код группы по ЦО-12': 'min'
    }
    if params['year_variant'][0] != '2026':
        agg_params['so_' + params['year_variant'][0]] = 'sum'
        agg_params['pp_' + params['year_variant'][0]] = 'sum'
        agg_params['delta_' + params['year_variant'][0]] = 'sum'

    sorting_param = 'Код группы по ЦО-12' if group1_variant == 'Наименование груза ЦО-12' else CON.PR_P
    sorting_asc = True if group1_variant == 'Наименование груза ЦО-12' else False

    group_parameter = [group1_variant] if group2_variant is None else [group1_variant, group2_variant]
    df_grouped = df.groupby(group_parameter).agg(agg_params).reset_index()
    df_grouped = df_grouped.sort_values(by=sorting_param, ascending=sorting_asc)

    if group2_variant is not None:
        df_high = df_grouped.groupby(group1_variant).agg(
            agg_params).reset_index()
        df_high[group2_variant] = 'ИТОГО'
        df_grouped = pd.concat([df_grouped, df_high], ignore_index=True)
        df_grouped = df_grouped.sort_values(by=[sorting_param, CON.PR_P],
                                            ascending=[sorting_asc, False])

    # операции со сгруппированными данными
    new_t = 'so_' + params['year_variant'][0] if params['year_variant'][0] != '2026' else 'so_start'
    old_t = 'pp_' + params['year_variant'][0] if params['year_variant'][0] != '2026' else CON.PR_P

    df_grouped['Тариф на вагон_НТУ'] = df_grouped[new_t] / df_grouped[CON.VAG]
    df_grouped['Тариф на вагон_ДТУ'] = df_grouped[old_t] / df_grouped[CON.VAG]
    df_grouped['Тариф на тонну_ДТУ'] = df_grouped[old_t] / df_grouped[CON.P]
    df_grouped['Тариф на тонну_НТУ'] = df_grouped[new_t] / df_grouped[CON.P]

    return df_grouped


def cost_index_multiply(df, year, start_year):
    parameter = 'Темп роста себестоимости (грузовые перевозки)'
    total_index = df.query('Параметр == @parameter and Год <= @year and Год >= @start_year')[
        'Значение'].prod()
    return total_index


def tarif_index_multiply(df, year, start_year):
    parameter = 'Индексация тарифов'
    total_index = df.query('Параметр == @parameter and Год <= @year and Год >= @start_year')[
        'Значение'].prod()
    return total_index


# на основании параметров выбрать столбец стоимостной основы
def get_so_column(params):
    if params['costs_base_variant'] == 'option1':  # ЦПС
        if params['approach_variant'] == 'option1':  # плоские
            if params['direction_variant'] == 'option1':  # пл_сс
                return CON.SO_SS
            elif params['direction_variant'] == 'option2':  # пл_3з
                return CON.SO_3Z
            elif params['direction_variant'] == 'option3':  # пл_комб
                return CON.SO_KB
            else:  # пл_пом
                return CON.SO_PM
        else:  # с дифф
            if params['direction_variant'] == 'option1':  # дифф_сс
                return CON.SO_SS_DIFF
            elif params['direction_variant'] == 'option2':  # дифф_3з
                return CON.SO_3Z_DIFF
            elif params['direction_variant'] == 'option3':  # дифф_комб
                return CON.SO_KB_DIFF
            else:  # дифф_пом
                return CON.SO_PM_DIFF
    else:  # расходы
        if params['costs_variant'] == 'option1':
            return CON.PER
        return CON.POL


market_df = pd.read_excel('data/market/market.xlsx')
def market_coefficient(row, market_params):
    if row[CON.CARGO] != 'Уголь каменный': return 1
    if row['Вид сообщения'] == 'импорт': return 1
    elif row['Вид сообщения'] == 'транзит': return 1
    elif row['Вид сообщения'] == 'внутрироссийское':
        target_row = market_df.loc[(market_df['Наименование груза ЦО-12'] == 'Уголь каменный') &
               (market_df['Вид сообщения'] == 'внутрироссийское') &
               (market_df['Направление'] == 'Общее')].iloc[0]

    elif row['Вид сообщения'] == 'экспорт':
        if row['Направление'] == 'Северо-Запад':
            direction ='Северо-Запад'
            price = market_params.get('coal').get('west')
        elif row['Направление'] == 'Восток':
            direction = 'Восток'
            price = market_params.get('coal').get('east')
        elif row['Направление'] == 'Юг':
            direction = 'Юг'
            price = market_params.get('coal').get('south')

        if price == 0: price = 'Текущие'

        target_row = market_df.loc[
            (market_df['Наименование груза ЦО-12'] == 'Уголь каменный') &
            (market_df['Вид сообщения'] == 'экспорт') &
            (market_df['Направление'] == direction) &
            (market_df['Цена'] == price)].iloc[0]

    if row['growth_percent'] < 0.1:
        return 1
    elif row['growth_percent'] < 0.3:
        return target_row['Увеличение на 10%']
    elif row['growth_percent'] < 0.5:
        return target_row['Увеличение на 30%']
    elif row['growth_percent'] < 0.75:
        return target_row['Увеличение на 50%']
    elif row['growth_percent'] < 1:
        return target_row['Увеличение на 75%']
    else:
        return target_row['Увеличение на 100%']



