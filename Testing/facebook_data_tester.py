import re
import pandas as pd
import xlsxwriter as xlsw
import itertools

with open("facebook_data/train.txt") as f:
    raw_data = f.readlines()

delimiter = (
    "<dialogue>(.*)(?:YOU: |THEM: )<selection>"  # Set delimiter to get the text part.
)

text_data = [
    re.search(delimiter, data).group(1).strip() for data in raw_data
]  # Get the data between <dialogue> tags and Strip the whitespaces from the data

print("Raw data:", raw_data[1000])
print("Text data:", text_data[1000])

you_delimeter = "(YOU: )(.*?)<eos>"
them_delimeter = "(THEM: )(.*?)<eos>"
all_sentences_delimiter = "(?:THEM: |YOU: )(.*?)<eos>"

you_sentences = [re.findall(you_delimeter, data) for data in text_data]
them_sentences = [re.findall(them_delimeter, data) for data in text_data]
all_sentences = [re.findall(all_sentences_delimiter, data) for data in text_data]

merged_all_sentences = list(itertools.chain(*all_sentences))
merged_you_sentences = list(itertools.chain(*you_sentences))

print("You sentences:", merged_you_sentences[0])

# df = pd.DataFrame({'Sentences': you_sentences})
#
# writer = pd.ExcelWriter("facebook_sentences.xlsx", engine='xlsxwriter')
#
# df.to_excel(writer, sheet_name="Facebook_Data")
#
# writer.save()
