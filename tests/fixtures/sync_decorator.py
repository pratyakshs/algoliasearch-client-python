import asyncio

from algoliasearch.iterators import Iterator


class SyncDecorator(object):
    @property
    def name(self):
        return self.__base.name

    def __init__(self, base):
        self.__base = base

    def __getattr__(self, name):
        method = getattr(self.__base, name)
        if str(type(method)) != "<class 'method'>" and str(
                type(method)) != "<class 'function'>":
            return method

        method = getattr(self.__base, name + '_async')

        def closure(*args, **kwargs):
            result = method(*args, **kwargs)

            if str(type(result)) == "<class 'generator'>":
                return asyncio.get_event_loop().run_until_complete(
                    asyncio.gather(result))[0]

            if isinstance(result, Iterator):
                return self.iterator_to_array(result)

            return result

        return closure

    def init_index(self, name):
        return SyncDecorator(self.__base.init_index(name))

    def user(self, user_token):
        return SyncDecorator(self.__base.user(user_token))

    def iterator_to_array(self, iterator):
        async def closure():
            return [obj async for obj in iterator]

        return asyncio.get_event_loop().run_until_complete(closure())
