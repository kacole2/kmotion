# kmotion
kmotion is a wrapper script that uses the kubernetes python client and velero under the covers to very quickly migrate an entire kubernetes application (including Services, Deployments, PODs) from one Kubernetes cluster to another.

## Prerequisites
To leverage kmotion you will need the following.
1. Python3 Installed
2. The kmotion script (from this repo).
3. A kubeconfig file with two clusters configured and access to those two clusters.


## Using Kmotion

To deploy the sample workload into the Source Cluster:

    $ kubectl apply -f sample/lucky13.yaml

This will create a namespace and add a deployment and service.

To view the page locally with a port forward:

    $ kubectl port-forward -n lucky13 svc/nginx 8000:80

Now navigate to http://localhost:8000/index.html in your browser.  The index page will show the name of the node on which the pod you're connected to is running.

## Lucky 13 Docker Image

This docker image uses the `index.sh` to generate an index page that displays the node on which the pod is running.  In order to alter this index page, simply alter the html that `index.sh` stamps out.  If you use additional environment variables, be sure to make the env vars available through the `sample/lucky13.yaml` manifest.  The existing example uses the downward API to set the `MY_NODE_NAME` var.

If you make a change to the index script, build a new image with:

    $ docker build -t myrepo/lucky13 .

And push the image:

    $ docker push myrepo/lucky13

Now replace the `lander2k2/lucky13` image name in `image/lucky13.yaml` with your new image and apply it:

    $ kubectl apply -f sample/lucky13.yaml

