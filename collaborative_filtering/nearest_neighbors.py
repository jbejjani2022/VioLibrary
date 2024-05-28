import io  # noqa
import csv

from surprise import Reader, Dataset, get_dataset_dir, KNNBaseline

def read_item_names():
    rid_to_name = {}
    name_to_rid = {}
    with open('data/works.csv', newline='', encoding='ISO-8859-1') as csvfile:
        work_reader = csv.reader(csvfile)
        next(work_reader)
        for row in work_reader:
            rid = row[0]
            name = row[2]
            rid_to_name[rid] = name
            name_to_rid[name] = rid
            
    return rid_to_name, name_to_rid


# Load in dataset
data_path = 'data/favorites.csv'
reader = Reader(line_format = 'user item rating', sep=',', skip_lines=1)
dataset = Dataset.load_from_file(data_path, reader=reader)
# Build full Surprise training set from dataset
trainset = dataset.build_full_trainset()

# Define similarity measure
sim_options = {
    'name': 'cosine',
    'user_based': False # using item-based collaborative filtering
}

# Train the algorithm to compute the similarities between items
# sim_options = {"name": "pearson_baseline", "user_based": False}
algo = KNNBaseline(sim_options=sim_options)
algo.fit(trainset)

# Read the mappings raw id <-> movie name
rid_to_name, name_to_rid = read_item_names()

# Retrieve inner id of the work
work = 'Partita no. 2 for Solo Violin in D minor, BWV.1004'
work_raw_id = name_to_rid[work]
work_inner_id = algo.trainset.to_inner_iid(work_raw_id)

# Retrieve inner ids of the nearest neighbors of the work
work_neighbors = algo.get_neighbors(work_inner_id, k=10)

# Convert inner ids of the neighbors into names.
work_neighbors = (
    algo.trainset.to_raw_iid(inner_id) for inner_id in work_neighbors
)
work_neighbors = (rid_to_name[rid] for rid in work_neighbors)

print()
print(f"The 3 nearest neighbors of {work}:")
for work in work_neighbors:
    print(work)