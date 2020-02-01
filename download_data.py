from __future__ import print_function
import os
from shutil import copyfile
from google_drive_downloader import GoogleDriveDownloader as gdd

DATA = {
    "mf_aglomerated.csv": "1CA-bTDqXY5-1RpFEjdD0t5EhNZbsnsc-",
    "meteo_stations.csv":"1nqrH3_6Jlxd0xY7clMUHDIJaeR7pEMY9",
    "synop.csv":"1GTdcZdyCbVWPN2GNNJzuJ8CvRgQBBkv8",
    "forests.json":"1vZPbKjY2Sve3RpHcRftJdEywRetSyqE0"
}

def main(output_dir='data'):
    filenames = DATA
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    for file_name, file_id in filenames.items():
        output_file = os.path.join(output_dir, file_name)
        if os.path.exists(output_file):
            continue
        gdd.download_file_from_google_drive(file_id=file_id,
                                            dest_path=output_file)
        if os.path.exists(os.path.join('submissions', 'starting_kit')):
            copyfile(
                output_file,
                os.path.join('submissions', 'starting_kit', file_name)
            )


if __name__ == '__main__':
    test = os.getenv('RAMP_TEST_MODE', 0)
    if test:
        print("Testing mode, not downloading any data.")
    else:
        main()
