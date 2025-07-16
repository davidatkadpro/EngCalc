# lib/apps/calc_basic.py
# Basic arithmetic/scientific calc module

from .calc_core import register_calc

META = {
    "id": "basic",
    "name": "Basic Calculator",
    "inputs": [],
    "outputs": [],
}

def compute(params, materials=None):
    return {}

register_calc(META, compute) 