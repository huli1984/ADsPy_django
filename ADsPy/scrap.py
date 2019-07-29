import time


def join_tring(s):
    joined = "".join(s)
    return joined


def clean_string(s):
    clean = str(s).replace("[", "").replace("]", "").replace(",", "")
    return clean


def loop_way(s):
    word = ""
    for elem in s:
        word += elem
    return word


if __name__ == "__main__":

    my_list = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]

    start_time = time.time()
    joined_s = join_tring(my_list)
    print(start_time - time.time())
    print(joined_s, "join string method")
    print("")

    start_time = time.time()
    clean_s = clean_string(my_list)
    print(start_time - time.time())
    print(clean_s, "clean string method")
    print("")

    start_time = time.time()
    looped = loop_way(my_list)
    print(start_time - time.time())
    print(looped, "with loop way")
    print("")

