import pandas as pd
import numpy
import difflib
import os

if __name__ == "__main__":
    '''df = pd.DataFrame()
    df = pd.read_csv("result.csv")
    element = "Funerale Milano Città A 1.254€ | Contattaci Telefonicamente.‎"
    col = "presence at 5 km"
    print(df.loc[df["website title"] == element, col])
    df.loc[df["website title"] == element, col] = ["merda"]
    print(df.loc[df["website title"] == element, col])'''
    '''cpt = sum([len(files) for r, d, files in os.walk("CSVs")])
    print(cpt)'''

    '''set_one = {'Pompe Funebri | Tortarolo &amp; Conti | pompefunebritortaroloeconti.com\u200e', 'Pompe Funebri | Del Buono | pompefunebridelbuono.com\u200e', 'Pompe Funebri | Onoranze Funebri Ferro | pompefunebriferrovarazze.it\u200e', 'Onoranze Funebri | Pompe Funebri Liguri | PompeFunebriLiguri.com\u200e'}
    set_two = {'Pompe Funebri | Tortarolo &amp; Conti | pompefunebritortaroloeconti.com\u200e', 'Pompe Funebri | Del Buono | pompefunebridelbuono.com\u200e', 'Pompe Funebri | Onoranze Funebri Ferro | pompefunebriferrovarazze.it\u200e', 'Onoranze Funebri | Pompe Funebri Liguri | PompeFunebriLiguri.com\u200e'}
    print(set_one.intersection(set_two))
    print(len(set_one.intersection(set_two)))'''

    '''df = pd.read_csv("result.csv")
    df.set_index("datetime")
    df.reset_index()

    element = "Pompe Funebri | Del Buono | pompefunebridelbuono.com‎‎‎".strip("\u200e")
    element = element + ("\u200e")
    km = "presence at 5 km"

    print(df.loc[(df["website title"] == element) & (df["datetime"] == "2019-03-22 14:06:58.486228"), km])
    df.loc[df["website title"] == element, km] = ["fiori"]
    print(df[km])'''

    df1 = pd.DataFrame([['ABC', 2018, 5, 2, 3],
                        ['ABC', 2017, 52, 21, 31], ['ABC', 2016, 15, 12, 13],
                        ['ABC', 2015, 25, 22, 3]],
                       columns=['Player', 'Year', 'GS', 'G', 'MP'])

    df2 = pd.DataFrame([["ABC", 2017]], columns=['Player', 'Year'])

    # first sort the DataFrames
    df1.sort_index(inplace=True)
    df2.sort_index(inplace=True)

    # prepare the Booleans responses
    check_1 = df1["Player"] == df2["Player"].to_list()[0]
    years_list = (int(df2["Year"].tolist()[0])-i for i in range(0, 3))
    check_2 = df1.Year.map(int).isin(years_list)

    # apply the masks
    print(df1[check_1 & check_2])

