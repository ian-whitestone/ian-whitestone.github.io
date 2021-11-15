---
layout: post
title: Continuous docker builds with Github Actions
author: ianwhitestone
summary: Building & pushing a Docker image to Google Container Registry with Github Actions
comments: false
image: images/docker-gcr-ga/docker-ga-gcr.png
---

{% include head.html %}

<p align="center">
    <img width="75%" src="{{ site.baseurl }}{% link images/docker-gcr-ga/docker-ga-gcr.png %}">
</p>

I've recently been using Docker to package up my Python environment for deployment in a [Dask cluster on Google Cloud Platform]({% post_url 2020-09-29-single-node-dask-cluster-on-gcp %}) (GCP). If you're spinning up Dask clusters in an active codebase, you'll want to make sure you're regularly updating your Docker image with the latest dependencies and code. To avoid the hassle of manually rebuilding your Docker image whenever things change, I recommend creating a simple [Github Actions](https://github.com/features/actions) workflow that rebuilds your Docker image automatically. This can be configured to run whenever a new commit is pushed to master or a development branch, or any other [events that trigger a workflow](https://docs.github.com/en/free-pro-team@latest/actions/reference/events-that-trigger-workflows).

In this example, I'll be using Google's [Container Registry](https://cloud.google.com/container-registry) (GCR) product to host my Docker image due to its [tight integration with Google Compute Engine](https://cloud.google.com/compute/docs/containers/deploying-containers), but this workflow can easily be extended to push your image to any registry.

## Creating a service account in GCP

In order to let Github Actions push to your GCR repository, you'll need to create a service account with the [required permissions and roles](https://cloud.google.com/container-registry/docs/access-control#permissions_and_roles). I'll show you how to do this from the GCP console, but you could accomplish the same thing directly from the command line with the [gcloud CLI](https://cloud.google.com/sdk/gcloud).

First, create a new role from the IAM & Admin section of the GCR console. You can see the list of 8 storage permissions the role has access to. I arrived at this set through a trial and error process where I kept incrementally adding new permissions until the workflow succeeded without a permission error (doing my best to respect the [principle of least privilege](https://en.wikipedia.org/wiki/Principle_of_least_privilege)).

<p align="center">
    <img width="75%" src="{{ site.baseurl }}{% link images/docker-gcr-ga/gcr-role.png %}">
</p>

Next, create a new service account with a meaningful name:

<p align="center">
    <img width="75%" src="{{ site.baseurl }}{% link images/docker-gcr-ga/gcr-service-account-step-1.png %}">
</p>

And then attach the role you just created:

<p align="center">
    <img width="75%" src="{{ site.baseurl }}{% link images/docker-gcr-ga/gcr-service-account-step-2.png %}">
</p>

I didn't grant any user access in step 3. Once that account is created, you can create a new private key by clicking "Add Key" at the bottom. Be sure to select the JSON format when presented with the option.

<p align="center">
    <img width="75%" src="{{ site.baseurl }}{% link images/docker-gcr-ga/gcr-service-account-step-3.png %}">
</p>

## Configuring secrets for Github Actions

We'll need to store this private key you just created as a secret in our Github repository. After downloading this JSON key file to your local computer, you can run the following command (if you're on a Mac) to copy the encoded contents of the key to your clipboard:

`cat ~/Downloads/<Your_Private_Service_Account_key>.json | base64 | pbcopy`

You can then create a new secret in your Github repository, `GCP_SERVICE_ACCOUNT_KEY`, and paste in those contents. It's also good practice to keep your GCP project ID private as well, so I usually store that as another secret, `GCP_PROJECT_ID`.


## Github Actions workflow

With those in place, you can leverage the [setup-gcloud](https://github.com/google-github-actions/setup-gcloud) custom action the Google team maintains to setup and authorize the `gcloud` CLI in your Github Actions workflow. Running `gcloud auth configure-docker` then configures Docker so that you can push directly to your GCR repository.

Here's an example workflow that builds & pushes a Docker image to GCR on every commit to master:

```yaml
# .github/workflows/docker-gcp.yml
name: Docker-GCP
on:
  push:
    branches:
      - master
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2

    - name: Setup gcloud
      uses: GoogleCloudPlatform/github-actions/setup-gcloud@master
      with:
        version: '290.0.1'
        service_account_key: {% raw %}${{ secrets.GCP_SERVICE_ACCOUNT_KEY }} {% endraw %}
        project_id: {% raw %}${{ secrets.GCP_PROJECT_ID }} {% endraw %}

    - name: Configure docker for GCP
      run: gcloud auth configure-docker

    - name: Build docker image
      run: {% raw %} docker build -t gcr.io/${{ secrets.GCP_PROJECT_ID }}/<YOUR_IMAGE_NAME>:latest . {% endraw %}

    - name: Push to Google Container Registry
      run: {% raw %} docker push gcr.io/${{ secrets.GCP_PROJECT_ID }}/<YOUR_IMAGE_NAME>:latest {% endraw %}
```

### Alternate workflow with Docker Hub

If you're instead using [Docker Hub](https://hub.docker.com/) as a registry, your workflow becomes a bit simpler. Assuming you have your Docker Hub username & password available as secrets in your Github repository, your workflow could look something like this:

```yaml
# .github/workflows/docker-hub.yml
name: Docker-Hub
on:
  push:
    branches:
      - master
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2

    - name: Docker Hub login
      env:
        DOCKER_USERNAME: {% raw %}${{ secrets.DOCKER_USERNAME }} {% endraw %}
        DOCKER_PASSWORD: {% raw %}${{ secrets.DOCKER_PASSWORD }} {% endraw %}
      run: echo $DOCKER_PASSWORD | docker login --username $DOCKER_USERNAME --password-stdin

    - name: Build docker image
      run: docker build -t <YOUR_DOCKER_HUB_REPO_NAME>/<YOUR_IMAGE_NAME>:latest

    - name: Push to Docker Hub
      run: docker push <YOUR_DOCKER_HUB_REPO_NAME>/<YOUR_IMAGE_NAME>:latest
```
