import argparse
from cutout_from_scanner import process_all


def main():
    parser = argparse.ArgumentParser(description="photo main runner")
    parser.add_argument("--input", "-i", default="input", help="input directory")
    parser.add_argument("--output", "-o", default="output", help="output directory")
    parser.add_argument("--adjust", action="store_true", help="apply auto_adjust to pieces")
    args = parser.parse_args()

    process_all(input_dir=args.input, output_dir=args.output, do_adjust=args.adjust)


if __name__ == "__main__":
    main()
