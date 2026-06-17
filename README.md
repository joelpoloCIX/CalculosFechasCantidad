# Calculador de Años/Meses/Días y Conversor de Número a Texto

Pequeña app en Python (Tkinter) que calcula la diferencia en años, meses y días entre dos fechas y convierte un número entero a texto en español.

Requisitos:
- Python 3.8+
- `num2words` (opcional, mejora la conversión a texto)

Instalación rápida:

```bash
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
.venv\Scripts\activate     # Windows (PowerShell: .venv\Scripts\Activate.ps1)
pip install -r requirements.txt
```

Ejecutar:

```bash
python main.py
```

Notas:
- Si `num2words` no está instalado, la app usa un conversor simple de reserva para números pequeños.
- Las fechas deben introducirse en formato `DD/MM/AAAA`.
