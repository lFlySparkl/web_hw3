import re
import os
import zipfile
import concurrent.futures
from pathlib import Path
from multiprocessing import cpu_count

CATEGORIES = {
    "Audios": [".MP3", ".OGG", ".WAV", ".AMR", ".WMA", ".FLAC"],
    "Images": [".JPEG", ".PNG", ".JPG", ".SVG"],
    "Videos": [".AVI", ".MP4", ".MOV", ".MKV"],
    "Docs": [".DOC", ".DOCX", ".TXT", ".PDF", ".XLSX", ".PPTX"],
    "Archives": [".ZIP", ".GZ", ".TAR"],
}


def normalize(file_name: str) -> str:
    file_name_prefix = os.path.splitext(file_name)[0]
    file_name_suffix = os.path.splitext(file_name)[1]

    TRANS = {}
    CYRILLIC_SYMBOLS = (
        "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯЄІЇҐ"
    )
    TRANSLATION = (
        "a",
        "b",
        "v",
        "g",
        "d",
        "e",
        "e",
        "j",
        "z",
        "i",
        "j",
        "k",
        "l",
        "m",
        "n",
        "o",
        "p",
        "r",
        "s",
        "t",
        "u",
        "f",
        "h",
        "ts",
        "ch",
        "sh",
        "sch",
        "",
        "y",
        "",
        "e",
        "yu",
        "ya",
        "je",
        "i",
        "ji",
        "g",
        "A",
        "B",
        "V",
        "G",
        "D",
        "E",
        "E",
        "J",
        "Z",
        "I",
        "J",
        "K",
        "L",
        "M",
        "N",
        "O",
        "P",
        "R",
        "S",
        "T",
        "U",
        "F",
        "H",
        "TS",
        "CH",
        "SH",
        "SCH",
        "",
        "Y",
        "",
        "E",
        "YU",
        "UA",
        "JE",
        "I",
        "JI",
        "G",
    )

    for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):
        TRANS[ord(c)] = l

    new_file_name = re.sub("[^A-Za-z0-9]", "_", file_name_prefix.translate(TRANS))

    return new_file_name + file_name_suffix


def move_file(file: Path, category: str, root_dir: Path):
    target_dir = root_dir.joinpath(category)

    if not target_dir.exists():
        target_dir.mkdir()

    new_path = target_dir.joinpath(normalize(file.name))

    file.replace(new_path)


def get_categories(file: Path):
    ext = file.suffix.upper()

    for cat, exts in CATEGORIES.items():
        if ext in exts:
            return cat

    return "Other"


# def sort_folder(path: Path):
#     for element in path.glob("**/*"):
#         if element.is_file():
#             category = get_categories(element)
#             move_file(element, category, path)


def remove_empty_folders(path: Path):
    empty = True

    for item in path.glob("*"):
        if item.is_file():
            empty = False

        if item.is_dir() and not remove_empty_folders(item):
            empty = False

    if empty:
        path.rmdir()

    return empty


def unzip_archives(path: str):
    archives_path = str(path) + "\Archives"

    if os.path.isdir(archives_path):
        for path, dir_list, file_list in os.walk(archives_path):
            for file_name in file_list:
                if file_name.endswith(".zip"):
                    abs_file_path = os.path.join(archives_path, file_name)

                    parent_path = os.path.split(abs_file_path)[0]
                    output_folder_name = os.path.splitext(abs_file_path)[0]
                    output_path = os.path.join(parent_path, output_folder_name)

                    zip_obj = zipfile.ZipFile(abs_file_path, "r")
                    zip_obj.extractall(output_path)
                    zip_obj.close()
                    os.remove(abs_file_path)


# def main(path):
#     get_path = False

#     while get_path is False:
#         if not Path(path).exists():
#             path = str(input("Wrong path to folder, try again: "))
#         else:
#             get_path = True
#             path = Path(path)

#     sort_folder(path)
#     remove_empty_folders(path)
#     unzip_archives(path)

#     return "All good"


def sort_folder_parallel(path: Path):
    def process_element(element):
        if element.is_file():
            category = get_categories(element)
            move_file(element, category, path)

    with concurrent.futures.ThreadPoolExecutor(max_workers=cpu_count()) as executor:
        futures = [executor.submit(process_element, element) for element in path.glob("**/*")]

    for future in concurrent.futures.as_completed(futures):
        try:
            future.result()
        except Exception as e:
            print(f"Error processing element: {e}")

def main_parallel(path):
    get_path = False

    while not get_path:
        if not Path(path).exists():
            path = str(input("Wrong path to folder, try again: "))
        else:
            get_path = True
            path = Path(path)

    sort_folder_parallel(path)
    remove_empty_folders(path)
    unzip_archives(path)

    return "All good"

if __name__ == "__main__":
    path = str(input("Write path to folder: "))
    # print(main())
    print(main_parallel(path))