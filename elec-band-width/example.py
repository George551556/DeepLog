import argparse
import torch
import math
import mysql.connector
from datetime import datetime
from deeplog              import DeepLog
from deeplog.preprocessor import Preprocessor

# 数据库配置信息
db_config = {
    'host': '127.0.0.1',       # 数据库主机地址
    'user': 'user',   # 数据库用户名
    'password': 'abc', # 数据库密码
    'database': 'karen' # 数据库名
}
def add_data_to_mysql(db_config, sdpid, curScore, flag):
    print('start insert into db...')
    # 连接到MySQL数据库
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    # data Resolve
    
    curTime = datetime.now()
    lastTime = datetime.now()
    
    # SQL 插入语句
    sql = '''INSERT INTO elec_health (sdpid, curScore, curTime, lastTime, flag)
             VALUES (%s, %s, %s, %s, %s)'''
    
    # 执行插入操作
    cursor.execute(sql, (sdpid, curScore, curTime, lastTime, flag))
    
    # 提交事务
    conn.commit()
    
    # 关闭游标和连接
    cursor.close()
    conn.close()


def healthScore(t, f, logicFalse):
    logicT = t+f-logicFalse
    print('T/F :', t, f, '  logic T/F :', logicT, logicFalse)
    print('直接比例结果：%.2f'%(t/(t+f)))
    print('逻辑比例结果：%.2f'%(logicT/(t+f)))
    
    return round(t/(t+f)*100, 1), round(logicT/(t+f)*100, 1) # 返回百分制结果
    # numerator = math.exp(t)
    # denominator = numerator+math.exp(f)
    # print('逻辑比例结果：%.2f'%(numerator/denominator))

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

    # return when num of data is small
    if len(X.numpy())<30:
        print('有效数据不足')
        return

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
    model_path = './weight-band-width.pth'
    deeplog.load_state_dict(torch.load(model_path, map_location='cpu'))

    # Predict using deeplog
    y_pred, confidence = deeplog.predict(
        X = X,
        k = 3,
    )

    # print('------------------------------------')
    # print('预测结果如下：(每行的第一个列表表示滑动窗口读入的真实数据，第二个列表为三个可能性依次降低的下一个事件ID)')
    retTrue = 0 
    retFalse = 0
    # 用一个滑动窗口长度为3，只有连续预测错误3个及以上时才认为产生错误，这样的结果记为逻辑错误数logicFalse
    lglth = 3
    widws = [True] * lglth
    logicFalse = 0

    # 逐个遍历预测
    for i in range(len(y_pred.numpy())):
        if i < 20:
            continue # Skip predictions for the first 20 elements
        isGood = False
        if i == len(y_pred.numpy()) - 1:
            # print(X.numpy()[i], y_pred.numpy()[i])
            continue
        for j in range(len(y_pred.numpy()[i])):
            if y_pred.numpy()[i][j] == X.numpy()[i + 1][19]:
                # Prediction matches the true value
                # print(X.numpy()[i], y_pred.numpy()[i]) # 输出原始数据与预测结果
                isGood = True
                retTrue += 1
                break
        if not isGood:
            # print(X.numpy()[i], y_pred.numpy()[i], '预测异常') # 输出原始数据与预测结果
            retFalse += 1
        
        # update slide window
        for i in range(lglth-1):
            widws[i] = widws[i+1]
        widws[lglth-1] = isGood
        logicFalse += 1
        for i in range(len(widws)):
            if widws[i]==True:
                logicFalse -= 1
                break

    # get health My Score
    _, lgScore = healthScore(retTrue, retFalse, logicFalse)
    # insert into db
    add_data_to_mysql(db_config, 3, lgScore, 1)
    # print('shape: ', y_pred.numpy().shape)

if __name__ == "__main__":
    main()
