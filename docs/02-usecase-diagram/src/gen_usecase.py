"""Диаграмма прецедентов (UML Use Case Diagram). Запуск: python3 gen_usecase.py -> usecase-diagram.png/.svg"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle, Circle

plt.rcParams['font.family'] = ['Liberation Sans', 'DejaVu Sans']
plt.rcParams['svg.fonttype'] = 'none'

W = 1560
X0, X1 = 430, 1030           # границы системы
CX = (X0 + X1) / 2           # центр столбца прецедентов
OW, OH = 330, 50             # размеры овала
STEP = 72                    # шаг между овалами

groups = [
    ('Клиент', ['Забронировать автомобиль', 'Начать аренду', 'Завершить аренду', 'Оплатить поездку',
                'Сообщить об инциденте', 'Обратиться в поддержку', 'Зарегистрироваться']),
    ('Менеджер проката', ['Проверить документы клиента', 'Обработать инцидент', 'Рассмотреть обращение',
                          'Начислить штраф или доплату', 'Создать заявку на обслуживание']),
    ('Техник', ['Принять заявку на обслуживание', 'Выполнить обслуживание', 'Осмотреть автомобиль после аренды']),
    ('Администратор', ['Управлять автопарком', 'Управлять тарифами и штрафами', 'Управлять сотрудниками',
                       'Сформировать отчёт']),
]
extra_gap_after = {'Завершить аренду': 22, 'Зарегистрироваться': 30}   # место под стрелки include/extend

# координаты овалов
pos, y, first = {}, 140, True
actor_cases = {}
for actor, cases in groups:
    if not first:
        y += 18
    first = False
    actor_cases[actor] = []
    for c in cases:
        pos[c] = y
        actor_cases[actor].append(c)
        y += STEP + extra_gap_after.get(c, 0)
H = y + 20

fig = plt.figure(figsize=(W / 100, H / 100), dpi=100)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis('off')

# граница системы
ax.add_patch(Rectangle((X0, 50), X1 - X0, H - 70, fc='#fbfcfe', ec='#1f3a5f', lw=2, zorder=0))
ax.text(CX, 78, 'Система каршеринга', ha='center', va='center', fontsize=15, fontweight='bold', color='#1f3a5f')

def stickman(x, yc, name):
    ax.add_patch(Circle((x, yc - 30), 11, fc='white', ec='#1f3a5f', lw=2, zorder=3))
    for (a, b, c, d) in [(x, yc - 19, x, yc + 14), (x - 22, yc - 8, x + 22, yc - 8),
                         (x, yc + 14, x - 16, yc + 42), (x, yc + 14, x + 16, yc + 42)]:
        ax.plot([a, c], [b, d], color='#1f3a5f', lw=2, zorder=3)
    ax.text(x, yc + 62, name, ha='center', va='center', fontsize=11.5, fontweight='bold')

def system_box(x, yc, name, w=250):
    ax.add_patch(Rectangle((x - w / 2, yc - 30), w, 60, fc='#f2f2f2', ec='#555', lw=1.5, ls='--', zorder=3))
    ax.text(x, yc - 9, '«system»', ha='center', va='center', fontsize=9.5, style='italic')
    ax.text(x, yc + 9, name, ha='center', va='center', fontsize=10.5)

# овалы
for c, yy in pos.items():
    ax.add_patch(Ellipse((CX, yy), OW, OH, fc='#e8f0fb', ec='#1f3a5f', lw=1.4, zorder=3))
    ax.text(CX, yy, c, ha='center', va='center', fontsize=10.5, zorder=4)

# акторы и ассоциации
AX = 190
for actor, cases in actor_cases.items():
    ys = [pos[c] for c in cases]
    yc = (min(ys) + max(ys)) / 2
    stickman(AX, yc - 6, actor)
    for c in cases:
        ax.plot([AX + 24, CX - OW / 2 + 4], [yc - 14, pos[c]], color='#333', lw=1.1, zorder=2)

# внешние системы
EX = 1290
ext = {
    'Сервис проверки\nдокументов': (pos['Зарегистрироваться'] - 40, ['Зарегистрироваться']),
    'СМС-сервис': (pos['Зарегистрироваться'] + 40, ['Зарегистрироваться']),
    'Телематика автомобиля': ((pos['Начать аренду'] + pos['Завершить аренду']) / 2 - 8, ['Начать аренду', 'Завершить аренду']),
    'Платёжный шлюз': (pos['Оплатить поездку'] + 6, ['Начать аренду', 'Оплатить поездку']),
}
for name, (yy, cases) in ext.items():
    system_box(EX, yy, name.replace('\n', ' ') if '\n' not in name else name.replace('\n', ' '))
    for c in cases:
        ax.plot([EX - 125, CX + OW / 2 - 4], [yy, pos[c]], color='#333', lw=1.1, zorder=2)

# include / extend
def dashed_arrow(p0, p1, label, lx):
    ax.annotate('', xy=p1, xytext=p0, zorder=5,
                arrowprops=dict(arrowstyle='-|>', ls='--', color='#333', lw=1.3, shrinkA=0, shrinkB=0, mutation_scale=13))
    ax.text(lx, (p0[1] + p1[1]) / 2, label, ha='left', va='center', fontsize=9.5, style='italic',
            bbox=dict(fc='white', ec='none', pad=1))

y3, y4 = pos['Завершить аренду'], pos['Оплатить поездку']
dashed_arrow((CX, y3 + OH / 2), (CX, y4 - OH / 2), '«include»', CX + 8)
y7, y8 = pos['Зарегистрироваться'], pos['Проверить документы клиента']
dashed_arrow((CX, y8 - OH / 2), (CX, y7 + OH / 2), '«extend»', CX + 8)

fig.savefig('usecase-diagram.png', dpi=110)
fig.savefig('usecase-diagram.svg')
