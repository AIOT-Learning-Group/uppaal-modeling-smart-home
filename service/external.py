from typing import List
import subprocess

DRAWER_PATH = "epg_service_jar/epg-service.jar"


def invoke_external_java_service(params: List[str], executive: str = DRAWER_PATH) -> str:
    prefix = ['java', '-jar', executive]
    result = subprocess.run(prefix + params, stdout=subprocess.PIPE, text=True)
    return result.stdout


if __name__ == "__main__":
    prefix = ['java', '-jar', "epg_service_jar/epg-service.jar"]
    # params = ["--operation=load-time-automaton", "--name=Rule1"]
    # params = ["--operation=parse-full-xml"]
    params = ["--operation=filter-interactive-system"]
    params.append(
        "--data=" + open("composed.xml", "r").read())
    result = subprocess.run(prefix + params, stdout=subprocess.PIPE, text=True)
    print(result.stdout)
    pass
