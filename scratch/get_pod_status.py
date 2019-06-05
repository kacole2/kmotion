#!/usr/bin/python3

# Hackathon Lucky Team13

from kubernetes import client
from kubernetes import config
from pick import pick
import sys
import time


timestr = time.strftime("%Y%m%d-%H%M%S")
contexts, active_context = config.list_kube_config_contexts()
if not contexts:
    print("Cannot find any context in kube-config file.")
    sys.exit(0)

# Create Python List of all contexts for use by PICK Module
contexts = [context['name'] for context in contexts]
active_index = contexts.index(active_context['name'])

# PICK to select SOURCE Cluster for KMOTION
cluster1, first_index = pick(contexts, title="Pick the Cluster to look at . . .",
                             default_index=active_index)
client1 = client.CoreV1Api(
    api_client=config.new_client_from_config(context=cluster1))

# Create Python List of all PODs in SRC Namespace for PICK Module
source_pods = [i.metadata.name for i in client1.list_pod_for_all_namespaces().items]
selected_pod = pick(source_pods, title="Pick the POD to get status from")

start_time = time.time()
for i in client1.list_pod_for_all_namespaces().items:
    if selected_pod[0] == i.metadata.name: # Return the Kubernetes API POD object
        #DEBUG print("--Found the POD Object for Selected POD")
        source_pod_object = i

print ('This is the POD you selected {0}'.format(source_pod_object.metadata.name))
print('{0} is in the {1} namespace'.format(source_pod_object.metadata.name,source_pod_object.metadata.namespace))
print ('Getting status for POD {0}'.format(source_pod_object.metadata.name))

while True:
    pod = client1.read_namespaced_pod(name=source_pod_object.metadata.name,
                                   namespace=source_pod_object.metadata.namespace)

    if pod.status.phase == 'Running':
        print("\n|-|-|-|-|-| Restored POD", pod.metadata.name, " is Running on Recovery Cluster ", cluster1)
        break
    else:
        print('Restored POD {0} status is. Current status is {1}'.format(pod.metadata.name,pod.status.phase ))
        time.sleep(3)

print ('Done. {0} Pod status is = {1}'.format(pod.metadata.name, pod.status.phase))
### Check POD Status of Restored PODs in Recovery Cluster


end_time = time.time()

