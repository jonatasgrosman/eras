class FreelingConstants_PT_BR(object):

	config_file = 'pt.cfg'

	tagset_positional = {"category_back":{"A":"adjective","C":"conjunction","D":"determiner","N":"noun","P":"pronoun","R":"adverb","S":"adposition","V":"verb","Z":"number","W":"date","I":"interjection"},
							"category":{"adjective":{"A"},"conjunction":{"C"},"determiner":{"D"},"noun":{"N"},"pronoun":{"P"},"adverb":{"R"},"adposition":{"S"},"verb":{"V"},"number":{"Z"},"date":{"W"},"interjection":{"I"}},
							 "type":{"adjective":{"O","Q","P"},"conjunction":{"C","S"},"determiner":{"A","D","E","I","T","N","P"},"noun":{"C","P"},"pronoun":{"D","E","I","T","N","P","R"},"adverb":{"N","G"},"adposition":{"P"},"verb":{"M","A","S"},"number":{"d","m","p","u"}},
							 "degree":{"adjective":{"S","V"},"noun":{"A","D"}},
							 "gen":{"adjective":{"F","M","C"},"determiner":{"F","M","C","N"},"noun":{"F","M","C","N"},"pronoun":{"F","M","C","N"},"verb":{"F","M","C","N"}},
							 "num":{"adjective":{"S","P","N"},"determiner":{"S","P","N"},"noun":{"S","P","N"},"pronoun":{"S","P","N"},"verb":{"S","P"}},
							 "possessorpers":{"adjective":{1,2,3}},
							 "possessornum":{"adjective":{"S","P","N"},"determiner":{"S","P"}},
							 "person":{"determiner":{1,2,3},"pronoun":{1,2,3},"verb":{1,2,3}},
							 "neclass":{"noun":{"S","G","O","V"}},
						 	 "nesubclass":{"noun":{}},
							 "case":{"pronoun":{"N","A","D","O"}},
							 "polite":{"pronoun":"P"},
							 "mood":{"verb":{"I","S","M","P","G","N"}},
							 "tense":{"verb":{"P","I","F","S","C"}},
	}

	tagorder_positional = {"adjective":["category","type","degree","gen","num","possessorpers","possessornum"],
							"conjunction":["category","type"],
							"determiner":["category","type","person","gen","num","possessornum"],
							"noun":["category","type","gen","num","neclass","nesubclass","degree"],
							"pronoun":["category","type","person","gen","num","case","polite"],
							"adverb":["category","type"],
							"adposition":["category","type"],
							"verb":["category","type","mood","tense","person","num","gen"],
							"number":["category","type"],
							"date":["category"],
							"interjection":["category"],
	}

	tagset_non_positional = {"Fd":["punctuation","colon"], "Fc":["punctuation","comma"],"Flt":["punctuation","curlybracket","close"],
							 "Fla":["punctuation","curlybracket","open"], "Fs":["punctuation","etc"], "Fat":["punctuation","exclamationmark","close"],
							 "Faa":["punctuation","exclamationmark","open"],"Fg":["punctuation","hyphen"],"Fz":["punctuation","other"],
							 "Fpt":["punctuation","parenthesis","close"],"Fpa":["punctuation","parenthesis","open"],
							 "Ft":["punctuation","percentage"],"Fp":["punctuation","period"],"Fit":["punctuation","questionmark","close"],
							 "Fia":["punctuation","questionmark","open"],"Fe":["punctuation","quotation"],
							 "Frc":["punctuation","quotation","close"],"Fra":["punctuation","quotation","open"],
							 "Fx":["punctuation","semicolon"],"Fh":["punctuation","slash"],
							 "Fct":["punctuation","squarebracket","close"], "Fca":["punctuation","squarebracket","open"]}

	tagorder_non_positional = {"punctuation":["pos","type","punctenclose"]}

class FreelingConstants_EN_US(object):

	config_file = 'en.cfg'

	tagset_positional = {"category_back":{"Z":"number","W":"date","I":"interjection"},
						 "category":{"number":"Z", "date":"W", "interjection":"I"},
						 "type":{"number":{"d","m","p","u"}}}


	tagorder_positional = {"number":['category','type'],
						   "date":['category'],
						   "interjection":['category']}

	tagset_non_positional = {"JJ":["adjective"],"JJR":["adjective","comparative"],"JJS":["adjective","superlative"],
							 "POS":["adposition","possessive"],"RB":["adverb","general"],"RBR":["adverb","general","comparative"],
							 "RBS":["adverb","general","superlative"],"WRB":["adverb","interrogative"],
							 "CC":["conjunction","coordinating"], "DT":["determiner"], "WDT":["determiner","interrogative"],
							 "PDT":["determiner","predeterminer"], "UH":["interjection"], "NNS":["noun","common","plural"],
					 		 "NN":["noun","common","singular"], "NNP":["noun","proper"], "NP00000":["noun","proper"],
							 "NP":["noun","proper"], "NP00G00":["noun","proper","location"],
							 "NP00O00":["noun","proper","organization"], "NP00V00":["noun","proper","other"],
							 "NP00SP0":["noun","proper","person"], "NNPS":["noun","proper","plural"],
							 "RP":["particle"], "TO":["particle","to"], "IN":["preposition"],
							 "EX":["pronoun"], "WP":["pronoun","interrogative"], "PRP":["pronoun","personal"],
							 "PRP$":["pronoun","possessive"], "WP$":["pronoun","possessive"],
							 "MD":["verb","modal"], "VBG":["verb","gerund"], "VB":["verb","infinitive"],
							 "VBN":["verb","participle"], "VBD":["verb","past"], "VBP":["verb","personal"], "VBZ":["verb","personal","3"],
							 "Fd":["punctuation","colon"], "Fc":["punctuation","comma"],"Flt":["punctuation","curlybracket","close"],
							 "Fla":["punctuation","curlybracket","open"], "Fs":["punctuation","etc"], "Fat":["punctuation","exclamationmark","close"],
							 "Faa":["punctuation","exclamationmark","open"],"Fg":["punctuation","hyphen"],"Fz":["punctuation","other"],
							 "Fpt":["punctuation","parenthesis","close"],"Fpa":["punctuation","parenthesis","open"],
							 "Ft":["punctuation","percentage"],"Fp":["punctuation","period"],"Fit":["punctuation","questionmark","close"],
							 "Fia":["punctuation","questionmark","open"],"Fe":["punctuation","quotation"],
							 "Frc":["punctuation","quotation","close"],"Fra":["punctuation","quotation","open"],
							 "Fx":["punctuation","semicolon"],"Fh":["punctuation","slash"],
							 "Fct":["punctuation","squarebracket","close"], "Fca":["punctuation","squarebracket","open"]}

	tagorder_non_positional = {"punctuation":["pos","type","punctenclose"], "adjective":["pos","degree"],
							   "adposition":["pos","type"],"adverb":["pos","type","degree"],"conjunction":["pos","type"],
							   "determiner":["pos","type"], "interjection":["pos"],"noun":["pos","type","num/neclass"],
							   "particle":["pos","type"], "preposition":["pos"],
							   "pronoun":["pos","type"], "verb":["pos","type/vform","person"]}
