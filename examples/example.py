# import DeepLog and Preprocessor
import torch
from deeplog              import DeepLog
from deeplog.preprocessor import Preprocessor

##############################################################################
#                                 Load data                                  #
##############################################################################

# Create preprocessor for loading data
preprocessor = Preprocessor(
    length  = 20,           # Extract sequences of 20 items
    timeout = float('inf'), # Do not include a maximum allowed time between events
)

# Load data from csv file
# X, y, label, mapping = preprocessor.csv("<path/to/file.csv>")
# Load data from txt file
X, y, label, mapping = preprocessor.text(
    path = "D:\my_projects\python\DeepLog\examples\data\elec-op-data-testing.txt",
    mapping= {i: i for i in range(0, 29)}
)
##############################################################################
#                                  DeepLog                                   #
##############################################################################

# Create DeepLog object
deeplog = DeepLog(
    input_size  = 30, # Number of different events to expect
    hidden_size = 64 , # Hidden dimension, we suggest 64
    output_size = 30, # Number of different events to expect
)

# Optionally cast data and DeepLog to cuda, if available
# deeplog = deeplog.to("cuda")
# X       = X      .to("cuda")
# y       = y      .to("cuda")

# 加载模型权重
model_path = 'D:\my_projects\python\DeepLog\examples\\new_weight-elec-oneline.pth'
# torch.save(deeplog.state_dict(), model_path)
# return
deeplog.load_state_dict(torch.load(model_path, map_location='cpu'))

# Train deeplog
# deeplog.fit(
#     X          = X,
#     y          = y,
#     epochs     = 10,
#     batch_size = 128,
# )

# Predict using deeplog
y_pred, confidence = deeplog.predict(
    X = X,
    k = 3,
)
print('------------------------------------')
print('预测结果如下：(每行的第一个列表表示滑动窗口读入的真实数据，第二个列表为三个可能性依次降低的下一个事件ID)')
for i in range(len(y_pred.numpy())):
    if i<20:
        continue # 跳过前20个元素的预测
    isGood = False
    if i==len(y_pred.numpy())-1:
        print(X.numpy()[i], y_pred.numpy()[i])
        continue
    for j in range(len(y_pred.numpy()[i])):
        if y_pred.numpy()[i][j]==X.numpy()[i+1][19]:
            # 预测结果存在与真实值匹配的值
            print(X.numpy()[i], y_pred.numpy()[i])
            isGood = True
            continue
    if isGood==False:
        print(X.numpy()[i], y_pred.numpy()[i], '预测异常')

print('shape: ', y_pred.numpy().shape)

# [[10 13  3  8 14 12  4  0  7]
#  [10 14 13  8 12  3  4  1  7]
# ...
# 预测输出为以上类型，每一行代表一条数据的预测概率，且上面的表示这两个数据属于编号为10这个类别的概率最高
# 属于其他类别13、3、8..。的概率依次递减。具体有多少列与设置的top-K有关
