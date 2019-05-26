import sys
sys.path.append('./src')
import scrape_funcs


def main():
    scrape_funcs.scrape_yd_profiles()
    return 0


if __name__ == "__main__":
    main()
