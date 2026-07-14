# fin_lib

Personal library of useful functions for financial analysis.

## Modules

- `df_bootstrapping.py` — Function for bootstrapping the zcb curve from given swap rates.
- `df_interpolation.py` — Log-linear interpolation of a discount factor between two known times.
- `nss_calibration.py` — Functions for calibrating a Nelson-Siegel-Svensson model and displaying the results.

## Installing

```bash
pip install git+https://github.com/tuonome/fin_lib.git
```

If currently working on fin_lib and a project in parallel:

```bash
pip install -e /percorso/locale/fin_lib
```

## How to use

```python
from fin_lib import function_name

result = function_name(...)
```