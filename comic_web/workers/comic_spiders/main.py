from workers.comic_spiders import arg_parse, version
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))


# for unittest
cmd_args = None


def main():
    args = arg_parse.parser.parse_args(cmd_args)

    version.show_welcome()

    # from workers.comic_spiders.scheduler import Scheduler
    from workers.comic_spiders.schedulerToDB import Scheduler
    from workers.comic_spiders import parser_selector
    s = Scheduler(url=args.url, output_path=args.output_path, parser=parser_selector.get_parser(
        args.url), fetch_only=args.fetch_only, proxy=args.proxy, verify_ssl=args.verify_ssl)
    # s = Scheduler(url=args.url, output_path=args.output_path, parser=parser_selector.get_parser(args.url), fetch_only=args.fetch_only, proxy=args.proxy, verify_ssl=args.verify_ssl)
    s.run()


if __name__ == '__main__':
    main()
