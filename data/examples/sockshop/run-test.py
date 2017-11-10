import docker
import os
import glob

client = docker.APIClient(base_url='unix://var/run/docker.sock')


sockshop_dir = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "sockshop-app")
print(sockshop_dir)

tosker_yaml_files = list()
os.chdir(sockshop_dir)
for tosker_file in glob.glob("*.yaml"):
    tosker_yaml_files.append(os.path.join(sockshop_dir, tosker_file))


# run tosker
for tosker_yaml_file in tosker_yaml_files:
    print("Starting {} yaml file ...".format(
        os.path.basename(os.path.normpath(tosker_yaml_file))))
    os.system("tosker {0} create start".format(tosker_yaml_file))

    sockshop_containers = [(container['Id'], container['Names'][0]) for container in client.containers() if "sockshop" in container['Names'][0]]
