import csv, io, re, datetime
from typing import List, Dict, Any

def _scale_from_units(hdr: str, unit: str) -> float:
    """
    Return the factor to multiply the raw CSV number by, based on the unit cell.
    Handles strings like 'x10³ mm³' or slightly corrupted 'x10? mm?'.
    Falls back to sensible defaults for steel tables:
      - I* (mm^4) -> x10^6
      - Z*/S* (mm^3) -> x10^3
    """
    if not unit:
        return 1.0
    # Try to read the "x10^n" part, accepting superscripts or normal digits
    m = re.search(r"x\s*10\s*[\^]?\s*([0-9]+)|x10([⁰¹²³⁴⁵⁶⁷⁸⁹])", unit)
    if m:
        if m.group(1):
            return 10 ** int(m.group(1))
        # Superscript fallback (rare if CSV preserved it)
        supers = "⁰¹²³⁴⁵⁶⁷⁸⁹"
        return 10 ** supers.index(m.group(2))
    # Heuristics if the exponent was lost:
    if hdr.strip().lower() in ("ix", "iy"):
        return 1e6
    if hdr.strip().lower() in ("zx", "zy", "sx", "sy"):
        return 1e3
    return 1.0

def _num(s: str):
    if s is None:
        return None
    t = s.strip()
    if t == "":
        return None
    t = t.replace(",", "")
    try:
        if re.fullmatch(r"[+-]?\d+", t):
            return int(t)
        return float(t)
    except ValueError:
        return t  # leave as string (e.g., 'C', 'HR')

def _clean_designation(desc: str) -> str:
    # e.g., "310UC158 (G300)" -> "310UC158"
    if not desc:
        return ""
    return desc.split("(", 1)[0].strip()

def _type_from_designation(designation: str) -> str:
    # Extract letters in the middle: 610 UB 125 -> 'UB'; 310UC158 -> 'UC'
    m = re.search(r"[A-Za-z]{2,3}", designation)
    return m.group(0).upper() if m else ""

def sections_csv_to_schema(
    csv_text: str,
    *,
    source="Australian Steel Standards",
    region="AU",
    material="steel"
) -> List[Dict[str, Any]]:
    """
    Convert the provided CSV (headers row, units row, then data) into the JSON schema:
    {
      source, region, material, type, designation,
      dimensions: { d_mm, bf_mm, tf_mm, tw_mm, r_mm },
      properties: { mass_kg_per_m, area_mm2, Ix_mm4, Iy_mm4, Zx_mm3, Zy_mm3, rx_mm, ry_mm, Sx_mm3, Sy_mm3 },
      raw_data: { extracted_at: YYYY-MM-DD }
    }
    """
    f = io.StringIO(csv_text.strip("\ufeff \n\r"))
    rows = list(csv.reader(f))
    # Drop fully blank rows
    rows = [r for r in rows if any(c.strip() for c in r)]
    if len(rows) < 3:
        raise ValueError("Expected at least 3 rows (headers, units, data).")

    headers = [h.strip().strip('"') for h in rows[0]]
    units   = [u.strip().strip('"') for u in rows[1]]
    H = {i: h for i, h in enumerate(headers)}

    # helpful index helpers (first match wins)
    def idx_of(name: str) -> int:
        return next((i for i, h in enumerate(headers) if h == name), -1)

    # pick first 'tw' as web thickness
    tw_indices = [i for i, h in enumerate(headers) if h == "tw"]
    idx_tw = tw_indices[0] if tw_indices else -1

    # column indexes we need
    idx_desc = idx_of("Description")
    idx_W    = idx_of("Weight")
    idx_d    = idx_of("d")
    idx_bf   = idx_of("bf")
    idx_tf   = idx_of("tf")
    idx_r1   = idx_of("r1")
    idx_Ag   = idx_of("Ag")
    idx_Ix   = idx_of("Ix")
    idx_Iy   = idx_of("Iy")
    idx_Zx   = idx_of("Zx")
    idx_Zy   = idx_of("Zy")
    idx_rx   = idx_of("rx")
    idx_ry   = idx_of("ry")
    idx_Sx   = idx_of("Sx")
    idx_Sy   = idx_of("Sy")

    # unit scales
    def scale_at(idx: int) -> float:
        if idx < 0 or idx >= len(units):
            return 1.0
        return _scale_from_units(headers[idx], units[idx])

    scale_Ix = scale_at(idx_Ix)
    scale_Iy = scale_at(idx_Iy)
    scale_Zx = scale_at(idx_Zx)
    scale_Zy = scale_at(idx_Zy)
    scale_Sx = scale_at(idx_Sx)
    scale_Sy = scale_at(idx_Sy)

    out: List[Dict[str, Any]] = []
    today = datetime.date.today().isoformat()

    for row in rows[2:]:
        # pad/truncate row
        if len(row) < len(headers):
            row = row + [""] * (len(headers) - len(row))
        elif len(row) > len(headers):
            row = row[:len(headers)]

        designation = _clean_designation(row[idx_desc] if idx_desc >= 0 else "")
        typ = _type_from_designation(designation)

        def val(idx):  # simple getter
            return _num(row[idx]) if idx >= 0 else None

        obj = {
            "source": source,
            "region": region,
            "material": material,
            "type": typ,
            "designation": designation,
            "dimensions": {
                "d_mm":  val(idx_d),
                "bf_mm": val(idx_bf),
                "tf_mm": val(idx_tf),
                "tw_mm": val(idx_tw),
                "r_mm":  val(idx_r1),
            },
            "properties": {
                "mass_kg_per_m": val(idx_W),
                "area_mm2":      val(idx_Ag),
                "Ix_mm4":  (val(idx_Ix) * scale_Ix) if val(idx_Ix) is not None else None,
                "Iy_mm4":  (val(idx_Iy) * scale_Iy) if val(idx_Iy) is not None else None,
                "Zx_mm3":  (val(idx_Zx) * scale_Zx) if val(idx_Zx) is not None else None,
                "Zy_mm3":  (val(idx_Zy) * scale_Zy) if val(idx_Zy) is not None else None,
                "rx_mm":   val(idx_rx),
                "ry_mm":   val(idx_ry),
                "Sx_mm3":  (val(idx_Sx) * scale_Sx) if val(idx_Sx) is not None else None,
                "Sy_mm3":  (val(idx_Sy) * scale_Sy) if val(idx_Sy) is not None else None,
            },
            "raw_data": {
                "extracted_at": today
            }
        }
        out.append(obj)

    return out

