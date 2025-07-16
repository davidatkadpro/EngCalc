# lib/apps/calc_structural/beam_span.py
# Beam span engineering calc module

from ..calc_core import register_calc

META = {
    "id": "beam_span",
    "name": "Beam Span Capacity",
    "inputs": [],
    "outputs": [],
}

def compute(params, materials=None):
    return {}

register_calc(META, compute) 