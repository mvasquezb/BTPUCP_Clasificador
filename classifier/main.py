#!/usr/bin/env python3

import sys
from dataloader import DataLoader


class Main(object):
    def __init__(self, career):
        super(Main, self).__init__()
        self.career = career
        self.io = DataLoader(root='..')

    def run(self, data_file):
        # (labelledData,
        #  dataset,
        #  dictionary,
        #  categories) = self.io.get_data_for_career(self.career)
        data = self.io.get_data_for_career(self.career)
        # import json
        # with open('data.json', 'w') as f:
        #     json.dump(data, f, indent=2, ensure_ascii=False)
        return ''


def main(args=None):
    # from sklearn.datasets import fetch_20newsgroups
    # from sklearn.feature_extraction.text import TfidfVectorizer

    # categories = ['alt.atheism', 'soc.religion.christian',
    #               'comp.graphics', 'sci.med']
    # twenty_train = fetch_20newsgroups(subset='train', categories=categories,
    #                                   shuffle=True, random_state=42)

    # count_vec = TfidfVectorizer()
    # X_train_tfidf = count_vec.fit_transform(twenty_train.data)
    # print(X_train_counts)

    # return
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
