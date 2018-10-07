## Kube-render

[![Build Status](https://travis-ci.org/jusbrasil/kube-render.svg?branch=master)](https://travis-ci.org/jusbrasil/kube-render)

A tool for rendering Kubernetes (k8s) templates into Manifests.
It supports most of [Helm](https://github.com/kubernetes/helm) rendering features.

The idea behind this project is to provide a simple mechanism of rendering Manifests.
It might be helpful when you can't or don't want to use Helm, but want some help with a more "complex" set of rendering features.

To install it, use:
```
pip install kuberender
```

Once you install it, you can use `kube-render --help`, which will output its usage, as in:

```
Usage: kube-render [OPTIONS]

Options:
  -v, --verbose            Whether it should print generated files or not
  -c, --context TEXT       Yaml file path to be loaded into context. Supports
                           merging.
  -s, --set TEXT           Vars that override context files. Format: key=value
  -t, --template-dir TEXT  Folder holding templates that should be rendered
  -u, --template-url TEXT  URL to download templates from (writes on ~/.kube-
                           render/templates). Accepts URLs on pip format
  -A, --apply              Apply rendered files using `kubectl apply`
  -w, --working-dir TEXT   Base directory for loading templates and context
                           files
  --help                   Show this message and exit.
```

You can find usage examples by looking at the tests, but a sample render looks like this:
```
$ kube-render -w tests/resources -c base.yaml  -c extended.yaml --set image.tag=3.0.7 -v
```

As it's in the verbose mode, it will show the computed context and the generated manifest:
```
### Computed context:
image:
  pullPolicy: Always
  repository: redis
  tag: 3.0.7
instance_name: news-page-cache
replicaCount: 1
resources:
  limits:
    cpu: 0.3
    memory: 64M

### Rendered deployment.yaml
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: redis-news-page-cache
  labels:
    name:
    service: redis
spec:
  replicas: 1
  template:
    metadata:
      labels:
        name:
        service: redis
    spec:
      containers:
      - name: redis-news-page-cache
        image: "redis:3.0.7"
        imagePullPolicy: Always
        resources:
          limits:
            memory: "64M"
            cpu: 0.3
```

If you want to use the generated manifest and upload it, include the parameter -A (or --apply).
Basically, what it does, is to call `$ kubectl apply` with a subprocess call.

