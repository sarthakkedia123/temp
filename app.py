import streamlit as st
import pandas as pd
import pickle as pkl
st.title('Stock Matcher')

all_quality=pkl.load(open('all_quality.pkl','rb'))
all_quality=list(pd.DataFrame(all_quality)['id'].values)
all_quality=[str(i) for i in all_quality]

sheet_id = "1SKaE617b7LR0oo8npsl9JuH_V6GGk3vVQzqPtW1r9mw"
sheet_name = "A_J_Entry"

gsheet_url = pd.ExcelFile(f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx")
df = pd.read_excel(gsheet_url,usecols=['A/J','QUANTITY','QUALITY','WEAVER/PROCESS','DATE','CHECK'])
df.drop(['CHECK'],axis=1,inplace=True)

#Converting float values of the QUALITY into int, keeping string values as it is, and then whole quality values into string
#Eg. 1100.00 -> 1100 -> '1100'

def func(x):
    try:
        return int(x)
    except:
        return x

for i in range(len(df)):
    df.loc[[i],['QUALITY']]=func(df.loc[i]['QUALITY'])
    df.loc[[i],['QUALITY']]=str(df.loc[i]['QUALITY'])

df['DATE']=df['DATE'].astype(str)

#Aavak Dataframe
#A_entry: consists of Unique Aavak Entries

df_A=pd.DataFrame(df[df['A/J']=='A'])
df_A.reset_index(drop=True,inplace=True)
df_A.columns=['A/J','A_QUANTITY','QUALITY','WEAVER/PROCESS','DATE']

#Unique Aavak entries
A_entry=list((df_A['QUALITY'].value_counts().index))

#Aavak entry not in all_quality: a
a=[]
for i in range(len(all_quality)):
    if(all_quality[i] not in A_entry):
        a.append(all_quality[i])

a_final=df_A.groupby(by='QUALITY')[['A_QUANTITY']].sum().transpose()
for i in range(len(a)):
    a_final.loc[['A_QUANTITY'],[a[i]]]=0

#Javak Dataframe
#J_entry: consists of Unique Aavak Entries

df_J=pd.DataFrame(df[df['A/J']=='J'])
df_J.reset_index(drop=True,inplace=True)
df_J.columns=['A/J','J_QUANTITY','QUALITY','WEAVER/PROCESS','DATE']

#Unique Javak entries
J_entry=list((df_J['QUALITY'].value_counts().index))

#Javak entry not in all_quality: b
b=[]
for i in range(len(all_quality)):
    if(all_quality[i] not in J_entry):
        b.append(all_quality[i])

j_final=(df_J.groupby(by='QUALITY')[['J_QUANTITY']].sum().transpose())

for i in range(len(b)):
    j_final.loc[['J_QUANTITY'],[b[i]]]=0

prev_stock=pkl.load(open('prev_stock.pkl','rb'))
prev_stock=pd.DataFrame(prev_stock)
prev_stock.columns=[str(i) for i in prev_stock]

#making the final dataframe: final_df

final_df=pd.concat([a_final,prev_stock],axis=0)
final_df.loc['SUM_TOTAL']=final_df.loc['A_QUANTITY'][:]+final_df.loc['PREVIOUS_STOCK'][:]
final_df=pd.concat([final_df,j_final])
final_df.loc['BALANCE']=final_df.loc['SUM_TOTAL'][:]-final_df.loc['J_QUANTITY'][:]
final_df=final_df.transpose()
sum_total=pd.DataFrame(final_df.sum()).transpose()
sum_total.index=['Total']
final_df_with_total=pd.concat([final_df,sum_total])

date=pd.Timestamp("today").strftime("%d/%m/%Y")
name='final_df_with_total '+date+'.xlsx'
name=name.replace('/','_')

#final_df_with_total.to_excel('/Users/Hp/Desktop/office/Stock Matcher/cloth/weekly_data/'+name)
st.dataframe(final_df_with_total)

@st.cache_data
def convert_df(data_frame):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return data_frame.to_csv().encode('utf-8')

csv = convert_df(final_df_with_total)

st.download_button(
    label="Download data as CSV",
    data=csv,
    file_name='final_df_with_total_'+date+'.csv',
    mime='text/csv'
)

st.text('Do you want to update the previous stock? Type Y/N')
if st.button('Yes'):
    prev_stock=pd.DataFrame(final_df['BALANCE']).transpose()
    prev_stock.index=['PREVIOUS_STOCK']
    #prev_stock.to_excel(r'C:/Users/Hp/Desktop/office/Stock Matcher/cloth/prev_stock.xlsx',index=False)
    pkl.dump(prev_stock.to_dict(),open('prev_stock.pkl','wb'))
    st.text('Previous Stock Updated Successfully')
if st.button('No '):
    st.text('Thank You..no updation has taken place')



