"""
The tool to check the availability or syntax of domain, IP or URL.

::


    ██████╗ ██╗   ██╗███████╗██╗   ██╗███╗   ██╗ ██████╗███████╗██████╗ ██╗     ███████╗
    ██╔══██╗╚██╗ ██╔╝██╔════╝██║   ██║████╗  ██║██╔════╝██╔════╝██╔══██╗██║     ██╔════╝
    ██████╔╝ ╚████╔╝ █████╗  ██║   ██║██╔██╗ ██║██║     █████╗  ██████╔╝██║     █████╗
    ██╔═══╝   ╚██╔╝  ██╔══╝  ██║   ██║██║╚██╗██║██║     ██╔══╝  ██╔══██╗██║     ██╔══╝
    ██║        ██║   ██║     ╚██████╔╝██║ ╚████║╚██████╗███████╗██████╔╝███████╗███████╗
    ╚═╝        ╚═╝   ╚═╝      ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝╚══════╝╚═════╝ ╚══════╝╚══════╝

Provides ans interface which let us interact with the Collection API.

Author:
    Nissar Chababy, @funilrys, contactTATAfunilrysTODTODcom

Special thanks:
    https://pyfunceble.github.io/#/special-thanks

Contributors:
    https://pyfunceble.github.io/#/contributors

Project link:
    https://github.com/funilrys/PyFunceble

Project documentation:
    https://pyfunceble.readthedocs.io/en/dev/

Project homepage:
    https://pyfunceble.github.io/

License:
::


    Copyright 2017, 2018, 2019, 2020, 2022, 2023, 2024 Nissar Chababy

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        https://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

import json
from typing import List, Optional, Union

import requests
import requests.exceptions

import PyFunceble.facility
import PyFunceble.storage
from PyFunceble.checker.availability.status import AvailabilityCheckerStatus
from PyFunceble.checker.reputation.status import ReputationCheckerStatus
from PyFunceble.checker.syntax.status import SyntaxCheckerStatus
from PyFunceble.helpers.environment_variable import EnvironmentVariableHelper


class CollectionQueryTool:
    """
    Provides the interface to the collection dataset.

    :param token:
        The token to use to communicate with the API.

        .. warning::
            If :code:`None` is given, the class constructor will try to load the
            PYFUNCEBLE_COLLECTION_API_TOKEN environment variable.

    :param url_base:
        The base of the URL to communicate with.

    :param preferred_status_origin:
        The preferred data origin.
        It can be :code:`frequent`, :code:`latest` or :code:`recommended`.
    """

    SUPPORTED_CHECKERS: List[str] = ["syntax", "reputation", "availability"]
    SUPPORTED_STATUS_ORIGIN: List[str] = ["frequent", "latest", "recommended"]

    STD_URL_BASE: str = "http://localhost:8001"
    STD_PREFERRED_STATUS_ORIGIN: str = "frequent"
    STD_TIMEOUT: float = 5.0

    _token: Optional[str] = None
    """
    The token to use while communicating with the collection API.
    """

    _url_base: Optional[str] = None
    """
    The base of the URL to communicate with.
    """

    _preferred_status_origin: Optional[str] = None
    """
    The preferred data origin
    """

    _is_modern_api: Optional[bool] = None
    """
    Whether we are working with the modern or legacy API.
    """

    _timeout: float = 5.0
    """
    The timeout to use while communicating with the API.
    """

    session: Optional[requests.Session] = None

    def __init__(
        self,
        *,
        token: Optional[str] = None,
        url_base: Optional[str] = None,
        preferred_status_origin: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> None:
        if token is not None:
            self.token = token
        else:
            self.token = EnvironmentVariableHelper(
                "PYFUNCEBLE_COLLECTION_API_TOKEN"
            ).get_value(default="")

        if url_base is not None:
            self.url_base = url_base
        else:
            self.guess_and_set_url_base()

        if preferred_status_origin is not None:
            self.preferred_status_origin = preferred_status_origin
        else:
            self.guess_and_set_preferred_status_origin()

        if timeout is not None:
            self.timeout = timeout
        else:
            self.guess_and_set_timeout()

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.token}" if self.token else None,
                "X-Pyfunceble-Version": PyFunceble.storage.PROJECT_VERSION,
                "Content-Type": "application/json",
            }
        )

    def __contains__(self, value: str) -> bool:
        """
        Checks if the given value is in the collection.

        :param value:
            The value to check.
        """

        return self.pull(value) is not None

    def __getitem__(self, value: str) -> Optional[dict]:
        """
        Gets the information about the given value.

        :param value:
            The value to get the information about.
        """

        return self.pull(value)

    @property
    def token(self) -> Optional[str]:
        """
        Provides the currently set token.
        """

        return self._token

    @token.setter
    def token(self, value: str) -> None:
        """
        Sets the value of the :code:`_token` attribute.

        :param value:
            The value to set.

        :raise TypeError:
            When the given :code:`value` is not a :py:class:`str`
        """

        if not isinstance(value, str):
            raise TypeError(f"<value> should be {str}, {type(value)} given.")

        self._token = value

    def set_token(self, value: str) -> "CollectionQueryTool":
        """
        Sets the value of the :code:`_token` attribute.

        :param value:
            The value to set.
        """

        self.token = value

        return self

    @property
    def url_base(self) -> Optional[str]:
        """
        Provides the value of the :code:`_url_base` attribute.
        """

        return self._url_base

    @url_base.setter
    def url_base(self, value: str) -> None:
        """
        Sets the base of the URL to work with.

        :param value:
            The value to set.

        :raise TypeError:
            When the given :code:`value` is not a :py:class:`str`.

        :raise ValueError:
            When the given :code:`value` does not have a scheme.
        """

        if not isinstance(value, str):
            raise TypeError(f"<value> should be {str}, {type(value)} given.")

        if not value.startswith(("http", "https")):
            raise ValueError(
                f"<value> is missing the scheme (http/https), {value} given."
            )

        self._url_base = value.rstrip("/")

    def set_url_base(self, value: str) -> "CollectionQueryTool":
        """
        Sets the base of the URL to work with.

        :parma value:
            The value to set.
        """

        self.url_base = value

        return self

    @property
    def is_modern_api(self) -> bool:
        """
        Provides the value of the :code:`_is_modern_api` attribute.
        """

        return self._is_modern_api

    @is_modern_api.setter
    def is_modern_api(self, value: bool) -> None:
        """
        Sets the value of the :code:`_is_modern_api` attribute.

        :param value:
            The value to set.

        :raise TypeError:
            When the given :code:`value` is not a :py:class:`bool`.
        """

        if not isinstance(value, bool):
            raise TypeError(f"<value> should be {bool}, {type(value)} given.")

        self._is_modern_api = value

    def set_is_modern_api(self, value: bool) -> "CollectionQueryTool":
        """
        Sets the value of the :code:`_is_modern_api` attribute.

        :param value:
            The value to set.
        """

        self.is_modern_api = value

        return self

    @property
    def timeout(self) -> float:
        """
        Provides the value of the :code:`_timeout` attribute.
        """

        return self._timeout

    @timeout.setter
    def timeout(self, value: float) -> None:
        """
        Sets the value of the :code:`_timeout` attribute.

        :param value:
            The value to set.

        :raise TypeError:
            When the given :code:`value` is not a :py:class:`float`.
        """

        if not isinstance(value, (int, float)):
            raise TypeError(f"<value> should be {float}, {type(value)} given.")

        self._timeout = value

    def set_timeout(self, value: float) -> "CollectionQueryTool":
        """
        Sets the value of the :code:`_timeout` attribute.

        :param value:
            The value to set.
        """

        self.timeout = value

        return self

    def guess_and_set_url_base(self) -> "CollectionQueryTool":
        """
        Try to guess the URL base to work with.
        """

        if PyFunceble.facility.ConfigLoader.is_already_loaded():
            if isinstance(PyFunceble.storage.CONFIGURATION.collection.url_base, str):
                self.url_base = PyFunceble.storage.CONFIGURATION.collection.url_base
            else:
                self.url_base = self.STD_URL_BASE
        elif EnvironmentVariableHelper("PYFUNCEBLE_COLLECTION_API_URL").exists():
            self.url_base = EnvironmentVariableHelper(
                "PYFUNCEBLE_COLLECTION_API_URL"
            ).get_value()
        else:
            self.url_base = self.STD_URL_BASE

        return self

    def guess_and_set_is_modern_api(self) -> "CollectionQueryTool":
        """
        Try to guess if we are working with a legacy version.
        """

        if self.token:
            try:
                response = self.session.get(
                    f"{self.url_base}/v1/stats/subject",
                    timeout=self.timeout,
                )

                response.raise_for_status()

                self.is_modern_api = False
            except (requests.RequestException, json.decoder.JSONDecodeError):
                self.is_modern_api = True
        else:
            self.is_modern_api = False

        return self

    @property
    def preferred_status_origin(self) -> Optional[str]:
        """
        Provides the value of the :code:`_preferred_status_origin` attribute.
        """

        return self._preferred_status_origin

    @preferred_status_origin.setter
    def preferred_status_origin(self, value: str) -> None:
        """
        Sets the preferred status origin.

        :param value:
            The value to set.

        :raise TypeError:
            When the given :code:`value` is not a :py:class:`str`.

        :raise ValueError:
            When the given :code:`value` is not supported.
        """

        if not isinstance(value, str):
            raise TypeError(f"<value> should be {str}, {type(value)} given.")

        if value not in self.SUPPORTED_STATUS_ORIGIN:
            raise ValueError(f"<value> ({value}) is not supported.")

        self._preferred_status_origin = value

    def set_preferred_status_origin(self, value: str) -> "CollectionQueryTool":
        """
        Sets the preferred status origin.

        :parma value:
            The value to set.
        """

        self.preferred_status_origin = value

        return self

    def guess_and_set_preferred_status_origin(self) -> "CollectionQueryTool":
        """
        Try to guess the preferred status origin.
        """

        if PyFunceble.facility.ConfigLoader.is_already_loaded():
            if isinstance(
                PyFunceble.storage.CONFIGURATION.collection.preferred_status_origin, str
            ):
                self.preferred_status_origin = (
                    PyFunceble.storage.CONFIGURATION.collection.preferred_status_origin
                )
            else:
                self.preferred_status_origin = self.STD_PREFERRED_STATUS_ORIGIN
        else:
            self.preferred_status_origin = self.STD_PREFERRED_STATUS_ORIGIN

        return self

    def guess_and_set_timeout(self) -> "CollectionQueryTool":
        """
        Try to guess the timeout to use.
        """

        if PyFunceble.facility.ConfigLoader.is_already_loaded():
            self.timeout = PyFunceble.storage.CONFIGURATION.lookup.timeout
        else:
            self.timeout = self.STD_TIMEOUT

        return self

    def ensure_is_modern_api_is_set(func):  # pylint: disable=no-self-argument
        """
        Ensures that the :code:`is_modern_api` attribute is set before running
        the decorated method.
        """

        def wrapper(self, *args, **kwargs):
            if self.is_modern_api is None:
                self.guess_and_set_is_modern_api()

            return func(self, *args, **kwargs)  # pylint: disable=not-callable

        return wrapper

    @ensure_is_modern_api_is_set
    def pull(self, subject: str) -> Optional[dict]:
        """
        Pulls all data related to the subject or :py:class:`None`

        :param subject:
            The subject to search for.

        :raise TypeError:
            When the given :code:`subject` is not a :py:class:`str`.

        :return:
            The response of the search.
        """

        PyFunceble.facility.Logger.info("Starting to search subject: %r", subject)

        if not isinstance(subject, str):
            raise TypeError(f"<subject> should be {str}, {type(subject)} given.")

        if self.is_modern_api:
            if self.token:
                url = f"{self.url_base}/v1/aggregation/subject/search"
            else:
                url = f"{self.url_base}/v1/hub/aggregation/subject/search"
        else:
            url = f"{self.url_base}/v1/subject/search"

        try:
            response = self.session.post(
                url,
                json={"subject": subject},
                timeout=self.timeout,
            )

            response_json = response.json()

            if response.status_code == 200:
                PyFunceble.facility.Logger.debug(
                    "Successfully search subject: %r. Response: %r",
                    subject,
                    response_json,
                )

                PyFunceble.facility.Logger.info(
                    "Finished to search subject: %r", subject
                )

                return response_json
        except (requests.RequestException, json.decoder.JSONDecodeError):
            response_json = {}

        PyFunceble.facility.Logger.debug(
            "Failed to search subject: %r. Response: %r", subject, response_json
        )
        PyFunceble.facility.Logger.info("Finished to search subject: %r", subject)

        return None

    @ensure_is_modern_api_is_set
    def push(
        self,
        checker_status: Union[
            AvailabilityCheckerStatus, SyntaxCheckerStatus, ReputationCheckerStatus
        ],
    ) -> Optional[dict]:
        """
        Push the given status to the collection.

        :param checker_status:
            The status to push.

        :raise TypeError:
            - When the given :code:`checker_status` is not a
              :py:class:`AvailabilityCheckerStatus`,
              :py:class:`SyntaxCheckerStatus` or
              :py:class:`ReputationCheckerStatus`.

            - When the given :code:`checker_status.subject` is not a
              :py:class:`str`.

        :raise ValueError:
            When the given :code:`checker_status.subject` is empty.
        """

        if not isinstance(
            checker_status,
            (AvailabilityCheckerStatus, SyntaxCheckerStatus, ReputationCheckerStatus),
        ):
            raise TypeError(
                f"<checker_status> should be {AvailabilityCheckerStatus}, "
                f"{SyntaxCheckerStatus} or {ReputationCheckerStatus}, "
                f"{type(checker_status)} given."
            )

        if not isinstance(checker_status.subject, str):
            raise TypeError(
                f"<checker_status.subject> should be {str}, "
                f"{type(checker_status.subject)} given."
            )

        if not isinstance(checker_status.checker_type, str):
            raise TypeError(
                f"<checker_status_checker_type> should be {str}, "
                f"{type(checker_status.subject)} given."
            )

        if checker_status.subject == "":
            raise ValueError("<checker_status.subject> cannot be empty.")

        if (
            not self.is_modern_api
            and hasattr(checker_status, "expiration_date")
            and checker_status.expiration_date
        ):
            self.__push_whois(checker_status)

        data = self.__push_status(
            checker_status.checker_type.lower(), checker_status.to_json()
        )

        return data

    def guess_all_settings(
        self,
    ) -> "CollectionQueryTool":  # pragma: no cover ## Underlying tested
        """
        Try to guess all settings.
        """

        to_ignore = ["guess_all_settings"]

        for method in dir(self):
            if method in to_ignore or not method.startswith("guess_"):
                continue

            getattr(self, method)()

        return self

    def __push_status(
        self, checker_type: str, data: Union[dict, str]
    ) -> Optional[dict]:
        """
        Submits the given status to the collection.

        :param checker_type:
            The type of the checker.
        :param data:
            The data to submit.

        :raise TypeError:
            - When :code:`checker_type` is not a :py:class:`str`.

            - When :code:`data` is not a :py:class:`dict`.

        :raise ValueError:
            When the given :code:`checker_type` is not a subject checker type.
        """

        if not self.token:
            return None

        if checker_type not in self.SUPPORTED_CHECKERS:
            raise ValueError(f"<checker_type> ({checker_type}) is not supported.")

        PyFunceble.facility.Logger.info("Starting to submit status: %r", data)

        if self.is_modern_api:
            if not self.token:
                url = f"{self.url_base}/v1/hub/status/{checker_type}"
            else:
                url = f"{self.url_base}/v1/contracts/self-delivery"
        else:
            url = f"{self.url_base}/v1/status/{checker_type}"

        try:
            if isinstance(data, dict):
                response = self.session.post(
                    url,
                    json=data,
                    timeout=self.timeout,
                )
            elif isinstance(
                data,
                (
                    AvailabilityCheckerStatus,
                    SyntaxCheckerStatus,
                    ReputationCheckerStatus,
                ),
            ):
                response = self.session.post(
                    url,
                    json=data.to_dict(),
                    timeout=self.timeout,
                )
            else:
                response = self.session.post(
                    url,
                    data=data,
                    timeout=self.timeout,
                )

            response_json = response.json()

            if response.status_code == 200:
                PyFunceble.facility.Logger.debug(
                    "Successfully submitted data: %r to %s", data, url
                )

                PyFunceble.facility.Logger.info("Finished to submit status: %r", data)
                return response_json
        except (requests.RequestException, json.decoder.JSONDecodeError):
            response_json = {}

        PyFunceble.facility.Logger.debug(
            "Failed to submit data: %r to %s. Response: %r", data, url, response_json
        )

        PyFunceble.facility.Logger.info("Finished to submit status: %r", data)

        return None

    def __push_whois(self, data: dict) -> Optional[dict]:
        """
        Submits the given WHOIS data into the given subject.

        :param checker_type:
            The type of the checker.
        :param data:
            The data to submit.

        :raise TypeError:
            - When :code:`checker_type` is not a :py:class:`str`.

            - When :code:`data` is not a :py:class:`dict`.

        :raise ValueError:
            When the given :code:`checker_type` is not a subject checker type.
        """

        if not self.token:
            return None

        if isinstance(
            data,
            (AvailabilityCheckerStatus, SyntaxCheckerStatus, ReputationCheckerStatus),
        ):
            data = data.to_dict()

        if not isinstance(data, dict):  # pragma: no cover ## Should never happen
            raise TypeError(f"<data> should be {dict}, {type(data)} given.")

        PyFunceble.facility.Logger.info("Starting to submit WHOIS: %r", data)

        url = f"{self.url_base}/v1/status/whois"

        try:
            response = self.session.post(
                url,
                json=data,
                timeout=self.timeout,
            )

            response_json = response.json()

            if response.status_code == 200:
                PyFunceble.facility.Logger.debug(
                    "Successfully submitted WHOIS data: %r to %s", data, url
                )

                PyFunceble.facility.Logger.info("Finished to submit WHOIS: %r", data)
                return response_json
        except (requests.RequestException, json.decoder.JSONDecodeError):
            response_json = {}

        PyFunceble.facility.Logger.debug(
            "Failed to WHOIS data: %r to %s. Response: %r", data, url, response_json
        )

        PyFunceble.facility.Logger.info("Finished to submit WHOIS: %r", data)
        return None
