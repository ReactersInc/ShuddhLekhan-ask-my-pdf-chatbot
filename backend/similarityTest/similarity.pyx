from sentence_transformers import SentenceTransformer

from indicnlp.tokenize.indic_tokenize import trivial_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

english_stopwords = set(stopwords.words('english'))
from stopwords_hindi import hindi_sw
hindi_stopwords = hindi_sw.get_hindi_sw()


def preprocess_english(text: str) -> str:
    tokens = word_tokenize(text)
    filtered = [tok.lower() for tok in tokens if tok.isalpha() and tok.lower() not in english_stopwords]
    return ' '.join(filtered)


def preprocess_hindi(text: str) -> str:
    tokens = trivial_tokenize(text)
    if hindi_stopwords:
        filtered = [tok for tok in tokens
                    if tok.strip() 
                    and not all(ch in '.,।()[]{}—–-;' for ch in tok) 
                    and tok not in hindi_stopwords]
    else:
        filtered = tokens
    return ' '.join(filtered)


def main() -> None:
    eng1 = ("The Industrial Revolution, which began in Britain in the late eighteenth century, marked a profound shift from agrarian economies to industrialized societies. "
            "Fueled by innovations such as the steam engine and mechanized textile looms, factories sprang up across the countryside, enabling mass production at unprecedented scales. "
            "This rapid transformation not only increased output but also fundamentally altered patterns of work and daily life: people migrated from rural villages to burgeoning urban centers in search of steady wages. "
            "Nonetheless, the era laid the groundwork for modern infrastructure, with railways and canals weaving together once-isolated regions. By the mid–nineteenth century, the Industrial Revolution had swept beyond Britain’s borders, reshaping societies across Europe and North America. "
            "Its legacy endures in today’s global manufacturing networks and the very structure of modern cities.")
    eng2 = ("In the final decades of the 1700s, Great Britain experienced a dramatic metamorphosis known as the Industrial Revolution, transitioning society away from subsistence farming toward mechanized industry. "
            "Key breakthroughs—most notably James Watt’s improvements to the steam engine and the invention of spinning jennies—allowed entrepreneurs to establish large-scale mills and workshops. "
            "Villagers flooded into newly built towns where factories offered regular paychecks, forever changing the fabric of everyday existence. Yet with progress came repercussions: cramped tenements, polluted waterways, and a widening gulf between the prosperous mill proprietors and their overworked labor force. "
            "Despite these hardships, this period witnessed the birth of modern transport networks—steam locomotives and barges that linked raw-material sources to urban manufacturing hubs. By 1850, these innovations had propagated internationally, driving industrialization in France, Germany, and the United States. "
            "Today’s sprawling metropolitan areas and global trade corridors trace their roots back to those early factory towns and iron rails.")
    e1 = preprocess_english(eng1)
    e2 = preprocess_english(eng2)

    vec_en = TfidfVectorizer(ngram_range=(1,5), max_features=4000)
    m_en = vec_en.fit_transform([e1, e2])
    tfidf_sim_en = cosine_similarity(m_en)[0,1]

    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    emb_en = model.encode([eng1, eng2])
    bert_sim_en = cosine_similarity([emb_en[0]], [emb_en[1]])[0,0]

    ensemble_en = 0.4 * tfidf_sim_en + 0.6 * bert_sim_en
    print(f"EN TF-IDF: {tfidf_sim_en:.3f}, BERT: {bert_sim_en:.3f}, Ensemble: {ensemble_en:.3f}")

    text1 = "असम एक बहुभाषी प्रदेश है। यहाँ सौ से भी अधिक भाषाएँ एवं उपभाषाएँ विभिन्न जाति-जनजाति द्वारा बोली जाती हैं।"
    text2 = "असम एक अत्यंत बहुभाषी, सांस्कृतिक रूप से समृद्ध प्रदेश है। यहाँ सौ से भी अधिक प्रमुख भाषाएँ एवं उपभाषाएँ विभिन्न जाति-जनजाति (जैसे असमिया, बोडो, रबाहा, कार्बी) द्वारा जीवंत रूप में बोली जाती हैं।"
    h1 = preprocess_hindi(text1)
    h2 = preprocess_hindi(text2)

    vec_hi = TfidfVectorizer(ngram_range=(1,5), max_features=4000)
    m_hi = vec_hi.fit_transform([h1, h2])
    tfidf_sim_hi = cosine_similarity(m_hi)[0,1]

    emb_hi = model.encode([text1, text2])
    bert_sim_hi = cosine_similarity([emb_hi[0]], [emb_hi[1]])[0,0]

    ensemble_hi = 0.4 * tfidf_sim_hi + 0.6 * bert_sim_hi
    print(f"HI TF-IDF: {tfidf_sim_hi:.3f}, BERT: {bert_sim_hi:.3f}, Ensemble: {ensemble_hi:.3f}")

if __name__ == '__main__':
    main()
