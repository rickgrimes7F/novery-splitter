import json
import asyncio
import httpx
import random

CONCURRENCY = 30
TIMEOUT = 10


def parse_cookie(cookie_field):
    cookie_field = (cookie_field or "").strip()

    if not cookie_field:
        return ""

    try:
        obj = json.loads(cookie_field)
        if isinstance(obj, dict):
            return "; ".join(f"{k}={v}" for k, v in obj.items())
    except:
        pass

    return cookie_field


async def check_uid(uid, cookie, original_line, client, sem):
    headers = {}

    if cookie:
        headers["Cookie"] = cookie

    async with sem:
        await asyncio.sleep(random.uniform(0, 0.04))

        try:
            r = await client.get(
                "https://www.facebook.com/",
                headers=headers,
                timeout=TIMEOUT,
                follow_redirects=True
            )

            final_url = str(r.url).lower()

            if "confirmemail.php" in final_url:
                return {
                    "uid": uid,
                    "status": "nv",
                    "line": original_line
                }

            else:
                return {
                    "uid": uid,
                    "status": "ok",
                    "line": original_line
                }

        except:
            return {
                "uid": uid,
                "status": "error",
                "line": original_line
            }


async def run_checker(lines):
    sem = asyncio.Semaphore(CONCURRENCY)

    entries = []

    for line in lines:
        parts = line.split("|", 2)

        if len(parts) >= 3:
            uid, pw, cookies = parts
        elif len(parts) == 2:
            uid, cookies = parts
        else:
            continue

        cookie = parse_cookie(cookies)
        entries.append((uid, cookie, line))

    async with httpx.AsyncClient() as client:
        tasks = [
            check_uid(uid, cookie, line, client, sem)
            for uid, cookie, line in entries
        ]

        return await asyncio.gather(*tasks)


def handler(request):
    body = json.loads(request["body"])

    raw_data = body.get("data", "")
    lines = [
        x.strip()
        for x in raw_data.split("\n")
        if x.strip()
    ]

    results = asyncio.run(run_checker(lines))

    return {
        "statusCode": 200,
        "body": json.dumps(results)
    }
