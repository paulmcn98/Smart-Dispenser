import mysql.connector
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
#This simpe neural network predicts the time in minutes after a dispenser is used until the next time it is used and not ignored
class FeedForward:

    def __init__(self, input = 2, hidden = 3, output = 1, learning_rate = 0.3):
        # number of nodes for each layer
        self.input_nodes = input
        self.hidden_nodes = hidden
        self.output_nodes = output
        
        # weight matrices
        # wih = weights from input(i) to hidden(h)
        # who = weights from hidden(i) to output(o)
        self.wih = np.random.randn(self.input_nodes, self.hidden_nodes).T
        self.who = np.random.randn(self.hidden_nodes, self.output_nodes).T

        # learning rate
        self.learn = learning_rate

    # sigmoid activation function
    def sigmoid(self, x):
        return 1/(1+np.exp(-x))

    def forward(self, input):
        # matrix dot product of weight wih and input
        # to produce the input for the hidden layer
        hidden_input = np.dot(self.wih, input)

        # to produce output of hidden layer
        hidden_output = self.sigmoid(hidden_input)
        
        # matrix dot product of weight who and output from
        # hidden layer to produce the input for the output layer
        final_input = np.dot(self.who, hidden_output)

        # to produce output of output layer
        final_output = self.sigmoid(final_input)

        return final_output, hidden_output

    def error(self, target, final_output):
        # error is the distance from target and prediction
        error = target - final_output
        # hidden error is the dot product of the weight who transposed
        # and the error calcualted above
        hidden_error = np.dot(self.who.T, error) 

        return error, hidden_error

    def backpropagation(self, input, hidden_output, final_output, error, hidden_error):
        # update the weight who with errors previously calculated
        self.who += self.learn * np.dot((error * final_output * (1.0 - final_output)), hidden_output.T)
        
        # update the weight wih with errors previously calculated
        self.wih += self.learn * np.dot((hidden_error * hidden_output * (1.0 - hidden_output)), input.T)
        
    def train(self, input, target):
        # reshape input and target into 2d matrices
        input = np.array(input, ndmin=2).T
        target = np.array(target, ndmin=2).T

        # forward pass throught network
        final_output, hidden_output = self.forward(input)

        # get errors from forward pass result
        error, hidden_error = self.error(target, final_output)

        # backpropagate the errors through the network, updating weights
        self.backpropagation(input, hidden_output, final_output, error, hidden_error)

        # return training results
        return final_output

    def test(self, input):
        # transpose input
        input = input.T
        # perform one forward pass through the network to get predictions
        final_output, hidden_output = self.forward(input)

        # return prediction
        return final_output


def get_minutes(device, result):
	#Gather all dates from devices in database
    dates = [] 
    for row in result:
    	if row[0] == device:
    		if row[1] not in dates:
    			dates.append(row[1])

    #Gather times and convert to minutes for training the neural network
    times = []
    for date in dates:
    	daytimes = []
    	for row in result:
    		if row[0] == device and row[1] == date and row[3] == 1:
    			daytimes.append(row[2])
    	if len(daytimes)%2 != 0:
    		tmp = []
    		daytimes.pop()
    		for time in daytimes:
    			hour_in_minutes = int(time[:2])*60
    			minutes = int(time[3:])
    			tmp.append(hour_in_minutes + minutes)
    			tmp = sorted(tmp)
    		for time in tmp:
    			times.append(time) 
    	else:
    		tmp = []
    		for time in daytimes:
    			hour_in_minutes = int(time[:2])*60
    			minutes = int(time[3:])
    			tmp.append(hour_in_minutes + minutes)
    			tmp = sorted(tmp)
    		for time in tmp:
    			times.append(time)

    return times

#this function removes values less than zero which is caused by a the jump from one date to the next
def remove(values):
    new_values = []
    values_less_than_zero = 0
    for i in range(0, len(values)):
        if values[i] >= 0:
            new_values.append(values[i])
    return new_values

def plot(actual, train, test):
    actual = np.diff(actual)
    actual = np.array(actual).tolist()
    actual = remove(actual)
    #plot the actual values
    plt.plot(actual, label="Actual")
    train = np.diff(train)
    train = np.array(train).tolist()
    train = remove(train)
    #plot the training predictions
    plt.plot(train, label="Train prediction")
    test = np.diff(test)
    test = np.array(test).tolist()
    test = remove(test)
    #connect training and test lines
    test.insert(0, train[-1])
    #plot the test predictions
    plt.plot([x for x in range(len(train)-1, len(train) + len(test)-1)], test, label="Test prediction")
    plt.xlabel("Number of dispenses")
    plt.ylabel("Minutes until next dispenal")
    plt.title("Dispenser Prediction")
    plt.legend()
    plt.grid()
    plt.show()

def mape(actual, prediction): 
    # mean absolute percentage error (MAPE)
    return np.mean(np.abs((actual - prediction) / actual)) * 100


def main():
	#connect to mysql
    mydb = mysql.connector.connect(
    	host="localhost",
    	user="root",
    	passwd="intragroup16",
    	database="dispenserdb"
    )
    mycursor = mydb.cursor()
    
    #mySQL query
    mycursor.execute("SELECT device_id, date, time, used FROM dispenserdb.dispenser")
    result = mycursor.fetchall()

    #Gather all devices ids in database
    device_ids = [] 
    for row in result:
    	if row[0] not in device_ids:
    		device_ids.append(row[0])

    #Pick one dispenser to perform machine learning on
    device = device_ids[0]

    times = get_minutes(device, result)

    # X = times of previous 2 dispensals
    # y = time of following dispenal
    X = [[times[i-2], times[i-1]] for i in range(len(times[:102])) if i >= 2]
    y = [[i] for i in times[2:102]]

    X = np.array(X, dtype=float)
    y = np.array(y, dtype=float)

    assert len(X) == len(y)

    #Normalise the data
    X = np.divide(X, 1140)
    y = np.divide(y, 1140)

    #create neural network
    NN = FeedForward()

    #number of training cycles
    epochs = 100

    #train the neural network
    for e in range(epochs):
        for n in X:
            output = NN.train(X, y)

    #De-normalise data
    output = np.dot(output, 1140)
    y = np.dot(y, 1140)
    #transpose the numpy array
    output = output.T

    #change data type so it can be plotted
    predictions = pd.DataFrame(output)

    #print mape accuracy of the training data
    print("Training MAPE accuracy of minutes between dispensals: {:.4f}%".format(100 - mape(y, output)))

    #input = times of previous 2 dispensals
    #test_target = time of following dispenal
    input = [[times[i-2], times[i-1]] for i in range(102, 152)]
    test_target = [[i] for i in times[102:152]]

    assert len(input) == len(test_target)

    input = np.array(input, dtype=float)
    test_target = np.array(test_target, dtype=float)
 
    #Normalise data
    input = np.divide(input, 1140)
    #test predictions
    test = NN.test(input)

    #De-normalise data
    input = np.dot(input, 1140)
    test = np.dot(test, 1140)

    #transpose the numpy array
    test = test.T

    print("Test MAPE accuracy of minutes between dispensals: {:.4f}%".format(100 - mape(test_target, test)))
    
    #convert array to list
    output = np.array(output).tolist()
    train = []
    for e in output:
        train.append(e[0])

    #convert array to list
    test = np.array(test).tolist()
    test_results = []
    for e in test:
        test_results.append(e[0])
    #plot the results
    plot(times[2:152], train, test_results)

if __name__ == '__main__':
	main()