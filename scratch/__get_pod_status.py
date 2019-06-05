import time

from kubernetes import config
from kubernetes.client import Configuration
from kubernetes.client.apis import core_v1_api
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream
from kubernetes import client
from kubernetes import config
from pick import pick

def main():

    name = 'busybox-test'
    resp = None

    timestr = time.strftime("%Y%m%d-%H%M%S")
    contexts, active_context = config.list_kube_config_contexts()
    if not contexts:
        print("Cannot find any context in kube-config file.")
        return

    # Create Python List of all contexts for use by PICK Module
    contexts = [context['name'] for context in contexts]
    active_index = contexts.index(active_context['name'])

    # PICK to select SOURCE Cluster for KMOTION
    cluster1, first_index = pick(contexts, title="Pick the source Cluster Context for the POD to kmotioned",
                                 default_index=active_index)
    client1 = client.CoreV1Api(
        api_client=config.new_client_from_config(context=cluster1))

    # Create Python List of all PODs in SRC Namespace for PICK Module
    source_pods = [i.metadata.name for i in client1.list_pod_for_all_namespaces().items]
    selected_pod = pick(source_pods, title="Pick the POD to be backed up")

    pod_name == selected_pod.metadata.name  # Return the Kubernetes API POD object
    pod_namespace == selected_pod.metadata.name
    try:
        resp = client1.read_namespaced_pod(name=i.metadata.name,
                                       namespace='default')
    except ApiException as e:
        if e.status != 404:
            print("Unknown error: %s" % e)
            exit(1)

    if not resp:
        print("Error--> Pod %s does not exist. " % name)


    while True:
        resp = client1.read_namespaced_pod(name=i.metadata.name,
                                       namespace='lucky13')
        if resp.status.phase != 'Pending':
            break
        time.sleep(1)
    print("Done.")


if __name__ == '__main__':
    main()
