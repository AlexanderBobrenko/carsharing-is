"""Мини-рисовальщик диаграмм деятельности (UML Activity Diagram) с дорожками (swimlanes).
Использование: см. ad_registration.py и др. Запуск: python3 ad_*.py -> PNG + SVG.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, Circle, Rectangle

plt.rcParams['font.family'] = ['Liberation Sans', 'DejaVu Sans']
plt.rcParams['svg.fonttype'] = 'none'

ACTION_FILL, ACTION_EDGE = '#e8f0fb', '#1f3a5f'
DEC_FILL, DEC_EDGE = '#fff4d6', '#8a6d1d'
LINE = '#333333'


class Diagram:
    def __init__(self, lanes, row_h=118, top=56):
        self.lanes, self.row_h, self.top = lanes, row_h, top
        self.x0, x = [], 0
        for _, w in lanes:
            self.x0.append(x)
            x += w
        self.width = x
        self.nodes, self.edges = {}, []

    def lane_cx(self, lane):
        return self.x0[lane] + self.lanes[lane][1] / 2

    def y(self, row):
        return self.top + row * self.row_h

    def node(self, id, kind, lane, row, text='', dx=0, w=None, h=None, x1=None, x2=None):
        """kind: start | end | action | decision | bar. Для bar задайте x1/x2 в виде (lane, dx)."""
        cx, cy = self.lane_cx(lane) + dx, self.y(row)
        if kind in ('start', 'end'):
            w = h = 26
        elif kind == 'action':
            w = w or 240
            h = h or (64 if text.count('\n') < 2 else 80)
        elif kind == 'decision':
            w, h = w or 270, h or 122
        elif kind == 'bar':
            a = self.lane_cx(x1[0]) + x1[1]
            b = self.lane_cx(x2[0]) + x2[1]
            cx, w, h = (a + b) / 2, abs(b - a) + 60, 9
        self.nodes[id] = dict(kind=kind, cx=cx, cy=cy, w=w, h=h, text=text)

    def edge(self, src, dst, label='', out='b', inn='t', my=None, lab=None):
        self.edges.append(dict(src=src, dst=dst, label=label, out=out, inn=inn, my=my, lab=lab))

    def _anchor(self, nid, side, hint_x=None):
        n = self.nodes[nid]
        cx, cy, w, h = n['cx'], n['cy'], n['w'], n['h']
        if n['kind'] == 'bar' and side in 'tb':
            lo, hi = cx - w / 2 + 12, cx + w / 2 - 12
            cx = min(max(hint_x if hint_x is not None else cx, lo), hi)
        return {'t': (cx, cy - h / 2), 'b': (cx, cy + h / 2),
                'l': (cx - w / 2, cy), 'r': (cx + w / 2, cy)}[side]

    def _route(self, e):
        s, d = self.nodes[e['src']], self.nodes[e['dst']]
        p0 = self._anchor(e['src'], e['out'], d['cx'])
        p1 = self._anchor(e['dst'], e['inn'], s['cx'])
        o, i = e['out'], e['inn']
        (x0, y0), (x1, y1) = p0, p1
        if o == 'b' and i == 't':
            if abs(x0 - x1) < 1:
                pts = [p0, p1]
            else:
                my = self.y(e['my']) if e['my'] is not None else (y0 + y1) / 2
                pts = [p0, (x0, my), (x1, my), p1]
        elif o in 'rl' and i == 't':
            pts = [p0, (x1, y0), p1]
        elif o in 'rl' and i in 'rl':
            if abs(y0 - y1) < 1:
                pts = [p0, p1]
            else:
                mx = (x0 + x1) / 2
                pts = [p0, (mx, y0), (mx, y1), p1]
        elif o == 'b' and i in 'rl':
            pts = [p0, (x0, y1), p1]
        elif o == 't' and i in 'rl':
            pts = [p0, (x0, y1), p1]
        else:
            raise ValueError(e)
        return pts

    def draw(self, basename, title=None):
        H = self.top + (max(n['cy'] for n in self.nodes.values()) - self.top) + self.row_h * 0.9
        fig = plt.figure(figsize=(self.width / 100, H / 100), dpi=100)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, self.width)
        ax.set_ylim(H, 0)
        ax.axis('off')
        # дорожки
        for k, (name, w) in enumerate(self.lanes):
            ax.add_patch(Rectangle((self.x0[k], 0), w, H, fc='#f6f8fb' if k % 2 == 0 else 'white',
                                   ec='#9aa7b8', lw=1, zorder=0))
            ax.add_patch(Rectangle((self.x0[k], 0), w, 38, fc='#1f3a5f', ec='#1f3a5f', zorder=1))
            ax.text(self.x0[k] + w / 2, 19, name, ha='center', va='center', color='white',
                    fontsize=11, fontweight='bold', zorder=2)
        # связи
        for e in self.edges:
            pts = self._route(e)
            for a, b in zip(pts[:-2], pts[1:-1]):
                ax.plot([a[0], b[0]], [a[1], b[1]], color=LINE, lw=1.3, zorder=3, solid_capstyle='butt')
            ax.annotate('', xy=pts[-1], xytext=pts[-2], zorder=3,
                        arrowprops=dict(arrowstyle='-|>', color=LINE, lw=1.3, shrinkA=0, shrinkB=0,
                                        mutation_scale=13))
            if e['label']:
                (x0, y0) = pts[0]
                if e['lab']:
                    lx, ly, ha = e['lab']
                elif e['out'] == 'b':
                    lx, ly, ha = x0 + 7, y0 + 14, 'left'
                elif e['out'] == 'r':
                    lx, ly, ha = x0 + 8, y0 - 11, 'left'
                elif e['out'] == 'l':
                    lx, ly, ha = x0 - 8, y0 - 11, 'right'
                else:
                    lx, ly, ha = x0 + 7, y0 - 14, 'left'
                ax.text(lx, ly, e['label'], ha=ha, va='center', fontsize=9, style='italic',
                        color='#222', zorder=6, bbox=dict(fc='white', ec='none', pad=1.2, alpha=0.9))
        # узлы
        for n in self.nodes.values():
            cx, cy, w, h, k = n['cx'], n['cy'], n['w'], n['h'], n['kind']
            if k == 'start':
                ax.add_patch(Circle((cx, cy), 13, fc='black', ec='black', zorder=5))
            elif k == 'end':
                ax.add_patch(Circle((cx, cy), 13, fc='white', ec='black', lw=2.2, zorder=5))
                ax.add_patch(Circle((cx, cy), 7.5, fc='black', ec='black', zorder=6))
            elif k == 'action':
                ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                             boxstyle='round,pad=0,rounding_size=14', fc=ACTION_FILL, ec=ACTION_EDGE,
                             lw=1.5, zorder=5))
                ax.text(cx, cy, n['text'], ha='center', va='center', fontsize=9.3, zorder=6,
                        linespacing=1.25)
            elif k == 'decision':
                ax.add_patch(Polygon([(cx, cy - h / 2), (cx + w / 2, cy), (cx, cy + h / 2), (cx - w / 2, cy)],
                             fc=DEC_FILL, ec=DEC_EDGE, lw=1.5, zorder=5))
                ax.text(cx, cy, n['text'], ha='center', va='center', fontsize=8.8, zorder=6,
                        linespacing=1.2)
            elif k == 'bar':
                ax.add_patch(Rectangle((cx - w / 2, cy - h / 2), w, h, fc='black', ec='black', zorder=5))
        fig.savefig(basename + '.png', dpi=110)
        fig.savefig(basename + '.svg')
        plt.close(fig)
