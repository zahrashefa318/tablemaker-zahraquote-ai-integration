from typing import List, Dict, Any, Optional
from html import escape

def order_columns(
    rows: List[Dict[str, Any]],
    columns: Optional[List[str]] = None,
) -> List[str]:
    if columns:
        return columns

    cols = []
    for row in rows:
        for key in row:
            if key not in cols:
                cols.append(key)
    return cols

def to_html(rows:List[Dict[str,Any]], columns:List[str])->str:
    # CSS + wrapper so the header sticks and borders look clean
    css = """
    <style>
      .tm-wrap { max-height: 420px; overflow: auto;
                 border: 1px solid #e5e7eb; border-radius: 10px; }
      .tm      { width: 100%; border-collapse: collapse;
                 font: 14px/1.5 system-ui,-apple-system,Segoe UI,Roboto,"Helvetica Neue",Arial,sans-serif; }
      .tm th, .tm td { border: 1px solid #e5e7eb; padding: 10px 12px; text-align: left; vertical-align: top; }
      .tm thead th { position: sticky; top: 0; z-index: 1; background: #f8fafc; box-shadow: 0 1px 0 rgba(0,0,0,0.05) inset; }
      .tm tbody tr:nth-child(even) td { background: #fafafa; }
      .tm tbody tr:hover td { background: #f1f5f9; }
    </style>
    """
    #---------Table header from keys in dictionary--------------------
    tableHeader="<thead><tr>"+ "". join(f"<th>{escape(str(c))}</th>" for c in columns)+"</tr></thead>"
    trs=[]
    for r in rows:
        tds=[]
        for c in columns:
            v=r.get(c , "")
            tds.append(f"<td>{'' if v is None else escape(str(v))}</td>")
        trs.append(f"<tr>{ "".join(tds)}</tr>")

    tableBody="<tbody>"+"".join(trs)+"</tbody>"
    return f"""{css}<div class="tm-wrap"><table class="tm">{tableHeader}{tableBody}</table></div>"""

def to_markdown(rows, columns):
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join("---" for _ in columns) + " |"
    lines = [header, sep]

    for r in rows:
        lines.append("| " + " | ".join(str(r.get(c,"")) for c in columns) + " |")

    return "\n".join(lines)
