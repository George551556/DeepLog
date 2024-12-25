# Import pytorch
import torch

# Import DeepLog and Preprocessor
from deeplog              import DeepLog
from deeplog.preprocessor import Preprocessor

# Imports for showing metrics
import numpy as np
from sklearn.metrics import classification_report

# lkz import
from datetime import datetime

##############################################################################
#                                 Load data                                  #
##############################################################################

# Create preprocessor for loading data
preprocessor = Preprocessor(
    length  = 20,           # Extract sequences of 20 items
    timeout = float('inf'), # Do not include a maximum allowed time between events
)

# Load normal data from HDFS dataset
X, y, label, mapping = preprocessor.text(
    path    = "./data/systemd-resolve_net.txt",
    verbose = False,
    mapping = {i: i for i in range(0, 99)}
    # nrows   = 10_000, # Uncomment/change this line to only load a limited number of rows
)

# Split in train & test data (80:20 ratio)
X_train = X[:4*X.shape[0]//5 ]
X_test  = X[ 4*X.shape[0]//5:]
y_train = y[:4*y.shape[0]//5 ]
y_test  = y[ 4*y.shape[0]//5:]

##############################################################################
#                                  DeepLog                                   #
##############################################################################

# Create DeepLog object
deeplog = DeepLog(
    input_size  = 100, # Number of different events to expect
    hidden_size = 64, # Hidden dimension, we suggest 64
    output_size = 100, # Number of different events to expect
)

# Optionally cast data and DeepLog to cuda, if available
# if torch.cuda.is_available():
#     # Set deeplog to device
#     deeplog = deeplog.to("cuda")

#     # Set data to device
#     X_train = X_train.to("cuda")
#     y_train = y_train.to("cuda")
#     X_test  = X_test .to("cuda")
#     y_test  = y_test .to("cuda")

def main(k1):
    # Train deeplog
    deeplog.fit(
        X          = X_train,
        y          = y_train,
        epochs     = 2000,
        batch_size = 128,
        optimizer  = torch.optim.Adam,
    )

    # 保存模型权重
    model_path = './weight-band-width.pth'
    torch.save(deeplog.state_dict(), model_path)
    # return
    # deeplog.load_state_dict(torch.load(model_path))

    # Predict normal data using deeplog
    y_pred, confidence = deeplog.predict(
        X = X_test,
        # 默认k=3
        k = k1, # Change this value to get the top k predictions (called 'g' in DeepLog paper, see Figure 6)
    )


    ################################################################################
    #                            Classification report                             #
    ################################################################################

    # Transform to numpy for classification report
    y_true = y_test.cpu().numpy()
    y_pred = y_pred.cpu().numpy()

    # Set prediction to "most likely" prediction
    prediction = y_pred[:, 0]
    # In case correct prediction was in top k, set prediction to correct prediction
    for column in range(1, y_pred.shape[1]):
        # Get mask where prediction in given column is correct
        mask = y_pred[:, column] == y_true
        # Adjust prediction
        prediction[mask] = y_true[mask]

    # Show classification report
    print(classification_report(
        y_true = y_true,
        y_pred = prediction,
        digits = 4,
        zero_division = 0,
    ))

if __name__ == "__main__":
    main(3)
    # main(9)