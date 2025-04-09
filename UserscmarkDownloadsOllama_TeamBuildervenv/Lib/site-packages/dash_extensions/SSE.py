# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class SSE(Component):
    """A SSE component.
The SSE component makes it possible to collect data from e.g. a ResponseStream. It's a wrapper around the SSE.js library.
https://github.com/mpetazzoni/sse.js

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- animate_chunk (number; default 1):
    Chunk size (i.e. number of characters) for the animation.

- animate_delay (number; default 0):
    If set, each character is delayed by some amount of time. Used to
    animate the stream.

- animate_prefix (string; optional):
    Prefix to be excluded from the animation.

- animate_suffix (string; optional):
    Suffix to be excluded from the animation.

- animation (string; optional):
    The data value. Either the latest, or the concatenated depending
    on the `concat` property.

- concat (boolean; default True):
    A boolean indicating if the stream values should be concatenated.

- done (boolean; optional):
    A boolean indicating if the (current) stream has ended.

- options (dict; optional):
    Options passed to the SSE constructor.
    https://github.com/mpetazzoni/sse.js?tab=readme-ov-file#options-reference.

    `options` is a dict with keys:

    - headers (dict; optional)

    - method (string; optional)

    - payload (dict | string; optional)

    - withCredentials (boolean; optional)

    - start (boolean; optional)

    - debug (boolean; optional)

- url (string; optional):
    URL of the endpoint.

- value (string; optional):
    The data value. Either the latest, or the concatenated depending
    on the `concat` property."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_extensions'
    _type = 'SSE'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, options=Component.UNDEFINED, url=Component.UNDEFINED, concat=Component.UNDEFINED, value=Component.UNDEFINED, animate_delay=Component.UNDEFINED, animate_chunk=Component.UNDEFINED, animate_prefix=Component.UNDEFINED, animate_suffix=Component.UNDEFINED, animation=Component.UNDEFINED, done=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'animate_chunk', 'animate_delay', 'animate_prefix', 'animate_suffix', 'animation', 'concat', 'done', 'options', 'url', 'value']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'animate_chunk', 'animate_delay', 'animate_prefix', 'animate_suffix', 'animation', 'concat', 'done', 'options', 'url', 'value']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(SSE, self).__init__(**args)
