# Print guide — diy-spirometer (Bambu A1, PETG)

Totals (model v3, 2026-10-15): ≈470 g PETG, ≈27 h, ≈360 THB. All parts fit the 256 mm bed.
Profile: 0.2 mm layer, 4 walls (≥1.6 mm), 20 % gyroid, 0.4 nozzle. Printed hole sizes already include the 0.4 mm fit rule.

| Part | File | Orientation | Supports | Notes |
|---|---|---|---|---|
| Housing left | housing_left.stl | **outer face down** (seam face up) | none inside; tree supports only for the display window counter-bore if the slicer asks | blue; heat-set M3x5 inserts go into the **right** half only |
| Housing right | housing_right.stl | outer face down | as above | 4 × M3x5x4.5 inserts at the seam bosses, 1 × 6x3 magnet pocket in the grip end |
| Flow tube | flow_tube.stl | **vertical, mouth end down** | exit ring (flat 3 mm lip) + the manifold block's horizontal channel need small supports/bridging; mouth ring is 45° (no support) | white; the venturi cone prints at 10.5° from vertical = clean. Do NOT print lying down (venturi would be oval). Test the channel with a Ø2 mm wire before use |
| Top cover | top_cover.stl | flat side (z=0) down | none | 4 × 5x2 magnets glued, polarity checked against the housing seats |
| Mouthpiece | mouthpiece.stl | wide end down | none | personal item — print one per user, wash with mild soap |
| Dock | dock.stl | **bottom face down** | none | 4 × M3x4x4.5 inserts in the underside, 2 pogo holes Ø2.2, magnet pocket Ø6.2 |
| Dock bottom | dock_bottom.stl | flat | none | M3x6 countersunk ×4 |

## Post-print
1. Heat-set inserts at 220 °C with the iron tip straight; insert flush. Brass **contact** inserts (M3x4x4.5) go into the grip end of each half *before* closing (contacts are NOT on the seam: left half w=13, right half w=37).
2. Magnets: 5x2 mm ×8 (cover + housing seats), 6x3 mm ×2 (grip + dock). Test polarity with the parts together, then glue (CA).
3. Pogo pins: Ø2.0 barrel in the Ø2.2 holes, a drop of CA/hot-glue; solder wires to the rear ends.
4. Flow tube: ream the Ø2 channel, then check by blowing through each nipple — air must come out of the matching tap.
5. Leak test: plug the mouth end, put 3 L syringe on the exit, push to 300 Pa (≈3 cmH2O), pressure must hold; the venturi has no other seals than the 2 silicone stubs.

## Known risks (not yet verified by a real print)
- Manifold channel Ø2.4 printed horizontally (bridging) may sag → ream it.
- 2.4 mm shell wall is only 6 perimeters of 0.4 — OK for PETG but grip ridges are 1 mm deep.
- Venturi surface roughness changes the discharge coefficient → calibrate K after every re-print.
