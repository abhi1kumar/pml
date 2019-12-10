

"""
    Sample Run:
    python train.py

    Start training the framework. 
 
"""
import argparse
import numpy as np

from util import *
from EM_Algorithm import *
from test.test_read_data_split import *

parser = argparse.ArgumentParser(description='Read XML data from files')
parser.add_argument('--dir_path'            , type=str, default='Bibtex'        , help='path of the directory containing data-file')
parser.add_argument('--data_filename'       , type=str, default='Bibtex_data.txt'    , help='rel path of data_filename')
parser.add_argument('--train_split_filename', type=str, default='bibtex_trSplit.txt' , help='rel path of train_split_filename')
parser.add_argument('--test_split_filename' , type=str, default='bibtex_tstSplit.txt', help='rel path of test_split_filename')
args = parser.parse_args()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

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

num_iterations  = 100
num_seen_labels = 110
num_all_labels  = Y.shape[1]

lambda_u    = 1.0
lambda_v    = 1.0
lambda_beta = 1.0
lambda_w    = 1.0
lambda_psi  = 1.0
r           = 5.0
K           = 500
topk        = 5
M = torch.matmul(Y.t(), Y)[:num_seen_labels,:].float().to(device)  #label co-occurrence matrix

for split_idx in range(num_splits):
    split = train_indices_for_each_split[split_idx]
    train_X = X[split, :]
    train_Y = Y[split, :num_seen_labels]

    # Initialisation
    V    = torch.rand(train_Y.shape[1], K).float().to(device)
    W    = torch.rand(train_X.shape[1], K).float().to(device)
    U    = torch.matmul(train_X, W).to(device)
    beta = torch.rand(M.shape[1], K).float().to(device)

    U, V, beta, W, psi = EM_algorithm(num_iterations, train_X, train_Y, V, U, M, W, beta, lambda_u, lambda_v, lambda_beta, lambda_w, lambda_psi, r, num_seen_labels)
    precision = precision_at_k(X, Y, W, beta, psi, topk)
    print("Split index : {} \t Precision : {}".format(split_idx, precision))
