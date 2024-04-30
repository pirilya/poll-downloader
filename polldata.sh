#source ../protected/cgi-env/bin/activate
#pip install asyncio
#pip install aiohttp

while :; do
    python3 ../protected/update_masterlist.py
    for i in {1..10}
    do
        python3 ../protected/update_results.py
        sleep 60 # sleep 60 seconds, ie a minute
    done
done