import json
import asyncio
import aiohttp
import os
import urllib
import time

def extract_poll_data(post):
    result = {}
    #result["post_id"] = post["id_string"]
    for block in post["content"]:
        if block["type"] == "poll":
            result["question"] = block["question"]
            result["client_id"] = block["client_id"]
            result["answers"] = block["answers"]
            result["start_timestamp"] = block["timestamp"]
            result["end_timestamp"] = block["settings"]["expire_after"] + block["timestamp"]
            result["active"] = (not os.path.exists(f"sexyman-poll/data/{post['id_string']}_final.json")) and result["end_timestamp"] + 3600 > time.time()
            return result

async def get_poll_posts():
    url = "https://www.tumblr.com/api/v2/blog/mcytblrsexymen/posts?api_key=[insert your own API key here]&npf=true&tag=Actual%20Polls&limit=50"
    headers = {"User-Agent" : "	Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers = headers) as response:
            posts_content = await response.json()
        assert posts_content["meta"]["status"] == 200
        polls = {post["id_string"] : extract_poll_data(post) for post in posts_content["response"]["posts"] if extract_poll_data(post) != None}
    return polls


def main():
    # i still don't know why asyncio.run doesn't work
    results = asyncio.get_event_loop().run_until_complete(get_poll_posts())
    filename = "sexyman-poll/data/polls.json"
    if os.path.exists(filename):
        with open(filename, "r") as f:
            old_data = json.loads(f.read())
            for post_id in old_data:
                if post_id not in results:
                    results[post_id] = old_data[post_id]
    with open(filename, "w") as f:
        f.write(json.dumps(results))
    return


main()