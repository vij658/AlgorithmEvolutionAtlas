"""Era 2 of the book: the topics in order, with the short labels used on time lines and era maps."""
ERA = dict(
    num=2,
    folder="era-02-algorithms-travel",
    title="Algorithms Travel",
    span="c. 200 BCE to 1424 CE",
    lede="In the first era, procedures were invented in a few places. In this one they travel: from China and India to "
         "Baghdad, and from Baghdad to Pisa. Along the way they gain a sign for nothing, a name, and the first infinite series.",
    intro="Eleven steps, from columns of rods on a Chinese counting board to π computed to sixteen decimal places in "
          "Samarkand. The procedures cross languages and number systems, and several are found twice, centuries apart.",
)

# (number, slug, page title, date, time-line label, module, Java class)
TOPICS = [
    (1, "fangcheng", "Elimination on the Counting Board", "c. 200 BCE – 263 CE", "Fangcheng: elimination on the board", "e2_01_fangcheng", "FangCheng"),
    (2, "ptolemys-chords", "Ptolemy's Table of Chords", "c. 150 CE", "Ptolemy's table of chords", "e2_02_chords", "PtolemyChords"),
    (3, "chinese-remainder-problem", "The Chinese Remainder Problem", "3rd–5th century CE", "Sunzi's remainder problem", "e2_03_remainders", "ChineseRemainder"),
    (4, "zero-becomes-a-number", "Zero Becomes a Number", "628 CE", "Brahmagupta's rules for zero", "e2_04_zero", "ZeroAsANumber"),
    (5, "chakravala", "The Chakravala and Pell's Equation", "628–1150 CE", "The chakravala", "e2_05_chakravala", "Chakravala"),
    (6, "algorism-and-al-jabr", "Algorism and Al-Jabr", "c. 820–830 CE", "al-Khwarizmi's written procedures", "e2_06_aljabr", "AlKhwarizmi"),
    (7, "frequency-analysis", "Frequency Analysis", "9th century CE", "al-Kindi's frequency analysis", "e2_07_frequency", "FrequencyAnalysis"),
    (8, "liber-abaci", "Fibonacci's Liber Abaci", "1202 CE", "Liber Abaci", "e2_08_liber_abaci", "LiberAbaci"),
    (9, "qin-jiushao", "Horner's Method, Nearly Six Centuries Early", "1247 CE", "Qin Jiushao's root method", "e2_09_qin", "QinJiushao"),
    (10, "madhava-series", "Madhava's Series for Pi", "c. 1400 CE", "Madhava's series for π", "e2_10_madhava", "MadhavaSeries"),
    (11, "al-kashi-pi", "Al-Kashi's Pi", "1424 CE", "al-Kashi's π", "e2_11_alkashi", "AlKashiPi"),
]


# The era map: where each topic's box sits, and which older idea each development reuses.
# An arrow is a link between ideas, not a claim that one culture learned it from another.
_C = [30, 395, 760]
MAP = dict(
    w=1000, h=660, bw=210, bh=76,
    at={1: (_C[0], 20), 3: (_C[1], 20), 2: (_C[2], 20),
        4: (_C[1], 200), 6: (_C[2], 200),
        9: (_C[0], 380), 5: (_C[1], 380), 8: (_C[2], 380),
        10: (_C[0], 560), 7: (_C[1], 560), 11: (_C[2], 560)},
    color={4: "red"},
    edges=[
        (1, 9, "⊕ the counting board", dict(ports=("bottom", "top"), dx=8, anchor="start")),
        (3, 9, "⊕ the Da Yan rule", dict(ports=("bottom:0.2", "top:0.8"), at=0.3, dx=6, dy=-2)),
        (4, 6, "⊕ a digit for nothing", dict(ports=("right", "left"), dy=-10)),
        (4, 5, "⊕ rules for negatives", dict(ports=("bottom", "top"), dx=8, anchor="start")),
        (6, 8, "⊕ column arithmetic", dict(ports=("bottom", "top"), dx=-8, anchor="end")),
        (6, 7, "both in Baghdad", dict(ports=("bottom:0.2", "top:0.8"), dashed=True, at=0.5)),
    ],
    caption="An arrow means the later development reuses the earlier idea. It does not claim one culture learned it "
            "from another; where a borrowing is documented, the topic page says so. The dashed line joins two "
            "developments that shared a city, not a procedure. Boxes without arrows build on Era 1: Ptolemy on "
            "Babylonian tables, Madhava and al-Kashi on Archimedes.",
)


def timeline_events():
    return [(t[3], t[4]) for t in TOPICS]
