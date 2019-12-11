

"""
    Sample Run:
    python train.py

    Start training the framework. 
 
"""
import argparse
import numpy as np
import random

from util import *
from EM_Algorithm import *
from test.test_read_data_split import *
from hyperparameters import *

parser = argparse.ArgumentParser(description='Read XML data from files')
parser.add_argument('--dir_path'            , type=str, default='data/Bibtex'        , help='path of the directory containing data-file')
parser.add_argument('--data_filename'       , type=str, default='Bibtex_data.txt'    , help='rel path of data_filename')
parser.add_argument('--train_split_filename', type=str, default='bibtex_trSplit.txt' , help='rel path of train_split_filename')
parser.add_argument('--test_split_filename' , type=str, default='bibtex_tstSplit.txt', help='rel path of test_split_filename')
args = parser.parse_args()

# Get the data and the labels on the dataset
X, Y = get_data_labels_from_datafile(args.dir_path, args.data_filename)
X, Y = torch.tensor(X).float().to(device), torch.tensor(Y).float().to(device)

train_indices_for_each_split = get_indices_for_different_splits(args.dir_path, args.train_split_filename)
test_indices_for_each_split  = get_indices_for_different_splits(args.dir_path, args.test_split_filename)
num_splits = train_indices_for_each_split.shape[0]

# Get some stats
print("")
print("Number of splits             = {}".format(num_splits))
print("Train indices for each split =", train_indices_for_each_split.shape)
print("Test indices for each split  =", test_indices_for_each_split.shape)

num_all_labels  = Y.shape[1]
seen_label_indices = np.array(random.sample(range(num_all_labels), num_seen_labels))
print(seen_label_indices)

for split_idx in range(num_splits):
    train_indices = train_indices_for_each_split[split_idx]
    test_indices  = test_indices_for_each_split [split_idx]

    # Train data with seen and all labels
    train_X      = X[train_indices]
    train_Y_seen = Y[train_indices, seen_label_indices]
    train_Y      = Y[train_indices]

    # Test data with seen and all labels
    test_X      = X[test_indices]
    test_Y_seen = Y[test_indices, seen_label_indices]
    test_Y      = Y[test_indices]

    # Label co-occurrence matrix
    M = torch.matmul(train_Y.t(), train_Y)[seen_label_indices,:].float().to(device) 

    # Initialisation
    V    = torch.normal(mean = 0, std = np.sqrt(1/train_Y.shape[1]), size = (train_Y_seen.shape[1], K)).float().to(device)
    W    = torch.normal(mean = 0, std = np.sqrt(1/train_X.shape[1]), size = (train_X.shape[1], K)).float().to(device)
    U    = torch.matmul(train_X, W).to(device)
    beta = torch.normal(mean = 0, std = np.sqrt(1/M.shape[1]), size = (M.shape[1], K)).float().to(device)

    print("Train Data   X      shape =", train_X.shape)
    print("Train Labels Y seen shape =", train_Y_seen.shape)
    U, V, beta, W, psi = EM_algorithm(num_iterations, train_X, train_Y, train_Y_seen, V, U, M, W, beta, lambda_u, lambda_v, lambda_beta, lambda_w, lambda_psi, r, num_seen_labels, test_X, test_Y, test_Y_seen, topk, cyclic)

    # Get Train and Test precision
    precision_train = precision_at_k(train_X, train_Y_seen, W, beta, psi, topk)
    precision_test = precision_at_k(test_X, test_Y_seen, W, beta, psi, topk)
    print("                                         EM Algorithm Completed")
    print("\n==================================================================================================\n")
    print("Split_index= {:2d} Precision@{}_train= {:.4f} Precision@{}_test= {:.4f}".format(split_idx, topk, precision_train, topk, precision_test))
    break
