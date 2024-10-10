import collections.abc
import json
import typing

import charm


class _Databag(typing.Mapping[str, typing.Any]):
    def __init__(self, databag: typing.Mapping[str, str], /):
        self._databag = databag

    def __repr__(self):
        return f"{type(self).__name__}({repr(self._databag)})"

    def __getitem__(self, key: str):
        return json.loads(self._databag[key])

    def __iter__(self):
        return iter(self._databag.keys())

    def __len__(self):
        return len(self._databag)


class _WriteableDatabag(_Databag, typing.MutableMapping[str, typing.Any]):
    def __setitem__(self, key: str, value):
        self._databag[key] = json.dumps(value)

    def __delitem__(self, key):
        del self._databag[key]


class Relation(charm.Relation, typing.Mapping[str, typing.Mapping[str, typing.Any]]):
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
