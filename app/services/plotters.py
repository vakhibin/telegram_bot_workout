import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


def plot_cumulative_progress(calories, water, calorie_limit, calorie_goal, water_limit):
    # Находим максимальную длину среди входных списков
    max_length = max(len(calories), len(water))

    # Дополняем списки до одинаковой длины (в данном случае - до max_length)
    calories = np.pad(calories, (0, max_length - len(calories)), constant_values=0)
    water = np.pad(water, (0, max_length - len(water)), constant_values=0)

    # Кумулятивная сумма
    cumulative_calories = np.cumsum(calories)
    cumulative_water = np.cumsum(water)

    # Создание DataFrame для удобства работы с Seaborn
    df = pd.DataFrame({
        'День': list(range(max_length)),
        'Калории': cumulative_calories,
        'Вода': cumulative_water
    })

    # Создание графиков
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))

    # Добавление графика для калорий
    sns.lineplot(data=df, x='День', y='Калории', marker='o', color='blue', label='Калории', ax=ax1)
    ax1.axhline(y=calorie_limit, color='red', linestyle='--', label='Граница калорий')
    ax1.axhline(y=calorie_goal, color='pink', linestyle='--', label='Goal калорий')
    ax1.set_title('Кумулятивный прогресс по калориям')
    ax1.set_xlabel('День')
    ax1.set_ylabel('Калории')
    ax1.legend(title='Легенда')
    ax1.grid(alpha=0.4)

    # Добавление графика для воды
    sns.lineplot(data=df, x='День', y='Вода', marker='o', color='green', label='Вода', ax=ax2)
    ax2.axhline(y=water_limit, color='red', linestyle='--', label='Goal по воде')
    ax2.set_title('Кумулятивный прогресс по воде')
    ax2.set_xlabel('День')
    ax2.set_ylabel('Вода (мл)')
    ax2.legend(title='Легенда')
    ax2.grid(alpha=0.4)

    # Возвращение объекта фигуры
    fig.tight_layout()  # Автоматическая настройка отступов
    plt.close(fig)  # Закрываем текущее окно, чтобы не отображать его сразу
    return fig