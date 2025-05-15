# Numeric Stream

{% hint style="info" %}
For information on how to create a `NumericStream` please visit the Quick Start docs: [#stream.of](../../quick-start.md#stream.of "mention")
{% endhint %}

### `interquartile_range()`: Calculate the interquartile range

Calculates the interquartile range of a numerical Stream. Returns either `int` or `float`.

```python
Stream.of([1, 2, 3, 4, 5, 7, 7, 8, 9, 9]) \
    .interquartile_range() # Returns 5
```

### `first_quartile()`: Calculate the first quartile

Calculates the first quartile of a numerical Stream. Returns either `int` or `float`.

```python
Stream.of([1, 2, 3, 4, 5, 7, 7, 8, 9, 9]) \
    .first_quartile() # Returns 3
```

### `mean()`: Calculate the mean

Calculates the mean of a numerical Stream. Returns either `int` or `float`.

```python
Stream.of([1, 2, 3, 4, 5, 7, 7, 8, 9, 9]) \
    .mean() # Returns 5.5
```

### `median()`: Calculate the median

Calculates the median of a numerical Stream. Returns either `int` or `float`.

```python
Stream.of([1, 2, 3, 4, 5, 7, 7, 8, 9, 9]) \
    .median() # Returns 6.0
```

### `mode()`: Calculate the mode

Calculates the mode(s) (most frequently occurring element/elements) of a numerical Stream. Returns a list of either `int`, `float`or `None`.&#x20;

```python
Stream.of([1, 2, 3, 4, 5, 7, 7, 8, 9, 9]) \
    .mode() # Returns [7, 9]
```

### `range()`: Calculate the range

Calculates the range of a numerical Stream. Returns either `int` or `float`.

```python
Stream.of([1, 2, 3, 4, 5, 7, 7, 8, 9, 9]) \
    .range() # Returns 8
```

### `third_quartile()`: Calculate the range

Calculates the third quartile of a numerical Stream. Returns either `int` or `float`.

```python
Stream.of([1, 2, 3, 4, 5, 7, 7, 8, 9, 9]) \
    .third_quartile() # Returns 8
```

### `sum()`: Calculate the sum

Calculates the sum of all elements of a numerical Stream. Returns either `int` or `float`.

```python
Stream.of([1, 2, 3]) \
    .sum() # Returns 6
```
