import docker
import os
import glob
import json
import datetime
import numpy

client = docker.APIClient(base_url='unix://var/run/docker.sock')


def collect_stats(sockshop_containers, ntimes=1):
    # {"name" : "component name", "timestamps": "datetime", "docker_stats":...}
    stats_average = dict()
    for c_id in sockshop_containers:
        stats_average[c_id] = {"usage": [],
                               "max_usage": [], "rss": [], "total_rss": []}

    for i in range(ntimes):
        stats = []
        for container_id in sockshop_containers:
            docker_stats = client.stats(
                container_id, decode=True, stream=False)
            container_stats = dict()
            container_stats["timestamp"] = datetime.datetime.now().isoformat()
            container_stats["name"] = docker_stats['name']
            container_stats["docker_stats"] = docker_stats

            stats.append(container_stats)
            # print(stats_average)
            stats_average[container_id]['usage'].append(
                docker_stats['memory_stats']['usage'])
            stats_average[container_id]['max_usage'].append(
                docker_stats['memory_stats']['max_usage'])
            stats_average[container_id]['rss'].append(
                docker_stats['memory_stats']['stats']['rss'])
            stats_average[container_id]['total_rss'].append(
                docker_stats['memory_stats']['stats']['total_rss'])

        with open("tosker_{0}.log".format(ntimes), 'w') as outfile:
            json.dump(stats, outfile)
    # print(stats_average)
    n_containers = 0;
    for key, value in stats_average.items():
        stats_average[key]["avg_usage"] = numpy.mean(value['usage'])
        stats_average[key]["avg_max_usage"] = numpy.mean(value['max_usage'])
        stats_average[key]["avg_rss"] = numpy.mean(value['usage'])
        stats_average[key]["avg_total_rss"] = numpy.mean(value['total_rss'])
        n_containers+=1
    avg_usage = []
    avg_max_usage = []
    avg_rss = []
    avg_total_rss = []
    for key, value in stats_average.items():
        avg_usage.append(value["avg_usage"])
        avg_max_usage.append(value["avg_max_usage"])
        avg_rss.append(value["avg_rss"])
        avg_total_rss.append(value["avg_total_rss"])
    # print(stats_average)

    # final_stats = {"usage": numpy.mean(avg_usage), "max_usage": numpy.mean(avg_max_usage),
                #    "rss": numpy.mean(avg_rss), "avg_total_rss": numpy.mean(avg_total_rss)}
    print(n_containers, "containers")
    print("Usage :{0},\nMax usage:{1},\nRss:{2},\nTotal rss:{3}".format(
                    numpy.mean(avg_usage)/1024/1024,
                    numpy.mean(avg_max_usage)/1024/1024,
                    numpy.mean(avg_rss)/1024/1024,
                    numpy.mean(avg_total_rss)/1024/1024
                    ))


sockshop_dir = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "sockshop-app")
print(sockshop_dir)

tosker_yaml_files = list()
os.chdir(sockshop_dir)
for tosker_file in glob.glob("*.yaml"):
    tosker_yaml_files.append(os.path.join(sockshop_dir, tosker_file))

# run tosker
# for tosker_yaml_file in tosker_yaml_files:
# print("Starting {} yaml file ...".format(
#     os.path.basename(os.path.normpath(tosker_yaml_file))))
# os.system("tosker {0} create start".format(tosker_yaml_file))
sockshop_containers = [container['Id'] for container in client.containers(
) if "sockshop" in container['Names'][0]]

collect_stats(sockshop_containers, ntimes=3)


# client.stats(client.containers()[0]['Id'], stream=False)['memory_stats']
#  {'limit': 8274780160,
#     'max_usage': 634081280,
#     'usage': 598896640
#     'stats': {'inactive_anon': 16384,
#                 'rss': 53108736,
#                 'mapped_file': 4907008,
#                 'dirty': 3379200,
#                 'active_file': 395481088,
#                 'unevictable': 0,
#                 'total_writeback': 0,
#                 'total_cache': 545763328, 'active_anon': 53432320, 'total_pgpgout': 1152618,
#                 'total_active_file': 395481088,
# 'total_rss': 53108736,
#                 'inactive_file': 149889024, 'writeback': 0, 'total_unevictable': 0,
#                 'total_pgpgin': 1290140, 'rss_huge': 16777216, 'pgpgin': 1290140,
#                 'total_dirty': 3379200, 'pgmajfault': 0, 'total_mapped_file': 4907008,
#                 'cache': 545763328, 'total_inactive_file': 149889024,
#                 'total_inactive_anon': 16384, 'total_pgfault': 1497954, 'total_active_anon': 53432320,
#                 'total_rss_huge': 16777216, 'hierarchical_memory_limit': 9223372036854771712,
#                 'total_pgmajfault': 0, 'pgfault': 1497954, 'pgpgout': 1152618
#                 },
#     }
#
# #
# # {
# #    "storage_stats":{ },
#    "memory_stats":{
#    "name":"/sockshop_group-go.front-end-node",
#    "cpu_stats":{ },
#    "precpu_stats":{ },
#    "read":"2017-11-10T09:39:58.567678054Z",
#    "num_procs":0,
#    "blkio_stats":{ },
#    "networks":{ },
#    "preread":"2017-11-10T09:39:57.56778472Z",
#    "pids_stats":{ },
#    "id":"b3b991051ff614137685ccd6cd57dd02e63aacfe1a22440b1d81024f7d644466"
# }
