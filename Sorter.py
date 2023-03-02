"""
Критерии приёма задания
    все файлы и папки переименовываются при помощи функции normalize.
    расширения файлов не изменяются после переименования.
    пустые папки удаляются
    скрипт игнорирует папки archives, video, audio, documents, images;
    распакованное содержимое архива переносится в папку archives в подпапку, названную точно так же, как и архив, но без расширения в конце;
    файлы, расширения которых неизвестны, остаются без изменений.
"""

# %Run Sorter.py /home/am1/Desktop/Python_projects/Test_folder/Test-folder

# + працює нормалізація і сортування всіх перерахованих (відомих) типів файлів
# + файли невідомих типів вносяться в список знайдених і залишаються без змін
# + нормалізація тек працює
# + прописана обробка тек (реркурсивно) і видалення порожніх тек після обробки
# + виводиться список знайдених файлів в кожній категорії (зі старими іменами файлів)
# + вивід результатів відформатований в таблицю
# - не передбачено варіант коли зустрічається файл з іменем, яке вже існує в одній із тек призначення


import shutil, os, pathlib, itertools
from sys import argv

VALID_SYMBOLS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
KNOWN_EXTENSIONS = ('JPEG', 'PNG', 'JPG', 'SVG', 'AVI', 'MP4', 'MOV', 'MKV', 'DOC',
                    'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX', 'MP3', 'OGG', 'WAV', 'AMR')  # архіви сюди не входять, бо для них буде інший спосіб обробки

images = ['JPEG', 'PNG', 'JPG', 'SVG']
video = ['AVI', 'MP4', 'MOV', 'MKV']
documents = ['DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX']
audio = ['MP3', 'OGG', 'WAV', 'AMR']
archives = ['ZIP', 'GZ', 'TAR']
ignore_folders = ["images", "documents","audio", "video", "archives"]

known_extensions_found = set()  # використовуємо set щоб одразу відсіяти дублікати
unknown_extensions_found = set()
files_found = 0
archives_found = []
files_by_categories = {"images": [], "documents": [], "audio": [], "video": [], "archives": [], "unknown": []}  # сюди складаємо імена всіх файлів, які зустрічаються


def file_processor(element):
    global files_found
    element = pathlib.Path(element)
    files_found += 1
    extension = str(element.suffix.upper()[1:])
    
    def known_file_sorter(folder):
        target_path = os.path.join(argv[1], folder)
        if not pathlib.Path(target_path).exists():
            os.makedirs(target_path)
        old_name = element.name  # ім'я файлу з розширенням
        new_name = normalize(old_name)
        old_name = element  # повний шлях до файлу
        new_name = os.path.join(target_path, new_name)
        os.rename(old_name, new_name)
        files_by_categories[folder].append(element.name)
        
    if extension in KNOWN_EXTENSIONS:
        if extension in images:
            known_file_sorter("images")
        elif extension in documents:
            known_file_sorter("documents")
        elif extension in audio:
            known_file_sorter("audio")
        elif extension in video:
            known_file_sorter("video")
        known_extensions_found.update([extension])
    elif extension in archives:
        target_path = os.path.join(argv[1], "archives")
        if not pathlib.Path(target_path).exists():
            os.makedirs(target_path)
        shutil.unpack_archive(element, target_path, extension.lower())
        files_by_categories["archives"].append(element.name)
        archives_found.append(element)
        known_extensions_found.update([extension])
    else:
        files_by_categories["unknown"].append(element.name)
        unknown_extensions_found.update([extension])


def normalize(name: str) -> str:  # функція отримує шлях до повного імені елементу (файлу або теки) разом з розширенням
    CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯЄІЇҐ"
    TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
                   "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g", 'A', 'B', 'V', 'G',
                   'D', 'E', 'E', 'J', 'Z', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'R', 'S', 'T', 'U', 'F', 'H', 'TS', 'CH',
                   'SH', 'SCH', '', 'Y', '', 'E', 'YU', 'YA', 'JE', 'I', 'JI', 'G')
    TRANS = {}
        
    for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):  # наповнюємо словник з ключами для використання при транслітерації
        TRANS[ord(c)] = l
        TRANS[ord(c.upper())] = l.upper()
    index = name.rfind(".")  # знаходимо індекс крапки (звідки починається розширення файлу)
    if index == -1:  # для файлів і тек, які не мають розширення
        transliterated_name = name.translate(TRANS)
        normalized = ""
        for i in transliterated_name:  # конфліктні символи в перекладеному імені заміняємо на "_"
            if i in VALID_SYMBOLS:
                normalized += i
            else:
                normalized += "_"        
    else:
        extension = name[index+1:]  # для файлів і тек, які мають розширення
        transliterated_name = name[:index].translate(TRANS)
        normalized = ""
        for i in transliterated_name:  # конфліктні символи в перекладеному імені заміняємо на "_"
            if i in VALID_SYMBOLS:
                normalized += i
            else:
                normalized += "_"
        normalized += "." + extension
    return normalized


def parser(path):  # "головна" функція: отримує шлях до теки і вирішує що робити з елементами, які в ній знаходяться
    path = pathlib.Path(path)
    for element in path.iterdir():
        if element.is_file():  # всі файли передаються в іншу функцію
            file_processor(element)
        elif element.is_dir():  # всі теки обробляються тут 
            if element.name in ignore_folders:  # для ігронування певних тек згідно з умовами завдання
                #print(f"Ignoring folder: {element}")
                pass
            elif os.listdir(element) == []:  # видаляємо порожні теки
                os.rmdir(element)
            else:
                new_name = normalize(element.name)  # нормалізуємо ім'я
                new_name = (os.path.join(os.path.dirname(element), new_name))  # dirname видає адресу теки, в якій знаходиться елемент 
                os.rename(element, new_name)  # перейменовуємо елемент
                parser(new_name)  # рекурсивно передаємо шлях до теки для обробки вмісту або видалення порожніх тек після обробки
                if os.listdir(new_name) == []:
                    os.rmdir(new_name)


def formatted_output(dictionary):  # функція для форматування результатів перед прінтом  
    container = []
    container.append("|{:*^20}|{:*^20}|{:*^20}|{:*^20}|{:*^20}|{:*^20}|".format("Images", "Documents", "Audio", "Video", "Archives", "Unknown"))
    lst1 = files_by_categories["images"]
    lst2 = files_by_categories["documents"]
    lst3 = files_by_categories["audio"]
    lst4 = files_by_categories["video"]
    lst5 = files_by_categories["archives"]
    lst6 = files_by_categories["unknown"]
    for i in itertools.zip_longest(lst1, lst2, lst3, lst4, lst5, lst6):  # беремо списки всіх категорів файлів і формуємо таблицю за найдовшим списком 
        lst1a = (str(i[0]) if i[0] != None else "")  # "комірки" таблиці зі значенням "None" заповнюємо порожнім рядком, для кращого вигляду
        lst2a = (str(i[1]) if i[1] != None else "")
        lst3a = (str(i[2]) if i[2] != None else "")
        lst4a = (str(i[3]) if i[3] != None else "")
        lst5a = (str(i[4]) if i[4] != None else "")
        lst6a = (str(i[5]) if i[5] != None else "")
        container.append("|{:<20}|{:<20}|{:<20}|{:<20}|{:<20}|{:<20}|".format(lst1a, lst2a, lst3a, lst4a, lst5a, lst6a))
    
    return container


parser(argv[1])
print(f"The following {len(known_extensions_found)} known extensions were found: {tuple(known_extensions_found)}")
print(f"The following {len(unknown_extensions_found)} unknown extensions were found: {tuple(unknown_extensions_found)}")
print(f"The following {files_found} files (original names) were found (by categories):")
for i in formatted_output(files_by_categories):  # список файлів (зі старими іменами) виводимо на екран "в колонках"
    print(i)

for element in archives_found:  # видаляємо оригінали файлів-архівів
    os.remove(element)
