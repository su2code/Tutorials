#!/usr/bin/env python3

"""Plot the pressure history and acoustic spectrum for the tutorial."""

import csv
import json
import os

os.environ.setdefault("MPLCONFIGDIR", ".matplotlib")

import matplotlib.pyplot as plt


def read_csv_columns(filename):
    with open(filename, newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file, skipinitialspace=True)
        original_fields = reader.fieldnames
        clean_fields = [field.strip().strip('"') for field in original_fields]
        columns = {field: [] for field in clean_fields}

        for row in reader:
            for original, clean in zip(original_fields, clean_fields):
                columns[clean].append(float(row[original]))

    return columns


def style_axes(ax):
    ax.grid(True, color="#d0d0d0", linewidth=0.7, alpha=0.7)
    ax.tick_params(direction="in", length=4, width=1.0, colors="#1a1a1a")
    for spine in ax.spines.values():
        spine.set_color("#1a1a1a")
        spine.set_linewidth(1.0)


plt.rcParams.update(
    {
        "figure.figsize": (7.2, 4.6),
        "figure.dpi": 150,
        "savefig.dpi": 200,
        "font.size": 11,
        "axes.labelsize": 12,
        "axes.titlesize": 12,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "axes.linewidth": 1.0,
        "lines.linewidth": 1.5,
    }
)

history = read_csv_columns("history_aeroacoustics.csv")
spectrum = read_csv_columns("acoustic_spectrum.csv")

with open("acoustic_summary.json", encoding="utf-8") as summary_file:
    summary = json.load(summary_file)

metrics = summary["signals"]["mic1"]
dominant_frequency = metrics["dominant_frequency_hz"]
oaspl = metrics["oaspl_db"]
red = "#b2182b"

fig, ax = plt.subplots()
ax.plot(history["Cur_Time"], history["mic1"], color=red)
ax.set_xlabel("Time [s]")
ax.set_ylabel("Pressure [Pa]")
ax.set_title("Pressure probe history")
style_axes(ax)
fig.tight_layout()
fig.savefig("pressure_history.png", bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots()
ax.semilogx(spectrum["Frequency_Hz"], spectrum["mic1_SPL_dB"], color=red)
ax.axvline(
    dominant_frequency,
    color="#1a1a1a",
    linestyle="--",
    linewidth=1.1,
    label="Dominant frequency = {:.4g} Hz".format(dominant_frequency),
)
ax.set_xlabel("Frequency [Hz]")
ax.set_ylabel("Narrowband SPL [dB]")
ax.set_title("Pressure spectrum, OASPL = {:.2f} dB".format(oaspl))
style_axes(ax)
ax.grid(True, which="both", color="#d0d0d0", linewidth=0.7, alpha=0.7)
ax.legend(frameon=False, loc="upper right")
fig.tight_layout()
fig.savefig("pressure_spectrum.png", bbox_inches="tight")
plt.close(fig)
