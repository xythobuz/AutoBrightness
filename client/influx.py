#!/usr/bin/env python

import aiohttp
import asyncio

influx_host = 'http://INFLUX_DB_IP_HERE:8086'
influx_path = '/write?db=INFLUX_DB_NAME_HERE'

cache = {}

async def async_write(id_tags, name, value):
    data = id_tags + " " + name + "=" + str(float(value))
    async with aiohttp.ClientSession(influx_host) as session:
        await session.post(influx_path, data=data)

def write(id_tags, name, value):
    asyncio.run(async_write(id_tags, name, value))
