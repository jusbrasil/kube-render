## Kube-render

A POC tool for rendering Kubernetes (k8s) templates into Manifests.
It supports most of [Helm](https://github.com/kubernetes/helm) rendering features.

The idea behind this project is to provide a simple mechanism of rendering Manifests.
It might be helpful when you can't or don't want to use Helm, but want some help with a more "complex" set of rendering features.

It's not on Pypi yet. If you want to install it in dev mode, you can clone the repo and install with:
```
pip install --editable .
```

Once you install it, you can use `kube-render --help`, which will output its usage, as in:

```
$ kube-render --help

Usage: kube-render [OPTIONS]

Options:
  -v, --verbose            Whether it should print generated files or not
  -c, --context TEXT       Yaml file path to be loaded into context. Supports
                           merging.
  -s, --set TEXT           Vars that override context files. Format: key=value
  -t, --template-dir TEXT  Folder holding templates that should be rendered
  -o, --output-dir TEXT    Folder that rendered templates should be put in
  --no-save                Only prints templates. Doesn't create files
  -A, --apply              Apply rendered files using `kubectl apply`
  --help                   Show this message and exit.
```

It's just a POC and there are no tests yet.. but if you wanna try, go to examples folder and run something like
```
$ kube-render -t example/templates/ -c example/context_base.yaml  -c example/context_override.yaml --set root.something.c=whatsup -v

### Computed variables:root:
  something:
    a: hello
    b: man
    c: whatsup

### Rendered deployment.yaml
a: hello
b: man
c: whatsup
```

