#!/usr/bin/env python
import async_timeout
import random
import os
import arrow

from urllib.parse import urlparse

from owllook.config import USER_AGENT, LOGGER, TIMEZONE, PROXY


def use_proxy(retries=3, proxy=None, **kwargs):
    """
    In some cases you need to use a proxy to access the site
    
    The function to be decorated must support the ``proxy`` parameter
        such as:
            @use_proxy
            def fun(proxy=None):
                pass
    
    :param retries: Number of failed visits to retry. Default is 3.
    :param proxy: proxy setting .if not set. Default is PROXY which is setting in config
    """
    proxy_kwargs = kwargs

    def proxy_decorator(func):
        async def wrapper(*args, **kwargs):
            retry_count = 0
            result = None
            while retry_count < retries and not result:
                proxy_ = proxy or PROXY
                if proxy_:
                    kwargs.update({'proxy': proxy_})
                result = await func(*args, **kwargs)
            return result
        return wrapper

    return proxy_decorator


def get_data(filename, default='') -> list:
    """
    Get data from a file
    :param filename: filename
    :param default: default value
    :return: data
    """
    root_folder = os.path.dirname(os.path.dirname(__file__))
    user_agents_file = os.path.join(
        os.path.join(root_folder, 'data'), filename)
    try:
        with open(user_agents_file) as fp:
            data = [_.strip() for _ in fp.readlines()]
    except:
        data = [default]
    return data


def get_random_user_agent() -> str:
    """
    Get a random user agent string.
    :return: Random user agent string.
    """
    return random.choice(get_data('user_agents.txt', USER_AGENT))


def get_time() -> str:
    utc = arrow.utcnow()
    local = utc.to(TIMEZONE)
    time = local.format("YYYY-MM-DD HH:mm:ss")
    return time


def get_netloc(url):
    """
    获取netloc
    :param url: 
    :return:  netloc
    """
    netloc = urlparse(url).netloc
    return netloc or None


@use_proxy
async def target_fetch(client, url, proxy=None):
    """
    :param proxy: proxy setting
    :param client: aiohttp client
    :param url: targer url
    :return: text
    """
    with async_timeout.timeout(20):
        try:
            headers = {'user-agent': get_random_user_agent()}
            async with client.get(url, headers=headers, proxy=proxy) as response:
                assert response.status == 200
                LOGGER.info('Task url: {}'.format(response.url))
                try:
                    text = await response.text()
                except:
                    text = await response.read()
                return text
        except Exception as e:
            LOGGER.exception(e)
            return None
