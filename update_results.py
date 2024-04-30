import json
import asyncio
import aiohttp
import os
import urllib
import platform

async def get_poll_result(folder, post_id, poll_data, session, headers):
    result_url = f"https://www.tumblr.com/api/v2/polls/ao3topshipsbracket/{post_id}/{poll_data['client_id']}/results"
    async with session.get(result_url, headers = headers) as response:
        poll_result = await response.json()
    assert poll_result["meta"]["status"] == 200
    answers = poll_data["answers"]
    answers.sort(key = lambda x: x["client_id"]) # important for ensuring consistent order so we can csv
    #print(poll_result["response"])
    for answer in answers:
        answer["votes"] = poll_result["response"]["results"][answer["client_id"]]
        del answer["client_id"]
    if (poll_data["end_timestamp"] < poll_result["response"]["timestamp"]):
        with open(os.path.join(folder, f"{post_id}_final.json"), "w") as f:
            f.write(json.dumps(answers))
    with open(os.path.join(folder, f"{post_id}_latest.json"), "w") as f:
        f.write(json.dumps(answers))
    all_path = os.path.join(folder, f"{post_id}_all.csv")
    if not os.path.exists(all_path):
        with open(all_path, "w") as f:
            labels = ["time"] + [answer["answer_text"] for answer in answers]
            f.write(",".join(labels) + "\n")
    with open(all_path, "a") as f:
        values = [str(poll_result["response"]["timestamp"])] + [str(answer["votes"]) for answer in answers]
        f.write(",".join(values) + "\n")

    #poll_data["result"] = poll_result["response"]


async def main():
    folder = "polls/tumblrtopships/data"
    with open(os.path.join(folder, "polls.json"), "r") as f:
        raw_data = f.read()
    polls = json.loads(raw_data)
    headers = {"User-Agent" : "	Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0"}
    async with aiohttp.ClientSession() as session:
        await asyncio.gather( *(get_poll_result(folder, post_id, polls[post_id], session, headers) for post_id in polls if polls[post_id]["active"]) )
    return



if platform.system()=='Windows': # thank you https://stackoverflow.com/questions/45600579/asyncio-event-loop-is-closed-when-getting-loop
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())
