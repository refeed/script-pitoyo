import linecache
import openpyxl
import os
import pandas
import shutil

from aws_sort_template_verifier import TEMPLATE_VERIFIER, RAIN_TOTAL_LINE_LOCATION

# Inti scriptnya sama cuma jadi ada 6 kolom
# Hasil tetep excel
# Ada 6 ARG di dalam satu file RIH
# Kolom mulai dari D, ada CMAX, dkk

# KONFIGURASI
SUMBER_TABLE_PATH = 'C:\\Users\\~phi~\\Desktop\\New folder\\tabel aws fix_29 Juni_update.xlsx'
SUMBER_DAN_HASIL_TABLE_SHEET_NAME = 'ARG PANGKALAN LAMPAN'
SUMBER_SORTIR_PATH = 'C:\\Users\\~phi~\\Desktop\\New folder\\DATA AWAL\\04_CMAX_SEKINE.rih'
COPY_FILE = False  # Set ke True agar file disalin ke TUJUAN_COPY_PATH
TUJUAN_COPY_PATH = 'C:\\Users\\~phi~\\Downloads\\AWS_Sort\\lampan'
NAMA_FILE_HASIL = 'hasil (sheet = %s)(metode = %s).xlsx' % (
        SUMBER_DAN_HASIL_TABLE_SHEET_NAME,
        os.path.splitext(os.path.basename(SUMBER_SORTIR_PATH))[0])
KOLOM_PRINT_HASIL = 'O'

sumber_table_df = pandas.read_excel(SUMBER_TABLE_PATH, sheet_name=SUMBER_DAN_HASIL_TABLE_SHEET_NAME)
# For writing we use openpyxl, pandas' API is just very troublesome to use
sumber_table_openpyxl_wb = openpyxl.load_workbook(filename=SUMBER_TABLE_PATH)
sumber_table_openpyxl_ws = sumber_table_openpyxl_wb[SUMBER_DAN_HASIL_TABLE_SHEET_NAME]


def get_real_time_and_date(date, time):
    # Mendapatkan tanggal dan waktu yang sudah dinormalisasi
    # esp. untuk case argumen `time` bernilai 24, maka akan diganti
    # ke 0.00 dan tanggal ditambah satu
    #
    # Params:
    # date: pandas._libs.tslibs.timestamps.Timestamp
    # time: int atau float
    # returns tuple (date, time)
    new_date, new_time = date, time

    if time == 24.0:
        new_date = date + pandas.DateOffset(1)
        new_time = 0.0

    if type(date) is not pandas._libs.tslibs.timestamps.Timestamp:
        new_date = None
    if type(time) is not float:
        new_time, new_date = None, None

    return new_date, new_time


def get_and_copy_file_to_destination(date, time, copy=True):
    """
    Copy and return the source path that will be copied
    set `copy` to False, so the function doesn't run the copying part, and
    only return the path that was planned to be copied.
    """
    dir_source_path = os.path.join(SUMBER_SORTIR_PATH, '2018-{month}-{day}'.format(
                month=('%.2d' % date.month),
                day=('%.2d' % date.day)))

    file_name_to_be_copied = '2018{month}{day}{hour}00'.format(
                month=('%.2d' % date.month),
                day=('%.2d' % date.day),
                hour=('%.2d' % int(time)))

    full_path_start_name_tobe_copied = os.path.join(dir_source_path, file_name_to_be_copied)

    filename_found = None
    for filename in os.listdir(dir_source_path):
        if (filename.startswith(file_name_to_be_copied) and
                filename.endswith('.rih.ascii')):
            filename_found = filename

    if filename_found is None:
        raise Exception('File "%s" tidak ditemukan' % (
    full_path_start_name_tobe_copied))

    path_to_be_copied = os.path.join(dir_source_path, filename_found)

    if copy:
        print('Copied ' + shutil.copy(path_to_be_copied, TUJUAN_COPY_PATH))

    return path_to_be_copied


def verify_file_format(filepath):
    for number_test_line, test_line in TEMPLATE_VERIFIER['SANITY_CHECK']:
        assert linecache.getline(filepath, number_test_line) == test_line


def get_rain_total_value(filepath):
    """Get rain total value from rih.ascii file based on SUMBER_DAN_HASIL_TABLE_SHEET_NAME"""
    raw_value = linecache.getline(filepath, RAIN_TOTAL_LINE_LOCATION[SUMBER_DAN_HASIL_TABLE_SHEET_NAME])
    rain_values_str = raw_value.strip().split(':')[1].strip().split(',')
    rain_value_sum = sum([float(i) for i in rain_values_str])
    return rain_value_sum


if __name__ == "__main__":
    prev_tanggal = None # Tanggal dari iterasi sebelumnya
    for index, row in sumber_table_df.iterrows():
        tanggal, waktu = get_real_time_and_date((row[0] if type(row[0]) is not pandas._libs.tslibs.nattype.NaTType
                                                else prev_tanggal) , row[1])

        if None in {waktu, tanggal}:
            tanggal = None
            waktu = None
            prev_tanggal = None
            continue

        copied_filename = get_and_copy_file_to_destination(tanggal, waktu, copy=COPY_FILE)

        verify_file_format(copied_filename)
        sumber_table_openpyxl_ws.cell(row=index + 2, column=(ord(KOLOM_PRINT_HASIL.upper()) - ord('A') + 1)).value = get_rain_total_value(copied_filename)

        prev_tanggal = tanggal
        linecache.clearcache()

    sumber_table_openpyxl_wb.save(NAMA_FILE_HASIL)
    print('Written %s' % NAMA_FILE_HASIL)
