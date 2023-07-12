from cutlet import Cutlet
import os

C = Cutlet("kunrei")
for fn in os.listdir("./before/"):
    ff = open("./before/" + fn, "r", encoding="utf8").readlines()[::-1]
    out = ""
    while len(ff) > 0:
        k = ff.pop().strip()
        out += k + "\n"
        out += C.romaji(k) + "\n"
        out += ff.pop().strip() + "\n"
    
    outf = open("./after/" + fn, "w", encoding="utf8")
    outf.write(out.strip())
    