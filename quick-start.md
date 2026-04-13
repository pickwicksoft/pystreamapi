---
description: Get started in just a few seconds!
---

# Quick Start

## Installation

To start using PyStreamAPI just install the core module with this command:

```bash
pip install streams.py
```

If you want to install pystreamapi together with the optional extensions, use this command:

```bash
pip install 'streams.py[all]'
```

This will install pystreamapi together with all optional loader extras: `xml_loader` (XML support) and `json_loader` (streaming JSON support via ijson). TOML and YAML support are included in the core install. You can also install extras individually, as described on the following page:

[data-loaders.md](reference/data-loaders.md "mention")

Afterward, you can import it with:

```python
from pystreamapi import Stream
```

:tada: PyStreamAPI is now ready to process your data

## Build a new Stream

PyStreamAPI offers two types of Streams, both of which are available in either sequential or parallel versions:

* (Normal) `Stream`: Offers operations that do not depend on the types. The same functionality as Streams in other programming languages.
* `NumericStream`: This stream extends the capabilities of the default stream by introducing numerical operations. It is designed specifically for use with numerical data sources and can only be applied to such data.

There are a few factory methods that create new Streams:

### `Stream.of()`

```python
Stream.of([1, 2, 3]) # Can return a sequential or a parallel stream
```

Using the `of()` method will let the implementation decide which `Stream` to use. If the source is numerical, a `NumericStream` is created.

### `Stream.parallel_of()`

```python
Stream.parallel_of([1, 2, 3]) # Returns a parallel stream (Either normal or numeric)
```

### `Stream.sequential_of()`

```python
Stream.sequential_of([1, 2, 3]) # Returns a sequential stream (Either normal or numeric)
```

### `Stream.of_noneable()`

```python
# Can return a sequential or a parallel stream (Either normal or numeric)
Stream.of_noneable([1, 2, 3])

# Returns a sequential or a parallel, empty stream (Either normal or numeric)
Stream.of_noneable(None) 
```

If the source is `None`, you get an empty `Stream`

### `Stream.iterate()`

```python
Stream.iterate(0, lambda n: n + 2)
```

Creates a Stream of an infinite Iterator created by iterative application of a function f to an initial element seed, producing a Stream consisting of seed, f(seed), f(f(seed)), etc.

{% hint style="info" %}
**Note** Do not forget to limit the stream with `.limit()`
{% endhint %}

### `Stream.concat()`

```python
Stream.concat(Stream.of([1, 2]), Stream.of([3, 4])) 
# Like Stream.of([1, 2, 3, 4])
```

Creates a new Stream from multiple Streams. Order doesn't change.
