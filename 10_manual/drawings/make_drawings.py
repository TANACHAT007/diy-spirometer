"""Orthographic part drawings (A3 landscape, 1st-angle-style layout: front / top / right) from 04_print_stl/*.stl.
Feature edges (angle > 28 deg) of faces that face the viewer + silhouette; overall dimensions; title block.
usage: py make_drawings.py   -> drawings/Spiro_part_drawings.pdf  (+ per-part PNG)
Note: STLs are print-oriented; hidden edges behind other geometry are not removed (occlusion ignored)."""
import json, pathlib, numpy as np, trimesh, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.collections import LineCollection, PolyCollection

R = pathlib.Path(__file__).resolve().parents[2]
STL = R / "04_print_stl"
OUT = pathlib.Path(__file__).parent
FEAT = {}
_fp = R / "02_design" / "_brep_features.json"
if _fp.exists():
    FEAT = json.loads(_fp.read_text())
STATS = {p["file"]: p for p in json.loads((STL / "print_stats.json").read_text())["parts"]}
NAMES = {"housing_left": "Housing, left half", "housing_right": "Housing, right half", "top_cover": "Top cover (magnetic)",
         "flow_tube": "Venturi flow tube D28/d23", "mouthpiece": "Mouthpiece (single use)", "bezel": "Display bezel",
         "button_cap": "Button cap", "dock": "Charging dock, base", "dock_cradle": "Charging dock, cradle", "dock_bottom": "Charging dock, base plate"}
# view = (name, axis to look along (drop), horizontal axis, vertical axis)
VIEWS = [("Front (XZ)", 1, 0, 2), ("Top (XY)", 2, 0, 1), ("Right (YZ)", 0, 1, 2)]


def edges_for(mesh, drop):
    n = mesh.face_normals
    view = np.zeros(3); view[drop] = 1.0
    front = n @ view > 1e-6                      # faces seen from +drop
    adj = mesh.face_adjacency
    ang = mesh.face_adjacency_angles
    e = mesh.face_adjacency_edges
    sharp = ang > np.radians(28)
    vis = front[adj[:, 0]] | front[adj[:, 1]]
    sil = front[adj[:, 0]] != front[adj[:, 1]]  # silhouette
    pick = (sharp & vis) | sil
    return mesh.vertices[e[pick]]               # (k,2,3)


def draw_holes(ax, feats, drop, h, v):
    ai = "xyz".index
    for f in feats:
        if f["kind"] != "hole" or ai(f["axis"]) != drop or f["d"] < 1.2:
            continue
        cx, cy = f["center"][h], f["center"][v]; r = f["d"] / 2
        ax.add_patch(plt.Circle((cx, cy), r, fill=False, lw=0.5, color="#06c"))
        ax.plot([cx - r * 1.5, cx + r * 1.5], [cy, cy], color="#06c", lw=0.3, dashes=(6, 1.5, 1, 1.5))
        ax.plot([cx, cx], [cy - r * 1.5, cy + r * 1.5], color="#06c", lw=0.3, dashes=(6, 1.5, 1, 1.5))
        ax.text(cx + r * 1.15, cy + r * 1.15, f"{f['d']:g}", fontsize=5, color="#06c")


def hole_table(feats):
    g = {}
    for f in feats:
        if f["kind"] == "hole" and f["d"] >= 1.2:
            g.setdefault((f["d"], f["axis"]), []).append(f)
    return sorted(g.items())


def draw_view(ax, mesh, drop, h, v, title, scale, feats=()):
    seg = edges_for(mesh, drop)[:, :, [h, v]]
    ax.add_collection(LineCollection(seg, colors="k", linewidths=0.35))
    draw_holes(ax, feats, drop, h, v)
    lo = mesh.bounds[0][[h, v]]; hi = mesh.bounds[1][[h, v]]
    pad = 0.12 * (hi - lo).max() + 6
    ax.set_xlim(lo[0] - pad, hi[0] + pad); ax.set_ylim(lo[1] - pad, hi[1] + pad)
    ax.set_aspect("equal"); ax.axis("off")
    w, hh = hi - lo
    off = pad * 0.55
    kw = dict(arrowprops=dict(arrowstyle="<->", lw=0.6, color="#b00"), annotation_clip=False)
    ax.annotate("", (lo[0], lo[1] - off), (hi[0], lo[1] - off), **kw)
    ax.text((lo[0] + hi[0]) / 2, lo[1] - off - pad * 0.28, f"{w:.1f}", ha="center", va="top", fontsize=8, color="#b00")
    ax.annotate("", (hi[0] + off, lo[1]), (hi[0] + off, hi[1]), **kw)
    ax.text(hi[0] + off + pad * 0.15, (lo[1] + hi[1]) / 2, f"{hh:.1f}", ha="left", va="center", fontsize=8, color="#b00", rotation=90)
    ax.set_title(title, fontsize=9, loc="left")


def sheet(pdf, stl, idx, total):
    key = stl.stem
    mesh = trimesh.load(stl)
    st = STATS.get(stl.name, {})
    fig = plt.figure(figsize=(16.54, 11.69))        # A3 landscape in inches
    fig.patch.set_facecolor("white")
    fig.add_artist(plt.Rectangle((0.015, 0.02), 0.97, 0.96, fill=False, lw=1.4, transform=fig.transFigure))
    gs = fig.add_gridspec(2, 2, left=0.05, right=0.95, top=0.93, bottom=0.2, wspace=0.18, hspace=0.12)
    for i, (t, d, h, v) in enumerate(VIEWS):
        draw_view(fig.add_subplot(gs[i // 2, i % 2]), mesh, d, h, v, t, 1, FEAT.get(key, []))
    ax = fig.add_subplot(gs[1, 1]); ax.axis("off")
    ax.text(0, 1.0, "Overall size X x Y x Z (mm)", fontsize=10, weight="bold")
    ax.text(0, 0.88, " x ".join(f"{x:.1f}" for x in mesh.extents), fontsize=14)
    ax.text(0, 0.7, f"Volume {mesh.volume/1000:.1f} cm3", fontsize=10)
    ax.text(0, 0.62, f"Print: {st.get('grams','?')} g, {st.get('hours','?')} h (PETG, Bambu A1)", fontsize=10)
    rows = hole_table(FEAT.get(key, []))
    if rows:
        import textwrap
        txt = "Holes (blue) dia mm / axis / qty:  " + ";  ".join(f"{d:g}/{a}/{len(v)}" for (d, a), v in rows)
        ax.text(0, 0.42, chr(10).join(textwrap.wrap(txt, 78)), fontsize=7, color="#06c", va="top")
    ax.text(0, 0.02, "General tolerance +/-0.2 mm (FDM). Dimensions in mm.\nHidden edges not shown. See print_guide.md for orientation.", fontsize=8, color="#555")
    tb = fig.add_axes([0.05, 0.035, 0.9, 0.14]); tb.axis("off"); tb.set_xlim(0, 1); tb.set_ylim(0, 1)
    tb.add_patch(plt.Rectangle((0, 0), 1, 1, fill=False, lw=1.2))
    for x in (0.55, 0.72, 0.86):
        tb.plot([x, x], [0, 1], "k", lw=0.8)
    tb.plot([0.55, 1], [0.5, 0.5], "k", lw=0.8)
    tb.text(0.01, 0.62, NAMES.get(key, key), fontsize=20, weight="bold")
    tb.text(0.01, 0.2, "Spiro - DIY IoT spirometer (v8)   file: " + stl.name, fontsize=10)
    tb.text(0.56, 0.68, "Team MEDTHAI", fontsize=11); tb.text(0.56, 0.18, "Drawn by Claude (auto) from CAD", fontsize=9)
    tb.text(0.73, 0.68, "Scale: fit", fontsize=11); tb.text(0.73, 0.18, "Educational prototype", fontsize=9)
    tb.text(0.87, 0.68, f"Sheet {idx}/{total}", fontsize=11); tb.text(0.87, 0.18, "Rev. A", fontsize=9)
    pdf.savefig(fig); fig.savefig(OUT / f"{key}.png", dpi=70); plt.close(fig)


if __name__ == "__main__":
    files = sorted(STL.glob("*.stl"))
    with PdfPages(OUT / "Spiro_part_drawings.pdf") as pdf:
        for i, f in enumerate(files, 1):
            sheet(pdf, f, i, len(files)); print("ok", f.name, flush=True)
