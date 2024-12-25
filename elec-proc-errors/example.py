import argparse
import torch
from deeplog              import DeepLog
from deeplog.preprocessor import Preprocessor

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run DeepLog model prediction.")
    parser.add_argument(
        "file_path",
        type=str,
        help="Relative path to the input txt file containing the dataset.",
    )
    args = parser.parse_args()

    # Extract file path from arguments
    file_path = args.file_path
    ##############################################################################
    #                                 Load data                                  #
    ##############################################################################

    # Create preprocessor for loading data
    preprocessor = Preprocessor(
        length  = 20,           # Extract sequences of 20 items
        timeout = float('inf'), # Do not include a maximum allowed time between events
    )

    # Load data from txt file
    X, y, label, mapping = preprocessor.text(
        path = file_path,
        mapping= {i: i for i in range(0, 99)}
    )

    ##############################################################################
    #                                  DeepLog                                   #
    ##############################################################################

    # Create DeepLog object
    deeplog = DeepLog(
        input_size  = 100, # Number of different events to expect
        hidden_size = 64 , # Hidden dimension, we suggest 64
        output_size = 100, # Number of different events to expect
    )

    # Optionally cast data and DeepLog to cuda, if available
    # deeplog = deeplog.to("cuda")
    # X       = X      .to("cuda")
    # y       = y      .to("cuda")

    # Load model weights
    model_path = './weight-proc-errors.pth'
    deeplog.load_state_dict(torch.load(model_path, map_location='cpu'))

    # Predict using deeplog
    y_pred, confidence = deeplog.predict(
        X = X,
        k = 3,
    )

    print('------------------------------------')
    print('预测结果如下：(每行的第一个列表表示滑动窗口读入的真实数据，第二个列表为三个可能性依次降低的下一个事件ID)')
    for i in range(len(y_pred.numpy())):
        if i < 20:
            continue # Skip predictions for the first 20 elements
        isGood = False
        if i == len(y_pred.numpy()) - 1:
            print(X.numpy()[i], y_pred.numpy()[i])
            continue
        for j in range(len(y_pred.numpy()[i])):
            if y_pred.numpy()[i][j] == X.numpy()[i + 1][19]:
                # Prediction matches the true value
                print(X.numpy()[i], y_pred.numpy()[i])
                isGood = True
                continue
        if not isGood:
            print(X.numpy()[i], y_pred.numpy()[i], '预测异常')

    print('shape: ', y_pred.numpy().shape)

if __name__ == "__main__":
    main()
