from random import randint
import time
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count


def how_long(func, *args):
    start_time = time.time()
    func(*args)
    end_time = time.time()
    return end_time - start_time


def factorize(*number):
    output = []
    for num in number:
        out = []
        i = 1
        while i**2 <= num:
            if num % i == 0:
                out.append(i)
                if i != num // i:
                    out.append(num // i)
            i += 1
        out.sort()
        output.append(out)
    return output


def factorize_processes(*number):
    with ProcessPoolExecutor(max_workers=cpu_count()) as executor:
        output = executor.map(factorize, number)
    return [out[0] for out in output]


if __name__ == "__main__":
    a, b, c, d = factorize(128, 255, 99999, 10651060)

    assert a == [1, 2, 4, 8, 16, 32, 64, 128]
    assert b == [1, 3, 5, 15, 17, 51, 85, 255]
    assert c == [1, 3, 9, 41, 123, 271, 369, 813, 2439, 11111, 33333, 99999]
    assert d == [1, 2, 4, 5, 7, 10, 14, 20, 28, 35, 70, 140, 76079, 152158, 304316, 380395, 532553, 760790, 1065106, 1521580, 2130212, 2662765, 5325530, 10651060]

    a, b, c, d = factorize_processes(128, 255, 99999, 10651060)

    assert a == [1, 2, 4, 8, 16, 32, 64, 128]
    assert b == [1, 3, 5, 15, 17, 51, 85, 255]
    assert c == [1, 3, 9, 41, 123, 271, 369, 813, 2439, 11111, 33333, 99999]
    assert d == [1, 2, 4, 5, 7, 10, 14, 20, 28, 35, 70, 140, 76079, 152158, 304316, 380395, 532553, 760790, 1065106, 1521580, 2130212, 2662765, 5325530, 10651060]

    speed_test_input = []
    for i in range(16):
        out = randint(1, 99) * 10 ** 12
        speed_test_input.append(out)

    print(f"Test sequnce: {speed_test_input}")

    print(f"Sequential calculation:", end=" ")
    print(f"{how_long(factorize, *speed_test_input)} sec")

    print("Parallel calculation:", end=" ")
    print(f"{how_long(factorize_processes, *speed_test_input)} sec")
