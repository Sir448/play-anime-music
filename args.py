import argparse


def str2bool(v):
    if isinstance(v, bool):
        return v
    v = v.lower()
    if v in ("yes", "true", "t", "1"):
        return True
    elif v in ("no", "false", "f", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError(f"Boolean value expected, got {v}")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--include-ops", type=str2bool, help="Include openings")
    parser.add_argument("--include-eds", type=str2bool, help="Include endings")
    parser.add_argument("--use-yt-dlp", type=str2bool, help="Use yt-dlp search")
    parser.add_argument("--search_page_limit", type=int, help="Number of items per search")
    return parser.parse_args()
