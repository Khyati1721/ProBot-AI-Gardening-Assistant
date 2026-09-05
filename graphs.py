import os
import tempfile
import pandas as pd
import matplotlib.pyplot as plt


def graph_generator(df):
    """
    Generate up to 3 meaningful charts from a dataframe.
    Returns list of image paths.
    """

    images = []

    # Remove old charts
    for i in range(1, 4):
        if os.path.exists(f"chart{i}.png"):
            os.remove(f"chart{i}.png")

    try:
        categorical = df.select_dtypes(include=["object", "category"]).columns.tolist()
        numeric = df.select_dtypes(include=["number"]).columns.tolist()
        chart_no = 1

        if categorical and chart_no <= 3:
            col = categorical[0]
            plt.figure(figsize=(8, 5))
            df[col].value_counts().head(10).plot(kind="bar")
            plt.title(f"{col} Counts")
            plt.xlabel(col)
            plt.ylabel("Count")
            plt.xticks(rotation=45)
            plt.tight_layout()
            filename = f"chart{chart_no}.png"
            plt.savefig(filename)
            plt.close()
            images.append(filename)
            chart_no += 1

        if numeric and chart_no <= 3:
            col = numeric[0]
            plt.figure(figsize=(8, 5))
            df[col].plot(kind="hist", bins=20)
            plt.title(f"Distribution of {col}")
            plt.xlabel(col)
            plt.tight_layout()
            filename = f"chart{chart_no}.png"
            plt.savefig(filename)
            plt.close()
            images.append(filename)
            chart_no += 1

        if len(numeric) >= 2 and chart_no <= 3:
            x = numeric[0]
            y = numeric[1]
            plt.figure(figsize=(8, 5))
            plt.scatter(df[x], df[y])
            plt.xlabel(x)
            plt.ylabel(y)
            plt.title(f"{x} vs {y}")
            plt.tight_layout()
            filename = f"chart{chart_no}.png"
            plt.savefig(filename)
            plt.close()
            images.append(filename)

        return images
    
    except Exception as e:
        print(e)
        return []