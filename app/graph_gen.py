# importing the required modules
import matplotlib.pyplot as plt
import os

# req query db for the logged projects
# make function with project argument ?
# which queries:
# open / closed punches
# open / closed punches for system
# save png
# embed png in html


def index_plot(destination, data1):

    if len(data1) > 1:
        if data1[0] is not None:
            if data1[0][0] == 0:
                if data1[0] is not None:
                    y1 = data1[0][1]
                else:
                    y1 = 0

                if data1[1] is not None:
                    y2 = data1[1][1]
                else:
                    y2 = 0

            else:
                if data1[1] is not None:
                    y1 = data1[1][1]
                else:
                    y1 = 0

                if data1[0] is not None:
                    y2 = data1[0][1]
                else:
                    y2 = 0
    elif len(data1) == 1:
            if data1[0][0] == 0:
                if data1[0] is not None:
                    y1 = data1[0][1]
                    y2 = 0
                else:
                    y1 = 0
                    y2 = data1[0][1]

    else:
        y1 = y2 = 0

    # x axis values
    x = [0, 1]
    # corresponding y axis values
    y = [y1, y2]

    # plotting the points
    plt.bar(x, y)
    plt.xticks(x, ('open', 'closed'))

    # giving a title to my graph
    plt.title('Overall Punch Items')

    # function to show the plot
    os.remove(destination + 'dashboard_1.png')
    plt.savefig(destination + 'dashboard_1.png')
