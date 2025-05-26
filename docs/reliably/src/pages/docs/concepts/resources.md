---
layout: ~/layouts/DocsLayout.astro
title: Resources
description: Catalog of your infrastructure and platform resources.
---

Reliably is able to capture a large variety of your infrastructure and platform
resources. Reliably uses your resources to provide feedback of threats as well
as reliability testing coverage.

<p>Under the hood, <strong>Reliably uses the <a href="https://pypi.org/project/lueur/" rel="noreferer noopener" target="_blank">open-source lueur library <span class="screen-reader-text">External link will open in a new tab</span></a> 
to list your resources.</strong></p>

<div class="markdown-tip">

Resources is an experimental feature not yet complete. In the future, Reliably
will use this resource catalog to automatically suggest the most
appropriate set of experiments to conduct.
</div>

## Connectors

To list resources from your infrastructure or platform, Reliably needs the
appropriate credentials.

Reliably supports the following targets:

* Kubernetes
* AWS
* GCP
* GitHub

### Kubernetes

To read resources from a Kubernetes cluster, provide the right credentials
a service account.

Reliably will first look for the default kubeconfig file it can find:

<p><img src="/images/docs/concepts/resources/kubernetes-connector.png" alt="A screenshot of the Reliably Resources Kubernetes Connector" width="655" /></p>

Alternatively you may provide your own credentials:

<p><img src="/images/docs/concepts/resources/kubernetes-connector-extended.png
" alt="A screenshot of the Reliably Resources Kubernetes Connector" width="655" /></p>

### AWS

To read resources from AWS, provide the right credentials using an access key
and secret key.

Reliably will first look for the default settings file it can find:

<p><img src="/images/docs/concepts/resources/aws-connector.png" alt="A screenshot of the Reliably Resources AWS Connector" width="655" /></p>

Alternatively you may provide your own credentials:

<p><img src="/images/docs/concepts/resources/aws-connector-extended.png
" alt="A screenshot of the Reliably Resources AWS Connector" width="655" /></p>

### GCP

To read resources from GCP, provide the right credentials.

Reliably will first look for the default settings file it can find:

<p><img src="/images/docs/concepts/resources/gcp-connector.png" alt="A screenshot of the Reliably Resources GCP Connector" width="655" /></p>

Alternatively you may provide your own credentials:

<p><img src="/images/docs/concepts/resources/gcp-connector-extended.png
" alt="A screenshot of the Reliably Resources GCP Connector" width="655" /></p>

### GitHub

To read resources from GitHub, provide a GitHub token:

<p><img src="/images/docs/concepts/resources/github-connector.png
" alt="A screenshot of the Reliably Resources GitHub Connector" width="655" /></p>

## Resource Catalog

Once configured, Reliably lists, reads resources and stores them into its
storage. They can be now browed.

You may refresh the catalog by clicking on the Manage > Refresh button.


<p><img src="/images/docs/concepts/resources/kubernetes-listing.png
" alt="A screenshot of the Reliably Resources listing" width="655" /></p>

## Resource View

The typical view of a resource represents a couple of metadata, a list
of potential relations to that resource and finally the yaml representation
of the resource as a diff between the last two most recent refresh operations.


<p><img src="/images/docs/concepts/resources/resource-view-1.png
" alt="A screenshot of the Reliably Resource view"  /></p>


<p><img src="/images/docs/concepts/resources/resource-view-2.png
" alt="A screenshot of the Reliably Resource view"  /></p>
