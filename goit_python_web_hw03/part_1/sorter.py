from pathlib import Path
from threading import Thread


FILETYPES = {
    "images": ('JPEG', 'PNG', 'JPG', 'SVG'),
    "video": ('AVI', 'MP4', 'MOV', 'MKV'),
    "documents": ('DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'),
    "audio": ('MP3', 'OGG', 'WAV', 'AMR'),
    "archives": ('ZIP', 'GZ', 'TAR'),
    "unknown": ()
}


class Sorter():

    def __init__(self, path: str | Path) -> None:
        self.__path = Path(path)
        if not self.__path.is_dir():
            raise FileNotFoundError("No such directory")
        self.__reserved_dirs = {}
        self.mk_dirs()

    @staticmethod
    def smart_mv(old_path: Path, new_path: Path) -> None:
        path = new_path.joinpath(old_path.name)
        if path.exists():
            filename = old_path.stem
            fileext = old_path.suffix
            i = 1
            while True:
                path = new_path.joinpath(f"{filename}_{i}{fileext}")
                if path.exists():
                    i += 1
                else:
                    break
        old_path.rename(path)

    def path_by_filetype(self, file_path: Path) -> Path:
        ext = file_path.suffix[1::].upper()
        for path, exts in self.__reserved_dirs.items():
            if ext in exts:
                return path
        return path

    def mk_dirs(self) -> None:
        for dir_path, exts in FILETYPES.items():
            path = self.__path.joinpath(dir_path)
            if path.exists():
                self.smart_mv(path, path.parent)
            path.mkdir()
            self.__reserved_dirs[path] = exts

    def sort_it_out(self, new_path: None | Path = None) -> None:
        path = new_path if new_path else self.__path
        threads = []
        for item in path.iterdir():
            if item in self.__reserved_dirs:
                continue
            if item.is_dir():
                thread = Thread(target=self.sort_it_out, args=(item,))
                thread.start()
                threads.append(thread)
            else:
                thread = Thread(
                    target=self.smart_mv,
                    args=(item, self.path_by_filetype(item))
                )
                thread.start()
                threads.append(thread)
        [el.join() for el in threads]
        if path is not self.__path:
            path.rmdir()
