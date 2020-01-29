from __future__ import print_function

import os
from shutil import copyfile

try:
    from urllib.request import urlretrieve
except ImportError:
    from urllib import urlretrieve

# full URLS:
# https://ndownloader.figshare.com/files/18473234 # award notices
# https://ndownloader.figshare.com/files/18474977 # test
# https://ndownloader.figshare.com/files/18475136 # train

# TODO: Refactor this for the new data

URLBASE = 'https://ndownloader.figshare.com/files/{}'
URLS = ['18473234', '18475136', '18474977']
DATA = ['award_notices_RAMP.csv.zip', 'company_revenue_TRAIN.csv.zip',
        'company_revenue_TEST.csv.zip']


def main(output_dir='data'):
    filenames = DATA
    full_urls = [URLBASE.format(url) for url in URLS]

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    for url, filename in zip(full_urls, filenames):
        output_file = os.path.join(output_dir, filename)

        if os.path.exists(output_file):
            continue

        print("Downloading from {} ...".format(url))
        urlretrieve(url, filename=output_file)
        print("=> File saved as {}".format(output_file))

    # copy awards data to submission file
    if os.path.exists(os.path.join('submissions', 'starting_kit')):
        copyfile(
            os.path.join('data', DATA[0]),
            os.path.join('submissions', 'starting_kit',
                         DATA[0])
        )


if __name__ == '__main__':
    test = os.getenv('RAMP_TEST_MODE', 0)

    if test:
        print("Testing mode, not downloading any data.")
    else:
        main()
