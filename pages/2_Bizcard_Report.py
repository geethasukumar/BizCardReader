import mysql.connector
from mysql.connector import Error
import pandas as pd
import streamlit as st
import base64
import io
from PIL import Image
import io

# MySQL DB connect
def mysql_db_connect():
   
    hostname= "localhost"
    database= "bizcard_ocr"
    username= "root"
    password= ""
    connection = None
    try:
        connection = mysql.connector.connect(
            host=hostname,
            database=database,
            user=username,
            password=''
        )
        if connection.is_connected():
            
            return connection
    except Error as e:
        st.write(f"Error: {e}")
        st.write('Error mysql_db_connect - MYSQL DB connection failed!!')
      
   
#Card details retrieval 
def retrieve_bizcard_data(connection):
    
    try:
        cursor = connection.cursor()
            
        cursor.execute('select * from bizcard_data')
    
        # Fetch all the rows returned by the query
        rows = cursor.fetchall()

        # Get the column names from the cursor description
        columns = [desc[0].upper().replace('_',' ') for desc in cursor.description]

        # Create a Pandas DataFrame from the query result
        st.session_state.bizcard_df = pd.DataFrame(rows, columns=columns)
        
        #df['selected'] = 0;
        st.session_state.bizcard_df['CARD IMAGE'] = 'data:image/png;base64,' + st.session_state.bizcard_df['CARD IMAGE']
        
             
                
        # Move last column to the first
        temp_cols=st.session_state.bizcard_df.columns.tolist()
        new_cols=temp_cols[-1:] + temp_cols[:-1]
       
        st.session_state.bizcard_df=st.session_state.bizcard_df[new_cols]

        st.session_state.bizcard_df.insert(0, "Select", False)
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
  
  
  
# show the bizcard  
def show_bizcard_data(connection, data_df): 
      
        edited_df = st.data_editor(
            data_df,
            column_config={
                "Select": st.column_config.CheckboxColumn(
                    "Select",
                    help="Select to delete record",
                    default=False,
                ),
                "CARD IMAGE": st.column_config.ImageColumn(
                "Preview Card", help="Streamlit app preview screenshots"
                )
               
            },
           
            hide_index=True,
        )
        
        # Filter the dataframe using the temporary column, then drop the column
        selected_rows = edited_df[edited_df.Select]
        rows_to_drop = selected_rows.drop('Select', axis=1)
        
        if st.button("Delete Card(s)"):
            try:
                cursor = connection.cursor()
                for idx in rows_to_drop['CARD ID']:
                    
                    del_q='delete from bizcard_data where card_id=%s'
                    cursor.execute(del_q,[idx])
                    st.write('Card deleted!!!')
                    
                connection.commit()
                
               
            except Error as e:
                print(f"Error: {e}")
            finally:
                cursor.close()
            connection.close()    
                
            # To refresh the page after re-run    
            st.experimental_rerun()   
       
        
        
# Main program definition       
def main():

    st.title ("BizCardX: Business Card Data with OCR")
    st.markdown ("Business Card Data Report")
    st.markdown("By Geetha Sukumar")
    m = st.markdown("""
                    <style>
                    div.stButton > button:first-child {
                        background-color: red;
                        color:#ffffff;
                    }


                    </style>""", unsafe_allow_html=True)
                    
                    
    connection = mysql_db_connect()
    retrieve_bizcard_data(connection)
    show_bizcard_data(connection,st.session_state.bizcard_df)
    connection.close()
  

if __name__ == "__main__":
    main()
