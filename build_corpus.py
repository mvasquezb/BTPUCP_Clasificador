import sys
import csv
import os
import bisect


class OfferCSV:
    column_names = []

    def __init__(self,
                 id,
                 title='',
                 description='',
                 qualifications='',
                 category=''):
        self.id = int(id)
        self.title = title
        self.description = description
        self.qualifications = qualifications
        self.category = ''

    @classmethod
    def from_csv_row(cls, row_str):
        return cls(id=int(row_str[0]),
                   title=row_str[1],
                   description=row_str[2],
                   qualifications=row_str[3],
                   category=row_str[4] if len(row_str) == 5 else '')

    @classmethod
    def from_csv(cls, name_or_file):
        in_file = name_or_file
        if type(name_or_file) is str:
            in_file = open(name_or_file, newline='')

        reader = csv.reader(in_file)
        cls.column_names = next(reader)

        offers = []
        for row in reader:
            offers.append(cls.from_csv_row(row))
        in_file.close()

        return offers

    @classmethod
    def to_csv(cls, offer_list, name_or_file, filter=lambda offer: True):
        out = name_or_file
        if type(name_or_file) is str:
            out = open(name_or_file, mode='w', newline='')

        writer = csv.writer(out)
        if not cls.column_names:
            cls.column_names = []
        if 'category' not in cls.column_names[-1].lower():
            cls.column_names.append('Job Category')
        writer.writerow(cls.column_names)

        for offer in offer_list:
            if filter(offer):
                row = offer.to_csv_row()
                writer.writerow(row)
        out.close()

    def to_csv_row(self):
        print(self.category)
        return [self.id,
                self.title,
                self.description,
                self.qualifications,
                self.category,
                ]

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return not (self == other)

    def __gt__(self, other):
        return self.id > other.id

    def __lt__(self, other):
        return not (self == other or self > other)


def usage(args, help=False):
    if args[1] == '--tag' or help:
        print("Usage: python3 {name} --tag untagged_data_file tagged_id_file tagged_out_file untagged_out_file"
          .format(name=args[0]))

    if args[1] == '--merge' or help:
        print("Usage: python3 {name} --merge in_file in_file ... out_file".format(name=args[0]))


def index(lst, x):
    'Locate the leftmost value exactly equal to x'
    i = bisect.bisect_left(lst, x)
    if i != len(lst) and lst[i] == x:
        return i
    raise ValueError


def tag_data(offer_list, name_or_file):
    in_file = name_or_file
    if type(in_file) is str:
        in_file = open(name_or_file, newline='')
    reader = csv.reader(in_file)
    for row in reader:
        ind = index(offer_list, OfferCSV(int(row[0])))
        offer_list[ind].category = row[1]


def tag_(args):
    if len(args) != 5:
        usage(args)
        return

    if not os.path.isfile(args[1]) or not os.path.isfile(args[2]):
        usage(args)
        return

    offers = OfferCSV.from_csv(args[1])
    offers.sort(key=lambda offer: offer.id)
    tag_data(offers, args[2])
    OfferCSV.to_csv(offers, args[3], filter=lambda offer: offer.category)
    OfferCSV.to_csv(offers, args[4], filter=lambda offer: not offer.category)


def merge_(args):
    if len(args) <= 2:
        usage(args)
        return

    out_file = args.pop()
    offer_list = []
    for filename in args[1:]:
        try:
            offers = OfferCSV.from_csv(filename)
            offer_list += offers
        except Exception as e:
            print(e)

    OfferCSV.to_csv(offer_list, out_file)


def main(args=None):
    if args is None:
        args = sys.argv

    if args[1] not in ['--help', '-h', '--tag', '--merge']:
        usage(args, help=True)

    if len(args) == 2 and args[1] in ['--help', '-h']:
        usage(args[0], help=True)
        return

    if args[1] == '--tag':
        tag_(args)
        return

    if args[1] == '--merge':
        merge_(args)
        return


if __name__ == '__main__':
    main()
