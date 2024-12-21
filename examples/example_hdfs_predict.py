# Import pytorch
import torch

# Import DeepLog and Preprocessor
from deeplog              import DeepLog
from deeplog              import MultiDimDeepLog
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
    path    = r"D:\my_projects\Python\DeepLog\examples\data\elec-data-oneline.txt",
    verbose = False,
    mapping = {i: i for i in range(0, 29)}
    # nrows   = 10_000, # Uncomment/change this line to only load a limited number of rows
)

# Split in train test data (20:80 ratio)
X_train = X[:4*X.shape[0]//5 ]
X_test  = X[ 4*X.shape[0]//5:]
y_train = y[:4*y.shape[0]//5 ]
y_test  = y[ 4*y.shape[0]//5:]

##############################################################################
#                                  DeepLog                                   #
##############################################################################

# Create DeepLog object
deeplog = MultiDimDeepLog(
    input_size  = 30, # Number of different events to expect
    hidden_size = 64, # Hidden dimension, we suggest 64
    output_size = 30, # Number of different events to expect
    num_dimensions=5, # Number of 1D data dimensions to process
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
# X_train重复num_dimensions次,变成X_train.shape[0],5,X_train.shape[1]
X_train = X_train.unsqueeze(1).repeat(1, deeplog.num_dimensions, 1)
X_test  = X_test .unsqueeze(1).repeat(1, deeplog.num_dimensions, 1)
# y_train重复num_dimensions次,变成X_train.shape[0],5
y_train = y_train.unsqueeze(1).repeat(1, deeplog.num_dimensions).view(-1, deeplog.num_dimensions)
y_test  = y_test .unsqueeze(1).repeat(1, deeplog.num_dimensions).view(-1, deeplog.num_dimensions)
# y_train = y_train.unsqueeze(1).repeat(1, deeplog.num_dimensions).view(-1)

# 多维的nn.NLLLoss
class MyCriterion(torch.nn.Module):
    def __init__(self):
        super(MyCriterion, self).__init__()

    def forward(self, input, target):
        # input: [batch_size, num_dimensions, output_size]
        # target: [batch_size, num_dimensions]
        # return: [batch_size, num_dimensions]
        # return torch.nn.functional.nll_loss(input, target)
        # return torch.nn.functional.nll_loss(input.view(-1, input.size(2)), target.view(-1))
        return torch.nn.functional.nll_loss(input.view(-1, input.size(2)), target.view(-1), ignore_index=-1)




def main(k1):
    # Train deeplog
    deeplog.fit(
        X          = X_train.view(X_train.shape[0],-1,X_train.shape[1]),
        y          = y_train,
        epochs     = 10,
        batch_size = 128,
        optimizer  = torch.optim.Adam,
        criterion=MyCriterion,
    )

    # 保存模型权重
    model_path = './weight-mul.pth'
    torch.save(deeplog.state_dict(), model_path)
    # return
    # deeplog.load_state_dict(torch.load(model_path))

    # Predict normal data using deeplog
    y_pred,_ = deeplog.predict(
        X = X_test.view(X_test.shape[0],-1,X_test.shape[1]),
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
    prediction = y_pred[:,:,0]
    # In case correct prediction was in top k, set prediction to correct prediction
    for column in range(1, y_pred.shape[1]):
        # Check if any value in the last dimension of y_pred matches y_true for the given column
        mask = (y_pred[:, column, :] == y_true[:, column][:, None]).any(axis=1)
        # Adjust prediction based on the mask
        prediction[mask] = y_true[:, column][mask]

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