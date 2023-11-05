"""proWES schema models."""

from datetime import datetime
from typing import Optional, Union

from pydantic import AnyUrl, BaseModel, EmailStr  # pylint: disable=no-name-in-module


# pragma pylint: disable=too-few-public-methods

class Organization(BaseModel):
    """Model for organization implementing GA4GH services.

    Attributes:
        name: Name of the organization responsible for the service.
        url: URL of the website of the organization (RFC 3986 format).
    """

    name: str
    url: AnyUrl


class ServiceType(BaseModel):
    """Model for GA4GH service type.

    Attributes:
        group: Namespace in reverse domain name format. Use `org.ga4gh` for
            implementations compliant with official GA4GH specifications. For services
            with custom APIs not standardized by GA4GH, or implementations diverging
            from official GA4GH specifications, use a different namespace (e.g. your
            organization's reverse domain name).
        artifact: Name of the API or GA4GH specification implemented. Official GA4GH
            types should be assigned as part of standards approval process. Custom
            artifacts are supported.
        version: Version of the API or specification. GA4GH specifications use
            semantic versioning.
    """

    group: str
    artifact: str
    version: str


class Service(BaseModel):
    """Model for GA4GH service.

    Attributes:
        id: Unique ID of this service. Reverse domain name notation is recommended,
            though not required. The identifier should attempt to be globally unique so
            it can be used in downstream aggregator services e.g. Service Registry.
        name: Name of this service. Should be human readable.
        type: Type of this service.
        description: Description of the service. Should be human readable and provide
            information about the service.
        organization: Organization providing the service.
        contactUrl: URL of the contact for the provider of this service, e.g. a link
            to a contact form (RFC 3986 format), or an email (RFC 2368 format).
        documentationUrl: URL of the documentation of this service (RFC 3986 format).
            This should help someone learn how to use your service, including any
            specifics required to access data, e.g. authentication.
        createdAt: Timestamp describing when the service was first deployed and
            available (RFC 3339 format).
        updatedAt: Timestamp describing when the service was last updated (RFC 3339
            format).
        environment: Environment the service is running in. Use this to distinguish
            between production, development and testing/staging deployments. Suggested
            values are prod, test, dev, staging. However this is advised and not
            enforced.
        version: Version of the service being described. Semantic versioning is
            recommended, but other identifiers, such as dates or commit hashes, are
            also allowed. The version should be changed whenever the service is
            updated.
    """

    id: str
    name: str
    type: ServiceType
    description: Optional[str]
    organization: Organization
    contactUrl: Optional[Union[AnyUrl, EmailStr]]
    documentationUrl: Optional[AnyUrl]
    createdAt: Optional[datetime]
    updatedAt: Optional[datetime]
    environment: Optional[str]
    version: str
