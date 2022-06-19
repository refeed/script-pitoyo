import linecache
import openpyxl
import os
import pandas
import shutil

from aws_sort_template_verifier import TEMPLATE_VERIFIER, RAIN_TOTAL_LINE_LOCATION
from task_id_mapping import METHOD_TASK_ID_MAPPING

# Inti scriptnya sama cuma jadi ada 6 kolom
# Hasil tetep excel
# Ada 6 ARG di dalam satu file RIH
# Kolom mulai dari D, ada CMAX, dkk

# KONFIGURASI
SUMBER_TABLE_PATH = 'Hasil(1).xlsx'
SUMBER_SORTIR_PATH = '2021-01-01-20220619T064917Z-001'
COPY_FILE = False  # Set ke True agar file disalin ke TUJUAN_COPY_PATH
TUJUAN_COPY_PATH = 'hasil_dir'
NAMA_FILE_HASIL = 'hasil.xlsx'
KOLOM_PRINT_HASIL_START = 'D'


def get_real_time_and_date(date, time):
    # Mendapatkan tanggal dan waktu yang sudah dinormalisasi
    # esp. untuk case argumen `time` bernilai 24, maka akan diganti
    # ke 0.00 dan tanggal ditambah satu
    #
    # Params:
    # date: pandas._libs.tslibs.timestamps.Timestamp
    # time: pandas._libs.tslibs.timestamps.Timestamp
    # returns tuple (date, time)
    new_date, new_time = date, time
    # Not used
    return new_date, new_time


def get_and_copy_file_to_destination(date, time, task_id, copy=True):
    """
    Copy and return the source path that will be copied
    set `copy` to False, so the function doesn't run the copying part, and
    only return the path that was planned to be copied.

    New file format reference:
    2021010100000300
    YYYYMMDDHHMM**XX
    ** = Unknown
    XX = Task ID (two digit number)
    """
    dir_source_path = os.path.join(SUMBER_SORTIR_PATH, '2021-{month}-{day}'.format(
                month=('%.2d' % date.month),
                day=('%.2d' % date.day)))
    file_name_to_be_copied = '2021{month}{day}{hour}{minute}'.format(
                month=('%.2d' % date.month),
                day=('%.2d' % date.day),
                hour=('%.2d' % time.hour),
                minute=('%.2d' % time.minute))

    full_path_start_name_tobe_copied = os.path.join(dir_source_path, file_name_to_be_copied)

    filename_found = None
    for filename in os.listdir(dir_source_path):
        if (filename.startswith(file_name_to_be_copied) and
                filename.endswith(f'{task_id}.rih.ascii')):
            filename_found = filename

    if filename_found is None:
        raise Exception('File "%s" tidak ditemukan' % (full_path_start_name_tobe_copied))

    path_to_be_copied = os.path.join(dir_source_path, filename_found)

    if copy:
        print('Copied ' + shutil.copy(path_to_be_copied, TUJUAN_COPY_PATH))

    return path_to_be_copied


def verify_file_format(filepath):
    for number_test_line, test_line in TEMPLATE_VERIFIER['SANITY_CHECK']:
        assert linecache.getline(filepath, number_test_line) == test_line


def get_rain_total_value(filepath, arg_name):
    """Get rain total value from rih.ascii file based on arg_name"""
    raw_value = linecache.getline(filepath, RAIN_TOTAL_LINE_LOCATION[arg_name])
    rain_values_str = raw_value.strip().split(':')[1].strip().split(',')
    rain_value_sum = sum([float(i) for i in rain_values_str])
    return rain_value_sum


if __name__ == "__main__":
    prev_tanggal = None  # Tanggal dari iterasi sebelumnya

    # For writing we use openpyxl, pandas' API is just very troublesome to use
    sumber_table_openpyxl_wb = openpyxl.load_workbook(filename=SUMBER_TABLE_PATH)

    for arg_location in RAIN_TOTAL_LINE_LOCATION.keys():
        # arg_location is ARG Jerowaru, etc
        sumber_table_df = pandas.read_excel(SUMBER_TABLE_PATH, sheet_name=arg_location)

        for index, row in sumber_table_df.iterrows():
            tanggal = (row[0] if type(row[0]) is not pandas._libs.tslibs.nattype.NaTType
                else prev_tanggal)
            waktu = row[1]

            # HACK
            if (None in {tanggal, waktu} or
                    type(waktu) is float):
                continue

            column_num = ord(KOLOM_PRINT_HASIL_START.upper()) - ord('A') + 1

            for method_name, task_id in METHOD_TASK_ID_MAPPING.items():
                try:
                    copied_filename = get_and_copy_file_to_destination(
                        tanggal, waktu, task_id=task_id, copy=COPY_FILE)
                except Exception as e:
                    print(e)
                    continue
                print('Opening', copied_filename)
                verify_file_format(copied_filename)
                sumber_table_openpyxl_wb[arg_location].cell(row=index + 2, column=column_num).value = get_rain_total_value(copied_filename, arg_location)
                column_num += 1

            prev_tanggal = tanggal

    linecache.clearcache()
    sumber_table_openpyxl_wb.save(NAMA_FILE_HASIL)
    print('Written %s' % NAMA_FILE_HASIL)
