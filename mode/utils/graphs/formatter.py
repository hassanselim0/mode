"""Formatting graphs."""

from typing import Any, ClassVar, Dict, Mapping, Optional

from mode.utils.objects import label
from mode.utils.types.graphs import _T, GraphFormatterT


def dedent_initial(s: str, n: int = 4) -> str:
    """Remove indentation from first line of text."""
    return s[n:] if s[:n] == " " * n else s


def dedent(s: str, n: int = 4, sep: str = "\n") -> str:
    """Remove indentation."""
    return sep.join(dedent_initial(line) for line in s.splitlines())


class DOT:
    """Constants related to the dot format."""

    HEAD = dedent(
        """
        {IN}{type} {id} {{
        {INp}graph [{attrs}]
    """
    )
    ATTR = "{name}={value}"
    NODE = '{INp}"{0}" [{attrs}]'
    EDGE = '{INp}"{0}" {dir} "{1}" [{attrs}]'
    ATTRSEP = ", "
    DIRS: ClassVar[Dict] = {"graph": "--", "digraph": "->"}
    TAIL = "{IN}}}"


class GraphFormatter(GraphFormatterT):
    """Format dependency graphs."""

    _attr = DOT.ATTR.strip()
    _node = DOT.NODE.strip()
    _edge = DOT.EDGE.strip()
    _head = DOT.HEAD.strip()
    _tail = DOT.TAIL.strip()
    _attrsep = DOT.ATTRSEP
    _dirs: ClassVar[Dict] = dict(DOT.DIRS)

    scheme: Mapping[str, Any] = {
        "shape": "box",
        "arrowhead": "vee",
        "style": "filled",
        "fontname": "HelveticaNeue",
    }
    edge_scheme: Mapping[str, Any] = {
        "color": "darkseagreen4",
        "arrowcolor": "black",
        "arrowsize": 0.7,
    }
    node_scheme: Mapping[str, Any] = {
        "fillcolor": "palegreen3",
        "color": "palegreen4",
    }
    term_scheme: Mapping[str, Any] = {
        "fillcolor": "palegreen1",
        "color": "palegreen2",
    }
    graph_scheme: Mapping[str, Any] = {"bgcolor": "mintcream"}

    def __init__(
        self,
        root: Any = None,
        type: Optional[str] = None,
        id: Optional[str] = None,
        indent: int = 0,
        inw: str = " " * 4,
        **scheme: Any,
    ) -> None:
        self.id = id or "dependencies"
        self.root = root
        self.type = type or "digraph"
        self.direction = self._dirs[self.type]
        self.IN = inw * (indent or 0)
        self.INp = self.IN + inw
        self.scheme = dict(self.scheme, **scheme)
        self.graph_scheme = dict(self.graph_scheme, root=self.label(self.root))

    def attr(self, name: str, value: Any) -> str:
        return self.FMT(self._attr, name=name, value=f'"{value}"')

    def attrs(
        self, d: Optional[Mapping] = None, scheme: Optional[Mapping] = None
    ) -> str:
        scheme = {**self.scheme, **scheme} if scheme else self.scheme
        d = {**scheme, **d} if d else scheme
        return self._attrsep.join(str(self.attr(k, v)) for k, v in d.items())

    def head(self, **attrs: Any) -> str:
        return self.FMT(
            self._head,
            id=self.id,
            type=self.type,
            attrs=self.attrs(attrs, self.graph_scheme),
        )

    def tail(self) -> str:
        return self.FMT(self._tail)

    def label(self, obj: _T) -> str:
        return label(obj)

    def node(self, obj: _T, **attrs: Any) -> str:
        return self.draw_node(obj, self.node_scheme, attrs)

    def terminal_node(self, obj: _T, **attrs: Any) -> str:
        return self.draw_node(obj, self.term_scheme, attrs)

    def edge(self, a: _T, b: _T, **attrs: Any) -> str:
        return self.draw_edge(a, b, **attrs)

    def _enc(self, s: str) -> str:
        return s.encode("utf-8", "ignore").decode()

    def FMT(self, fmt: str, *args: Any, **kwargs: Any) -> str:
        return self._enc(
            fmt.format(*args, **dict(kwargs, IN=self.IN, INp=self.INp))
        )

    def draw_edge(
        self,
        a: _T,
        b: _T,
        scheme: Optional[Mapping] = None,
        attrs: Optional[Mapping] = None,
    ) -> str:
        return self.FMT(
            self._edge,
            self.label(a),
            self.label(b),
            dir=self.direction,
            attrs=self.attrs(attrs, self.edge_scheme),
        )

    def draw_node(
        self,
        obj: _T,
        scheme: Optional[Mapping] = None,
        attrs: Optional[Mapping] = None,
    ) -> str:
        return self.FMT(
            self._node, self.label(obj), attrs=self.attrs(attrs, scheme)
        )
