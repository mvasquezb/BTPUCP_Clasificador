#!/usr/bin/env python3

import sys


class Main(object):
    """docstring for Main"""
    def __init__(self, career):
        super(Main, self).__init__()
        self.career = career

    def run(self, data_file):

        return ''


def main(args=None):
    if args is None:
        args = sys.argv
    if len(args) < 3:
        print(
            """Faltan argumentos:
            {prog_name} CAREER_NAME DATA_FILENAME
            """.format(prog_name=sys.argv[0]),
            file=sys.stderr
        )
        return None
    core = Main(args[1])
    # res1,res2=core.EjecutarEntrenamiento()
    mat = core.run(args[2])
    # print(res1)
    # print(res2)
    print(mat)


if __name__ == '__main__':
    main()
