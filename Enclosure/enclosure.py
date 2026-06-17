"""
Hinged enclosure for: ESP32-C3 SuperMini, 40mm/8ohm speaker, 300mAh LiPo
(32x20x6), TP4056, MP3-TF-16P (DFPlayer), resistors, + a square push button.
Barrel hinge + 2mm pin. Print-ready STLs. Units mm.
"""
import numpy as np
import trimesh
from shapely.geometry import box as sbox
T = trimesh.transformations

# ---------------------- ENCLOSURE -------------------------------------
OUTER_W, OUTER_D, BODY_H = 68.0, 60.0, 46.0
WALL, FLOOR, CORNER_R = 2.8, 2.8, 6.0
LID_TOP, LID_CLEAR, LIP_DEPTH = 6.0, 0.5, 4.0

# Barrel hinge (back edge)
HINGE_R, N_KNUCKLE, HINGE_GAP, PIN_D, HINGE_SPAN = 4.0, 5, 0.45, 2.4, 46.0

# Push button (square hole, right wall +X)
BUTTON = 6.4         # square hole = 6x6 button + 0.4 tolerance
BUTTON_Z = 0.72      # fraction of BODY_H (raised)
BUTTON_Y = 18.0      # along the right wall (further back)

# SD module FLAT (parallel) against right wall (+X); microSD accessed from the TOP (lid open)
# Holder grips only the BOTTOM + CENTRE so the side pad rows stay exposed for soldering.
SD_W, SD_H, SD_THK = 20.0, 20.0, 1.8   # board width (Y), height (Z), thickness (X)
SD_Y, SD_ZB = -5.0, 21.0               # board centre Y; bottom Z set for 5mm clearance below the lid
SD_STAND = 0.0                          # PCB-to-wall gap; raise to ~2.5 if the card cage sits on the wall side
SD_LEDGE_T, SD_CLIP_W, SD_CLIP_H, SD_CLIP_T, SD_CLEAR = 2.5, 9.0, 11.0, 1.6, 0.4

# Speaker (40mm) grille + locating collar on front wall -Y
SPK_D = 40.0
SPK_Z = 0.50
COLLAR_W, COLLAR_H, SPK_CLEAR = 2.0, 6.0, 0.6
GRILLE_HOLE_D = 3.0

# TP4056 charge-port: USB-C opening through the BACK wall (+Y), back-right under the SD module
CHG_X, CHG_Z = 22.5, 8.0     # cutout centre (X along back wall, Z height)
CHG_W, CHG_H = 14.0, 8.0     # generous for a USB-C plug + cable boot

# Battery cradle (floor, back-left). Battery 32x20x6.
BATT_L, BATT_W, BATT_T = 32.0, 20.0, 6.0
CRAD_WALL, CRAD_CLEAR = 2.0, 0.8

# Generic PCB standoffs (4 posts, M2 pilot) -- reposition as needed
POST_D, POST_H, POST_PILOT = 5.0, 5.0, 1.7
PCB_POSTS = []   # standoff posts removed (mount boards with tape/glue)

SEG = 40
# ----------------------------------------------------------------------
AY, AZ = OUTER_D/2 + HINGE_R + 0.5, BODY_H   # axis fully behind back wall, at rim level
ix, iy = OUTER_W/2 - WALL, OUTER_D/2 - WALL      # interior wall faces


def rrect(w, d, r):
    r = max(0.01, min(r, w/2 - 1e-3, d/2 - 1e-3))
    return sbox(-(w/2-r), -(d/2-r), (w/2-r), (d/2-r)).buffer(r, quad_segs=SEG, join_style="round")

def prism(w, d, r, h, z0=0.0):
    m = trimesh.creation.extrude_polygon(rrect(w, d, r), height=h); m.apply_translation((0,0,z0)); return m

def block(xs, ys, zs):
    b = trimesh.creation.box(extents=(xs[1]-xs[0], ys[1]-ys[0], zs[1]-zs[0]))
    b.apply_translation(((xs[0]+xs[1])/2,(ys[0]+ys[1])/2,(zs[0]+zs[1])/2)); return b

def cyl_along(axis, d, length, c):
    m = trimesh.creation.cylinder(radius=d/2, height=length, sections=SEG)
    if axis == 'x': m.apply_transform(T.rotation_matrix(np.pi/2,(0,1,0)))
    if axis == 'y': m.apply_transform(T.rotation_matrix(np.pi/2,(1,0,0)))
    m.apply_translation(c); return m

# ---- BODY shell + hinge ---------------------------------------------
body = trimesh.boolean.difference([
    prism(OUTER_W, OUTER_D, CORNER_R, BODY_H),
    prism(OUTER_W-2*WALL, OUTER_D-2*WALL, max(CORNER_R-WALL,0.5), BODY_H, z0=FLOOR)])

seg = HINGE_SPAN/N_KNUCKLE
add, lid_knuckles = [body], []
for i in range(N_KNUCKLE):
    xc = -HINGE_SPAN/2 + i*seg + seg/2
    klen = seg - HINGE_GAP
    barrel = cyl_along('x', 2*HINGE_R, klen, (xc, AY, AZ))
    if i % 2 == 0:
        add += [barrel, block((xc-klen/2,xc+klen/2),(iy,AY),(BODY_H-HINGE_R,AZ))]
    else:
        lid_knuckles += [barrel, block((xc-klen/2,xc+klen/2),(OUTER_D/2-HINGE_R,AY),(BODY_H,BODY_H+LID_TOP))]
body = trimesh.boolean.union(add)

# ---- additive features ----------------------------------------------
adds = [body]
# speaker locating collar (inside front wall)
fy = -iy
collar = trimesh.boolean.difference([
    cyl_along('y', SPK_D+2*COLLAR_W, COLLAR_H, (0, fy+COLLAR_H/2, BODY_H*SPK_Z)),
    cyl_along('y', SPK_D+SPK_CLEAR, COLLAR_H+2, (0, fy+COLLAR_H/2, BODY_H*SPK_Z))])
adds.append(collar)
# battery cradle (back-left)
cl, cw = BATT_L+2*CRAD_CLEAR+2*CRAD_WALL, BATT_W+2*CRAD_CLEAR+2*CRAD_WALL
bx0, by0 = -ix, iy-cw
crad = trimesh.boolean.difference([
    block((bx0,bx0+cl),(by0,by0+cw),(FLOOR,FLOOR+BATT_T+2)),
    block((bx0+CRAD_WALL,bx0+cl-CRAD_WALL),(by0+CRAD_WALL,by0+cw-CRAD_WALL),(FLOOR,FLOOR+BATT_T+3)),
    block((bx0+cl*0.3,bx0+cl*0.7),(by0-1,by0+CRAD_WALL+1),(FLOOR+2,FLOOR+BATT_T+3))])  # finger notch
adds.append(crad)
# PCB standoffs
for (px,py) in PCB_POSTS:
    post = trimesh.boolean.difference([
        cyl_along('z', POST_D, POST_H, (px,py,FLOOR+POST_H/2)),
        cyl_along('z', POST_PILOT, POST_H+2, (px,py,FLOOR+POST_H-3))])
    adds.append(post)
# SD module flat holder (right wall): bottom ledge + centre clip only -> side pad rows stay exposed
yf, yb = SD_Y - SD_W/2, SD_Y + SD_W/2
xb1 = ix - SD_STAND; xb0 = xb1 - SD_THK
adds.append(block((xb0-SD_CLIP_T, ix), (yf, yb), (SD_ZB-SD_LEDGE_T, SD_ZB)))                       # bottom ledge (under board)
adds.append(block((xb0-SD_CLIP_T, xb0-SD_CLEAR), (SD_Y-SD_CLIP_W/2, SD_Y+SD_CLIP_W/2), (SD_ZB, SD_ZB+SD_CLIP_H)))  # centre clip
adds.append(block((ix-6, ix), (SD_Y-SD_CLIP_W/2, SD_Y+SD_CLIP_W/2), (SD_ZB-12, SD_ZB-SD_LEDGE_T)))  # gusset under ledge
body = trimesh.boolean.union(adds)

# ---- subtractive features -------------------------------------------
cuts = [body]
# square button hole (right wall +X)
cuts.append(block((OUTER_W/2-WALL*2, OUTER_W/2+WALL*2),
                  (BUTTON_Y-BUTTON/2, BUTTON_Y+BUTTON/2),
                  (BODY_H*BUTTON_Z-BUTTON/2, BODY_H*BUTTON_Z+BUTTON/2)))
# TP4056 USB-C cutout through the BACK wall (+Y)
cuts.append(block((CHG_X-CHG_W/2, CHG_X+CHG_W/2),
                  (iy-1, OUTER_D/2+2),
                  (CHG_Z-CHG_H/2, CHG_Z+CHG_H/2)))
# speaker grille holes (front wall)
for ring_r, n in [(0,1),(7,6),(13,10),(18,14)]:
    for k in range(n):
        a = 2*np.pi*k/n
        cuts.append(cyl_along('y', GRILLE_HOLE_D, WALL*4,
                    (ring_r*np.cos(a), -OUTER_D/2, BODY_H*SPK_Z + ring_r*np.sin(a))))
# hinge pin
cuts.append(cyl_along('x', PIN_D, HINGE_SPAN+12, (0, AY, AZ)))
body = trimesh.boolean.difference(cuts)

# ---- LID (closed pose) ----------------------------------------------
plate = prism(OUTER_W, OUTER_D, CORNER_R, LID_TOP, z0=BODY_H)
lip_l = block((-OUTER_W/2+8, -14), (-iy+LID_CLEAR, -iy+LID_CLEAR+WALL), (BODY_H-LIP_DEPTH, BODY_H))
lip_r = block((14, OUTER_W/2-8),  (-iy+LID_CLEAR, -iy+LID_CLEAR+WALL), (BODY_H-LIP_DEPTH, BODY_H))
lid = trimesh.boolean.union([plate, lip_l, lip_r] + lid_knuckles)
lid = trimesh.boolean.difference([lid, cyl_along('x', PIN_D, HINGE_SPAN+12, (0, AY, AZ))])

# ---- EXPORT ----------------------------------------------------------
lid_print = lid.copy()
lid_print.apply_transform(T.rotation_matrix(np.pi,(1,0,0)))
lid_print.apply_translation((0,0,-lid_print.bounds[0][2]))
for name, m in (("enclosure_body", body), ("enclosure_lid", lid_print)):
    m.export(f"/home/claude/{name}.stl")
    print(f"{name:16s} watertight={m.is_watertight} size={m.extents.round(1)} vol={m.volume/1000:.1f}cm^3")

(body+lid).export("/home/claude/enc_closed.stl")
lo = lid.copy(); lo.apply_transform(T.rotation_matrix(np.radians(-115),(1,0,0),point=[0,AY,AZ]))
(body+lo).export("/home/claude/enc_open.stl")
print("ok")
