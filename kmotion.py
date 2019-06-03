# 2019 Team 13

from kubernetes import client, config
# install pick using "pip install pick". It is not included
# as a dependency because it only used in examples
from pick import pick


def main():
    source_pods = []
    contexts, active_context = config.list_kube_config_contexts()
    if not contexts:
        print("Cannot find any context in kube-config file.")
        return
    contexts = [context['name'] for context in contexts]
    active_index = contexts.index(active_context['name'])
    cluster1, first_index = pick(contexts, title="Pick the source Cluster Context for the POD to be backed up",
                                 default_index=active_index)

    client1 = client.CoreV1Api(
        api_client=config.new_client_from_config(context=cluster1))

    # TK - Added to setup
    source_pods = [i.metadata.name for i in client1.list_pod_for_all_namespaces().items]
    print("\nList of source_pods on %s:" % source_pods)
    selected_pod = pick(source_pods, title="Pick the POD to be backed up")

    for i in client1.list_pod_for_all_namespaces().items:
        if selected_pod[0] == i.metadata.name: # Return the Kubernetes API POD object
            print("Found the POD Object for Selected POD")
            source_pod_object = i

    print(type(source_pod_object))
    print ('This is the POD you selected {0}'.format(source_pod_object.metadata.name))

    labels = source_pod_object.metadata.




    # Original Code for listing pods
    print("\nList of pods on %s:" % cluster1)

    for i in client1.list_pod_for_all_namespaces().items:
        print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))



    cluster2, _ = pick(contexts, title="Pick the target Cluster Context for the POD to be restored to",
                       default_index=first_index)


    client2 = client.CoreV1Api(
        api_client=config.new_client_from_config(context=cluster2))





    '''
    print("\n\nList of pods on %s:" % cluster2)
    for i in client2.list_pod_for_all_namespaces().items:
        print("%s\t%s\t%s" %
              (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
    '''

if __name__ == '__main__':
    main()