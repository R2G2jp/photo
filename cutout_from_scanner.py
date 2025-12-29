import cv2
import numpy as np
import os

INPUT_DIR = "input"
OUTPUT_DIR = "output"
WHITE_TH = 240        # 白判定
MIN_WHITE_RUN = 25    # 白帯の最小高さ(px)
ASPECT = 127/89        # 横幅/縦長さ のアスペクト比 (width / height)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- 実行用関数 ---
def process_file(fname, input_dir=INPUT_DIR, output_dir=OUTPUT_DIR,
                 do_adjust=False, white_th=WHITE_TH,
                 min_white_run=MIN_WHITE_RUN, aspect=ASPECT):
    """1ファイル分を読み込み、分割して出力する."""
    img_path = os.path.join(input_dir, fname)
    try:
        with open(img_path, 'rb') as f:
            data = f.read()
    except Exception as e:
        print(f"open failed: {img_path}: {e}")
        return

    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        print(f"failed to open: {img_path}")
        return

    parts = split_image(img, white_th=white_th,
                        min_white_run=min_white_run, aspect=aspect)

    # 切り出した枚数と各ピースのサイズを表示（縦, 横）
    print(f"{fname}: found {len(parts)} pieces")
    for idx, p in enumerate(parts, 1):
        h, w = p.shape[:2]
        print(f"  piece {idx}: height={h}, width={w}")

    for i, p in enumerate(parts, 1):
        if do_adjust:
            p = auto_adjust(p)
        out = f"{os.path.splitext(fname)[0]}_{i:02}.jpg"
        ok, buf = cv2.imencode('.jpg', p, [cv2.IMWRITE_JPEG_QUALITY, 95])
        if not ok:
            print(f"imencode failed: {fname} part{i}")
            continue
        out_path = os.path.join(output_dir, out)
        try:
            with open(out_path, 'wb') as wf:
                wf.write(buf.tobytes())
            print(f"WROTE: {out_path} ({len(buf)} bytes)")
        except Exception as e:
            print(f"write failed: {out_path}: {e}")

def process_all(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR, do_adjust=False,
                white_th=WHITE_TH, min_white_run=MIN_WHITE_RUN, aspect=ASPECT):
    """ディレクトリ内の画像をすべて処理する."""
    os.makedirs(output_dir, exist_ok=True)
    for fname in os.listdir(input_dir):
        if not fname.lower().endswith((".jpg", ".png")):
            continue
        process_file(fname, input_dir=input_dir, output_dir=output_dir,
                     do_adjust=do_adjust, white_th=white_th,
                     min_white_run=min_white_run, aspect=aspect)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Cut out pieces from scanned images")
    parser.add_argument("--input", "-i", default=INPUT_DIR, help="input directory")
    parser.add_argument("--output", "-o", default=OUTPUT_DIR, help="output directory")
    parser.add_argument("--adjust", action="store_true", help="apply auto_adjust to pieces")
    args = parser.parse_args()

    process_all(input_dir=args.input, output_dir=args.output, do_adjust=args.adjust)

def auto_adjust(img):
    # コントラスト・明るさ
    img = cv2.convertScaleAbs(img, alpha=1.12, beta=-5)

    # 色温度補正（黄かぶり除去）
    b, g, r = cv2.split(img)
    b = cv2.add(b, 5)
    r = cv2.subtract(r, 5)
    img = cv2.merge([b, g, r])

    # 彩度を少し下げる
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    s = cv2.multiply(s, 0.92)
    return cv2.cvtColor(cv2.merge([h, s, v]), cv2.COLOR_HSV2BGR)

def split_image(img, white_th=WHITE_TH, min_white_run=MIN_WHITE_RUN, aspect=ASPECT):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    # 右側の大余白をカット
    col_mean = gray.mean(axis=0)
    right = w
    for x in range(w - 1, 0, -1):
        if col_mean[x] < white_th:
            right = x + 1
            break
    img = img[:, :right]

    # 切り出すべき縦高さをアスペクト比から決定
    target_h = max(1, int(right / aspect))

    # 縦方向の白帯検出
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    row_mean = gray.mean(axis=1)

    cuts = [0]
    run = 0
    for y, val in enumerate(row_mean):
        if val > white_th:
            run += 1
        else:
            if run >= min_white_run:
                cuts.append(y)
            run = 0
    cuts.append(img.shape[0])

    # 切り出し：各セグメントに対して target_h に合わせて上寄せで切り出す
    pieces = []
    for i in range(len(cuts) - 1):
        seg_top = cuts[i]
        seg_bottom = cuts[i + 1]
        seg_h = seg_bottom - seg_top
        if seg_h <= 0:
            continue

        #　上から target_h を切り出す
        top = max(0, seg_top)
        bottom = top + target_h
        pieces.append(img[top:bottom])

    return pieces
