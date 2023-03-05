
import shutil, os, pathlib
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
unknown_extensions_found = set()  # використовуємо set щоб одразу відсіяти дублікати
files_found = 0
archives_found = []
files_by_categories = {"images": [], "documents": [], "audio": [], "video": [], "archives": [], "unknown": []}  # сюди складаємо імена всіх файлів, які зустрічаються


def file_processor(element):  # функція приймає шлях до файлу, який треба обробити
    global files_found
    element = pathlib.Path(element)
    files_found += 1
    extension = str(element.suffix.upper()[1:])
    def known_file_sorter(folder):  # функція отримує назву теки, в яку буде переміщено файл який отримала материнська функція (element)
        target_path = os.path.join(argv[1], folder)
        if not pathlib.Path(target_path).exists():  # створюємо теку призначення, якщо її ще не існує
            os.makedirs(target_path)
        old_name_with_extension = element.name  # ім'я файлу з розширенням
        new_name = normalize(old_name_with_extension)  # нормалізоване ім'я, але ще не перевірене на дублікати в теці призначення
        old_name_with_extension = element  # повний шлях до файлу оригіналу
        full_future_path = pathlib.Path(os.path.join(target_path, new_name)) # повний шлях до майбутнього файлу
        counter = 0
        while True:  # далі тека призначення перевіряється на наявність файлу з таким іменем 
            if full_future_path.exists():  # якщо ім'я вже існує, то додаємо "_{counter}" в кінець імені і перевіряємо повторно
                old_name_with_extension = full_future_path.name
                dot_position = old_name_with_extension.rfind('.')  # кілька рядків чаклуємо щоб знайти розширення і виділити "чисте" ім'я для маніпуляцій з перейменування
                old_name_only = old_name_with_extension[:dot_position]
                extension = old_name_with_extension[dot_position:]
                new_name_full = (old_name_only + f"_{counter}" + extension)
                new_name_full_path = os.path.join(target_path, new_name_full)
                counter += 1
                full_future_path = pathlib.Path(new_name_full_path)
            else:
                new_name = full_future_path
                os.rename(element, new_name)
                break
        #files_by_categories[folder].append(element.name)  # зберігаємо ім'я оригіналу в контейнер для подальшого виводу результатів на екран
        files_by_categories[folder].append(element)  # зберігаємо повний шлях до оригіналу в контейнер для подальшого виводу результатів на екран
        return
    
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
        shutil.unpack_archive(element, target_path, extension.lower())  # для допрацювання в майбутньому: це розпакування треба виконувати коли впевнились, що буде створене унікальне ім'я теки
        #files_by_categories["archives"].append(element.name)
        files_by_categories["archives"].append(element)
        archives_found.append(element)
        known_extensions_found.update([extension])
    else:  # файли з невідомими розширеннями залишаються без змін, просто вносимо імена до списку з метою виводу результатів
        #files_by_categories["unknown"].append(element.name)
        files_by_categories["unknown"].append(element)
        unknown_extensions_found.update([extension])
    return

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


def parser(path):  # "головна" функція: отримує шлях до елементу (файл чи тека) і вирішує що з ним робити
    path = pathlib.Path(path)
    for element in path.iterdir():
        if element.is_file():  # всі файли передаються в іншу функцію
            file_processor(element)
        elif element.is_dir():  # всі теки обробляються тут
            if element.name in ignore_folders:  # ігноруємо певні теки згідно з умовами завдання
                pass
            elif os.listdir(element) == []:  # видаляємо теку, якщо вона порожня
                os.rmdir(element)
            else:  # прописуємо випадок коли при перейменуванні вже існує тека з таким іменем
                old_name = element.name  # ім'я теки
                new_name = normalize(old_name)  # нормалізоване ім'я, але ще не перевірене на дублікати в теці призначення
                new_name_full_path = (os.path.join(os.path.dirname(element), new_name))  # dirname видає parent адресу теки, в якій знаходиться тека, яку треба перейменувати
                old_name = element  # повний шлях до оригінальної теки
                full_future_path = pathlib.Path(new_name_full_path) # повний шлях до майбутньої теки
                counter = 0
                while True:  # далі тека призначення перевіряється на наявність теки з новим іменем 
                    if full_future_path.exists():  # якщо ім'я вже існує, то додаємо "_{counter}" в кінець імені і перевіряємо повторно
                        old_name_only = full_future_path.name
                        old_name = full_future_path
                        new_name_full = (old_name_only + f"_{counter}")
                        new_name_full_path = os.path.join(os.path.dirname(element), new_name_full)
                        counter += 1
                        full_future_path = pathlib.Path(new_name_full_path)
                    else:
                        new_name = full_future_path
                        os.rename(element, new_name)
                        break
                parser(full_future_path)  # рекурсивно передаємо шлях до теки для обробки вмісту і видалення існуючих порожніх тек
    return
 

def delete_empty_folders(path):
    for root, dirs, files in os.walk(path, topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            delete_empty_folders(dir_path)
            if not os.listdir(dir_path):
                os.rmdir(dir_path)
    return


if __name__ == "__main__":
    if len(argv) == 1:
        print("You should enter a valid path. No parameters were entered, exiting...")
    else:
        path = pathlib.Path(argv[1])
        if not path.exists():
            print(f"The entered path: '{path}' could not be found, exiting...")
        elif path.exists():
            print(f"The following valid path was entered: {path}\nProcessing...")
            parser(path)
            print(f"The following {len(known_extensions_found)} known extensions were found: {tuple(known_extensions_found)}")
            print(f"The following {len(unknown_extensions_found)} unknown extensions were found: {tuple(unknown_extensions_found)}")
            print(f"The following {files_found} files (original names) were found (by categories):")

            for i, v in files_by_categories.items():  # словник, в якому лежать оригінальні шляхи до всіх файлів
                print(f"{len(v)} {str(i).title()}:")
                for num, item in enumerate(v):
                    print("{:>4}: {}".format(num+1, item))

            for element in archives_found:  # видаляємо оригінали файлів-архівів
                os.remove(element)

            delete_empty_folders(path)  # видаляємо порожні теки

