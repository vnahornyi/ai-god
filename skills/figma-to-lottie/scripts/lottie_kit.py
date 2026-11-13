#!/usr/bin/env python3
"""Small builder for Lottie (Bodymovin 5.x) shape animations.

Import it from a one-off bake script, or run it as a CLI to convert one SVG path:

    python3 lottie_kit.py path "M10 32H57V65H10Z"

Only features every native Lottie renderer supports are emitted: shape layers, groups, paths, fills,
strokes, group and layer transforms, masks, linear, bezier and hold keyframes. No expressions,
no effects, no text, no merge paths.
"""

import json
import math
import re
import sys

PRECISION = 2

EASE = {
    "linear": ((0.0, 0.0), (1.0, 1.0)),
    "in-out-quad": ((0.455, 0.03), (0.515, 0.955)),
    "in-out-cubic": ((0.645, 0.045), (0.355, 1.0)),
    "out-strong": ((0.23, 1.0), (0.32, 1.0)),
    "in-out-strong": ((0.77, 0.0), (0.175, 1.0)),
}


def r(value):
    rounded = round(float(value), PRECISION)
    return 0.0 if rounded == 0 else rounded


def hex_color(value, alpha=1.0):
    value = value.lstrip("#")
    return [r(int(value[i : i + 2], 16) / 255) for i in (0, 2, 4)] + [alpha]


# ---------------------------------------------------------------- SVG path -> Lottie bezier


_TOKEN = re.compile(r"[MmLlHhVvCcSsQqTtZz]|-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")


def _subpaths(d):
    tokens = _TOKEN.findall(d)
    index, command = 0, None
    x = y = start_x = start_y = 0.0
    last_control = None
    current = None
    result = []

    def number():
        nonlocal index
        index += 1
        return float(tokens[index - 1])

    while index < len(tokens):
        if tokens[index].isalpha():
            command = tokens[index]
            index += 1
            if command in "Zz":
                if current:
                    current["closed"] = True
                    result.append(current)
                current = None
                x, y = start_x, start_y
                last_control = None
                continue
        relative = command.islower()
        upper = command.upper()
        base_x, base_y = (x, y) if relative else (0.0, 0.0)

        if upper == "M":
            if current:
                result.append(current)
            x, y = base_x + number(), base_y + number()
            start_x, start_y = x, y
            current = {"points": [(x, y)], "segments": [], "closed": False}
            command = "l" if relative else "L"
            last_control = None
            continue
        if current is None:
            current = {"points": [(x, y)], "segments": [], "closed": False}

        if upper in "LHV":
            if upper == "L":
                nx, ny = base_x + number(), base_y + number()
            elif upper == "H":
                nx, ny = base_x + number(), y
            else:
                nx, ny = x, base_y + number()
            current["segments"].append(((x, y), (nx, ny), (nx, ny)))
            last_control = None
        elif upper in "CS":
            if upper == "C":
                c1 = (base_x + number(), base_y + number())
            else:
                c1 = (2 * x - last_control[0], 2 * y - last_control[1]) if last_control else (x, y)
            c2 = (base_x + number(), base_y + number())
            nx, ny = base_x + number(), base_y + number()
            current["segments"].append((c1, c2, (nx, ny)))
            last_control = c2
        elif upper in "QT":
            if upper == "Q":
                q = (base_x + number(), base_y + number())
            else:
                q = (2 * x - last_control[0], 2 * y - last_control[1]) if last_control else (x, y)
            nx, ny = base_x + number(), base_y + number()
            c1 = (x + 2 / 3 * (q[0] - x), y + 2 / 3 * (q[1] - y))
            c2 = (nx + 2 / 3 * (q[0] - nx), ny + 2 / 3 * (q[1] - ny))
            current["segments"].append((c1, c2, (nx, ny)))
            last_control = q
        else:
            raise ValueError(f"unsupported SVG command {command!r}; convert arcs to curves first")
        current["points"].append((nx, ny))
        x, y = nx, ny

    if current:
        result.append(current)
    return result


def svg_path(d):
    """Lottie shapes ({i, o, v, c}) for an SVG path string, one per subpath."""
    shapes = []
    for sub in _subpaths(d):
        points, segments = sub["points"], sub["segments"]
        if sub["closed"] and len(points) > 1 and _same(points[-1], points[0]):
            points = points[:-1]
        count = len(points)
        vertices = [[r(px), r(py)] for px, py in points]
        out_t = [[0.0, 0.0] for _ in range(count)]
        in_t = [[0.0, 0.0] for _ in range(count)]
        for index, (c1, c2, _end) in enumerate(segments):
            start = points[index % count]
            end = points[(index + 1) % count]
            out_t[index % count] = [r(c1[0] - start[0]), r(c1[1] - start[1])]
            in_t[(index + 1) % count] = [r(c2[0] - end[0]), r(c2[1] - end[1])]
        shapes.append({"i": in_t, "o": out_t, "v": vertices, "c": sub["closed"]})
    return shapes


def _same(a, b):
    return math.isclose(a[0], b[0], abs_tol=1e-4) and math.isclose(a[1], b[1], abs_tol=1e-4)


# ---------------------------------------------------------------- properties and keyframes


def static(value):
    return {"a": 0, "k": value}


def _flat(value):
    if isinstance(value, dict):
        return [n for key in ("v", "i", "o") for point in value[key] for n in point]
    if isinstance(value, list):
        return [n for item in value for n in _flat(item)]
    return [float(value)]


def window(frames, ip, op):
    """Keep only the frames a layer living from ip to op can show, plus one on each side."""
    first = max([i for i, f in enumerate(frames) if f[0] <= ip] or [0])
    last = min([i for i, f in enumerate(frames) if f[0] >= op] or [len(frames) - 1])
    return frames[first : last + 1]


def simplify(frames, tolerance=0.05):
    """Drop baked samples that linear interpolation between the kept neighbours reproduces within
    `tolerance` (canvas units). Use on linear tracks only: baked geometry, never eased keyframes."""
    values = [_flat(f[1] if not isinstance(f[1], str) else svg_path(f[1])[0]) for f in frames]
    kept = [0]
    index = 1
    while index < len(frames):
        candidate = index + 1
        if candidate >= len(frames):
            kept.append(index)
            break
        start, t0 = kept[-1], frames[kept[-1]][0]
        span = frames[candidate][0] - t0
        fits = True
        for middle in range(start + 1, candidate):
            share = (frames[middle][0] - t0) / span
            for a, b, m in zip(values[start], values[candidate], values[middle]):
                if abs(a + (b - a) * share - m) > tolerance:
                    fits = False
                    break
            if not fits:
                break
        if not fits:
            kept.append(index)
        index += 1
    return [frames[i] for i in kept]


def keyframes(frames, ease="in-out-quad"):
    """frames: list of (time, value) or (time, value, ease_name | "hold"). The ease of a frame shapes
    the move from it to the next frame. A track whose values never change becomes static, and a frame
    equal to both neighbours is dropped."""
    flats = [_flat(f[1]) for f in frames]
    if all(flat == flats[0] for flat in flats):
        return static(frames[0][1])
    frames = [
        f for i, f in enumerate(frames)
        if i in (0, len(frames) - 1) or not (flats[i] == flats[i - 1] == flats[i + 1])
    ]
    result = []
    for index, frame in enumerate(frames):
        time, value = frame[0], frame[1]
        name = frame[2] if len(frame) > 2 else ease
        start = value if isinstance(value, list) else [value]
        item = {"t": r(time), "s": start}
        if index < len(frames) - 1:
            if name == "hold":
                item["h"] = 1
            else:
                (ox, oy), (ix, iy) = EASE[name]
                item["o"] = {"x": ox, "y": oy}
                item["i"] = {"x": ix, "y": iy}
        result.append(item)
    return {"a": 1, "k": result}


def path_keyframes(frames, ease="linear"):
    """Shape morph keyframes. Every frame's path must have the same vertex count and closedness."""
    converted = [(f[0], svg_path(f[1])[:1], *f[2:]) for f in frames]
    signatures = {(len(v[0]["v"]), v[0]["c"]) for _, v, *_ in converted}
    if len(signatures) != 1:
        raise ValueError(f"morph keyframes differ in topology: {sorted(signatures)}")
    animated = keyframes(converted, ease)
    if animated["a"] == 0:
        return static(animated["k"][0])
    for item in animated["k"]:
        item["s"] = item["s"] if isinstance(item["s"][0], dict) else [item["s"]]
    return animated


# ---------------------------------------------------------------- shape items, groups, layers


def path_item(d=None, animated=None, name="path"):
    return {"ty": "sh", "nm": name, "ks": animated or static(svg_path(d)[0])}


def fill(color, opacity=None):
    return {"ty": "fl", "nm": "fill", "c": color, "o": opacity or static(100), "r": 1}


def stroke(color, width, opacity=None, join=2, cap=2):
    return {"ty": "st", "nm": "stroke", "c": color, "o": opacity or static(100),
            "w": static(width), "lc": cap, "lj": join, "ml": 4}


def transform(position=None, anchor=None, rotation=None, opacity=None, scale=None):
    return {
        "ty": "tr",
        "p": position or static([0, 0]),
        "a": anchor or static([0, 0]),
        "s": scale or static([100, 100]),
        "r": rotation or static(0),
        "o": opacity or static(100),
        "sk": static(0),
        "sa": static(0),
    }


def group(name, items, tr=None):
    """Draw order inside a group: the first item is on top, so list stroke before fill."""
    return {"ty": "gr", "nm": name, "it": items + [tr or transform()]}


def shape_layer(name, shapes, ip, op, position=(0, 0), opacity=None, mask=None):
    layer = {
        "ddd": 0, "ty": 4, "nm": name, "sr": 1, "ao": 0, "bm": 0, "st": 0,
        "ip": r(ip), "op": r(op),
        "ks": {
            "o": opacity or static(100),
            "r": static(0),
            "p": static([position[0], position[1], 0]),
            "a": static([0, 0, 0]),
            "s": static([100, 100, 100]),
        },
        "shapes": shapes,
    }
    if mask:
        layer["hasMask"] = True
        layer["masksProperties"] = [
            {"inv": False, "mode": "a", "nm": "clip", "pt": static(svg_path(mask)[0]),
             "o": static(100), "x": static(0)}
        ]
    return layer


def precomp(asset_id, layers_top_first, frames):
    """An asset whose layers are stored once and placed by several precomp layers — the way to put
    the same content at two depths (behind and in front of something) without doubling the file."""
    for index, layer in enumerate(layers_top_first, start=1):
        layer["ind"] = index
        layer["ip"], layer["op"] = 0, r(frames)
    return {"id": asset_id, "layers": layers_top_first}


def precomp_layer(name, asset_id, width, height, ip, op, mask=None):
    layer = shape_layer(name, [], ip, op, mask=mask)
    del layer["shapes"]
    layer.update({"ty": 0, "refId": asset_id, "w": width, "h": height})
    return layer


def animation(name, width, height, fps, frames, layers_top_first, assets=()):
    """Lottie draws the first layer on top."""
    for index, layer in enumerate(layers_top_first, start=1):
        layer["ind"] = index
    return {"v": "5.7.4", "nm": name, "fr": fps, "ip": 0, "op": r(frames), "w": width, "h": height,
            "ddd": 0, "assets": list(assets), "layers": layers_top_first}


def dump(data, path):
    with open(path, "w") as handle:
        json.dump(data, handle, separators=(",", ":"))


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "path":
        print(json.dumps(svg_path(sys.argv[2])))
    else:
        print(__doc__)
        sys.exit(2)
