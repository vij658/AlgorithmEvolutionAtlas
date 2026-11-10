#!/usr/bin/env python3
"""Creates The Algorithm Evolution Atlas's watch-in-order playlists in your own YouTube account.

Run it once a day until it says it is finished. Google's free daily limit (10,000 units; each video added costs 50)
allows about 190 videos a day, so the 25 playlists take about 5 days. The script remembers where it stopped, in
atlas_progress.json beside it, and also checks what each playlist already holds, so running it twice never adds a
video twice.

Setup (once): see the steps in README-youtube-playlists.md, or in short:
  1. pip3 install google-api-python-client google-auth-oauthlib
  2. Put the OAuth file you downloaded from Google Cloud next to this script, named client_secret.json
  3. python3 make_youtube_playlists.py            (a browser window opens once to sign in)

Options:
  --dry-run            show what would be created, without signing in or changing anything
  --privacy unlisted   make the new playlists unlisted (default: private); "public" also works
"""
import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CLIENT = HERE / "client_secret.json"
TOKEN = HERE / "atlas_token.json"
PROGRESS = HERE / "atlas_progress.json"
SCOPES = ["https://www.googleapis.com/auth/youtube"]

# The 25 playlists, in book order: [number, title, topics covered, [video IDs in order]]
PLAYLISTS = [
    [1, "Chapter 1: Two numbers, one answer", "Adding two numbers", ["3qx5mzhOltM", "OOcclZ8ucrU", "4velJGSdqv0", "rV_Tt1qY1ZQ", "hwxyheQNXBU", "FiqgoORt6to", "GHKwjaKuXP8", "XO49TSyJF5s", "ZpB_IR7tl4g", "ecn-8iGDRSo", "hExfiB_UFzA"]],
    [2, "Era 1: The First Algorithms, part 1 of 2", "Tally Marks to The Square Root of Two", ["IT84fx5b9JY", "xU5gpR2NRIQ", "aNqUWLHofAg", "90e7pXCO-Gs", "aPZbXonPGHc", "_wHIk-_HJR8", "6-V-88jUjCg", "o1nB5sRFpVE", "gnNEDGkaauE", "X-iGv9a7tDs", "X0IDnXLYDl0", "KKL3v2Mb4Zw", "voTBCSL6UmA", "RR3zzQP3bII", "9Rtbe1ew91c", "Bw9BsMfTXpk", "iaSwsGX6-2k", "7Y6FVfOFaGA", "jsux7RzcIjw", "R9m2jck1f90", "58Z91hD5RXE", "BL6pGhnBdj8", "f4UoZSghQws", "mf5ynlcJOTg", "eyZ9DgKyXPQ", "dVOogx94Jao", "J5Ug3Cr8RUE", "BAoRwWflYbc", "NegYPgMAua4", "Us98ghhUu38", "pI76G2cKfj8", "00pdhwn7FYk", "MXveVqBxFow", "W3Np2cqiL0E", "v3vnxGEi07I", "th4kD2z98jQ", "Nr68x0su5co"]],
    [3, "Era 1: The First Algorithms, part 2 of 2", "Egyptian Doubling to The Sieve of Eratosthenes", ["KWMm_tkbMQ0", "qHXsKyVSPOU", "YWyyu8tV5OI", "2gBGi-sYFmQ", "lD0zUXLjS4Q", "xrUCL7tGKaI", "Ij2Q4487FHQ", "DuxgU8A6Cr4", "lYKB1S9sLTQ", "EHUgNLN8F1Y", "L-Wzglnm4dM", "SYRyKYmOJwM", "LzKMhPK0JF0", "SkUdjlQy3rk", "c-2I09cmth0", "MHcRxooUIUg", "uMBHkDiKLlI", "zfEr2ybuILY", "Adtx9h0Hcy0", "y1rVfa1nhjw", "4YfUrNoJ2pE", "yHwneN6zJmU", "5LhWIaWlprM", "H_2_nqKAZ5w", "cxZzTl_ZYLo", "HNOypQFpW3s", "VEQ30NKUZI0", "JAqr1hF9Rqs", "15tSavbsu2w", "k28N4735v4Q", "wNcFAQHJWAU", "iwjphFGZSEE", "_rJdkhlWZVQ", "gj-u8qXdmJA", "8lV37p29nR8", "lSU1RO33Gqs", "uXqSgMi-w1U", "0UwHcYaI-vc", "_Cq8HL3wgLw", "eyrUkjQYBlE", "P__PsS2J_y8", "V08g_lkKj6Q", "_BrrwbAnMbk", "Xxu95iiVcPI", "7CyBf-xZF4c", "fI6kv_GtKlM"]],
    [4, "Era 2: Algorithms Travel, part 1 of 2", "Elimination on the Counting Board to Algorism and Al-Jabr", ["AGB0EYROjac", "xIgwPqmt3NA", "eDb6iugi6Uk", "vhm1bPMAgyU", "pf8H2tc0alE", "-vh3j0aA5Gk", "HIFcftCSXO0", "W0LIrTZYPFE", "zGmIhevmDIQ", "llA6iW043XU", "xUpBBr5btvk", "1kXCGQIFbTA", "c4aVqLpYoPk", "U7bW1JKGezQ", "pzUOPxLmmbg", "TlzCEwGp4VM", "a9negsQP2qI", "CGhjhixDIKM", "M42uDLGRSpI", "MdePzlQtnCc", "8AZMsRH-Szw", "ffHHk_Yu9xw", "eu9ysTIsmoU", "kafREW2sX0M", "GV-M6dqCzAw", "D-oxsEknlIc", "A_e5jspsNsM", "o6vuZBc6qLk", "y6oS7zE71Dw", "UOisN20qV0c", "Ni0CHH2v5uQ", "vmETw2Iq5M4", "3ls3z-UzOSw", "9G8Rp2pFDuQ", "N8R5CiFIgK4", "WO6TLvHsytk", "oRkNaF0QvnI", "4C6ARwuRugI", "Q-UDR-A3iHQ", "oyhOlGsDXP8", "nJJ3O4qSHhM"]],
    [5, "Era 2: Algorithms Travel, part 2 of 2", "Frequency Analysis to Al-Kashi's Pi", ["l6jqKRXSShI", "fdKze86foTc", "tvZ5O3RJfCQ", "WSwO3qc4IQI", "gCWljzTavlo", "opqgXvGsk6U", "rte0RXI6wCk", "9x8HEECMfXM", "NDMgN2Vx2Ac", "nR7RibUjuGI", "mIL_XDR8gkw", "LuCNhWhwhy0", "SzL81tQ8T5c", "XiG_gNOyews", "by1l9rEdLi0", "feyaeq1Jcmk", "Z393AcN_Gz0", "RGrmEWj38bs", "3HepIVKLVUA", "E_G0rKE2O_k", "EOuGtGzqZHs", "ySLWP6K2s14", "3U7Hfz37GqA", "IlrxS8SQY8I", "MqtqY5-atuo", "ypxKzWi-Bwg", "lOpAVZUQGJ4", "QyyuAMi6vmk", "PxsEeB9Qg4Y", "BginHi3wGtc", "pflTgB0c_kY", "k8ktqz9KDWI", "VE0RmL9T5lA", "erFVGPqpRxQ", "ER0YaB8N-20", "HrRMnzANHHs", "r8YNb8yeXH8"]],
    [6, "Era 3: Tables and Machines, part 1 of 3", "Cardano's Cubic to The Problem of Points", ["NnTQGhZSmF4", "2t-Gv8RoXSM", "l0EaTehu7Ec", "h0OuDlZwZm8", "bW9FZIO2FZY", "X4I08Wfck3Q", "5nV2dXpKBgs", "cUzklzVXJwo", "VMRQMydiMyI", "kqVpPSzkTYA", "R1PSNQmJbmo", "P00OQmNxqr4", "NhZ9a6-3ig8", "lyieW-0S5n4", "9D3Rp3oiMVQ", "q6XlLiMC5F0", "3B6FymMv8b4", "bxV9n4Ohab0", "oYQdKbQ-sgM", "JUAU62-zYjU", "SeyMTzKYKqg", "3h71HAJWnVU", "5undFLMNohA", "4yAiRimEo0s", "OQMzstFo-sk", "SEeEAkpLUNk", "wjENvJyMfWg", "NJamYfjVRbA", "C_nV3cVNjog", "zDWr0683PzA", "W5XbuQq65Xc", "_YRfSe-f1FE", "3pRM4v0O29o", "IgNhFX2gHOc", "sunRpPcGwCo", "LurI8AYY18E", "hGtcSJMHaKs", "CBgCR1kHSUI", "Ir1jOc00570"]],
    [7, "Era 3: Tables and Machines, part 2 of 3", "Newton's Method to Least Squares, and the Lost Planet", ["4s-cGdk47xg", "qlNqPE_X4ME", "Cavm4RduP80", "-DpZOZTsdvg", "hO5q_g6HUnU", "wCJF_OMBWKY", "7RZn3B709wo", "MWD2A0Vg2V0", "vuL87WfRIQE", "sXxwr66Y79Y", "zDNaUi2cjv4", "LwR2qVJof14", "eIvBFbreqXY", "Jeb_J7xZf9A", "sJXTo3EZoxM", "fVq3F3uVqrY", "0skwFoGmS4Q", "nZwSo4vfw6c", "0XcCKf5xgSE", "eIb1cz06UwI", "5M-m62qTR-s", "Ax3VlsI0Npw", "xR4sGgwtR2I", "qZrfK2iE4UA", "eVyyb1OsX64", "-uuvswdhFYg", "P8hT5nDai6A", "S0ptaAXNxBU", "RdvKNJzUWyo", "lAYxDGt2PLM", "_w51fa96xQ4", "WCP98USBZ0w", "Zu-UlcfPPUk", "C0b7HL_7afs", "fYkD08R5Ymw"]],
    [8, "Era 3: Tables and Machines, part 3 of 3", "Gauss's Fast Fourier Transform to Hollerith's Tabulator", ["wmCIrpLBFds", "Uwzl3NLjG00", "mkGsMWi_j4Q", "QmgJmh2I3Fw", "nl9TZanwbBk", "nmgFG7PUHfo", "SK2XpvwU038", "QspORv1Ox2w", "50HKEjb9Gak", "ORH3TwgvJgI", "BlbQsKpq3Ak", "6JLXHvAKA3w", "juWOWzkpw5o", "_o3uejzyILY", "be1EM3gQkAY", "lLOAuYv87uU", "0EfE1ITDZ6E", "J7ITqnEmf-g", "5rtKoKFGFSM", "_fyUtU6LVNY", "mNZZtHsYiBo", "_JVwyW4zxQ4", "11PAUUOkZHQ", "_COKT-0JiOg", "RMe69AdlFdI", "4l8rq6imQAo", "AXtJLgzW3sQ", "YjQSDgCDcYU", "JQBRzsPhw2w", "CyqifpkRjQA", "0065zKzeCWI", "KG2M4ttzBnY", "kaQmAybWn-w", "Kvk3_MfF7SA", "17On5ItcrBA"]],
    [9, "Era 4: What Can Be Computed, part 1 of 3", "Hilbert's Questions to Gödel's Numbering", ["opIBDMtefR0", "eqvBaj8UYz4", "8pxzoSxb-nQ", "Y6VZD8yu_3U", "6raIgZq1KLU", "q87L9R9v274", "ORvDlbanMJ8", "gt8uCZYA2iU", "5MTG1TCZFFY", "t48a2M27kjM", "VrH6JhIFmcA", "1YZnic1Ug9g", "ydFM5yON-24", "IdEwx42C8nc", "rYSVFScr7qw", "CIe869Rce2k", "8AJPs3gvNlY", "KZeIEiBrT_w", "pyRJENi6O1Q", "-6k7bUoVvMM", "tByUQbJdt14", "sa9inM6Q0dI", "oh3ZOtVix8Y", "ZSPjZuZWCME", "OOtLaW0E9zI", "czcf73b0Ga0", "bQga6WqLUvs", "20QfaLQPLqQ", "ZtZaR7EcI5Y", "X_rP6G9Smhw", "F8KGidsuxgY", "CyIDiwGzqf8", "ScVvooR9g48", "O4ndIDcDSGc", "IuX8QMgy4qE", "PpSxqde0af4", "4Q3bLv8a4Y8", "6v0Rph8SLeI"]],
    [10, "Era 4: What Can Be Computed, part 2 of 3", "Church's Lambda Calculus to The Stored Program, and Merge Sort", ["eis11j_iGMs", "ViPNHMSUcog", "3VQ382QG-y4", "bAt1IcuhLZM", "VSnZzunIELs", "9T8A89jgeTI", "qzsxO79zxS8", "-kvYXLYeKLA", "-ZS_zFg4w5k", "E3keLeMwfHY", "PvLaPKPzq2I", "macM_MtS_w4", "wGLQiHXHWNk", "4tbCR10QGTI", "dNRDvLACg5Q", "pV7Y7d7CG_c", "3x8mSr8ZPGQ", "G2_Q9FoD-oQ", "mcX7iO_XCFA", "rWy-vY6xZ8s", "6eWvYWZeEi4", "rmzONLlR2UM", "jnADN_0M_2A", "H-o9VbvFbYQ", "PYUR9Ertj-g", "eHzsAoKXmZM", "5BpgAHBZgec", "SbqXqQ-2ixs", "RpPo1BGiScY", "1yem8k1jrTs", "LeTeilsd3sY", "3j0SWDX4AtU", "ZUJK2mgn8I8", "jlHkDBEumP0"]],
    [11, "Era 4: What Can Be Computed, part 3 of 3", "Monte Carlo to Hamming's Codes", ["7ESK5SaP-bc", "vIY_J85hHdw", "OgO1gpXSUzU", "TtcB1MOlNiY", "Ac4Z1VMsE3E", "Xhw3Be3gtto", "Bzzqx1F23a8", "E72DWgKP_1Y", "e313WNw1olk", "9YKLXFqCy6E", "wdUfeK8cyys", "1kBDbSbFyvc", "tdwnPbBW07c", "5WD3g8IwUew", "R4OlXb9aTvQ", "vbTZdladViE", "LodZWzrbayY", "3pRR8OK4UfE", "z2Whj_nL-x8", "yY97B8MMggY", "gI-qXk7XojA", "r5dPasQtbY8", "cBBTWcHkVVY", "H767hjCLk5A", "H7XFslRXJys", "X8jsijhllIA", "WPoQfKQlOjg", "h0jloehRKas", "9uAIGQBkQzc", "Bwih7_AT1oI", "MgkhrBSjhag"]],
    [12, "Era 5: The Programmer's Craft, part 1 of 3", "The Subroutine to Hashing", ["l26oaHV7D40", "2SPW5jFggZs", "9Os0o3wzS_I", "Q2sFmqvpBe0", "W8AeMrVtFLY", "oFAlof7v_a8", "DcZ1bFfDvSQ", "zR8V0lq029c", "X13oO5vxd9I", "r6I-Ahc0HB4", "sa-TUpSx1JA", "ZfQFUJhPqMM", "vhiiia1_hC4", "9B0gNXFEklU", "hSKE0xGnLVw", "0DQyPKD8RVU", "tBFLKLzpO8M", "CuYZIsBSguw", "OtDxDvCpPL4", "gmHoX_EqWF4", "JsTptu56GM8", "co4_ahEDCho", "B3y0RsVCyrw", "fsh7Kf4kLCI", "oMu2OzKUVjw", "KyUTuwz_b7Q", "FsfRsGFHuv4", "0M_kIqhwbFo", "b4b8ktEV4Bg", "owsI5SdkDnc", "54iv1si4YCM", "zeMa9sg-VJM"]],
    [13, "Era 5: The Programmer's Craft, part 2 of 3", "Dynamic Programming to The Compiler, and a Grammar for Languages", ["vYquumk4nWw", "aPQY__2H3tE", "oBt53YbR9Kk", "hbveibMDHfg", "Qk0zUZW-U_M", "OQ5jsbhAv_M", "cvGh1NMTq8A", "14BfO5lMiuk", "odW9FU8jPRQ", "N6dOwBde7-M", "qp8u-frRAnU", "c32zXYAK7CI", "X1DkoRGVRp4", "CdAmS9H93q4", "AKV1YmOgmOc", "ZhbIReLe-r8", "2wPS_6oSD6k", "38G5uSxylaY", "T_m27bhVQQQ", "EFg3u_E6eHU", "GazC3A4OQTE", "XB4MIexjvY0", "QXjU9qTsYCc", "awsH0iq0O1A", "Fj90r4l5rds", "NMWzgy8FsKs", "yKXiQAqou04", "EylBknGtkqA", "8cEhCx8pwio", "MMxMeX5emUA", "bxpc9Pp5pZM", "dZal5tpKxb8"]],
    [14, "Era 5: The Programmer's Craft, part 3 of 3", "Rosenblatt's Perceptron to Edmonds's Matching", ["ntKn5TPHHAk", "keq-e9EmC2M", "uclj81wBdxQ", "BbYV8UfMJSA", "bayIW0CpG6k", "fHDouTKwfXw", "XE4VP_8Y0BU", "Vs0kAQTUmE0", "7h1s2SojIRw", "YUkZYlGTZbg", "5iSZ7mh_RAk", "pDqwYVD3DKg", "uzrI5wuF1W0", "Gt2yBZAhsGM", "OnOt1hAkFJs", "zP2xbKerIds", "jDM6_TnYIqE", "FNeL18KsWPc", "5Q-__zhQ2Gs", "IDqdf7VicDs", "AE5I0xACpZs", "t0Cq6tVNRBA", "EmAM6Ij9Mow", "2DmK_H7IdTo", "HqPJF2L5h9U", "B7hVxCmfPtM", "PQczuB44lvg", "_U1AJZQxYTU", "wptevk0bshY", "HWHjQdNC-7Y", "ory4WMX0rDU", "wA6yz9EMIZM", "3roPs1Bvg1Q", "CqyECZ_gqZ4", "S8EYaz-ziHI", "UhYWLzuYW54"]],
    [15, "Era 6: Hard Problems and Public Keys, part 1 of 2", "The Fast Fourier Transform to B-Trees", ["h7apO7q16V0", "E8HeD-MUrjY", "EsJGuI7e_ZQ", "nqaFs-msgUQ", "ypugupAO_tg", "K1aoimUYTK8", "RMR75VzYoos", "Lu6EghdDO5A", "UtEORPakw5Y", "k-oCvIuq_kI", "XDIOC2EY5JE", "ukM_zzrIeXs", "NbwbQQB7xNQ", "pTB0EiLXUC8", "hNr3x_1UxwI", "m0pEj58xlyU", "ccRtIdlTqlU", "wRiGvNwpBYY", "RSl87lqOXDE", "-L-WgKMFuhE", "ySN5Wnu88nE", "eSOJ3ARN5FM", "CJmlP03ik5g", "7kXSIavVeXA", "HLG61NVOU0s", "7bsEN8mwUB8", "GmU7SimFkpU", "_ZIHxHjnVHs", "vzt9c7iWPxs", "XkY2DOUCWMU", "FX4C-JpTFgY", "588JS1EaByU", "0oJyNmEbS4w", "fDAPJ7rvcUw", "DruwS2_cVys", "MpzCQs4u_Oo", "NvrpuBAMddw", "FCtGbrou5DM", "hrbJZDKN5Rg", "8g7T7VedSe0", "K1a2Bk8NrYQ", "5jC2nebEvas", "aZjYr87r1b8", "tT2DT9Z4H-0", "Ay2AbTk_QEg", "xAQga907NVU", "uyLy462Fmk8"]],
    [16, "Era 6: Hard Problems and Public Keys, part 2 of 2", "NP-Completeness to Logical Clocks", ["YX40hbAHx3s", "OY41QYPI8cw", "u2DLlNQiPB4", "O7pq43hIE_0", "DbyXdvwE0G8", "eHZifpgyH_4", "W9G_1xG77LE", "LW_37i96htQ", "vW9ynqCdFQc", "wX3Bfmyu6QM", "0p5NilbKETI", "PMMc4VsIacU", "7fujbpJ0LB4", "IBfWDYSffUU", "wUgWX0nc4NY", "_1TDxihjtoE", "aZXi1unBdJA", "jFZsDDB0-vo", "2kREIkF9UAs", "6-JjHa-qLPk", "GSIDS_lvRv4", "lyWZf_pcwJQ", "YEBfamv-_do", "NmM9HA2MQGI", "Yjrfm_oRO0w", "wXB-V_Keiu8", "4zahvcJ9glg", "tBzaMfV94uA", "8i0UnX7Snkc", "WxVGBEWor1g", "G-h1Dph9IOE", "1DegxRXeP6U", "xWdAgFregt0", "V5-7GzOfADQ", "4Xyhb72LCX4", "Wj606N0IAsw", "goOa3DGezUA", "RV5aUr8sZD0", "_DoIa8TIcTI", "p4HnBe_KzKM", "NLtt4S9ErIA", "Mjab_aZsdxw", "SJPvNi4HrWQ", "x-D8iFU1d-o", "gHXajP9T9WU", "ummQWQgkWOA", "3J9lqpMjA2I", "UYZIHP120go", "5BHizc7BPyE"]],
    [17, "Era 7: Randomness, Networks and Learning, part 1 of 3", "Linear Programming in Polynomial Time to Simulated Annealing", ["YY09OGdK-6E", "M0LcK1ipJTc", "K4imQJK_F38", "aMz7-a6nG6E", "5HWTpadNa_E", "zm4mfr-QT1E", "mswU-rpa1og", "RE_LdTnkpOs", "S9JGmA5_unY", "DMtFhACPnTY", "PbFVTb7Pndc", "3AcQyTs_Es4", "qHMLy5JjbjQ", "C0PuixiGInM", "Bvj72wN0OVk", "tdnf3S2S5xw", "rIlixnNpU7g", "_e4wNoTV3Gw", "Q0xYCN-rvUs", "EFb8E4j49Ng", "1pmBjIZ20pE", "GiDsjIBOVoA", "XaXsJJh-Q5Y", "FyyVbuLZav8", "GU5q871ui7Y", "7IpvsfRgTTY", "oX2wIGSn4jY"]],
    [18, "Era 7: Randomness, Networks and Learning, part 2 of 3", "Splay Trees and Amortized Analysis to The Barnes–Hut Tree Code", ["MTl8djZFWE0", "wKla4Vqrlzw", "3MpzavN3Mco", "D9BZk1giMws", "qMmqOHr75b8", "PnbyRmfA1Jc", "ZWE9BReKjac", "k7jdcWDfpow", "fOGdb1CTu5c", "5qzNe1hk0oY", "5ovdoxnfFVc", "ftTYooCjhuo", "WjFu2cy_0vM", "aircAruvnKk", "CqOfi41LfDw", "uXt8qF2Zzfo", "IHZwWFHWa-w", "sDv4f4s2SB8", "Ilg3gGewQ5U", "IN2XmBhILt4", "VMj-3S1tku0", "YG15m2VwSjA", "HaHsqDjWMLU", "tIeHLnjs5U8", "7axImc1sxa0", "nZHjD3cI-EU", "tOlKLJ4WmSE", "OJxEcs0w_kE", "U1tIa5z_QkE", "ASAowY6yJII"]],
    [19, "Era 7: Randomness, Networks and Learning, part 3 of 3", "Karp–Rabin Fingerprints to AdaBoost", ["BfUejqd07yo", "BQ9E-2umSWc", "eeiSPXCzUiE", "qQ8vS2btsxI", "BRO7mVIFt08", "AEaKrq3SpW8", "JFch3ctY6nE", "kRS4J-m5n04", "cPLDaypKQkU", "h5HjdwkiurE", "g_IaVepNDT4", "JhHMJCUmq28", "RQWpF2Gb-gU", "lvTqbM5Dq4Q", "hOlOY7NyMfs", "k_kyepATqB8", "ha5Fs6l-vGk", "uISnQE6Qsls", "QxcOWfEbXf4", "GYbCttCF25A", "6BJbEWyO_N0", "rQ7wwh4HRZM", "nBFRhjYw1Pg", "kvVGj5V65io", "UHGgpfxlaiE", "DYyXgxYmSYU", "sN5ZcJLDMaE", "J4Wdy0Wc_xQ", "LsK-xG1cLYA", "AtYN8QP-U6w", "UHBmv7qCey4", "MIPkK5ZAsms", "L6BlpGnCYVg", "svZT8cdQOgw"]],
    [20, "Era 8: The Web, the Genome and the Ledger, part 1 of 3", "Support Vector Machines to Consistent Hashing", ["_YPScrckx28", "efR1C6CvhmE", "_PwhiWxHK8o", "zcqTlRgURGA", "-PvsRdlISls", "Q7vT0--5VII", "N_RQj4OL1mg", "Toet3EiSFcM", "Pjsq6-BkVQs", "9zi6-RjlYrU", "nwZjiQra0EA", "OacQnsvauZs", "ea6x57k6iZ4", "vC9-auOJXD0", "byrZXT0a24g", "2uKoKKLgZ4c", "9z2OtPOi8T0", "R2j9yx6UcY0", "aFVnWq3RHYU", "T8hD0ofzDP0", "GjSb-0PHS40", "s9xSfIw83tk", "xbTM3t26xLk", "ibxXO-b14j4", "hJitoHv4rAU", "oJT62C4DVno", "B_PexYrEcEw", "tQhYqKTS08w", "RMNve6ZqhHo", "UF9Iqmg94tk", "zaRkONvyGr8", "9kd1aj8E30k", "1QdKhNpsj8M", "Ki-Dnqk4mss", "5wOGj2kVMuY", "apHAqUG3Pi8"]],
    [21, "Era 8: The Web, the Genome and the Ledger, part 2 of 3", "MinHash and Locality-Sensitive Hashing to Paxos", ["96v3YO_fYI0", "uymzY0gu6yM", "GRHsg0d5X8Y", "aTwRpqUnQX8", "R-iFka68ZwM", "cEMuUGUM9oA", "t_8SpFV0l7A", "AsNTP8Kwu80", "yZv_yRgOvMg", "6niqTuYFZLQ", "qO_NLVjD6zE", "qowp6SQ9_Oo", "qhXZsFVxGKo", "b61DPVFX03I", "YCzL96nL7j0", "-OwYtltMeXY", "meonLcN7LD4", "JGQe4kiPnrU", "i3AkTO9HLXo", "tiGNiUk0C1M", "-5QpQ53-paI", "6A7BTVG_JYc", "DTbPct9B3yU", "vMz3q8Mm1uY", "rN6ma561tak", "2fnS-f-mwIo", "s8JqcZtvnsM", "d7nAGI_NZPk", "tw3gsBms-f8", "BVrlz9h3DMY", "U719vQz-WFs"]],
    [22, "Era 8: The Web, the Genome and the Ledger, part 3 of 3", "Genome Assembly with de Bruijn Graphs to Bitcoin's Proof-of-Work Ledger", ["wUAYwr6zPkY", "u1NJABmmIFE", "9czh_qUScVk", "tdIQClkCkow", "QykgNu0vdos", "9w3MR3_kfH8", "TNYZZKrjCSk", "XU73_ofTjws", "meppRKz50lc", "7l41zCX9ulk", "sDrXeCs3ghQ", "JUa27jxlV-E", "jbiaz_aHHUQ", "_9fbBSxhkuA", "HvMSRWTE2mI", "D7AHbyAlgIA", "0T5yjt-ErJU", "UEAMfLPZZhE", "cQP8WApzIQQ", "cvhKoniK5Uo", "MAJ0aW5g17c", "qxC4urJOchs", "FBILx6XVGCU", "aHCyHbRIz44", "EOYaKcjFa3o", "SbU1pahbbkc", "TneCIMAKeWI", "i2aY7tZ5S7U", "76B5cMEZA4Y", "LfBOmQt5nRw", "ji1C81GRuGI", "bBC-nXj3Ng4", "fOMVZXLjKYo", "ntAQsZV2_kk", "9V1bipPkCTU", "SSo_EIwHSd4", "_160oMzblY8"]],
    [23, "Era 9: Learning at Scale", "Fully Homomorphic Encryption to Algorithms That Find Algorithms", ["fLjPGhCDzKY", "hroyj8R8h60", "aruz58RarVA", "487AjvFW1lk", "HGwBXDKFk9I", "Nq3auVtvd9Q", "hbTONDwwPUk", "viZrOnJclY0", "rmVRLeJRkl4", "BWaHLmG1lak", "I5MGaBBy6n0", "uXEYuDwm7e4", "EgKmNEM40R0", "YbZ3zDzDnrw", "NE88eqLngkg", "p0wSmKslWi0", "JXQT_vxqwIs", "zduSFxRajkE", "HEikzVL-lZU", "mqknozQ-WAE", "GWt6Fu05voI", "C6tLw-rPQ2o", "UXW2yZndl7U", "BEFY7IHs0HM", "WXuK6gekU1Y", "eMlx5fFNoYc", "tIvKXrEDMhk", "kCc8FmEb1nY", "Ckr30ftMGU8", "K026C5YaB3A", "QcVns57MTxg", "G-A1d6P_1yo", "iv-5mZ_9CPY", "HoKDTa5jHvg", "zzKTpMPZ1wY", "Xe22fsiGQXA", "zy8ChVd_oTM", "gMOAud7hZg4", "2IgZuVGwEb0", "QJT3LszR2pA"]],
    [24, "The principles catalog, part 1 of 2", "Euclidean algorithm to Kadane and boyer moore majority", ["SR-jmdjzw-Y", "YZfPcvbwwvI", "kfOGNl2gdr0", "MeWonv4ef2k", "p4y34xphISA", "3rPwfmrCwVw", "eutzTEGgLpE", "oPMaAApBAXU", "We3YDTzNXEk", "eAVGRWSryGo", "e9U0QAFbfLI", "-F1f5mefSi0", "3IdvoI8O9hU", "spNpfmWZBmg", "lSIVK82o2sI", "qi9KIKDpHKY", "6CLl5xx5X-Y", "4lthpDkhMoU", "oz-LycQIL8g", "klcIklsWzrY", "a2ey9a70yY0", "gmur3e33A6A", "_JBkw60KPqw", "NLKQEOgBAnw", "a2OqhXHKSkI", "ymkIDOMS5kE", "PNXXqzU4YnM", "kMpEj7roKxM", "PZRI1IfStY0", "dQhj5RGtag0", "2-mxYrCNX60", "ib4BHvr5-Ao", "2Rr2tW9zvRg", "EzeYI7p9MjU", "MFhxShGxHWc", "hDn8iOc30Tk", "P8Xa2BitN3I", "ARvQcqJ_-NY", "tKwnms5iRBU", "G_UYXzGuqvM", "DKCbsiDBN6c", "xFv_Hl4B83A", "agnNZX2W1AY", "xbYr9JOC2Lk", "MK-NZ4hN7rs", "pVS3yhlzrlQ", "86CQq3pKSUw", "n5QY3x_GNDg", "4csAswCkXZM"]],
    [25, "The principles catalog, part 2 of 2", "Fisher yates and reservoir sampling to Gossip", ["xaSBvljOQkc", "gBTe7lFR3vc", "en0vyyJdDs4", "zaBhtODEL0w", "vf-cxgUXcMk", "_qeVmseIQv0", "pVfj6mxhdMw", "9Wi5WutPiww", "FtN3BYH2Zes", "oNI0rf2P9gE", "eL-KzMXSXXI", "73sneFXuTEg", "ibjEGG7ylHk", "JZBQLXgSGfs", "KaQ9wOrRwow", "bEmBh1HtYrw", "E24zUEKqgwQ", "lY4rSeX8IL4", "9xSiDO2CWbE", "lZU6RK0oazM", "cuieNj3NrZ8", "zQey2zav7jQ", "xa38Q2_pnlQ", "GU-tWlTYvD8", "LKxK12hlNgY", "fCn8zs912OE", "KvOS2MdKFwE", "KqjtNLPb5MM", "lfOOkEZLG-w", "1Qxnrf2pW10", "HBeFe4Ojxvs", "3JdQOExKtUY", "lJ8ydIuPFeU", "tQzanmpF8Ao", "psMMngLC2Ds", "dJI2saoM5_k", "ADHcBxEXvFA", "mQCJJqUfn9Y", "mhUQe4BKZXs", "f-06wUzZf58", "nFOjNrG-DZE", "2edhMsGlwng", "UqY1tF3zxjc", "9xFfOhasiOE", "x7drE24geUw", "I08syTslan8", "S3nq_Iq4eMI", "-36j_DGXEwE"]],
]


def load_progress():
    if PROGRESS.exists():
        return json.loads(PROGRESS.read_text())
    return {"playlists": {}, "skipped": {}}


def save_progress(p):
    PROGRESS.write_text(json.dumps(p, indent=1))


def connect():
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError:
        sys.exit("Missing libraries. Run:  pip3 install google-api-python-client google-auth-oauthlib")
    creds = None
    if TOKEN.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception:
            creds = None  # an app in Google's "testing" mode gets sign-ins that last 7 days; sign in again
    if not creds or not creds.valid:
        if not CLIENT.exists():
            sys.exit(f"Not found: {CLIENT}\nDownload your OAuth client (Desktop app) from Google Cloud and save it there as client_secret.json.")
        flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT), SCOPES)
        creds = flow.run_local_server(port=0, prompt="consent")
        TOKEN.write_text(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def reason(err):
    try:
        return json.loads(err.content.decode())["error"]["errors"][0]["reason"]
    except Exception:
        return ""


class QuotaDone(Exception):
    pass


def call(request):
    from googleapiclient.errors import HttpError
    for attempt in range(5):
        try:
            return request.execute()
        except HttpError as e:
            r = reason(e)
            if r in ("quotaExceeded", "dailyLimitExceeded"):
                raise QuotaDone()
            if r == "rateLimitExceeded" or e.resp.status in (500, 502, 503, 504):
                time.sleep(2 ** attempt)
                continue
            raise
    raise RuntimeError("YouTube kept refusing; try again later.")


def my_playlists(yt):
    """Title -> id for the playlists already in the account, so a lost progress file never causes duplicates."""
    out, token = {}, None
    while True:
        r = call(yt.playlists().list(part="snippet", mine=True, maxResults=50, pageToken=token))
        for it in r.get("items", []):
            out.setdefault(it["snippet"]["title"], it["id"])
        token = r.get("nextPageToken")
        if not token:
            return out


def items_in(yt, pid):
    ids, token = set(), None
    while True:
        r = call(yt.playlistItems().list(part="contentDetails", playlistId=pid, maxResults=50, pageToken=token))
        for it in r.get("items", []):
            ids.add(it["contentDetails"]["videoId"])
        token = r.get("nextPageToken")
        if not token:
            return ids


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--privacy", default="private", choices=["private", "unlisted", "public"])
    args = ap.parse_args()

    total = sum(len(p[3]) for p in PLAYLISTS)
    if args.dry_run:
        for num, title, span, ids in PLAYLISTS:
            print(f"{num:2d}. {title}  ({len(ids)} videos: {span})")
        print(f"\n{len(PLAYLISTS)} playlists, {total} videos. About {-(-total // 190)} days at Google's free daily limit.")
        return

    from googleapiclient.errors import HttpError
    yt = connect()
    prog = load_progress()
    added_today = 0
    try:
        existing = my_playlists(yt)
        for num, title, span, ids in PLAYLISTS:
            key = str(num)
            pid = prog["playlists"].get(key) or existing.get(title)
            if not pid:
                body = {"snippet": {"title": title,
                                    "description": f"The Algorithm Evolution Atlas, watched in book order: {span}. {len(ids)} videos."},
                        "status": {"privacyStatus": args.privacy}}
                pid = call(yt.playlists().insert(part="snippet,status", body=body))["id"]
                print(f"Created playlist {num}: {title}")
            prog["playlists"][key] = pid
            save_progress(prog)
            have = items_in(yt, pid)
            skipped = set(prog["skipped"].get(key, []))
            todo = [v for v in ids if v not in have and v not in skipped]
            if not todo:
                print(f"{num:2d}. {title}: complete ({len(have)} videos)")
                continue
            print(f"{num:2d}. {title}: adding {len(todo)} of {len(ids)}")
            for v in todo:
                body = {"snippet": {"playlistId": pid, "resourceId": {"kind": "youtube#video", "videoId": v}}}
                try:
                    call(yt.playlistItems().insert(part="snippet", body=body))
                    added_today += 1
                except HttpError as e:
                    if reason(e) in ("videoNotFound", "forbidden", "playlistItemsNotAccessible") or e.resp.status == 404:
                        prog["skipped"].setdefault(key, []).append(v)  # removed or private since the list was made
                        save_progress(prog)
                        print(f"    skipped {v} (no longer available)")
                        continue
                    raise
                time.sleep(0.2)
        nskip = sum(len(v) for v in prog["skipped"].values())
        print(f"\nFinished: all {len(PLAYLISTS)} playlists are complete" + (f" ({nskip} videos were no longer available)." if nskip else "."))
    except QuotaDone:
        print(f"\nAdded {added_today} videos today. Google's daily limit is reached; it resets at midnight Pacific time.")
        print("Run the same command again tomorrow; it carries on where it stopped.")
    finally:
        save_progress(prog)


if __name__ == "__main__":
    main()
