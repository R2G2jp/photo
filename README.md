# Photo Cutout (cutout_from_scanner)

本プログラムはL判の写真のスキャン画像から白地以外の領域を検出して切り出すツールです。左詰めで写真が配置されている前提で動きます。右側の白地部分を削除する過程で写真の幅を検出し、OpenCV と numpy を使い、縦方向の白帯で分割し、指定したアスペクト比（幅/高さ）に合わせて切り出します。コマンドライン実行とライブラリ利用の両方を想定しています。

## 特長
- 画像を自動で白帯（余白）で分割して複数枚を切り出す
- 切り出し後にアスペクト比（幅/高さ）から高さを決定して統一サイズで出力
- 切り出した各画像に簡易的な色補正（auto_adjust）をオプションで適用可能（今のところは大きな効果なし）
- Windows のパス周りに配慮して imencode + open により出力

## 必要条件
- Python 3.8+
- OpenCV (cv2)
- numpy

インストール例:
```powershell
pip install opencv-python numpy
```

## ファイル構成（主要）
- cutout_from_scanner.py - 実装本体（process_file, process_all, split_image, auto_adjust を提供）
- main.py - CLI ラッパー（cutout_from_scanner.process_all を呼び出す）
- input/ - 入力画像を置くディレクトリ
- output/ - 切り出し結果の出力先

## 使い方（CLI）
リポジトリルートで実行:
```powershell
uv run .\main.py --input input --output output --adjust --white-th 240 --min-white-run 25 --aspect 1.427
```

主なオプション:
- --input, -i: 入力ディレクトリ（デフォルト: input）
- --output, -o: 出力ディレクトリ（デフォルト: output）
- --adjust: 切り出し画像に auto_adjust を適用するフラグ
- --white-th: 白判定閾値（0-255, デフォルト: cutout_from_scanner.WHITE_TH）
- --min-white-run: 白帯と判定する最小連続行数（px, デフォルト: cutout_from_scanner.MIN_WHITE_RUN）
- --aspect: 出力のアスペクト比（幅/高さ, デフォルト: cutout_from_scanner.ASPECT）

## ライブラリとしての利用
Python から直接呼び出す例:
```python
from cutout_from_scanner import process_all, process_file

# ディレクトリ全体を処理
process_all("input", "output", do_adjust=True, white_th=240, min_white_run=25, aspect=1.427)

# 単一ファイルを処理
process_file("scan001.jpg", input_dir="input", output_dir="output", do_adjust=False)
```

関数:
- process_file(fname, input_dir, output_dir, do_adjust=False, white_th=..., min_white_run=..., aspect=...)
- process_all(input_dir, output_dir, do_adjust=False, white_th=..., min_white_run=..., aspect=...)
- split_image(img, white_th=..., min_white_run=..., aspect=...)
- auto_adjust(img)

## 出力確認
処理時に各ファイルごとに切り出した枚数と各ピースのサイズ（縦, 横）、および書き出しログ（WROTE: path）が標準出力に表示されます。

## 注意点
- 入力ファイル名に非 ASCII を含む場合でも出力は imencode + open を使うため安全ですが、環境依存の問題が残る場合は一時ファイル名での書き出し等を検討してください。
- 白閾値や最小白帯長はスキャン環境に合わせて調整してください。

## ライセンス

本プロジェクトは MIT ライセンスの下で提供されています。詳細はリポジトリの LICENSE ファイルを参照