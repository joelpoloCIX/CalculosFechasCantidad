import tkinter as tk
from tkinter import messagebox
from datetime import date, datetime
import calendar
from decimal import Decimal, ROUND_HALF_UP

try:
    from num2words import num2words
except Exception:
    num2words = None

try:
    from tkcalendar import DateEntry
except Exception:
    DateEntry = None


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
    # Fallback minimal implementation for small numbers
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
    # For larger numbers, use a simple representation
    return str(number)


class App:
    def __init__(self, root):
        self.root = root
        root.title('Calculador de Años/Meses/Días y Número a Texto')
        # Menú
        menubar = tk.Menu(root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label='Salir', accelerator='Cmd+Q' if root.tk.call('tk', 'windowingsystem') == 'aqua' else 'Ctrl+Q', command=root.quit)
        menubar.add_cascade(label='Archivo', menu=file_menu)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label='Acerca de', command=self.show_about)
        menubar.add_cascade(label='Ayuda', menu=help_menu)
        root.config(menu=menubar)

        # Atajos
        root.bind_all('<Command-q>', lambda e: root.quit())
        root.bind_all('<Control-q>', lambda e: root.quit())
        tk.Label(root, text='Fecha inicio:').grid(row=0, column=0, sticky='w', padx=6, pady=4)
        if DateEntry:
            self.start_entry = DateEntry(root, width=16, year=date.today().year, month=date.today().month, day=date.today().day, date_pattern='dd/mm/yyyy')
        else:
            self.start_entry = tk.Entry(root, width=20)
            self.start_entry.insert(0, date.today().strftime('%d/%m/%Y'))
        self.start_entry.grid(row=0, column=1, padx=6, pady=4)

        tk.Label(root, text='Fecha fin:').grid(row=1, column=0, sticky='w', padx=6, pady=4)
        if DateEntry:
            self.end_entry = DateEntry(root, width=16, year=date.today().year, month=date.today().month, day=date.today().day, date_pattern='dd/mm/yyyy')
        else:
            self.end_entry = tk.Entry(root, width=20)
            self.end_entry.insert(0, date.today().strftime('%d/%m/%Y'))
        self.end_entry.grid(row=1, column=1, padx=6, pady=4)

        self.calc_btn = tk.Button(root, text='Calcular diferencia', command=self.on_calculate)
        self.calc_btn.grid(row=2, column=0, columnspan=2, pady=6, padx=6, sticky='ew')

        self.result_var = tk.StringVar()
        tk.Label(root, textvariable=self.result_var, fg='blue').grid(row=3, column=0, columnspan=2)

        tk.Label(root, text='Número a convertir:').grid(row=4, column=0, sticky='w', padx=6, pady=4)
        self.num_entry = tk.Entry(root, width=20)
        self.num_entry.grid(row=4, column=1, padx=6, pady=4)

        btn_frame = tk.Frame(root)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=6)
        self.conv_btn = tk.Button(btn_frame, text='Convertir a texto', command=self.on_convert)
        self.conv_btn.pack(side='left', padx=4)
        self.copy_btn = tk.Button(btn_frame, text='Copiar', command=self.copy_text)
        self.copy_btn.pack(side='left', padx=4)
        self.clear_btn = tk.Button(btn_frame, text='Limpiar', command=self.clear_all)
        self.clear_btn.pack(side='left', padx=4)

        self.text_var = tk.StringVar()
        tk.Label(root, textvariable=self.text_var, fg='green', wraplength=500, justify='left').grid(row=6, column=0, columnspan=2, padx=6)

        root.columnconfigure(1, weight=1)

        # Barra de estado
        self.status_var = tk.StringVar()
        self.status_var.set('Listo')
        status = tk.Label(root, textvariable=self.status_var, bd=1, relief='sunken', anchor='w')
        status.grid(row=99, column=0, columnspan=2, sticky='we')

        # Validación numérica (enteros)
        vcmd = (root.register(self._validate_number), '%P')
        self.num_entry.config(validate='key', validatecommand=vcmd)

    def parse_date(self, s: str):
        try:
            return datetime.strptime(s.strip(), '%d/%m/%Y').date()
        except Exception:
            return None

    def _validate_number(self, new_value: str):
        if new_value in ('', '-', '.', '-.'):
            return True
        try:
            # Permitir decimales (usar coma o punto)
            Decimal(new_value.replace(',', '.'))
            return True
        except Exception:
            self.set_status('Sólo se permiten números (decimales)', timeout=1500)
            return False

    def set_status(self, text: str, timeout: int = 0):
        self.status_var.set(text)
        if timeout > 0:
            self.root.after(timeout, lambda: self.status_var.set('Listo'))

    def on_calculate(self):
        s = self.parse_date(self.start_entry.get())
        e = self.parse_date(self.end_entry.get())
        if not s or not e:
            messagebox.showerror('Error', 'Introduce fechas válidas en formato DD/MM/AAAA')
            self.set_status('Error: fechas inválidas', timeout=2000)
            return
        y, m, d = date_diff(s, e)
        self.result_var.set(f'{y} años, {m} meses, {d} días')
        self.set_status('Diferencia calculada', timeout=1500)

    def on_convert(self):
        v = self.num_entry.get().strip()
        if not v:
            messagebox.showerror('Error', 'Introduce un número válido')
            self.set_status('Error: número vacío', timeout=1500)
            return
        try:
            dec = Decimal(v.replace(',', '.')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        except Exception:
            messagebox.showerror('Error', 'El valor debe ser numérico')
            return

        sign = '-' if dec < 0 else ''
        dec_abs = abs(dec)
        total_cents = int((dec_abs * 100).to_integral_value(rounding=ROUND_HALF_UP))
        integer_part = total_cents // 100
        cents = total_cents % 100

        integer_text = number_to_text_es(integer_part)
        # Ajustes: usar 'un' en lugar de 'uno' cuando precede a la moneda
        if integer_part == 1 and integer_text.strip().lower() == 'uno':
            integer_text = 'un'

        # Mostrar los céntimos en formato numérico XX/100 NUEVOS SOLES
        cents_frac = f"{cents:02d}/100"
        # Formato final: Son: <Texto> con XX/100 Nuevos Soles (Title Case)
        formatted = f"Son: {integer_text} con {cents_frac} nuevos soles"
        if sign:
            formatted = 'Menos ' + formatted
        # Aplicar Title Case para visualización "Nombre Propio"
        formatted = formatted.title()
        self.text_var.set(formatted)
        self.set_status('Conversión completada', timeout=1500)

    def copy_text(self):
        txt = self.text_var.get().strip()
        # Si no hay texto convertido, copiar el resultado de la diferencia de fechas
        if not txt:
            txt = self.result_var.get().strip()
        if not txt:
            self.set_status('Nada para copiar', timeout=1500)
            return
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(txt)
            messagebox.showinfo('Copiado', 'Texto copiado al portapapeles')
        except Exception:
            messagebox.showwarning('Aviso', 'No se pudo copiar al portapapeles')

    def clear_all(self):
        if isinstance(self.start_entry, tk.Entry):
            self.start_entry.delete(0, 'end')
            self.start_entry.insert(0, date.today().isoformat())
        else:
            # DateEntry has set_date
            try:
                self.start_entry.set_date(date.today())
            except Exception:
                pass

        if isinstance(self.end_entry, tk.Entry):
            self.end_entry.delete(0, 'end')
            self.end_entry.insert(0, date.today().isoformat())
        else:
            try:
                self.end_entry.set_date(date.today())
            except Exception:
                pass

        self.num_entry.delete(0, 'end')
        self.text_var.set('')
        self.set_status('Campos limpiados', timeout=1000)

    def show_about(self):
        messagebox.showinfo('Acerca de', 'Calculador de Años/Meses/Días y Número a Texto\nHecho con Tkinter')


def main():
    print('DEBUG: main() start')
    root = tk.Tk()
    app = App(root)
    print('DEBUG: entering mainloop')
    root.mainloop()
    print('DEBUG: mainloop exited')


if __name__ == '__main__':
    print('DEBUG: __main__')
    main()
