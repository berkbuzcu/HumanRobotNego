import nltk
from nltk.tokenize import word_tokenize
import re
import copy
from human_robot_negotiation.HANT.nego_action import AbstractAction, AbstractActionFactory, Accept, Offer, ResourceAllocationActionFactory
from human_robot_negotiation.HANT.utility_space import UtilitySpace

class OfferClassifier:
	def __init__(self, human_utility_space: UtilitySpace, action_factory: AbstractActionFactory):
		self.keywords = ['apple', 'banana', 'orange', 'watermelon']
		self.stop_words = set(['my', 'myself', 'we', 'our', 'ours', 'ourselves', "you're", "you've", "you'll", "you'd", 'your', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she',
		"she's", 'her', 'hers', 'herself', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', "that'll", 'these', 'those', 'am', 'are', 'was',
		'were', 'be', 'been', 'being', 'has', 'had', 'having', 'does', 'did', 'doing', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'with', 'about', 'against', 'between', 'into',
		'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
		'how', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'nor', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've",
		'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma',
		'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't", "could", "the"])
		self.OFFER_SENTENCES = {}
		self.ARGUMENT_SENTENCES = []

		self.domain_keywords = human_utility_space.issue_names

		self.action_factory: AbstractActionFactory = action_factory
		self.human_utility_space: UtilitySpace = human_utility_space


	def get_offer_and_arguments(self, input):
		#print("input", input)
		processed_input = self.preprocess_input(input)
		# Control the acceptance.
		is_acceptance = self.check_if_acceptance(processed_input)
		if is_acceptance:
			return self.action_factory.create_acceptance(), True
		#print("processed", processed_input)
		tagged_words = self.tag_input_words(processed_input)
		#print("tagged words", tagged_words)
		sentences = self.seperate_tags_to_sentences(tagged_words)
		#print("seperated:", sentences)
		self.classify_sentences(sentences)
		print("offer sents: ", self.OFFER_SENTENCES)

		if len(self.OFFER_SENTENCES) == len(self.keywords):
			offer = self.action_factory.create_offer(self.OFFER_SENTENCES)
			self.OFFER_SENTENCES = {}
			return offer, True
			
		else:
			return self.action_factory.create_offer(self.OFFER_SENTENCES), False

	def check_if_acceptance(self, input):
		input = input.lower()
		# Check if the user accepts the offer.
		if (len(re.findall(r'\b' + "(no |not )deal" + r'\b', input)) == 0 and len(re.findall(r'\b' + "(deal|yes|agree)" + r'\b', input)) > 0 and
			len(re.findall(r'\b' + "(have|take|get|want|like|need|cant|can't|can not|cannot|won't|will not|if|do not|don't|keep)" + r'\b', input)) == 0):
			return True
		else:
			return False

	def preprocess_input(self, input):
		input = input.lower()

		input = input.replace("for", "four")
		input = input.replace("For", "four")
		input = input.replace("tree", "three")

		# Fix would like to 'verb' part in input.
		for offer_verb in ["have", "take", "get", "want", "like"]:
			# TODO FIX REGEX DUDE.
			input = re.sub(r'\b' + '(would like to |want to |need to |like to )' + re.escape(offer_verb) + r'\b', offer_verb, input)
		# Fix don't like don't want sentences.
		for offer_verb in ["have", "take", "get", "want", "like"]:
			for keyword in self.keywords:
				# replace sentences such as I dont want apple, i dont want any apple etc.
				input = re.sub(r'\b' + "(don't |do not )" + offer_verb + " (any )?" + keyword + "(s)?" + r'\b', offer_verb + " 0 " + keyword, input)
				# replace sentences such as not any apple.
				input = re.sub(r'\b' + '(not any |no )' + keyword + "(s)?" + r'\b', "0 " + keyword, input)
				# except apples
				input = re.sub(r'\b' + 'except( the)? ' + keyword + "(s)?" + r'\b', "0 " + keyword, input)
		# Fix would like in input.
		input = re.sub(r'\b' + 'would like' + r'\b', "want", input)
		# Remove 'll' from input.
		input = re.sub(r'\b' + "('ll |'d )" + r'\b', " ", input)
		# Fix the apple - the apples difference for every keyword in the domain.
		for keyword in self.keywords:
			# NOTE: 'the' without 's' can be 1 not sure tho.
			input = re.sub(r'\b' + '(all|full)( of)?( the)? ' + keyword + '(s)?' + r'\b', '4 ' + keyword + 's', input)
		# All the foods or fruits -> 4 apples, 4 oranges, 4 watermelons, 4 bananas
		input = re.sub(r'\b' + '(all )the ' + '(food |fruit )' + '(s)?' + r'\b', '4 apples, 4 oranges, 4 watermelons, 4 bananas', input)
		# All of them -> 4 apples, 4 oranges, 4 watermelons, 4 bananas
		input = re.sub(r'\b' + '(all of them|everything)' + r'\b', '4 apples, 4 oranges, 4 watermelons, 4 bananas', input)
		# Half of them -> 2 apple, 2 orange, 2 watermelon, 2 banana
		input = re.sub(r'\b' + 'half of them' + r'\b', '2 apples, 2 oranges, 2 watermelons, 2 bananas', input)
		# Accept -> except.
		input = re.sub(r'\b' + 'accept' + r'\b', 'except', input)
		# That's it, this is it --> you can have the rest.
		input = re.sub(r'\b' + "(that's it|this is it|that's all|that is all|(the )?rest is yours|nothing else)" + r'\b', 'you can have the rest', input)
		# All the remaining -> check what keywords are in the offer select remainings and set them to 4.
		if len(re.findall(r'\b' + "all (the )?remaining( fruit| fruits| one| ones)?" + r'\b', input)) != 0:
			remaining_keywords = self.keywords[:]
			for keyword in self.keywords:
				if keyword in input:
					remaining_keywords.remove(keyword)
			replace_text = ""
			for keyword in remaining_keywords:
				replace_text += " 4 " + keyword
			input = re.sub(r'\b' + "all (the )?remaining( fruit| fruits| one| ones)?" + r'\b', replace_text.strip(), input)
		print("Input:", input)
		return input

	def tag_input_words(self, processed_input):
		# Tokenize the input
		word_tokens = word_tokenize(processed_input)
		# Filter the input
		filtered_sentence = [w for w in word_tokens if not w in self.stop_words]
		# Tag the filtered input.
		tagged_words = nltk.pos_tag(filtered_sentence, tagset="universal")
		# Convert tagged word tuples to list in order to modify.
		tagged_words_list = [list(tagged_word) for tagged_word in tagged_words]
		for word_index, (word, tag) in enumerate(tagged_words_list):
			# Search for lower i and convert it to proper I.
			if word in ["i", "ill"]:
				tagged_words_list[word_index][0] = "I"
				tagged_words_list[word_index][1] = "PRON"
			if word.lower() in ["a", "an"]:
				tagged_words_list[word_index][0] = "1"
				tagged_words_list[word_index][1] = "NUM"
			if word.lower() in ["zero", "one", "two", "three", "four"]:
				if word.lower() == "zero":
					tagged_words_list[word_index][0] = "0"
					tagged_words_list[word_index][1] = "NUM"
				if word.lower() == "one":
					tagged_words_list[word_index][0] = "1"
					tagged_words_list[word_index][1] = "NUM"
				if word.lower() in ["two"]:
					tagged_words_list[word_index][0] = "2"
					tagged_words_list[word_index][1] = "NUM"
				if word.lower() in ["three"]:
					tagged_words_list[word_index][0] = "3"
					tagged_words_list[word_index][1] = "NUM"
				if word.lower() == "four":
					tagged_words_list[word_index][0] = "4"
					tagged_words_list[word_index][1] = "NUM"
			# Fix wrong tagging for rest word.
			if word.lower() in ["rest"]:
				tagged_words_list[word_index][1] = "NOUN"
			# Fix wrong tagging for keywords.
			for keyword in self.keywords:
				if (word == keyword or word == keyword + 's') and tag != 'NOUN':
					tagged_words_list[word_index][1] = "NOUN"
		return tagged_words_list

	def seperate_tags_to_sentences(self, tagged_words):
		turn_taking_sentence = []
		temp_tagged_words = copy.copy(tagged_words)
		# Seperate the you can have the rest and etc type sentences.
		for index, (word, tag) in enumerate(temp_tagged_words):
			if word.lower() == "you":
				try:
					if ((tagged_words[index + 1][0].lower() == "have" and tagged_words[index + 2][0].lower() == "rest") or
					(tagged_words[index + 1][0].lower() == "take" and tagged_words[index + 2][0].lower() == "rest")):
						you_word = tagged_words.pop(index)
						have_word = tagged_words.pop(index)
						rest_word = tagged_words.pop(index)
						turn_taking_sentence.append(you_word)
						turn_taking_sentence.append(have_word)
						turn_taking_sentence.append(rest_word)
						break
				except BaseException as e:
					continue

		# Create variable for input analysis.
		sentences_array = []
		# Control variable for seeing verb for the first time.
		first_time_verb = True
		# Create list for input tokens.
		sentence_tokens = []
		# Create list for temp input tokens.
		temp_sentence_tokens = []
		# Iterate for each word and tag in tagged words
		for word_index, (word, tag) in enumerate(tagged_words):
			# If we are seeing the verb first time just change the control sequence.
			if tag == 'VERB' and first_time_verb:
				first_time_verb = False
				sentence_tokens.append((word, tag))
			# Search for verb if there's already a input to seperate and if its not the first time we're seeing verb.
			elif tag == 'VERB' and not first_time_verb:
				# add second verb input tokens too.
				sentence_tokens.append((word, tag))
				# Search the tokens from reversed order until finding pronoun of the input and then just seperate them from pronoun.
				for s_index, (s_word, s_tag) in reversed(list(enumerate(sentence_tokens))):
					# Create temp variable and add it to the list for the second non-finished input.
					temp_word = sentence_tokens.pop(s_index)
					temp_sentence_tokens.append(temp_word)
					if s_tag == 'PRON':
						sentences_array.append(sentence_tokens)
						sentence_tokens = list(reversed(temp_sentence_tokens[:]))
						temp_sentence_tokens = []
						break
			else:
				sentence_tokens.append((word, tag))
		# Add last input to the list.
		sentences_array.append(sentence_tokens)
		# If turn taking sentence is present add to it.
		if len(turn_taking_sentence) > 0:
			sentences_array.append(turn_taking_sentence)
		return sentences_array

	def classify_sentences(self, sentences):
		# Iterate through all sentences for offer.

		for sentence in sentences:
			print("sentence", sentence)
			if len(sentence) < 2:
				continue

			is_offer_sentence = False
			# Try to get sentence subject.
			try:
				sentence_subject = [word for (word, tag) in sentence if tag == 'PRON'][0]
			except:
				sentence_subject = ""
			# Try to get sentence verb.
			try:
				sentence_verb = [word for (word, tag) in sentence if tag=='VERB'][0]
			except:
				sentence_verb = ""
			# Try to get sentence nouns.
			try:
				sentence_nouns = [(word, index) for index, (word, tag) in enumerate(sentence) if tag=='NOUN']
				# Try to get the first element if its empty it will go to exception.
				test_noun = sentence_nouns[0]
			except:
				sentence_nouns = [("", 0)]

			# Check if human wants something to themselves.
			if ((sentence_subject == "I" and not any(word for word, tag in sentence if word.lower() in ["n't", "not", "dont"]) and sentence_verb.lower() in ["have", "take", "get", "want", "like", "need", "keep"]) or
				(sentence_subject.lower() == "you" and not any(word for word, tag in sentence if word.lower() in ["n't", "not", "dont", "rest"]) and sentence_verb.lower() in ["offer", "give"]) or
				(sentence_subject.lower() in ["", "me"] and not any(word for word, tag in sentence if word.lower() in ["n't", "not", "dont"]) and sentence_verb == "")):
				is_offer_sentence = True
				# Iterate nouns of the sentences.

				for (noun, index) in sentence_nouns:
					keyword_match = [keyword for keyword in self.keywords if keyword in noun.lower()]
					# Check the except 1 apple phrases.
					if len(sentence) > 3 and (sentence[index-2][0].lower() == 'except'):
						try:
							if len(keyword_match) > 0 and (sentence[index-1][1] == 'NUM' and sentence[index-1][0] in ['0', '1', '2', '3', '4']):
								self.OFFER_SENTENCES[keyword_match[0]] = self.human_utility_space.issue_max_counts[keyword_match[0]] - int(sentence[index-1][0])

						except:
							continue
					else:
						try:
							if len(keyword_match) > 0 and (sentence[index-1][1] == 'NUM' and sentence[index-1][0] in ['0', '1', '2', '3', '4']):
								self.OFFER_SENTENCES[keyword_match[0]] = int(sentence[index-1][0])

						except:
							continue
			# Check if human gives something to our agent.
			elif ((sentence_subject == "I" and not any(word for word, tag in sentence if word.lower() in ["n't", "not", "dont"]) and sentence_verb.lower() in ["offer", "give"]) or
				(sentence_subject.lower() == "you" and not any(word for word, tag in sentence if (word.lower() in ["n't", "not", "dont", "rest"])) and sentence_verb.lower() in ["keep", "have", "take", "get", "want", "like"]) or
				(len(set(sentence_nouns[0]) & set(['offer', 'bid'])) > 0)):
				is_offer_sentence = True
				# Iterate nouns of the sentences.
				for (noun, index) in sentence_nouns:
					keyword_match = [keyword for keyword in self.keywords if keyword in noun.lower()]
					if len(keyword_match) > 0 and (sentence[index-1][1] == 'NUM' and sentence[index-1][0] in ['0', '1', '2', '3', '4']):
						# Check the except 1 apple phrases.
						if len(sentence) > 3 and (sentence[index-2][0].lower() == 'except'):
							try:
								print("except caught")
								self.OFFER_SENTENCES[keyword_match[0]] = int(sentence[index-1][0])
							except:
								continue
						else:
							try:
								self.OFFER_SENTENCES[keyword_match[0]] = self.human_utility_space.issue_max_counts[index-1] - int(sentence[index-1][0])
							except:
								continue
			# Check if human wants 'rest' for themself.
			if ( (sentence_subject == "I" and any(word for word, tag in sentence if word.lower() in ["rest"]) and sentence_verb.lower() in ["have", "take"]) or
				(any(word for word, tag in sentence if word.lower() in ["rest"]) and any(word for word, tag in sentence if word.lower() in ["mine"])) ):
				is_offer_sentence = True
				for keyword in [keyword for keyword in self.keywords if keyword not in self.OFFER_SENTENCES.keys()]:
					self.OFFER_SENTENCES[keyword] = 4
				break
			# Check if human gives 'rest' to agent.
			elif ( (sentence_subject == "you" and any(word for word, tag in sentence if word.lower() in ["rest"]) and sentence_verb.lower() in ["have", "take"])):
				is_offer_sentence = True
				for keyword in [keyword for keyword in self.keywords if keyword not in self.OFFER_SENTENCES.keys()]:
					self.OFFER_SENTENCES[keyword] = 0
				break
			if not is_offer_sentence:
				self.ARGUMENT_SENTENCES.append(sentence)
