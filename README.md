# kmotion
it's like vMotion, but for containers... get it?

## Sample Workload Deployment

To deploy the sample workload:

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

