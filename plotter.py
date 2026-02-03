import matplotlib.pyplot as plt
import pandas as pd


def main():

    df = pd.read_csv("schelling_stats.csv")

    plt.figure(figsize=(10,6))

    plt.plot(df['Threshold'], df['Segregation_Percentage'], marker='o', linestyle='-', color='b')

    plt.title("Schelling's Model (Threshold % vs Segregation)")
    plt.xlabel("Threshold")
    plt.ylabel("Final Segregation")

    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()