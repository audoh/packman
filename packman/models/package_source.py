from abc import ABC, abstractmethod
from typing import Callable, Iterable, Optional

from packman.utils.operation import Operation
from packman.utils.union import DiscriminatedUnion
from pydantic import BaseModel, Extra


class PackageVersion(BaseModel):
    name: str
    version: str
    description: Optional[str] = None


class BasePackageSource(BaseModel, ABC):
    type: str

    @abstractmethod
    def get_version(self, version: str) -> PackageVersion:
        ...

    @abstractmethod
    def fetch_version(self, version: str, operation: Operation, on_progress: Callable[[float], None] = lambda: None) -> None:
        ...

    @abstractmethod
    def get_latest_version(self) -> PackageVersion:
        ...

    @abstractmethod
    def get_versions(self) -> Iterable[str]:
        ...

    class Config:
        extra = Extra.forbid


PackageSource = DiscriminatedUnion(BasePackageSource, "type")
package_source = PackageSource.decorator()
