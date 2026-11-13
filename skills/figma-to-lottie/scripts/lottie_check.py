#!/usr/bin/env python3
"""Check a Lottie JSON before it ships to a native renderer.

    python3 lottie_check.py animation.json [--max-kb 60]

Fails (exit 1) on what native Lottie renderers drop or render differently, and reports the numbers
a reviewer asks about: size, layers, keyframes, baked share.
"""

import argparse
import json
import os
import sys

UNSUPPORTED_SHAPES = {"mm": "merge paths", "rp": "repeater"}
UNSUPPORTED_LAYERS = {5: "text layer", 1: "solid layer", 6: "audio layer"}


def walk(node, path="$"):
    yield path, node
    if isinstance(node, dict):
        for key, value in node.items():
            yield from walk(value, f"{path}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from walk(value, f"{path}[{index}]")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--max-kb", type=float, default=60)
    args = parser.parse_args()

    with open(args.file) as handle:
        data = json.load(handle)
    errors, warnings = [], []
    op = data.get("op", 0)
    size_kb = os.path.getsize(args.file) / 1024

    for key in ("v", "fr", "ip", "op", "w", "h", "layers"):
        if key not in data:
            errors.append(f"root is missing {key!r}")

    keyframe_count = 0
    for path, node in walk(data):
        if not isinstance(node, dict):
            continue
        if "x" in node and isinstance(node["x"], str):
            errors.append(f"{path}: expression — native renderers ignore it")
        if node.get("ty") in UNSUPPORTED_SHAPES:
            warnings.append(f"{path}: {UNSUPPORTED_SHAPES[node['ty']]} — check support on every target renderer")
        if node.get("a") == 1 and isinstance(node.get("k"), list):
            frames = node["k"]
            keyframe_count += len(frames)
            times = [f.get("t") for f in frames]
            if times != sorted(times):
                errors.append(f"{path}: keyframe times are not ascending")
            shapes = [f["s"][0] for f in frames if isinstance(f.get("s"), list) and f["s"] and isinstance(f["s"][0], dict) and "v" in f["s"][0]]
            if shapes:
                topologies = {(len(s["v"]), s.get("c")) for s in shapes}
                if len(topologies) > 1:
                    errors.append(f"{path}: morph keyframes differ in vertex count or closedness {sorted(topologies)}")
            for index, frame in enumerate(frames[:-1]):
                if not frame.get("h") and ("i" not in frame or "o" not in frame):
                    errors.append(f"{path}.k[{index}]: no easing handles and no hold")
            if times and (times[0] > op or times[-1] < 0):
                warnings.append(f"{path}: keyframes fall outside 0..{op}")

    layer_count = len(data.get("layers", []))
    for index, layer in enumerate(data.get("layers", [])):
        if layer.get("ty") in UNSUPPORTED_LAYERS:
            warnings.append(f"layers[{index}] {layer.get('nm')!r}: {UNSUPPORTED_LAYERS[layer['ty']]}")
        if layer.get("ip", 0) >= layer.get("op", op):
            errors.append(f"layers[{index}] {layer.get('nm')!r}: ip is not before op")
        if layer.get("ef"):
            errors.append(f"layers[{index}] {layer.get('nm')!r}: effects are not rendered natively")

    if size_kb > args.max_kb:
        errors.append(f"file is {size_kb:.1f} KB, over the {args.max_kb} KB budget")

    print(f"size {size_kb:.1f} KB · {layer_count} layers · {keyframe_count} keyframes · "
          f"{op} frames at {data.get('fr')} fps ({op / max(data.get('fr', 1), 1):.2f} s)")
    for line in warnings:
        print(f"warn  {line}")
    for line in errors:
        print(f"error {line}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
