from abc import ABC, abstractmethod
from collections.abc import Iterable
from colored import Fore, Style
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter


class Singleton:

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance


class Io(ABC, Singleton):

    @abstractmethod
    def print(self, string: str):
        pass

    @abstractmethod
    def input(
        self,
        verify_cls,
        request: str,
        completer: Iterable[str] = None,
        allow_empty: bool = False
    ):
        pass


class IoCli(Io):

    def print(self, string):
        print(string)

    def input(
        self,
        verify_cls,
        request: str,
        completer: Iterable[str] = None,
        allow_empty: bool = False
    ):
        inp_completer = WordCompleter(completer) if completer else None
        while True:
            try:
                inp = prompt(request, completer=inp_completer).strip()
                if not inp and allow_empty:
                    return None
                if not inp:
                    raise ValueError("Input can't be empty")
                return verify_cls(inp)
            except (ValueError, IndexError) as err:
                self.print(f"{Fore.red}{err}{Style.reset}")
