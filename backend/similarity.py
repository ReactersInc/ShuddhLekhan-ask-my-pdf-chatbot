from sentence_transformers import SentenceTransformer

from indicnlp.tokenize.indic_tokenize import trivial_tokenize #for tf-idf tokenization
from sklearn.feature_extraction.text import TfidfVectorizer #for tf-idf vectorization
from sklearn.metrics.pairwise import cosine_similarity #for calculating tf-idf vectro similarity

from nltk.tokenize import word_tokenize #for eng tokenization
from nltk.corpus import stopwords 

english_stopwords = set(stopwords.words('english'))

def preprocess_english(text: str) -> str:
    tokens = word_tokenize(text)
    filtered = [
        tok.lower() for tok in tokens
        if tok.isalpha() and tok.lower() not in english_stopwords
    ]
    print("Original EN:", text)
    print("Tokens EN:  ", tokens)
    print("Filtered EN:", filtered)
    return ' '.join(filtered)

eng1 = "The Industrial Revolution, which began in Britain in the late eighteenth century, marked a profound shift from agrarian economies to industrialized societies. Fueled by innovations such as the steam engine and mechanized textile looms, factories sprang up across the countryside, enabling mass production at unprecedented scales. This rapid transformation not only increased output but also fundamentally altered patterns of work and daily life: people migrated from rural villages to burgeoning urban centers in search of steady wages. Nonetheless, the era laid the groundwork for modern infrastructure, with railways and canals weaving together once-isolated regions. By the mid–nineteenth century, the Industrial Revolution had swept beyond Britain’s borders, reshaping societies across Europe and North America. Its legacy endures in today’s global manufacturing networks and the very structure of modern cities."
eng2 = "In the final decades of the 1700s, Great Britain experienced a dramatic metamorphosis known as the Industrial Revolution, transitioning society away from subsistence farming toward mechanized industry. Key breakthroughs—most notably James Watt’s improvements to the steam engine and the invention of spinning jennies—allowed entrepreneurs to establish large-scale mills and workshops. Villagers flooded into newly built towns where factories offered regular paychecks, forever changing the fabric of everyday existence.A computer program can easily produce gibberish - especially if it has been provided with garbage beforehand. This program does something a little different. It takes a block of text as input and works out the proportion of characters within the text according to a chosen order. For example, an order of 2 means the program looks at pairs of letters, an order of 3 means triplets of letters and so on. The software can regurgitate random text that is controlled by the proportion of characters. The results can be quite surprising. Yet with progress came repercussions: cramped tenements, polluted waterways, and a widening gulf between the prosperous mill proprietors and their overworked labor force. Despite these hardships, this period witnessed the birth of modern transport networks—steam locomotives and barges that linked raw-material sources to urban manufacturing hubs. By 1850, these innovations had propagated internationally, driving industrialization in France, Germany, and the United States. Today’s sprawling metropolitan areas and global trade corridors trace their roots back to those early factory towns and iron rails."

e1 = preprocess_english(eng1)
e2 = preprocess_english(eng2)

vec = TfidfVectorizer(ngram_range=(1,5), max_features=4000)
m  = vec.fit_transform([e1, e2])
tfidf_sim_en = cosine_similarity(m)[0,1]

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
emb = model.encode([eng1, eng2])
bert_sim_en = cosine_similarity([emb[0]],[emb[1]])[0,0]


ensemble_score = 0.4 * tfidf_sim_en + 0.6 * bert_sim_en

print("TF-IDF Similarity:", f"{tfidf_sim_en:.3f}")
print("BERT Similarity:  ", f"{bert_sim_en:.3f}")
print("Ensemble Score:   ", f"{ensemble_score:.3f}")

if ensemble_score > 0.8:
    print("Likely Plagiarized")
elif ensemble_score > 0.5:
    print("Possible Plagiarism")
else:
    print("Likely Original")

from stopwords_hindi import hindi_sw
hindi_stopwords = hindi_sw.get_hindi_sw()

text1 = "असम एक बहुभाषी प्रदेश है। यहाँ सौ से भी अधिक भाषाएँ एवं उपभाषाएँ विभिन्न जाति-जनजाति द्वारा बोली जाती हैं।"
text2 = "असम एक अत्यंत बहुभाषी, सांस्कृतिक रूप से समृद्ध प्रदेश है। यहाँ सौ से भी अधिक प्रमुख भाषाएँ एवं उपभाषाएँ विभिन्न जाति-जनजाति (जैसे असमिया, बोडो, रबाहा, कार्बी) द्वारा जीवंत रूप में बोली जाती हैं।"

def preprocess_hindi(text):
    tokens = trivial_tokenize(text)
    if hindi_stopwords:
        filtered = [
    tok for tok in tokens
    if tok.strip() and not all(ch in '.,।()[]{}—–-;' for ch in tok) 
    and tok not in hindi_stopwords
    ]
    else:
        filtered = tokens
    print("Original Text:    ", text)
    print("Tokens:           ", tokens)
    print("After stop-words: ", filtered)
    return ' '.join(filtered)

tfidf_text1 = preprocess_hindi(text1)
tfidf_text2 = preprocess_hindi(text2)

vectorizer = TfidfVectorizer(ngram_range=(1, 5), max_features=4000)
tfidf_matrix = vectorizer.fit_transform([tfidf_text1, tfidf_text2])
tfidf_sim = cosine_similarity(tfidf_matrix)[0,1]

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
embeddings = model.encode([text1, text2])
bert_sim = cosine_similarity([embeddings[0]], [embeddings[1]])[0,0]

ensemble_score = 0.4 * tfidf_sim + 0.6 * bert_sim

print("TF-IDF Similarity:", f"{tfidf_sim:.3f}")
print("BERT Similarity:  ", f"{bert_sim:.3f}")
print("Ensemble Score:   ", f"{ensemble_score:.3f}")

if ensemble_score > 0.8:
    print("Likely Plagiarized")
elif ensemble_score > 0.5:
    print("Possible Plagiarism")
else:
    print("Likely Original")
