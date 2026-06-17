from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.clipboard import Clipboard
from decimal import Decimal, ROUND_HALF_UP
import calendar
from datetime import datetime, date

try:
    from num2words import num2words
except Exception:
    num2words = None


def date_diff(start_date: date, end_date: date):
    if start_date > end_date:
        start_date, end_date = end_date, start_date

    y = end_date.year - start_date.year
    m = end_date.month - start_date.month
    d = end_date.day - start_date.day

    if d < 0:
        if end_date.month == 1:
            prev_month = 12
            prev_year = end_date.year - 1
        else:
            prev_month = end_date.month - 1
            prev_year = end_date.year
        days_in_prev_month = calendar.monthrange(prev_year, prev_month)[1]
        d += days_in_prev_month
        m -= 1

    if m < 0:
        m += 12
        y -= 1

    return y, m, d


def number_to_text_es(number: int) -> str:
    if num2words:
        try:
            return num2words(number, lang='es')
        except Exception:
            pass
    units = (
        'cero', 'uno', 'dos', 'tres', 'cuatro', 'cinco', 'seis', 'siete', 'ocho', 'nueve',
        'diez', 'once', 'doce', 'trece', 'catorce', 'quince', 'dieciséis', 'diecisiete', 'dieciocho', 'diecinueve'
    )
    tens = ('', '', 'veinte', 'treinta', 'cuarenta', 'cincuenta', 'sesenta', 'setenta', 'ochenta', 'noventa')

    if number < 0:
        return 'menos ' + number_to_text_es(-number)
    if number < 20:
        return units[number]
    if number < 100:
        t = number // 10
        u = number % 10
        if t == 2 and u != 0:
            return 'veinti' + units[u]
        return tens[t] + ('' if u == 0 else ' y ' + units[u])
    if number < 1000:
        h = number // 100
        rest = number % 100
        hundreds = {1: 'ciento', 2: 'doscientos', 3: 'trescientos', 4: 'cuatrocientos', 5: 'quinientos',
                    6: 'seiscientos', 7: 'setecientos', 8: 'ochocientos', 9: 'novecientos'}
        if number == 100:
            return 'cien'
        return hundreds[h] + ('' if rest == 0 else ' ' + number_to_text_es(rest))
    if number < 1000000:
        thousands = number // 1000
        rest = number % 1000
        prefix = ''
        if thousands == 1:
            prefix = 'mil'
        else:
            prefix = number_to_text_es(thousands) + ' mil'
        return prefix + ('' if rest == 0 else ' ' + number_to_text_es(rest))
    return str(number)


class CalcGrid(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 2

        self.add_widget(Label(text='Fecha inicio (DD/MM/AAAA):'))
        self.start_input = TextInput(text=date.today().strftime('%d/%m/%Y'), multiline=False)
        self.add_widget(self.start_input)

        self.add_widget(Label(text='Fecha fin (DD/MM/AAAA):'))
        self.end_input = TextInput(text=date.today().strftime('%d/%m/%Y'), multiline=False)
        self.add_widget(self.end_input)

        self.calc_btn = Button(text='Calcular diferencia')
        self.calc_btn.bind(on_press=self.on_calculate)
        self.add_widget(self.calc_btn)
        self.result_label = Label(text='')
        self.add_widget(self.result_label)

        self.add_widget(Label(text='Número a convertir:'))
        self.num_input = TextInput(text='', multiline=False)
        self.add_widget(self.num_input)

        self.conv_btn = Button(text='Convertir a texto')
        self.conv_btn.bind(on_press=self.on_convert)
        self.add_widget(self.conv_btn)

        self.copy_btn = Button(text='Copiar')
        self.copy_btn.bind(on_press=self.on_copy)
        self.add_widget(self.copy_btn)

        self.output_label = Label(text='')
        self.add_widget(self.output_label)
        self.add_widget(Label(text=''))

    def parse_date(self, s: str):
        try:
            return datetime.strptime(s.strip(), '%d/%m/%Y').date()
        except Exception:
            return None

    def on_calculate(self, instance):
        s = self.parse_date(self.start_input.text)
        e = self.parse_date(self.end_input.text)
        if not s or not e:
            self.result_label.text = 'Error: fechas inválidas'
            return
        y, m, d = date_diff(s, e)
        self.result_label.text = f'{y} años, {m} meses, {d} días'

    def on_convert(self, instance):
        v = self.num_input.text.strip()
        if not v:
            self.output_label.text = 'Error: número vacío'
            return
        try:
            dec = Decimal(v.replace(',', '.')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        except Exception:
            self.output_label.text = 'Error: valor numérico inválido'
            return

        sign = '-' if dec < 0 else ''
        dec_abs = abs(dec)
        total_cents = int((dec_abs * 100).to_integral_value(rounding=ROUND_HALF_UP))
        integer_part = total_cents // 100
        cents = total_cents % 100

        integer_text = number_to_text_es(integer_part)
        if integer_part == 1 and integer_text.strip().lower() == 'uno':
            integer_text = 'un'

        cents_frac = f"{cents:02d}/100"
        formatted = f"Son: {integer_text} con {cents_frac} nuevos soles"
        if sign:
            formatted = 'Menos ' + formatted
        formatted = formatted.title()
        self.output_label.text = formatted

    def on_copy(self, instance):
        txt = self.output_label.text.strip() or self.result_label.text.strip()
        if not txt:
            return
        try:
            Clipboard.copy(txt)
        except Exception:
            pass


class MyKivyApp(App):
    def build(self):
        return CalcGrid()


if __name__ == '__main__':
    MyKivyApp().run()
