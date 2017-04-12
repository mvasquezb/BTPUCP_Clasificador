from nltk.corpus import stopwords
import string
import re

from nltk.stem.snowball import SpanishStemmer


class TextProcessor:
    lemmatizer = None
    stopEnglish = None
    stopSpanish = None
    spanishStemmer = None

    def __init__(self):
        # self.lemmatizer = treetaggerwrapper.TreeTagger(TAGLANG='es')
        self.stopEnglish = stopwords.words('english')
        self.stopSpanish = stopwords.words('spanish')
        self.stopSpanish.append('y/o')
        self.spanishStemmer = SpanishStemmer()

    def _remove_numbers(self, text):
        "Elimina los números del texto"

        return ''.join([letter for letter in text if not letter.isdigit()])

    def _remove_punctuation(self, text):
        "Elimina los signos de puntuacion del texto"

        regex = re.compile('[%s]' % re.escape(string.punctuation))
        return regex.sub(' ', text)

    def preprocessText(self, text):
        text = text.lower()
        text = self._remove_punctuation(text)
        text = self._remove_numbers(text)
        return text

    def lematizeText(self, text):
        newText = ""
        firstElement = 0
        firstWord = True
        for word in text.split():
            if word not in self.stopEnglish and word not in self.stopSpanish:
                word = word.replace("\ufeff", "")
                lemmaResult = self.lemmatizer.tag_text(word)
                # Return [[word,type of word, lemma]]
                if (len(lemmaResult) != 0):
                    word = lemmaResult[firstElement].split()[2]
                    if firstWord:
                        newText += word
                        firstWord = False
                    else:
                        newText += " " + word
        return newText

    def stemText(self, text):
        newText = ""
        firstWord = True
        for word in text.split():
            if word not in self.stopEnglish and word not in self.stopSpanish:
                word = word.replace("\ufeff", "")
                wordStemmed = self.spanishStemmer.stem(word)
                if firstWord:
                    newText += wordStemmed
                    firstWord = False
                else:
                    newText += " " + wordStemmed
        return newText
