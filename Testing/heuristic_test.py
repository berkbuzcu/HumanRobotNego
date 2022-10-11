import nltk
from nltk.tokenize import word_tokenize

# Define domain keywords.
keywords = ["hat", "book", "ball"]

# Import stop words
stop_words = set(
    [
        "me",
        "my",
        "myself",
        "we",
        "our",
        "ours",
        "ourselves",
        "you're",
        "you've",
        "you'll",
        "you'd",
        "your",
        "yours",
        "yourself",
        "yourselves",
        "he",
        "him",
        "his",
        "himself",
        "she",
        "she's",
        "her",
        "hers",
        "herself",
        "it",
        "it's",
        "its",
        "itself",
        "they",
        "them",
        "their",
        "theirs",
        "themselves",
        "what",
        "which",
        "who",
        "whom",
        "this",
        "that",
        "that'll",
        "these",
        "those",
        "am",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "has",
        "had",
        "having",
        "does",
        "did",
        "doing",
        "the",
        "and",
        "but",
        "if",
        "or",
        "because",
        "as",
        "until",
        "while",
        "of",
        "at",
        "by",
        "for",
        "with",
        "about",
        "against",
        "between",
        "into",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "to",
        "from",
        "up",
        "down",
        "in",
        "out",
        "on",
        "off",
        "over",
        "under",
        "again",
        "further",
        "then",
        "once",
        "here",
        "there",
        "when",
        "where",
        "why",
        "how",
        "all",
        "both",
        "each",
        "few",
        "more",
        "most",
        "other",
        "some",
        "such",
        "no",
        "nor",
        "only",
        "own",
        "same",
        "so",
        "than",
        "too",
        "very",
        "s",
        "t",
        "can",
        "will",
        "just",
        "don",
        "should",
        "should've",
        "now",
        "d",
        "ll",
        "m",
        "o",
        "re",
        "ve",
        "y",
        "ain",
        "aren",
        "aren't",
        "couldn",
        "couldn't",
        "didn",
        "didn't",
        "doesn",
        "doesn't",
        "hadn",
        "hadn't",
        "hasn",
        "hasn't",
        "haven",
        "haven't",
        "isn",
        "isn't",
        "ma",
        "mightn",
        "mightn't",
        "mustn",
        "mustn't",
        "needn",
        "needn't",
        "shan",
        "shan't",
        "shouldn",
        "shouldn't",
        "wasn",
        "wasn't",
        "weren",
        "weren't",
        "won",
        "won't",
        "wouldn",
        "wouldn't",
        "would",
    ]
)


def tag_words(sentence):
    # Tokenize the input sentence
    word_tokens = word_tokenize(sentence)
    # Tag the filtered sentence.
    tagged_words = nltk.pos_tag(word_tokens, tagset="universal")
    # Convert tagged word tuples to list in order to modify.
    tagged_words_list = [
        list(tagged_word)
        for tagged_word in tagged_words
        if tagged_word[0] not in stop_words
    ]
    for word_index, (word, tag) in enumerate(tagged_words_list):
        # Search for lower i and convert it to proper I.
        if word == "i":
            tagged_words_list[word_index][0] = "I"
            tagged_words_list[word_index][1] = "PRON"
        if word.lower() in ["a", "an"]:
            tagged_words_list[word_index][0] = "1"
            tagged_words_list[word_index][1] = "NUM"
        if word.lower() in ["one", "two", "three", "four"]:
            if word.lower() == "one":
                tagged_words_list[word_index][0] = "1"
            if word.lower() == "two":
                tagged_words_list[word_index][0] = "2"
            if word.lower() == "three":
                tagged_words_list[word_index][0] = "3"
            if word.lower() == "four":
                tagged_words_list[word_index][0] = "4"
    return tagged_words_list


def new_seperator(tagged_words):
    # Create variable for sentence analysis.
    sentences_array = []
    # Control variable for seeing verb for the first time.
    first_time_verb = True
    # Create list for sentence tokens.
    sentence_tokens = []
    # Create list for temp sentence tokens.
    temp_sentence_tokens = []
    # Iterate for each word and tag in tagged words
    for word_index, (word, tag) in enumerate(tagged_words):
        # If we are seeing the verb first time just change the control sequence.
        if tag == "VERB" and first_time_verb:
            first_time_verb = False
            sentence_tokens.append((word, tag))
        # Search for verb if there's already a sentence to seperate and if its not the first time we're seeing verb.
        elif tag == "VERB" and not first_time_verb:
            # add second verb sentence tokens too.
            sentence_tokens.append((word, tag))
            # Search the tokens from reversed order until finding pronoun of the sentence and then just seperate them from pronoun.
            for s_index, (s_word, s_tag) in reversed(list(enumerate(sentence_tokens))):
                # Create temp variable and add it to the list for the second non-finished sentence.
                temp_word = sentence_tokens.pop(s_index)
                temp_sentence_tokens.append(temp_word)
                if s_tag == "PRON":
                    sentences_array.append(sentence_tokens)
                    sentence_tokens = list(reversed(temp_sentence_tokens[:]))
                    temp_sentence_tokens = []
                    break
        else:
            sentence_tokens.append((word, tag))
    # Add last sentence to the list.
    sentences_array.append(sentence_tokens)

    return sentences_array


def new_classify_sentences(seperated_sentences, OFFER_SENTENCES, ARGUMENT_SENTENCES):
    # Iterate through all sentences.
    for sentence in seperated_sentences:

        if any(word for word, index in sentence if word.lower() in ["deal", "accept"]):
            ARGUMENT_SENTENCES.append(sentence)
            return OFFER_SENTENCES, ARGUMENT_SENTENCES
        # Continue to check if it is not acceptance.
        is_offer_sentence = False
        # Get sentence subject.
        sentence_subject = [word for (word, tag) in sentence if tag == "PRON"][0]
        # Get sentence verb.
        sentence_verb = [word for (word, tag) in sentence if tag == "VERB"][0]
        # Get sentence nouns.
        sentence_nouns = [
            (word, index) for index, (word, tag) in enumerate(sentence) if tag == "NOUN"
        ]

        if (
            sentence_subject == "I"
            and not any(
                word for word, index in sentence if word in ["n't", "not", "dont"]
            )
            and sentence_verb in ["take", "get", "want", "like"]
        ) or (
            sentence_subject.lower() == "you"
            and not any(
                word for word, index in sentence if word in ["n't", "not", "dont"]
            )
            and sentence_verb in ["offer", "give"]
        ):
            # Iterate nouns of the sentences.
            for (noun, index) in sentence_nouns:
                keyword_match = [keyword for keyword in keywords if keyword in noun]
                if len(keyword_match) > 0 and (sentence[index - 1][1] == "NUM"):
                    OFFER_SENTENCES[keyword_match[0]] = 4 - int(sentence[index - 1][0])
        elif (
            (
                sentence_subject == "I"
                and not any(
                    word for word, index in sentence if word in ["n't", "not", "dont"]
                )
                and sentence_verb in ["offer", "give"]
            )
            or (
                sentence_subject.lower() == "you"
                and not any(
                    word
                    for word, index in sentence
                    if (word in ["n't", "not", "dont", "rest"])
                )
                and sentence_verb in ["have", "take", "get", "want", "like"]
            )
            or len(set(sentence_nouns[0]) & set(["offer", "bid"])) > 0
        ):
            # Iterate nouns of the sentences.
            for (noun, index) in sentence_nouns:
                keyword_match = [keyword for keyword in keywords if keyword in noun]
                if len(keyword_match) > 0 and (sentence[index - 1][1] == "NUM"):
                    OFFER_SENTENCES[keyword_match[0]] = int(sentence[index - 1][0])
        else:
            ARGUMENT_SENTENCES.append(sentence)
    return OFFER_SENTENCES, ARGUMENT_SENTENCES


def is_offer_done():
    global ALL_OFFER_SENTENCES, ALL_ARGUMENT_SENTENCES
    # Control each keyword in senteces.
    for offer_keyword in ALL_OFFER_SENTENCES.keys():
        if len(keywords) == 0:
            return True
        else:
            for keyword in keywords:
                if offer_keyword in keyword or keyword in offer_keyword:
                    keywords.remove(keyword)
            if len(keywords) == 0:
                return True
    for argument_sentence in ALL_ARGUMENT_SENTENCES:
        if any(word for word, index in argument_sentence if word in ["deal", "accept"]):
            return True
        for argument_keyword in argument_sentence:
            if argument_keyword[0].lower() == "rest":
                for keyword in keywords:
                    ALL_OFFER_SENTENCES[keyword] = 4
                return True
    return False


if __name__ == "__main__":
    ALL_OFFER_SENTENCES = {}
    ALL_ARGUMENT_SENTENCES = []
    while True:
        input_sentence = raw_input("Please enter your offer: ")
        tagged_words = tag_words(input_sentence)
        print("tagged words:", tagged_words)
        seperated_sentences = new_seperator(tagged_words)
        print("Seperated sentences:", seperated_sentences)
        ALL_OFFER_SENTENCES, ALL_ARGUMENT_SENTENCES = new_classify_sentences(
            seperated_sentences, ALL_OFFER_SENTENCES, ALL_ARGUMENT_SENTENCES
        )
        print("ALL offer sentences:", ALL_OFFER_SENTENCES)
        print("ALL argument sentences:", ALL_ARGUMENT_SENTENCES)

        if is_offer_done():
            ALL_ARGUMENT_SENTENCES = [list(elem) for elem in ALL_ARGUMENT_SENTENCES]
            print("I guess your offer is done.")
            print("ALL offer sentences:", ALL_OFFER_SENTENCES)
            print("ALL argument sentences:", ALL_ARGUMENT_SENTENCES)
            break
