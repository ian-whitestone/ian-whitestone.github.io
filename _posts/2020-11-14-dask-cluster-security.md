---
layout: post
title: Dask cluster security
author: ianwhitestone
summary: Adding TLS/SSL security to your Dask cluster
comments: true
image: images/dask-gcp/dask-gcp-bad-guy.png
---

{% include head.html %}

In my [last post]({% post_url 2020-09-29-single-node-dask-cluster-on-gcp %}) I showed how to get a single node Dask cluster running on a Google Cloud Platform (GCP) Compute Engine instance. However, one key pitfall I acknowledged was the lack of authentication & security. With the setup I gave, anyone could execute commands in my cluster and wreak all sorts of havoc, as depicted (very accurately, I must say) below.

<p align="center">
    <img width="75%" src="{{ site.baseurl }}{% link images/dask-gcp/dask-gcp-bad-guy.png %}">
</p>

In this brief follow up post I'll show how we can leverage Dask's [TLS/SSL security features](https://distributed.dask.org/en/latest/tls.html) to remove this risk.

# Adding security to the Dask cluster

Dask's support for TLS/SSL communication allows for both authentication and encrypted communication between everything involved in your cluster: workers, schedulers and clients. I am using a single certificate and private key for all endpoints in my deployment, but you can refer to the [Dask docs](https://distributed.dask.org/en/latest/tls.html) for other options. To get started, we'll generate a new certificate and private key using OpenSSL:

`openssl req -newkey rsa:2048 -new -nodes -x509 -days 3650 -keyout ~/.ssh/dask-cluster-key.pem -out ~/.ssh/dask-cluster-cert.pem`

This will generate two files: a certificate (`dask-cluster-cert.pem`) and a private key (`dask-cluster-key.pem`), and store them under your `.ssh` folder within the home directory. You can store them in a different location if you prefer.

Next, we'll need to update the [`dask-entrypoint.sh`](https://gist.github.com/ian-whitestone/d3b876e77743923b112d7d004d86480c#file-dask-entrypoint-sh) script I shared in the previous post. This script is responsible for starting up the dask cluster, and gets kicked off after the Compute Engine instance is created and our docker container starts running. First, we'll grab the contents for the certificate and private key from some environment variables (which we'll get to later) and then save them to disk:

```bash
RUN echo "$DASK_CLUSTER_CERT" > ~/dask-cluster-cert.pem
RUN echo "$DASK_CLUSTER_KEY" > ~/dask-cluster-key.pem
```

With the files on disk in the running container, we can now point the scheduler & worker jobs directly to them. Note that we are now using the TLS protocol when specifying the host, as opposed to TCP which we used previously.

```bash
# Start the dask scheduler & workers
echo "Starting dask-scheduler"
poetry run dask-scheduler \
    --tls-ca-file ~/dask-cluster-cert.pem \
    --tls-cert ~/dask-cluster-cert.pem \
    --tls-key ~/dask-cluster-key.pem > log.txt 2>&1 &

echo "Creating $num_workers dask workers"
for i in `seq $num_workers`
do
    poetry run dask-worker \
        --tls-ca-file ~/dask-cluster-cert.pem \
        --tls-cert ~/dask-cluster-cert.pem \
        --tls-key ~/dask-cluster-key.pem \
        --nthreads $threads_per_worker \
        --memory-limit "${memory_per_worker}GB" \
        tls://127.0.0.1:8786 > log.txt 2>&1 &
done
```

The `dask-entrypoint.sh` script we updated now requires that the contents of our certificate & private key files live in two environment variables, `DASK_CLUSTER_CERT` and `DASK_CLUSTER_KEY`. To securely<sup>1</sup> pass through our certificate & private key info, we'll provide them to the container as environment variables at runtime when the compute instance is created:

```bash
gcloud compute instances create-with-container dask-cluster-instance \
    --zone=us-central1-a \
    --machine-type=e2-highcpu-16 \
    --tags=dask-server \
    --container-env=MEMORY_PER_WORKER=1,THREADS_PER_WORKER=1,DASK_CLUSTER_CERT=$(cat ~/.ssh/dask_cluster_cert.pem),DASK_CLUSTER_KEY=$(cat ~/.ssh/dask_cluster_key.pem) \
    --scopes=https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/trace.append \
    --container-image=registry.hub.docker.com/ianwhitestone/domi-dask:latest
```

If you launch your dask cluster with this new configuration, you'll now find that the traditional method of connecting to the cluster with `Client(cluster_host)` no longer works. Just like we did with the scheduler and worker processes, we need to initialize our `Client` with the same credentials. For most projects, I typically have a `config.py` file which stores a bunch of settings & pointers to files and directories I need to access throughout the codebase. Something like this:

```python
# config.py
import os

HOME_DIRECTORY: str = os.path.expanduser("~")
DASK_CERT_FILEPATH: str = os.path.join(HOME_DIRECTORY, ".ssh", "dask-cluster-cert.pem")
DASK_KEY_FILEPATH: str = os.path.join(HOME_DIRECTORY, ".ssh", "dask-cluster-key.pem")
```

Whenever you create your Dask `Client`, you must now also provide a `Security` object which points to the certificate & private key files:

```python
# somewhere_else.py
from distributed import Client
from distributed.security import Security

from config import DASK_CERT_FILEPATH, DASK_KEY_FILEPATH

cluster_host_ip = '35.202.12.207'
sec = Security(
    tls_ca_file=DASK_CERT_FILEPATH,
    tls_client_cert=DASK_CERT_FILEPATH,
    tls_client_key=DASK_KEY_FILEPATH,
    require_encryption=True,
)
# Using TLS now instead of TCP!
client = Client(f"tls://{cluster_host_ip}:8786", security=sec)
```

And that's it, **no more bad guys!**

<p align="center">
    <img width="75%" src="{{ site.baseurl }}{% link images/dask-gcp/dask-gcp-bad-guy-blocked.png %}">
</p>

<hr>

**Notes**

<sup>1 </sup> There are many [differing opinions](https://stackoverflow.com/questions/22651647/docker-and-securing-passwords) on how to securely use secrets in a docker container. Please do your homework and consider what makes sense for you.
