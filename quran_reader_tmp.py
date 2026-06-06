import re
import requests
import pyperclip

from bs4 import BeautifulSoup

def get_quran_passage(surah, start_ayah, end_ayah, language="language_6"):
    languages = ",".join(sorted(["6", language.split('_')[-1]]))
    url = f"https://legacy.quran.com/{surah}/{start_ayah}-{end_ayah}?l={languages}"
    print(f"Loading from {url}")
    response = requests.get(url)
    page = response.content
    soup = BeautifulSoup(page)
    qReader = soup.find("div", {"id":"quranOutput"})
    return qReader

def extract_ayah(qReader, language="language_6"):
    ayat = qReader.find_all(recursive=False)
    lines = []
    for i in range(0, len(ayat), 2):
        ayah_name = ayat[i].get_attribute_list("name")[0]
        ayah_content = ayat[i+1].find("div", {"class":language}).find("span").text.replace("  "," ")
        lines.append(f"{ayah_name}\t{ayah_content}")
    return "\n".join(lines)

LANGUAGES = {
    "Transliteration": "language_5",
    "Sahih International": "language_6",
    "Muhsin Khan": "language_7",
    "Pickthall": "language_8",
    "Yusuf Ali": "language_9",
    "Shakir": "language_10",
    "Dr. Ghali": "language_11",
}

if __name__ == "__main__":
    surah = int(input("Enter Surah: "))
    start_ayah = int(input("Enter start ayah number: "))
    end_ayah = int(input("Enter end ayah number: "))
    language_display = "\n".join([f"{code.split('_')[-1]} = {name}" for name, code in LANGUAGES.items()])
    print(language_display)
    language = "language_" + input("Select Language: ")
    qReader = get_quran_passage(surah, start_ayah, end_ayah, language)
    output = extract_ayah(qReader)
    if input("Copy to clipboard? y/N: ").lower() == "y":
        pyperclip.copy(output)
    else:
        print(output)

