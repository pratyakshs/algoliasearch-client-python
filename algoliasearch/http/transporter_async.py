import asyncio

from typing import Generator

from algoliasearch.exceptions import (
    RequestException,
    AlgoliaUnreachableHostException
)
from algoliasearch.http.hosts import HostsCollection
from algoliasearch.http.transporter import (
    Transporter, RetryOutcome, Request, Response)


class TransporterAsync(Transporter):

    @asyncio.coroutine  # type: ignore
    def retry(self, hosts, request, relative_url):  # type: ignore
        # type: (HostsCollection, Request, str) -> dict

        for host in hosts.reset():

            request.url = 'https://%s/%s' % (
                host.url, relative_url)

            response = yield from self._requester.send(request)  # type: ignore

            decision = self._retry_strategy.decide(host, response)

            if decision == RetryOutcome.SUCCESS:
                return response.content if response.content is not None else {}
            elif decision == RetryOutcome.FAIL:
                content = response.error_message
                if response.content and 'message' in response.content:
                    content = response.content['message']

                raise RequestException(content, response.status_code)

        raise AlgoliaUnreachableHostException('Unreachable hosts')
