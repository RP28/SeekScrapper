import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

def analyze_jobs(csv_path="seek_jobs.csv", num_clusters=5, output_csv="seek_jobs_clustered.csv"):
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"CSV file not found at {csv_path}, run the scraper first")
        raise

    def print_basic_stats(df):
        print("Total jobs:", len(df))
        print(df[['Location','Company','Job Type','Work Arrangement']].describe(include='all'))
        print("\nTop locations:\n", df['Location'].value_counts().head())
        print("\nJob type distribution:\n", df['Job Type'].value_counts(dropna=False))
        print("\nWork arrangement distribution:\n", df['Work Arrangement'].value_counts(dropna=False))

    text_data = (df['Title'].fillna('') + ' ' + df.get('Short Description','').fillna('')).tolist()
    vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
    X = vectorizer.fit_transform(text_data)

    model = KMeans(n_clusters=num_clusters, random_state=42)
    labels = model.fit_predict(X)
    df['Cluster'] = labels

    order_centroids = model.cluster_centers_.argsort()[:, ::-1]
    terms = vectorizer.get_feature_names_out()

    print_basic_stats(df)
    print("\nCluster sizes:")
    print(df['Cluster'].value_counts())

    for i in range(num_clusters):
        print(f"\nCluster {i} top terms:")
        for ind in order_centroids[i, :10]:
            print(' %s' % terms[ind])

    df.to_csv(output_csv, index=False)
    print(f"Saved clustered data to {output_csv}")
    return df


if __name__ == "__main__":
    analyze_jobs()
