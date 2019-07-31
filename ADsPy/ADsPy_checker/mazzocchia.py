from psutil import NoSuchProcess
import psutil
import os
import signal
import glob
import time
from threading import Thread
from django.conf import settings


def auto_monnezzaro(args):
    print("starting auto mazzocchia")
    path = "{}/*.pid".format(args)
    jobs_dict = {}
    j_counter = 0
    while True:
        print("while turn")
        pid_file_list = glob.glob(path)
        for pid_file in pid_file_list:
            try:
                with open(pid_file, "r") as f:
                    print(pid_file, "pid file")
                    data = f.read()
                    data = data.split("_")
                    times = data[0].split("|")
                    ids = data[1].split("|")
                    j_timeout = times[1]
                    j_rest = times[2]
                    j_id = ids[0]

                    try:
                        if jobs_dict[j_id][1] == j_rest:
                            jobs_dict[j_id][2] += 1
                            if jobs_dict[j_id][2] > 2:
                                print("trying to kill")
                                print(ids, "ids", len(ids))
                                killed = 0
                                for i in range(1, len(ids)):
                                    print(ids[i])
                                    try:
                                        process = psutil.Process(int(ids[i]))
                                        children = process.children(recursive=True)
                                        for child in children:
                                            try:
                                                os.kill(child.pid, signal.SIGKILL)
                                            except (OSError, NoSuchProcess) as my_error:
                                                pass
                                        os.kill(int(ids[i]), signal.SIGTERM)
                                    except (OSError, NoSuchProcess) as my_error:
                                        print("nothign to kill", my_error)
                                        killed += 1
                                    else:
                                        print("killed {}".format(ids[i]))
                                        killed += 1
                                if killed >= 4:
                                    print("removing file", pid_file)
                                    del jobs_dict[j_id]
                                    os.remove(pid_file)
                            jobs_dict[j_id][1] = j_rest
                        else:
                            jobs_dict[j_id][1] = j_rest
                            jobs_dict[j_id][2] = 0

                    except KeyError:
                        jobs_dict[j_id] = [j_timeout, j_rest, j_counter]
                    print("pids opened, {}\r".format(jobs_dict))
            except (FileExistsError, IOError) as e:
                print("file not found, error {}".format(e))
        time.sleep(60)


if __name__ == "__main__":
    base_dir = None
    while not base_dir:
        print("startin garbage manager threead")
        try:
            with open("base_dir", 'r') as f:
                base_dir = f.read()
                f.close()
        except (FileNotFoundError, IOError) as e:
            print(e)
        if base_dir:
            pids_fil_address = "{}/pids".format(base_dir)
            garbage_control_thread = Thread(target=auto_monnezzaro, args=[pids_fil_address])
            garbage_control_thread.start()
        time.sleep(7)
