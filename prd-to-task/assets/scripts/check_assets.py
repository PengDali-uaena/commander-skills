#!/usr/bin/env python3
"""check_assets.py — 切图闸门：透明底 / @3x 尺寸 / 体积 / 角像素。

用法：
  python3 check_assets.py assets.review.tsv            # 读清单
  python3 check_assets.py --repo . assets.review.tsv
  python3 check_assets.py --allow-opaque assets.review.tsv
  cat assets.review.tsv | python3 check_assets.py -    # 从 stdin 读

清单格式（制表符或空格分隔，# 开头是注释）：
  <相对路径>  <逻辑宽>  <逻辑高>  [alpha|opaque]  [#备注]
  assets/images/order/review/emoji/level_1_terrible.png  38.46  36.54  alpha

判定（任一 FAIL 即退出码 1）：
  alpha  - 必须有 alpha 通道，且存在透明像素；RGB / 全不透明 RGBA 都判为展平图（export 的典型产物）
  opaque - 允许不透明，但 WARN：容器必须自己削圆角，否则白/黑底会露出来
  尺寸   - 宽高必须等于逻辑尺寸 ×3（±1px）
  体积   - 与上次记录比不变大（清单第 6 列可写 baseline 体积，缺省跳过）
"""

import os
import re
import struct
import sys
import zlib

CHANNELS = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}
COLOR_TYPE_NAME = {0: "GRAY", 2: "RGB", 3: "INDEXED", 4: "GRAY+ALPHA", 6: "RGBA"}


class PngError(Exception):
    pass


def decode_png(path):
    with open(path, "rb") as fh:
        data = fh.read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise PngError("不是 PNG")
    pos, idat = 8, []
    w = h = bd = ct = interlace = 0
    while pos + 8 <= len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        ctype = data[pos + 4:pos + 8]
        chunk = data[pos + 8:pos + 8 + length]
        pos += 12 + length
        if ctype == b"IHDR":
            w, h, bd, ct, _, _, interlace = struct.unpack(">IIBBBBB", chunk)
        elif ctype == b"IDAT":
            idat.append(chunk)
        elif ctype == b"IEND":
            break
    if bd != 8:
        raise PngError(f"只支持 8bit（当前 {bd}bit），改用 sips 核")
    if interlace:
        raise PngError("不支持隔行扫描")
    if ct not in CHANNELS:
        raise PngError(f"未知 color type {ct}")
    channels = CHANNELS[ct]
    raw = zlib.decompress(b"".join(idat))
    stride = (w * channels * bd + 7) // 8
    bpp = max(1, channels * bd // 8)
    rows = []
    prev = bytearray(stride)
    ptr = 0
    for _ in range(h):
        ftype = raw[ptr]
        ptr += 1
        line = bytearray(raw[ptr:ptr + stride])
        ptr += stride
        if ftype == 1:
            for i in range(bpp, stride):
                line[i] = (line[i] + line[i - bpp]) & 0xFF
        elif ftype == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif ftype == 3:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 0xFF
        elif ftype == 4:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                b = prev[i]
                c = prev[i - bpp] if i >= bpp else 0
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 0xFF
        rows.append(line)
        prev = line
    return {"w": w, "h": h, "ct": ct, "channels": channels, "rows": rows}


def pixel(img, x, y):
    row = img["rows"][y]
    ct, ch = img["ct"], img["channels"]
    if ct == 6:
        i = x * 4
        return (row[i], row[i + 1], row[i + 2], row[i + 3])
    if ct == 4:
        i = x * 2
        return (row[i], row[i], row[i], row[i + 1])
    if ct == 2:
        i = x * 3
        return (row[i], row[i + 1], row[i + 2], 255)
    if ct == 0:
        v = row[x]
        return (v, v, v, 255)
    v = row[x]
    return (v, v, v, 255)


def alpha_stats(img):
    if img["ct"] not in (4, 6):
        return 0, 0, 0  # min, transparent_px, sampled
    w, h = img["w"], img["h"]
    step = max(1, int((w * h / 200000) ** 0.5))
    amin, transparent, sampled = 255, 0, 0
    for y in range(0, h, step):
        for x in range(0, w, step):
            a = pixel(img, x, y)[3]
            sampled += 1
            if a < amin:
                amin = a
            if a == 0:
                transparent += 1
    return amin, transparent, sampled


def hexa(px):
    return "#%02x%02x%02x" % px[:3] + ("" if px[3] == 255 else "@%.2f" % (px[3] / 255))


def load_manifest(path):
    if path == "-":
        text = sys.stdin.read()
    else:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    entries = []
    for raw in text.split("\n"):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        parts = re.split(r"[\t ]+", line)
        if len(parts) < 3:
            raise SystemExit(f"清单行格式错误（至少要 路径 逻辑宽 逻辑高）：{raw}")
        rel, lw, lh = parts[0], float(parts[1]), float(parts[2])
        mode = parts[3].lower() if len(parts) > 3 else "auto"
        baseline = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else None
        entries.append({"rel": rel, "lw": lw, "lh": lh, "mode": mode, "baseline": baseline})
    return entries


def main():
    argv = sys.argv[1:]
    repo = "."
    allow_opaque = False  # 保留参数位：清单里没写 mode 时靠它放行不透明底
    rest = []
    i = 0
    while i < len(argv):
        if argv[i] == "--repo":
            repo = argv[i + 1]
            i += 2
        elif argv[i] == "--allow-opaque":
            allow_opaque = True
            i += 1
        else:
            rest.append(argv[i])
            i += 1
    if not rest:
        print(__doc__)
        return 2

    entries = load_manifest(rest[0])
    fails, warns = [], []
    for e in entries:
        path = os.path.join(repo, e["rel"])
        if not os.path.isfile(path):
            fails.append(f"{e['rel']}: 文件不存在")
            continue
        size = os.path.getsize(path)
        if e["rel"].lower().endswith(".svg"):
            print(f"OK   {e['rel']}  svg  {size} bytes")
            continue
        try:
            img = decode_png(path)
        except PngError as exc:
            warns.append(f"{e['rel']}: {exc}")
            continue
        mode = COLOR_TYPE_NAME[img["ct"]]
        amin, transparent, sampled = alpha_stats(img)
        c_tl = hexa(pixel(img, 0, 0))
        c_tr = hexa(pixel(img, img["w"] - 1, 0))
        c_bl = hexa(pixel(img, 0, img["h"] - 1))
        c_br = hexa(pixel(img, img["w"] - 1, img["h"] - 1))
        want_w, want_h = round(e["lw"] * 3), round(e["lh"] * 3)
        ok = True
        notes = []
        if abs(img["w"] - want_w) > 1 or abs(img["h"] - want_h) > 1:
            ok = False
            notes.append(f"尺寸 {img['w']}x{img['h']} != 逻辑{e['lw']}x{e['lh']}×3（{want_w}x{want_h}）")
        if e["mode"] == "opaque":
            notes.append("不透明底：容器必须自己 clip 圆角，否则角上会露出稿面底色")
            if img["ct"] in (4, 6) and transparent > 0:
                notes.append("清单标 opaque，但图里有透明像素，确认是否需要 alpha")
        else:
            if img["ct"] not in (4, 6):
                ok = False
                notes.append("无 alpha 通道 = export 展平图，改 rawImages 或让设计给透明导出")
            elif transparent == 0:
                ok = False
                notes.append("alpha 通道全不透明 = 展平图")
            if not allow_opaque and img["ct"] not in (4, 6):
                pass
        if e["baseline"] and size > e["baseline"]:
            ok = False
            notes.append(f"体积 {size} > baseline {e['baseline']}（无损压缩不得变大）")
        status = "OK  " if ok else "FAIL"
        line = (
            f"{status} {e['rel']}  {mode}  {img['w']}x{img['h']}  "
            f"alpha_min={amin} 透明像素={transparent}/{sampled}  {size}B  角 {c_tl}/{c_tr}/{c_bl}/{c_br}"
        )
        print(line)
        for n in notes:
            print(f"     - {n}")
        if not ok:
            fails.append(f"{e['rel']}: {'; '.join(notes)}")

    print(f"check_assets: {len(fails)} fail / {len(warns)} warn / {len(entries)} entries")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
