import cv2
import numpy as np
import os

INPUT_DIR = "input"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- デバッグ追加 ---
for fname in os.listdir(INPUT_DIR):
    if not fname.lower().endswith((".jpg", ".png")):
        continue
    img_path = os.path.join(INPUT_DIR, fname)
    #print("PROCESS:", repr(fname))
    #print(" FULLPATH:", img_path)
    #print(" EXISTS:", os.path.exists(img_path))
    try:
        size = os.path.getsize(img_path)
    except Exception as e:
        size = f"ERROR: {e}"
    #print(" SIZE(bytes):", size)

    try:
        with open(img_path, 'rb') as f:
            data = f.read()
    except Exception as e:
        print(" open failed:", e)
        continue

    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    #print(" imdecode ->", "ok" if img is not None else "None")
    if img is None:
        print(" failed to open (skip):", img_path)
        continue

    # ここで既存処理を続けるか最小チェックで終了
    # break  <-- 削除しました

WHITE_TH = 240        # 白判定
MIN_WHITE_RUN = 25    # 白帯の最小高さ(px)
ASPECT = 749/515        # 横幅/縦長さ のアスペクト比 (width / height)

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

def split_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    # 右側の大余白をカット
    col_mean = gray.mean(axis=0)
    right = w
    for x in range(w - 1, 0, -1):
        if col_mean[x] < WHITE_TH:
            right = x + 1
            break
    img = img[:, :right]

    # 切り出すべき縦高さをアスペクト比から決定
    target_h = max(1, int(right / ASPECT))

    # 縦方向の白帯検出
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    row_mean = gray.mean(axis=1)

    cuts = [0]
    run = 0
    for y, val in enumerate(row_mean):
        if val > WHITE_TH:
            run += 1
        else:
            if run >= MIN_WHITE_RUN:
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
        #if bottom > img.shape[0]:
        #    bottom = img.shape[0]
        #    top = max(0, bottom - target_h)

        # 最終フィルタ（実際の高さが十分か）
        #if bottom - top >= 200:
        pieces.append(img[top:bottom])

    return pieces

for fname in os.listdir(INPUT_DIR):
    if not fname.lower().endswith((".jpg", ".png")):
        continue

    # python
    img_path = os.path.join(INPUT_DIR, fname)
    with open(img_path, 'rb') as f:
        data = np.frombuffer(f.read(), dtype=np.uint8)
        img = cv2.imdecode(data, cv2.IMREAD_COLOR)

    if img is None:
        print(f"failed to open: {img_path}")
        continue

    parts = split_image(img)

    # 切り出した枚数と各ピースのサイズを表示（縦, 横）
    print(f"{fname}: found {len(parts)} pieces")
    for idx, p in enumerate(parts, 1):
        h, w = p.shape[:2]
        print(f"  piece {idx}: height={h}, width={w}")

    for i, p in enumerate(parts, 1):
        #p = auto_adjust(p)
        out = f"{os.path.splitext(fname)[0]}_{i:02}.jpg"

        # ここを imwrite -> imencode + open に置き換え
        ok, buf = cv2.imencode('.jpg', p, [cv2.IMWRITE_JPEG_QUALITY, 95])
        if not ok:
            print(f"imencode failed: {fname} part{i}")
            continue
        out_path = os.path.join(OUTPUT_DIR, out)
        with open(out_path, 'wb') as wf:
            wf.write(buf.tobytes())
