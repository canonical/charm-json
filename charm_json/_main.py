import collections.abc
import json
import typing

import charm


class _Databag(typing.Mapping[str, typing.Any]):
    _EXCLUDED_KEYS = ("egress-subnets", "ingress-address", "private-address")
    """Keys set by Juju
    
    These values are not JSON-encoded
    """

    def __init__(self, databag: typing.Mapping[str, str], /):
        self._databag = databag

    def __repr__(self):
        return f"{type(self).__name__}({repr(self._databag)})"

    def __getitem__(self, key: str):
        if key in self._EXCLUDED_KEYS:
            return self._databag[key]
        return json.loads(self._databag[key])

    def __iter__(self):
        return iter(self._databag.keys())

    def __len__(self):
        return len(self._databag)


class _WriteableDatabag(_Databag, typing.MutableMapping[str, typing.Any]):
    def __setitem__(self, key: str, value):
        if key in self._EXCLUDED_KEYS:
            if not isinstance(value, str):
                raise TypeError(
                    f"{repr(key)} is set by Juju and is not JSON-encoded. It must be set to type 'str', got '{type(value).__name__}': {repr(value)}"
                )
            self._databag[key] = value
        self._databag[key] = json.dumps(value)

    def __delitem__(self, key):
        del self._databag[key]


class Relation(charm.Relation, typing.Mapping[str, typing.Mapping[str, typing.Any]]):
    def __eq__(self, other):
        return isinstance(other, Relation) and super().__eq__(other)

    def __getitem__(self, key):
        databag = super().__getitem__(key)
        if isinstance(databag, collections.abc.MutableMapping):
            return _WriteableDatabag(databag)
        return _Databag(databag)

    @property
    def my_unit(self) -> typing.MutableMapping[str, typing.Any]:
        return super().my_unit

    @property
    def my_app(self) -> typing.Mapping[str, typing.Any]:
        return super().my_app

    @property
    def other_units(
        self,
    ) -> typing.Mapping[charm.Unit, typing.Mapping[str, typing.Any]]:
        return super().other_units

    @property
    def other_app(self) -> typing.Mapping[str, typing.Any]:
        return super().other_app


class PeerRelation(Relation, charm.PeerRelation):
    @property
    def all_units(self) -> typing.Mapping[charm.Unit, typing.Mapping[str, typing.Any]]:
        return super().all_units


class Endpoint(charm.Endpoint):
    @property
    def _relations(self):
        return [Relation(relation.id) for relation in super()._relations]

    @property
    def relation(self) -> typing.Optional[Relation]:
        return super().relation
