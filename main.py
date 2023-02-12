#!/usr/bin/env python3
"""Example for aiohttp.web basic server."""

import textwrap

from aiohttp import web

def crc16(data):
        crc = 0xFFFF
        l = len(data)
        i = 0
        while i < l:
            j = 0
            crc = crc ^ data[i]
            while j < 8:
                if (crc & 0x1):
                    mask = 0xA001
                else:
                    mask = 0x00
                crc = ((crc >> 1) & 0x7FFF) ^ mask
                j += 1
            i += 1
        if crc < 0:
            crc -= 256
        result = data + chr(crc % 256).encode('latin-1') + chr(crc // 256).encode('latin-1')
        return result


async def intro(request: web.Request) -> web.StreamResponse:
    txt = textwrap.dedent(
        """\
        Type {url}/hello/John  {url}/simple or {url}/change_body
        in browser url bar
    """
    ).format(url="127.0.0.1:8088")
    binary = txt.encode("utf8")
    resp = web.StreamResponse()
    resp.content_length = len(binary)
    resp.content_type = "text/plain"
    resp = web.StreamResponse()
    name = request.match_info.get("name")
    print(name)
    await resp.prepare(request)
    await resp.write(binary)
    return resp


async def simple(request: web.Request) -> web.StreamResponse:
    return web.Response(text="Simple answer")


async def change_body(request: web.Request) -> web.StreamResponse:
    resp = web.Response()
    resp.body = b"Body changed"
    resp.content_type = "text/plain"
    return resp


async def hello(request: web.Request) -> web.StreamResponse:
    resp = web.StreamResponse()
    name = request.match_info.get("name", "Anonymous")
    answer = ("recieved" + name).encode("utf8")
    resp.content_length = len(answer)
    resp.content_type = "text/plain"
    print("state=",name)
    await resp.prepare(request)
    await resp.write(answer)
    await resp.write_eof()
    return resp

async def input(request: web.Request) -> web.StreamResponse:
    resp = web.StreamResponse()
    name = request.match_info.get("name")
    b = str.encode(name)
    crc = crc16(b)
    answer = ("recieved " + name + " " + str(crc)).encode("utf8")
    resp.content_length = len(answer)
    resp.content_type = "text/plain"
    print("state=", name, str(crc))
    await resp.prepare(request)
    await resp.write(answer)
    await resp.write_eof()
    return resp

async def output(request: web.Request) -> web.StreamResponse:
    resp = web.StreamResponse()
    name = request.match_info.get("name")
    b = str.encode(name)
    crc = crc16(b)
    string = name
    a = string.split(',')
    # print(a)
    lena = len(a)
    for i in range(lena):
        e = a[1 - i].split(':')
        print(e)
    d = a[1].split(':')
    answer = (d[1]).encode("utf8")
    resp.content_length = len(answer)
    resp.content_type = "text/plain"
    # print("state=", name, str(crc))
    await resp.prepare(request)
    await resp.write(answer)
    await resp.write_eof()
    return resp


def init() -> web.Application:
    app = web.Application()
    app.router.add_get("/", intro)
    app.router.add_get("/simple", simple)
    app.router.add_get("/change_body", change_body)
    app.router.add_get("/input/{name}", input)
    app.router.add_get("/input", output)
    app.router.add_get("/output/{name}", output)
    app.router.add_get("/output", output)
    return app


web.run_app(init())
