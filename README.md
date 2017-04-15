## Kube-render

A tool that renders Kubernetes (k8s) templates into Manifests.

Just pip-install it and run with kube-render.
Once you install it, you can use kube-render --help, which will output its usage, as in:

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

No tests yet.. but if you wanna try, go to examples folder and run something like
```
kube-render -t example/templates/ -c example/context_base.yaml  -c example/context_override.yaml --set x=y --set y=z -v --set y=got_overriden
```
