#------------------------------------------------------------------------
# CLUSTERING FUNCTIONS
#------------------------------------------------------------------------
from sentence_transformers import SentenceTransformer
import hdbscan
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import silhouette_score
from clustering_helper import create_disaster_table, load_existing_disasters, update_bluesky_disaster_column, remove_noise_post, insert_new_disaster, update_disaster_centroid, get_unprocessed_posts
from generate_metadata import generate_disaster_metadata
import umap
import matplotlib.pyplot as plt
import datetime
import os
import json


SIMILARITY_THRESHOLD = 0.9
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

def embed_posts(posts):
    print("Embedding posts...")

    if not posts:
        print("No posts to embed.")
        return np.array([])

    texts = [post[1] for post in posts]  # post set consists of (Post_ID, Post_Original_Text)
    embeddings = model.encode(texts)
    print(f"Generated embeddings for {len(posts)} posts.")
    return embeddings

# cluster new posts based on embeddings
def cluster_and_get_centroids(embeddings, posts):
    print("Clustering posts using HDBSCAN...")
    clusterer = hdbscan.HDBSCAN(min_cluster_size=2)
    labels = clusterer.fit_predict(embeddings)

    clustered_posts = {}
    noise_posts = []

    for i, label in enumerate(labels):
        if label == -1:
            noise_posts.append((posts[i], embeddings[i]))  # keep noise post + vector
        else:
            clustered_posts.setdefault(label, []).append((posts[i], embeddings[i]))

    # compute centroids of each cluster
    cluster_centroids = {}
    for cluster_id, items in clustered_posts.items():
        vectors = [vec for _, vec in items]
        cluster_centroids[cluster_id] = np.mean(vectors, axis=0)

    print(f"Clustering complete. Found {len(clustered_posts)} clusters and {len(noise_posts)} noise posts.")
    return clustered_posts, cluster_centroids, noise_posts

# check to see if any new clusters can be merged with existing clusters
# if so, merge them and recompute the disaster's centroid
def assign_clusters_to_disasters(cluster_centroids, existing_disasters):
    print("Assigning clusters to existing disasters...")
    assignments = {}
    new_disaster_clusters = []

    for cluster_id, new_centroid in cluster_centroids.items():
        matched = False
        for disaster_id, existing_centroid in existing_disasters:
            similarity = cosine_similarity([new_centroid], [existing_centroid])[0][0]
            if similarity > SIMILARITY_THRESHOLD:
                assignments[cluster_id] = disaster_id
                matched = True

                updated_centroid = np.mean([existing_centroid, new_centroid], axis=0)
                update_disaster_centroid(disaster_id, updated_centroid)
                break

        if not matched:
            new_disaster_clusters.append(cluster_id)

    print(f"Assignments complete. Assigned {len(assignments)} clusters to existing disasters.")
    print(f"{len(new_disaster_clusters)} new clusters identified.")
    return assignments, new_disaster_clusters

# match embeddings marked as noise to existing clusters or drop them
def assign_noise_to_disasters(noise_posts, existing_disasters):
    print("Assigning noise posts to existing clusters or dropping them...")
    assigned = []
    dropped = []

    for post, embedding in noise_posts:
        matched = False
        for disaster_id, centroid in existing_disasters:
            similarity = cosine_similarity([embedding], [centroid])[0][0]
            if similarity > SIMILARITY_THRESHOLD:
                assigned.append((post[0], disaster_id))  # Post_ID, Disaster_ID
                matched = True

                updated_centroid = np.mean([centroid, embedding], axis=0)
                update_disaster_centroid(disaster_id, updated_centroid)
                break

        if not matched:
            dropped.append(post[0])  # Just Post_ID to drop later

    print(f"Assigned {len(assigned)} noise posts to existing clusters.")
    print(f"Dropped {len(dropped)} noise posts.")
    return assigned, dropped

# for new disaster clusters, query an llm to extract summaries, name of disaster, etc
def create_new_disasters_and_assign(clustered_posts, new_disaster_clusters, cluster_centroids):
    print("Creating new disasters and assigning posts...")
    post_to_disaster = []

    # Build input to LLM for all new clusters 
    cluster_inputs = [] 
    cluster_id_list = [] 
    cluster_centroid_list = [] 

    for cluster_id in new_disaster_clusters: 
        cluster_posts = clustered_posts[cluster_id]
        post_texts = [(post[0], post[1]) for post, _ in cluster_posts]
        # NOTE: This should later be based on clusters, not just today's time
        approx_date = datetime.datetime.now().strftime("%Y-%m-%d")

        cluster_inputs.append({
            "date": approx_date, 
            "posts": post_texts
        })

        cluster_id_list.append(cluster_id)
        cluster_centroid_list.append(cluster_centroids[cluster_id])
    
    print("LLM input preview:")
    print(json.dumps(cluster_inputs, indent=2, ensure_ascii=False))

    # Generate metadata for all clusters 
    metadata_list = generate_disaster_metadata(cluster_inputs)

    # Iterate through results and insert into DB
    for metadata, cluster_id, centroid in zip(metadata_list, cluster_id_list, cluster_centroid_list): 
        if not metadata or metadata.get("error"): 
            print(f"LLM failed to generate metadata. Skipping Cluster {cluster_id}")
            continue 
            
        name = metadata["disaster_name"]
        location_name = metadata["disaster_location"]
        lat = float(metadata["location"]["latitude"])
        long = float(metadata["location"]["longitude"])
        radius = float(metadata["location"]["radius"])
        date = metadata["start_date"]
        summary = metadata["summary"]

        print(f"Inserting disaster: {name} Cluster {cluster_id}")
        disaster_id = insert_new_disaster(name, location_name, centroid, lat, long, radius, date, summary)
        
        for post, _ in clustered_posts[cluster_id]:
            post_to_disaster.append((post[0], disaster_id))

    print(f"Created {len(new_disaster_clusters)} new disasters.")
    return post_to_disaster

# logs the performance of clustering at any given time and saves visualization of clusters
def evaluate_final_clusters(post_to_disaster, embeddings_dict):
    if len(post_to_disaster) < 2:
        print("Not enough posts to evaluate final clustering.")
        return

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    embeddings = []
    labels = []

    for post_id, disaster_id in post_to_disaster:
        if post_id in embeddings_dict:
            embeddings.append(embeddings_dict[post_id])
            labels.append(disaster_id)

    embeddings = np.array(embeddings)

    # calculate silhouette score
    try:
        silhouette = silhouette_score(embeddings, labels)
        print(f"Final Silhouette Score: {silhouette:.4f}")
    except Exception as e:
        print(f"Could not compute silhouette score: {e}")
        silhouette = None
    
    plot_dir = os.path.join(os.path.dirname(__file__), "cluster_plots")
    os.makedirs(plot_dir, exist_ok=True)
    plot_file = os.path.join(plot_dir, f"clusters_{timestamp}.png")

    # log to file
    with open("clustering_metrics_log.txt", "a", encoding="utf-8") as f:
        f.write(f"\n--- FINAL CLUSTER EVAL {timestamp} ---\n")
        f.write(f"Total Assigned Posts: {len(post_to_disaster)}\n")
        f.write(f"Unique Disaster Clusters: {len(set(labels))}\n")
        f.write(f"Silhouette Score: {silhouette if silhouette else 'N/A'}\n")

    # create cluster visualizations
    try:
        reducer = umap.UMAP()
        reduced = reducer.fit_transform(embeddings)

        plt.figure(figsize=(10, 7))
        scatter = plt.scatter(reduced[:, 0], reduced[:, 1], c=labels, cmap="tab20", s=10)
        plt.colorbar(scatter, label='Disaster ID')
        plt.title(f"Final Cluster Plot - {timestamp}")
        plt.savefig(plot_file)
        plt.close()
        print(f"Final cluster plot saved")
    except Exception as e:
        print(f"Error generating final cluster plot: {e}")

def cluster_and_process_posts():
    print("Processing and assigning posts...")
    create_disaster_table()
    posts = get_unprocessed_posts()
    embeddings = embed_posts(posts)

    existing_disasters = load_existing_disasters()
    clustered_posts, cluster_centroids, noise_posts = cluster_and_get_centroids(embeddings, posts)

    assignments, new_disaster_clusters = assign_clusters_to_disasters(cluster_centroids, existing_disasters)

    post_to_disaster = []
    for cluster_id, disaster_id in assignments.items():
        for post, _ in clustered_posts[cluster_id]:
            post_to_disaster.append((post[0], disaster_id))

    # create new disaster
    new_disaster_assignments = create_new_disasters_and_assign(clustered_posts, new_disaster_clusters, cluster_centroids)
    post_to_disaster.extend(new_disaster_assignments)

    # handle noise
    noise_assignments, noise_to_drop = assign_noise_to_disasters(noise_posts, existing_disasters)
    post_to_disaster.extend(noise_assignments)

    if post_to_disaster:
        update_bluesky_disaster_column(post_to_disaster)

    # can also just drop rows where disaster_id = null
    print(f"Dropping {len(noise_to_drop)} posts")
    for post_id in noise_to_drop:
        remove_noise_post(post_id)

    embeddings_dict = {post[0]: emb for post, emb in zip(posts, embeddings)}
    evaluate_final_clusters(post_to_disaster, embeddings_dict)

    print("Process complete.")
    return len(post_to_disaster), len(noise_to_drop)

