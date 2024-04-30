import json
import os
import csv
from datetime import datetime
from dateutil import tz
import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot as plt

plt.rcParams.update({'font.size': 14})

def make_plot(poll_id, poll, is_thumbnail, timezone):
    with open(f"polls/tumblrtopships/data/{poll_id}_all.csv") as f:
        reader = csv.reader(f)
        titles = reader.__next__()
        data_as_rows = [[int(x) for x in row] for row in reader]
        data = list(zip(*data_as_rows))
        time = [datetime.fromtimestamp(x, tz = timezone) for x in data[0]]
        data = data[1:]

    plot_colors = ["#c5ff21", "#0054c8"]
    if len(data) > 2:
        plot_colors = ["#f00", "#f90", "#ff0", "#9f0", "#0f0", "#0f9", "#0ff", "#09f", "#00f", "#90f", "#f0f", "#f09"]
        plot_colors += ["#999"] * (len(data) - len(plot_colors))

    bg_color = "#000" if is_thumbnail else "#fff"
    grid_color = "#999"
    grid_bold_color = "#fff" if is_thumbnail else "#000"
    plot_size = (6,4) if is_thumbnail else (12,8)
    
    fig, ax = plt.subplots(facecolor=bg_color, figsize=plot_size)

    for votes, color, title in zip(data, plot_colors, titles[1:]):
        line, = ax.plot(time, votes, color, linewidth=3)
        line.set_label(title)

    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M\n%b %d", tz = timezone))

    ax.legend(labelcolor = grid_bold_color, facecolor = bg_color, edgecolor = grid_color) # the box that labels the lines

    if is_thumbnail:
        #plt.subplots_adjust(bottom=.15) # default is .125, but we need a smidge more room for linebreak-containing x labels
        plt.tick_params(labelbottom = False) # changed my mind i'm removing the x labels now
    else:
        plt.xlabel("Time (UTC)")
        plt.ylabel("Number of votes")

    ax.set_facecolor(bg_color)
    ax.grid(True, color = grid_color)
    ax.tick_params(color = grid_color, labelcolor = grid_bold_color)

    plt.xlim(left = datetime.fromtimestamp(poll["start_timestamp"], tz = timezone))
    if not poll["active"]:
        plt.xlim(right = datetime.fromtimestamp(poll["end_timestamp"], tz = timezone))
    plt.ylim(bottom = 0)

    for spine in ax.spines.values():
        spine.set_color(grid_bold_color)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    if is_thumbnail:
        plt.savefig(f"polls/tumblrtopships/plots/{poll_id}_preview.png", bbox_inches = "tight")
    else:
        plt.savefig(f"polls/tumblrtopships/plots/{poll_id}.png")
    plt.close()


with open("polls/tumblrtopships/data/polls.json", "r") as f:
    raw_data = f.read()
polls = json.loads(raw_data)

timezone = tz.UTC # to get a timezone by name, do e.g. tz.gettz("America/New_York")
for poll_id, poll in polls.items():
    try:
        if poll["seconds_since_end"] < 1800: # 30 mins should be a safe margin, since we're running this every 15 mins
            make_plot(poll_id, poll, True, timezone)
            make_plot(poll_id, poll, False, timezone)
    except FileNotFoundError:
        pass

print("Script executed")