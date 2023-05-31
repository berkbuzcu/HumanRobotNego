from os import read
import nltk
from nltk.tokenize import word_tokenize
import re
from collections import ChainMap
import itertools

from human_robot_negotiation.HANT.nego_action import AbstractActionFactory, NormalActionFactory
from human_robot_negotiation.HANT.utility_space import UtilitySpace 


class HolidayOfferClassifier:
	def __init__(self, human_utility_space: UtilitySpace, action_factory):
		self.stop_words = set(['my', 'myself', 'we', 'our', 'ours', 'ourselves', "you're", "you've", "you'll", "you'd", 'your', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she',
		"she's", 'her', 'hers', 'herself', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', "that'll", 'these', 'those', 'am', 'are', 'was',
		'were', 'be', 'been', 'being', 'has', 'had', 'having', 'does', 'did', 'doing', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'with', 'about', 'against', 'between', 'into',
		'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
		'how', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'nor', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've",
		'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma',
		'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't", "could", "the"])

		#self.keywords = human_utility_space.issue_names[:]
		
		self.action_factory: AbstractActionFactory = action_factory

		self.value_issue_dict = {} # Keep value as key that keeps issue. 

		#[list(zip([[x] * len(dicts[x]) for x in dicts.keys()], list(item.keys()))) for item in dicts.values()]

		self.issue_values_list = human_utility_space.issue_values_list

		self.domain_keywords = list(itertools.chain(*self.issue_values_list.values()))

		issues_list = [[x] * len(self.issue_values_list[x]) for x in self.issue_values_list.keys()]
		self.value_issue_dict = dict(ChainMap(*[dict(zip(*i)) for i in zip(self.issue_values_list.values(), issues_list)]))
		self.keywords = self.value_issue_dict.keys()

		# for idx, keyword in enumerate(self.keywords):
		# 	self.issue_values_dict[keyword] = human_utility_space.issue_values_list[idx]

		self.OFFER_SENTENCES = {}
		self.ARGUMENT_SENTENCES = []

	def preprocess_input(self, input):
		input = input.lower()
		offer_verbs = ["go", "sleep", "rest", "drive", "take", "stay"]
		# Fix would like to 'verb' part in input.
		for offer_verb in offer_verbs:
			# TODO FIX REGEX DUDE.
			input = re.sub(r'\b' + '(would like to |want to |need to |like to )' + re.escape(offer_verb) + r'\b', offer_verb, input)
		# Fix don't like don't want sentences.
		for offer_verb in offer_verbs:
			for keyword in self.keywords:
				# replace sentences such as I dont want apple, i dont want any apple etc.
				input = re.sub(r'\b' + "(don't |do not )" + offer_verb + ".*" + keyword + r'\b', "", input)
				input = re.sub(r'\b' + 'instead of ' + keyword + r'\b', "", input)

		return input


	def get_offer_and_arguments(self, input):
		# Control the acceptance.
		processed_input = self.preprocess_input(input)

		is_acceptance = self.check_if_acceptance(processed_input)
		if is_acceptance:
			return self.action_factory.create_acceptance(), True

		tagged_words = self.tag_input_words(processed_input)
		# Merge numbers with after keywords.

		self.classify_sentences(tagged_words)

		is_complete = len(self.OFFER_SENTENCES.keys()) == len(self.issue_values_list.keys())
		
		print("OFFER SENTS: ", self.OFFER_SENTENCES)
		offer = self.action_factory.create_offer(self.OFFER_SENTENCES)
		
		if is_complete:
			self.OFFER_SENTENCES = {}

		return offer, is_complete

	def tag_input_words(self, processed_input):
		# Tokenize the input
		word_tokens = word_tokenize(processed_input)
		# Filter the input
		filtered_sentence = [w for w in word_tokens if not w in self.stop_words]
		# Tag the filtered input.
		tagged_words = nltk.pos_tag(filtered_sentence, tagset="universal")
		# Convert tagged word tuples to list in order to modify.
		tagged_words_list = [list(tagged_word) for tagged_word in tagged_words]
		
		skip_next=False
		for word_index, (word, tag) in enumerate(tagged_words_list):
			# Search for lower i and convert it to proper I.
			if skip_next:
				continue
			if word in ["i", "ill"]:
				tagged_words_list[word_index][0] = "I"
				tagged_words_list[word_index][1] = "PRON"
				
			if word.lower() in ["one", "two", "three", "1", "2", "3", "a"] and len(tagged_words_list) > (word_index + 1):
				if word.lower() == "one" or word.lower() == "a":
					word = "1"
				elif word.lower() == "two":
					word = "2"
				elif word.lower() == "three":
					word = "3" 

				check_words = ["week", "weeks", "days"]    

				min_keyword = None
				min_distance = 3        

				for check_word in check_words:
					lev_cost = nltk.edit_distance(tagged_words_list[word_index + 1][0].lower(), check_word)
					if lev_cost < min_distance:
						min_distance = lev_cost
						min_keyword = check_word

				if min_keyword:
					tagged_words_list[word_index][0] = word.lower() + " " + min_keyword
					tagged_words_list[word_index][1] = "NOUN"
					skip_next = True

			# Fix wrong tagging for keywords.
			for keyword in self.keywords:
				if (word == keyword or word == keyword + 's') and tag != 'NOUN':
					tagged_words_list[word_index][1] = "NOUN"
		return tagged_words_list   

	def check_if_acceptance(self, input):
		input = input.lower()
		print("ACCEPTANCE CHECK: ", input)
		# Check if the user accepts the offer.
		if (
			len(re.findall(r"\b" + "(no |not )deal" + r"\b", input)) == 0
			and len(re.findall(r"\b" + "(deal|yes|agree|accept)" + r"\b", input)) > 0
			and len(
				re.findall(
					r"\b"
					+ "(have|take|get|want|like|need|cant|can't|can not|cannot|won't|will not|if|do not|don't|keep)"
					+ r"\b",
					input,
				)
			)
			== 0
		):
			return True
		else:
			return False

	def classify_sentences(self, words):
		# Iterate through all sentences for offer.
		for word_tuple in words:
			word = word_tuple[0]
			#print("look here: ", word_tuple)
			#print(self.value_issue_dict.keys())

			if word in self.value_issue_dict.keys():
				self.OFFER_SENTENCES[self.value_issue_dict[word]] = word.lower()
			else:
				min_distance = 2
				min_keyword = None
				for value_name in self.value_issue_dict.keys():
					lev_cost = nltk.edit_distance(value_name, word.lower())
					if lev_cost < min_distance:
						min_distance = lev_cost
						min_keyword = value_name
				if min_keyword: 		
					self.OFFER_SENTENCES[self.value_issue_dict[min_keyword]] = min_keyword.lower()			


	def check_if_offer_is_done(self):
		# Control each keyword in senteces.
		for offer_keyword in self.OFFER_SENTENCES.keys():
			if len(self.keywords) == 0:
				return True
			else:
				for keyword in self.keywords:
					if offer_keyword in keyword or keyword in offer_keyword:
						self.keywords.remove(keyword)
				if len(self.keywords) == 0:
					return True
		return False
