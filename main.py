from run.agent import ag
import pandas as pd
df = pd.read_excel(r"C:\Users\kbbudak\Desktop\Sayım FarklarıTest.xlsx")
df["ACIKLAMA"] = ''
df["GRUBU"] = ''
for i in df.index:
    df_grup = ag.run_query(f"SELECT ACIKLAMA,GRUBU FROM IASMATBASIC "
                      f"WHERE MATERIAL ='{df['Malzeme'][i]}' AND COMPANY = '01'")
    try:
        df["ACIKLAMA"][i] = df_grup["ACIKLAMA"][0]
        df["GRUBU"][i] = df_grup["GRUBU"][0]
    except IndexError:
        print("bum")



df_prices = pd.read_excel(r"C:\Users\kbbudak\Desktop\fiyatlar.xlsx")
df_prices.columns = ["Malzeme","Price"]
df_final = df.merge(df_prices,how="left",on="Malzeme")
# mean_val = df_final[(df_final["GRUBU"] == 'VALFPLK') & (df_final["Price"].notna())]["Price"].mean()
# mask = (df_final["Price"].isna()) & (df_final["GRUBU"] == 'VALFPLK')
# df_final.loc[mask, "Price"] = df_final.loc[mask, "Price"].fillna(mean_val)

df_final["Price"] = df_final.groupby("GRUBU")["Price"].transform(lambda x: x.fillna(x.mean())).fillna(0)
df_final["Total_Price"] = df_final["Price"] * df_final["Fark"]
df_sum = df_final.groupby(["ACIKLAMA","GRUBU"]).agg({"Fark":"sum","Total_Price":"sum"})
df_sum.to_excel(r"C:\Users\kbbudak\Desktop\sayim raporu özet.xlsx")
df_final.to_excel(r"C:\Users\kbbudak\Desktop\sayim raporu.xlsx")