"""Диаграмма классов доменной модели (Graphviz). Запуск: python3 gen_classes.py -> class-diagram.dot/.png/.svg"""
import subprocess, html

FONT = 'Liberation Sans'
C = {}  # name -> (stereotype, attrs, methods, color)

def cls(name, attrs, methods=(), stereo=None, color='#e8f0fb'):
    C[name] = (stereo, attrs, methods, color)

cls('Money', ['amount: Decimal', 'currency: String'], stereo='value object', color='#f3ecff')
cls('Passport', ['series: String', 'number: String'], stereo='value object', color='#f3ecff')
cls('DrivingLicense', ['number: String', 'category: String', 'expiresOn: Date'], stereo='value object', color='#f3ecff')
cls('Customer', ['fullName: String', 'phone: String', 'birthDate: Date', 'drivingExperienceYears: Integer', 'status: CustomerStatus'],
    ['submitDocuments()', 'confirm()', 'reject(reason)', 'block()', 'canBook(): Boolean'])
cls('Contract', ['acceptedAt: DateTime', 'version: String'], ['accept()'])
cls('Employee', ['fullName: String', 'isActive: Boolean'])
cls('Manager', [], ['verifyDocuments()', 'decideIncident()', 'issueCharge()', 'resolveSupportRequest()'])
cls('Technician', [], ['performService()', 'inspectAfterRental()'])
cls('Administrator', [], ['manageFleet()', 'setTariff()'])
cls('ServiceZone', ['name: String'], ['contains(location): Boolean'])
cls('Vehicle', ['plateNumber: String', 'model: String', 'fuelLevel: Integer', 'status: VehicleStatus'],
    ['reserve()', 'release()', 'sendToService()', 'markAvailable()', 'decommission()'])
cls('Tariff', ['name: String', 'driveRate: Money', 'waitRate: Money', 'dayRate: Money'])
cls('Booking', ['createdAt: DateTime', 'expiresAt: DateTime', 'status: BookingStatus'], ['cancel()', 'convertToRental()'])
cls('Rental', ['startedAt: DateTime', 'finishedAt: DateTime', 'status: RentalStatus'],
    ['start()', 'finish()', 'close()', 'calculateCost(): Money'])
cls('Inspection', ['type: InspectionType', 'performedAt: DateTime', 'photos: List<Photo>', 'damages: String'])
cls('Payment', ['amount: Money', 'type: PaymentType', 'status: PaymentStatus'], ['execute()', 'release()'])
cls('Charge', ['type: ChargeType', 'amount: Money', 'reason: String', 'evidence: List<Photo>', 'status: ChargeStatus'],
    ['contest()', 'cancel()'])
cls('Incident', ['type: IncidentType', 'occurredAt: DateTime', 'clientAtFault: Boolean', 'status: IncidentStatus'],
    ['registerEvidence()', 'calculateClientShare(): Money', 'close()'])
cls('ServiceRequest', ['reason: ServiceReason', 'status: ServiceRequestStatus'], ['assign(technician)', 'complete()'])
cls('SupportRequest', ['topic: SupportTopic', 'text: String', 'status: SupportRequestStatus'], ['resolve(decision)'])

def label(name):
    st, attrs, meths, col = C[name]
    e = html.escape
    rows = []
    head = f'<b>{e(name)}</b>'
    if st:
        head = f'«{e(st)}»<br/>' + head
    rows.append(f'<tr><td bgcolor="{col}" cellpadding="5">{head}</td></tr>')
    rows.append('<tr><td align="left" balign="left" cellpadding="4">' + ('<br/>'.join('- ' + e(a) for a in attrs) if attrs else ' ') + '</td></tr>')
    rows.append('<tr><td align="left" balign="left" cellpadding="4">' + ('<br/>'.join('+ ' + e(m) for m in meths) if meths else ' ') + '</td></tr>')
    return '<<table border="0" cellborder="1" cellspacing="0" color="#1f3a5f">' + ''.join(rows) + '</table>>'

L = ['digraph G {', '  rankdir=TB; nodesep=0.55; ranksep=0.9; pad=0.3; dpi=120; splines=true; newrank=true;',
     f'  node [shape=plain, fontname="{FONT}", fontsize=11];',
     f'  edge [fontname="{FONT}", fontsize=10, color="#333333", arrowsize=0.9, labelfontsize=10];']
for n in C:
    L.append(f'  {n} [label={label(n)}];')

def assoc(a, b, name='', ma='', mb=''):
    L.append(f'  {a} -> {b} [arrowhead=vee, label=" {name} ", taillabel="{ma}", headlabel="{mb}", labeldistance=2.2];')
def comp(whole, part, name='', mw='1', mp=''):
    L.append(f'  {whole} -> {part} [dir=both, arrowtail=diamond, arrowhead=none, label=" {name} ", taillabel="{mw}", headlabel="{mp}", labeldistance=2.2];')
def aggr(whole, part, name='', mw='1', mp=''):
    L.append(f'  {whole} -> {part} [dir=both, arrowtail=odiamond, arrowhead=none, label=" {name} ", taillabel="{mw}", headlabel="{mp}", labeldistance=2.2];')
def gen(child, parent):
    L.append(f'  {child} -> {parent} [arrowhead=empty, color="#1f3a5f", penwidth=1.4];')

comp('Customer', 'Passport', 'имеет', '1', '1')
comp('Customer', 'DrivingLicense', 'имеет', '1', '1')
assoc('Customer', 'Contract', 'принимает', '1', '0..*')
assoc('Customer', 'Booking', 'создаёт', '1', '0..*')
assoc('Customer', 'SupportRequest', 'подаёт', '1', '0..*')
gen('Manager', 'Employee'); gen('Technician', 'Employee'); gen('Administrator', 'Employee')
aggr('ServiceZone', 'Vehicle', 'включает', '1', '0..*')
assoc('Booking', 'Vehicle', 'резервирует', '0..*', '1')
assoc('Booking', 'Tariff', 'по тарифу', '0..*', '1')
assoc('Booking', 'Rental', 'становится', '1', '0..1')
comp('Rental', 'Inspection', 'включает', '1', '1..2')
assoc('Rental', 'Payment', 'оплачивается', '1', '0..*')
assoc('Rental', 'Charge', 'порождает', '1', '0..*')
assoc('Rental', 'Incident', 'связана с', '1', '0..*')
assoc('Vehicle', 'ServiceRequest', 'требует', '1', '0..*')
assoc('Technician', 'ServiceRequest', 'выполняет', '1', '0..*')
assoc('SupportRequest', 'Charge', 'оспаривает', '0..*', '0..1')
assoc('Manager', 'SupportRequest', 'рассматривает', '1', '0..*')
assoc('Manager', 'Incident', 'обрабатывает', '1', '0..*')

notes = {
  'n1': ('{возраст ≥ 21 года;\\nстаж ≥ 2 лет}', 'Customer'),
  'n2': ('{expiresAt = createdAt\\n+ 15 минут}', 'Booking'),
  'n3': ('{удержание на время\\nаренды = 5 000 ₽}', 'Payment'),
  'n4': ('{у клиента не более одной\\nактивной брони или аренды}', 'Rental'),
}
for k, (t, target) in notes.items():
    L.append(f'  {k} [shape=note, label="{t}", fontname="{FONT}", fontsize=10, style=filled, fillcolor="#fff8c4", color="#8a6d1d"];')
    L.append(f'  {k} -> {target} [style=dashed, arrowhead=none, color="#8a6d1d"];')
L.append('  { rank=same; Money; Tariff; }')
L.append('}')
open('class-diagram.dot', 'w', encoding='utf-8').write('\n'.join(L))
subprocess.run(['dot', '-Tpng', 'class-diagram.dot', '-o', 'class-diagram.png'], check=True)
subprocess.run(['dot', '-Tsvg', 'class-diagram.dot', '-o', 'class-diagram.svg'], check=True)
