from globals import *
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import numpy as np
import re
import string


class Search:
    lemmer = WordNetLemmatizer()
    def preprocess(self, text):
        text = text.lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = re.sub(' +', ' ', text)
        tokens = word_tokenize(text)
        stop_words = stopwords.words('english')
        tokens = [self.lemmer.lemmatize(token) for token in tokens if token not in stop_words]
        return tokens

    def preprocess_loc_string(self, text):
        text = text.lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = re.sub(' +', ' ', text)
        tokens = word_tokenize(text)
        stop_words = stopwords.words('english')
        tokens = [token for token in tokens if token not in stop_words]
        return tokens

    def init_index(self):
        # events = list(db.events.find({}, {"event-details": 1, "eid": 1, "event-title": 1}))
        db.document_count.insert({"doc_count": 0})
        events = list(db.events.find(
            {"event-details": {"$exists": True}},
            {"event-details": 1, "eid": 1, "event-title": 1, "location":1}
        ))

        for event in events:
            self.update_index(event)

    def compute_score(self, query):
        query = self.preprocess(query)
        doc_count = db.document_count.find_one()["doc_count"]
        event_listings = list(db.events.find({"event-details": {"$exists": True}}))
        event_index = [event['eid'] for event in event_listings]
        print(event_index)
        event_listings = dict(zip(event_index, event_listings))

        scores = dict.fromkeys(event_index, 0)
        for term in query:
            counts = db.index.find_one({"term": term})
            if counts is not None:
                tf = counts['tf']
                idf = doc_count/counts['df']
                for key, val in tf.items():
                    scores[key] += val*np.log(idf)
            title_counts = db.index_title.find_one({"term": term})
            if title_counts is not None:
                for doc in title_counts["documents"]:
                    scores[doc] += 1

            location_counts = db.index_location.find_one({"term": term})
            if location_counts is not None:
                for doc in location_counts["documents"]:
                    scores[doc] += 2

        scores = dict(filter(lambda x: x[1] > 0, scores.items()))
        print(scores)
        scores = sorted(scores.items(), key=lambda kv: kv[1])
        scores.reverse()
        ranks = [score[0] for score in scores]
        ranked_docs = [event_listings[rank] for rank in ranks]
        for doc in ranked_docs:
            del doc['_id']
        return ranked_docs

    def update_index(self, event):
        print(event)
        description = self.preprocess(event["event-details"])
        title = self.preprocess(event["event-title"])
        location = self.preprocess(event["location"])

        for word in description:
            doc = db.index.find_one({"term": word})
            if doc is not None:
                db.index.update(
                    {"term": word},
                    {
                        "$inc": {"df": 1},
                        "$set": {"tf.{}".format(event["eid"]): description.count(word)/len(description)}
                    }
                )
            else:
                tf_dict = {"term": word}
                tf_dict["tf"] = {event["eid"]: description.count(word)/len(description)}
                tf_dict["df"] = 1
                db.index.insert(tf_dict)

        for word in title:
            doc = db.index_title.find_one({"term": word})
            if doc is None:
                index_entry = {"term": word, "documents": [event["eid"]]}
                db.index_title.insert(index_entry)
            else:
                db.index_title.update({"term": word}, {"$push": {"documents": event["eid"]}})

        for word in location:
            doc = db.index_location.find_one({"term": word})
            if doc is None:
                index_entry = {"term": word, "documents": [event['eid']]}
                db.index_location.insert(index_entry)
            else:
                db.index_location.update({"term": word}, {"$push": {"documents": event["eid"]}})
        db.document_count.update({}, {"$inc": {"doc_count": 1}})


# searcher = Search()
# searcher.init_index()
# print(searcher.compute_score("volunteer at a local doggos soup school"))
# print(searcher.compute_score("doggos school"))
