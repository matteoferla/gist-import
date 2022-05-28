# gist-import
GitHub Gist are handy snippets, which are meant to be copy-pasted into one's code... but what if you could import them?

> This is a low-priority work-in-progress weekend project.
> And may completely forget about it in the future.
> As I currently need to find the main Jupyter notebook the code was in...

## Background

[GitHub Gist](https://gist.github.com/) are snippets that aren't part of regular GitHub,
they are intended to be used in blogs etc. to show code-hightlighting by embedding the gist.
If one were to use in it Python, one should copy-paste it or do something convoluted.

![img.png](example_gist.png)

Say the gist is nice and isolated, with all the correct imports,
then this works fine.

```python
import requests

response = requests.get('https://gist.github.com/matteoferla/d0daee35fe6f598bc720ce0eeebbac97/raw/6f7ba15dde86f1066629af61e0724dbe6a62cceb/transmute_FindMCS_parameters.py')
response.raise_for_status()
exec(response.text)
transmute_FindMCS_parameters()
```

but things get messy quickly. As a placeholder for the `response.text` in the following examples a string is used.

The following works:

```python3
faux_gist:str = 'print(i)'  # pretend this is the gist from `response.text`
    
i = 'hello world'

exec(faux_gist)
```

But as soon as one moves away from the global namespace issues happen.

The `exec` function accepts optionally a `globals` and `locals` parameter.