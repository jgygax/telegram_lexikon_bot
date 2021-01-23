import re
import os
import csv

def print_out(out):
    print("=======================================================")
    print("..." + out[80000:81000]+"...")

with open("Fremdwörterduden-2.txt") as f:
    out = f.read()

replacements = [
    # Betonungen
    ("\n˙\n", "|"),
    ("\n\n", "|"),
    ("↑", ""),
    # Zeilenumbrüche
    ("-\n", ""),
    ("\n¯\n", ""),
    # Trennen nach definitionen
    (r"(ad (([\wäöü]+\|)+[\wäöü]+))", r"==========\1----------"),           # alle ad blablabla
    (r"(([\wäöü]+)-(([\wäöü]+\|)+[\wäöü]+))", r"==========\1----------"),   # alle Wörter mit Bindestrich, welche vor dem Bindestrich nur eine Silbe haben
    (r"(([\wäöüéè]+\|+)+[\wäöüéèà]*)", r"==========\1----------"),          # alle Einzelwörter
    (r"(ad) ==========",r"\1 "),                                            # entferne Zeichen zwischen ad und blablabla
    (r"--------------------",r"----------"),                                # entstanden durch Doppelmatch von ad blablabla und einzelwörter
    (r"-==========", r"-"),                                                 # entferne Quatsch in Bindestrichwörtern
    # Alles auf eine Zeile
    ("\n"," "),
    (r" *========== *", "\n==========\n"),
    (r" *---------- *", "\n"),
    # Keine Silben trennstriche
    (r"\|",""),
    # Keine Klammern
    (r"\[.*?\]", ""),
    (r"\(.*?\)", ""),
    (r"〈.*?〉", ""),
    # Erstes Element in der nummerierung
    (r"2\..*\n", "\n"),
    (r"1\.", ""),
    (r"a\)", ""),
    (r"b\).*\n", "\n"),
    # Alles bis zum Doppelpunkt weg
    (r"\n.*: *", "\n"),
    # Alles ab strichpunkt weg 
    (r";.*?\n", "\n"),
    # Doppelleerschläge weg
    (r" +"," "),
    # Leerschläge vor Punkten weg
    (r" \.","."),
    # Leerschläge vor Kommas weg
    (r" ,",",")
]

i = 0
while os.path.exists("out{}.txt".format(i)):
    os.remove("out{}.txt".format(i))
    i+=1

for i, (old, new) in enumerate(replacements):
    out = re.sub(old, new, out)
    with open("out{}.txt".format(i) ,"w+") as f:
        f.write(out)

# Finalize
word_chars = re.compile(r"^[a-zA-ZÄÖÜÈÉäöüèé]*$")
explanation_chars = re.compile(r"^[a-zA-ZÄÖÜÈÉäöüèé .,?!]*$")

with open("finalout.csv", "w+") as f:
    f.write("{}= {}\n".format("word", "explanation"))
    for entry in out.split("\n==========\n"):
        lines = entry.split("\n")
        if len(lines) == 2:
            word, explanation = lines
            word = word.strip()
            explanation = explanation.strip()
            n_explanation_words = len(explanation.split(" "))
            if n_explanation_words > 5 \
                    and len(word) > 3 \
                    and explanation_chars.match(explanation) \
                    and word_chars.match(word) \
                    and not "M M M M" in explanation:
                f.write("{}= {}\n".format(word, explanation))

print("Es hed no die Wörtli denne, wo öppis ned stemmt, well si ned alphabetisch sortiert send:\n")
with open("finalout.csv") as f:
        reader = csv.DictReader(f, delimiter="=")
        i = 0
        current_word = "a"
        i = 0
        for row in reader:
            next_word = row["word"].lower()
            if current_word > next_word:
                i+=1
                print(current_word, next_word)
            current_word = next_word
        print("\nSo vell send falsch: " + str(i))

print("\nOnd d'Abchürzige müesst mer ä no ersetze!")
