from datetime import datetime

from bson import ObjectId
from bson.errors import InvalidId
from pydantic.main import BaseModel, BaseConfig


class OID(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        try:
            return ObjectId(str(v))
        except InvalidId:
            raise ValueError("Not a valid ObjectId")


class MongoModel(BaseModel):
    class Config(BaseConfig):
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            ObjectId: lambda oid: str(oid),
        }

    @classmethod
    def from_mongo(cls, data: dict):
        """We must convert id into "id". """
        if not data:
            return data
        # id = data.pop('id', None)
        return cls(**dict(data))

    def mongo(self, **kwargs):
        exclude_unset = kwargs.pop('exclude_unset', True)
        by_alias = kwargs.pop('by_alias', True)

        parsed = self.dict(
            exclude_unset=exclude_unset,
            by_alias=by_alias,
            **kwargs,
        )

        # Mongo uses `id` as default key. We should stick to that as well.
        # if 'id' not in parsed and 'id' in parsed:
        #     parsed['id'] = parsed.pop('id')

        return parsed
