from keybert import KeyBERT

kw_model = KeyBERT("all-mpnet-base-v2")

def extract_keywords_bert(text):
    keywords = kw_model.extract_keywords(
        text,
        keyphrase_ngram_range=(1, 2),
        stop_words="english",
        top_n=5
    )
    return [kw for kw, score in keywords]


print(extract_keywords_bert("Forests are crucial for climate regulation, biodiversity, carbon storage, and resources. Monitoring them is es- sential for managing climate change, deforestation, and forest health, yet traditional surveys are labor-intensive and hard to scale. UAV-based RGB imagery (e.g., Acacia, Oil Palm [9] [10]) and LiDAR point clouds (e.g., FOR-instance [8]) have enabled automated monitoring. Early meth- ods using manual interpretation or hand-crafted features (e.g., height thresholds, template matching [4], YOLOv5 on CHM [5]) struggled under diverse conditions. UAV and LiDAR data provide high-resolution spatial and 3D structure, supporting canopy measurement and under- story analysis. Deep learning offers scalable and accurate solutions. Models like ForAINet [2] and TreeFormer [3] integrate with UAV pipelines for near real-time monitoring, en- abling tree detection, species classification, and anomaly detection. This survey reviews recent DL approaches using UAV and LiDAR data, focusing on (i) tree detec- tion, (ii) species classification, and (iii) forest anomaly detection. We cover datasets, challenges, and strategies such as data augmentation, semi-supervised learning, and image mosaicking, and discuss future directions for robust, scalable, and cost-effective forest analysis. Instead of listing existing models separately, this survey provides a unified view of how deep learning has been applied across forest-monitoring modalities and tasks. We propose a structured taxonomy that categorizes studies by data type (RGB, LiDAR, multimodal), task (tree detection, species classification, anomaly detec- tion), and model architecture (2D CNNs, Transformers, 3D, attention-based). This organization clarifies relation- ships between datasets, learning strategies, and perfor- mance outcomes. Detailed comparisons are summarized in Tables I–III, which collectively represent the taxon- omy of data, models, and tasks in this field. The paper is structured as follows: Section 2 intro- duces datasets and modalities; Section 3 reviews detec- tion, classification, and anomaly methods; Section 4 cov- ers network architectures; Section 5 discusses training strategies; Section 6 presents performance evaluation; Section 7 concludes and gives future directions."))