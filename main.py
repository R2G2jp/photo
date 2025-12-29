import argparse
import cutout_from_scanner
from cutout_from_scanner import process_all


def main():
    parser = argparse.ArgumentParser(description="photo main runner")
    parser.add_argument("--input", "-i", default="input", help="input directory")
    parser.add_argument("--output", "-o", default="output", help="output directory")
    parser.add_argument("--adjust", action="store_true", help="apply auto_adjust to pieces")

    # 追加: 白閾値、白帯長さ、アスペクト比をCUIで指定可能にする
    parser.add_argument("--white-th", type=int, default=cutout_from_scanner.WHITE_TH,
                        help=f"white threshold (default: {cutout_from_scanner.WHITE_TH})")
    parser.add_argument("--min-white-run", type=int, default=cutout_from_scanner.MIN_WHITE_RUN,
                        help=f"minimum white run height in px (default: {cutout_from_scanner.MIN_WHITE_RUN})")
    parser.add_argument("--aspect", type=float, default=cutout_from_scanner.ASPECT,
                        help=f"target aspect ratio width/height (default: {cutout_from_scanner.ASPECT})")

    args = parser.parse_args()

    process_all(input_dir=args.input, output_dir=args.output, do_adjust=args.adjust,
                white_th=args.white_th, min_white_run=args.min_white_run, aspect=args.aspect)


if __name__ == "__main__":
    main()
