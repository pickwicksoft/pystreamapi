# Data Loaders

Data loaders provide a convenient way to process data from various data files in your streams. You can access the values of each data set as if it were an object, containing the header names as attributes.

{% hint style="info" %}
Currently, PyStreamAPI supports reading data from CSV, JSON, XML, YAML and TOML files.
{% endhint %}

To use the loaders, you can import them with this line:

```python
from pystreamapi.loaders import csv, json, toml, xml, yaml
```

### CSV loader

In order to load the data from a CSV file, you can use the `csv` loader.

You just need the file's path, and you can optionally specify the delimiter and the encoding. By default, the encoding is set to UTF-8.&#x20;

By default, all values get converted to `int`, `float`, `bool` or otherwise `str`. The type casting can be disabled to speed up the reading time by setting the `cast_types` parameter to `False`.

The examples below use this CSV file:

{% code title="data.csv" fullWidth="false" %}
```csv
name;age
Joe;20
Jane;30
John;78
```
{% endcode %}

```python
from pystreamapi import Stream
from pystreamapi.loaders import csv

Stream.of(csv("path/to/data.csv", delimiter=";", encoding="us-ascii")) \
    .map(lambda x: x.name) \
    .for_each(print) # "Joe", "Jane", "John"
```

If you want to disable type conversion, you can use the loader like this:

```python
from pystreamapi import Stream
from pystreamapi.loaders import csv

Stream.of(csv("path/to/data.csv", cast_types=False, delimiter=";")) \
    .map(lambda x: x.age) \
    .for_each(print) # "20", "30", "78"
```

### JSON loader

In order to load the data from a JSON file, you can use the `json` loader.

The loader isn't included in the core version of pystreamapi. You can install it using the following command:

```bash
pip install 'streams.py[json_loader]'
```

:tada: Now you can use the loader as described below!

You can read data either from a JSON file or a string containing JSON. If you read from a string you have to set the `read_from_src` parameter to `True`.

By default, all values get converted to `int`, `float`, `bool` or otherwise `str`.&#x20;

The example below uses this JSON file:

{% code title="data.json" fullWidth="false" %}
```json
[
  {
    "name": "Joe",
    "age": 20
  },
  {
    "name": "Jane",
    "age": 30
  },
  {
    "name": "John",
    "age": 78
  }
]
```
{% endcode %}

```python
from pystreamapi import Stream
from pystreamapi.loaders import json

Stream.of(json("path/to/data.json")) \
    .map(lambda x: x.name) \
    .for_each(print) # "Joe", "Jane", "John"
```

If you want to pass the JSON directly as a string, you can do it like that:

```python
from pystreamapi import Stream
from pystreamapi.loaders import json

Stream.of(json("[{\"name\":\"Joe\",\"age\":20},{\"name\":\"Jane\",\"age\":30}]", 
               read_from_src=True)) \
    .map(lambda x: x.age) \
    .for_each(print)  # 20, 30
```

### XML loader

In order to load the data from an XML file, you can use the `xml` loader.

```python
def xml(src: str, read_from_src=False, retrieve_children=True, cast_types=True,
        encoding="utf-8")
```

The loader isn't included in the core version of pystreamapi. You can install it using the following command:

```bash
pip install 'streams.py[xml_loader]'
```

:tada: Now you can use the loader as described below!

You just need the file's path, and you can optionally specify the encoding. By default, the encoding is set to UTF-8.&#x20;

You can read data either from an XML file or a string containing XML. If you read from a string, you have to set the `read_from_src` parameter to `True`.

By default, all values get converted to `int`, `float`, `bool` or otherwise `str`. The type casting can be disabled to speed up the reading time by setting the `cast_types` parameter to `False`.

The XML loader directly retrieves the children nodes from the XML's root. By setting the `retrieve_children` parameter to `False` you disable this feature and your stream will only consist of one object containing the whole XML tree.

The examples below use this XML file:

{% code title="data.xml" %}
```xml
<employees>
    <employee>
        <name>John Doe</name>
        <cars>
            <car>Audi</car>
        </cars>
    </employee>
    <employee>
        <name>Alice Smith</name>
        <cars>
            <car>Volvo</car>
            <car>Volkswagen</car>
        </cars>
    </employee>
    <founder>
        <name>Martini Boss</name>
        <cars>
            <car>Bugatti</car>
            <car>Mercedes</car>
        </cars>
    </founder>
</employees>
```
{% endcode %}

Here you can see a few examples illustrating how to access different nodes.

```python
from pystreamapi import Stream
from pystreamapi.loaders import xml

Stream.of(xml("path/to/data.xml")) \
    .map(lambda x: x.name) \
    .for_each(print)  # John Doe, Alice Smith, Martini Boss
    
Stream.of(xml("path/to/data.xml")) \
      .map(lambda x: x.cars.car) \
      .for_each(print)  # 'Audi', ['Volvo', 'Volkswagen'], ['Bugatti', 'Mercedes']

Stream.of(xml("path/to/data.xml")) \
      .map(lambda x: type(x).__name__) \
      .for_each(print)  # employee, employee, founder
```

If you disable child retrieving, you have to map the object's children manually:

{% code title="data.xml" fullWidth="false" %}
```xml
<employees>
    <employee>
        <name>John Doe</name>
    </employee>
    <employee>
        <name>Alice Smith</name>
    </employee>
</employees>
```
{% endcode %}

<pre class="language-python"><code class="lang-python"><strong>from pystreamapi import Stream
</strong>from pystreamapi.loaders import xml

Stream.of(xml("data.xml", retrieve_children=False)) \
    .map(lambda x: x.employee) \
    .flat_map(lambda x: Stream.of(x)) \
    .map(lambda x: x.name) \
    .for_each(print)  # John Doe, Alice Smith
</code></pre>

### YAML loader

In order to load the data from a YAML file, you can use the `yaml` loader.

You can read data either from a YAML file or a string containing YAML. If you read from a string you have to set the `read_from_src` parameter to `True`.

By default, all values get converted to `int`, `float`, `bool` or otherwise `str`.&#x20;

The example below uses this YAML file:

{% code title="data.yaml" fullWidth="false" %}
```yaml
- name: Joe
  age: 20
- name: Jane
  age: 30
- name: John
  age: 78
```
{% endcode %}

```python
from pystreamapi import Stream
from pystreamapi.loaders import yaml

Stream.of(yaml("path/to/data.yaml")) \
    .map(lambda x: x.name) \
    .for_each(print) # "Joe", "Jane", "John"
```

If you want to pass the YAML directly as a string, you can do it like that:

```python
from pystreamapi import Stream
from pystreamapi.loaders import yaml

Stream.of(yaml("- name: Joe\n  age: 20\n- name: Jane\n  age: 30", 
               read_from_src=True)) \
    .map(lambda x: x.age) \
    .for_each(print)  # 20, 30
```

### TOML loader

In order to load the data from a TOML file, you can use the `toml` loader.

The `toml` loader is included in the core version of pystreamapi — no extra install is needed.

The loader reads the entire TOML document and yields it as a single namedtuple, so attributes map directly to top-level keys.

You can read data either from a TOML file or a string containing TOML. If you read from a string you have to set the `read_from_src` parameter to `True`.

The example below uses this TOML file:

{% code title="config.toml" fullWidth="false" %}
```toml
[server]
host = "localhost"
port = 8080

[database]
name = "mydb"
```
{% endcode %}

```python
from pystreamapi import Stream
from pystreamapi.loaders import toml

Stream.of(toml("path/to/config.toml")) \
    .map(lambda x: x.server.host) \
    .for_each(print)  # "localhost"
```

If you want to pass the TOML directly as a string, you can do it like that:

```python
from pystreamapi import Stream
from pystreamapi.loaders import toml

Stream.of(toml("[server]\nhost = \"localhost\"\nport = 8080", 
               read_from_src=True)) \
    .map(lambda x: x.server.port) \
    .for_each(print)  # 8080
```
